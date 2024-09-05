# ------------------------------------------------------
# ---------------------- main.py -----------------------
# ------------------------------------------------------
from PyQt5 import QtWidgets, uic, QtCore
from datetime import datetime
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from fabric import Connection
import traceback
import sys
import ui.rsc
import os
import numpy as np

from functions import measure

# Initalize GPIO pins on raspberry pi
try:
    import RPi.GPIO as GPIO
    from drivers.mks import MFC
    from drivers.temperature import TC
    from drivers.xgs600 import XGS600Driver
    from drivers.ultraflex import UltraHeat
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    pins = [2, 3, 4, 5, 6, 16, 17, 12, 13]
    GPIO.setup(pins, GPIO.OUT)
    
except:
    import emulators.GPIO as GPIO
    from emulators.mks import MFC
    from emulators.temperature import TC
    from emulators.xgs600 import XGS600Driver
    from emulators.ultraflex import UltraHeat


class GasControl(QtWidgets.QMainWindow):
    def __init__(self):
        super(GasControl, self).__init__()

        # Load the UI Page - added path too
        # ui_path = os.path.dirname(os.path.abspath(__file__))
        # uic.loadUi(os.path.join(ui_path, "ui/gas-UI.ui"), self)
        uic.loadUi("ui/gas-UI.ui", self)

        # Which gas connected to which (GPIO Pin)/(Relay-1) .
        self.gas_valves = {
            'Ar': {'relay': 4, 'button': self.ar_valve},
            'H2': {'relay': 6, 'button': self.h2_valve},
            'N2': {'relay': 5, 'button': self.n2_valve},
            'NH3': {'relay': 3, 'button': self.nh3_valve},
            'CO': {'relay': 2, 'button': self.co_valve},
            'V1': {'relay': 13, 'button': self.valve1},
            'V2': {'relay': 12, 'button': self.valve2},
            'V3': {'relay': 16, 'button': self.valve3},
            'V4': {'relay': 17, 'button': self.valve4}
        }

        # Mass Flow controller settings
        self.flow_controllers ={
            'Ar': {'addr': 231, 'flow_input': self.ar_flow_input, 'flow_read': self.ar_flow,'info': self.ar_info},
            'H2': {'addr': 233, 'flow_input': self.h2_flow_input, 'flow_read': self.h2_flow,'info': self.h2_info},
            'N2': {'addr': 232, 'flow_input': self.n2_flow_input, 'flow_read': self.n2_flow,'info': self.n2_info},
            'NH3': {'addr': 234, 'flow_input': self.nh3_flow_input, 'flow_read': self.nh3_flow,'info': self.nh3_info},
            'CO': {'addr': 230, 'flow_input': self.co_flow_input, 'flow_read': self.co_flow,'info': self.co_info},
        }

        # Initializing devices
        # Thermocouple settings - should be implemented in GUI
        #self.tcs = TC(CS_PINS=['D8'], tc_type='N')
        self.tcs = TC()

        self.m = MFC(port='/dev/ttyUSB0')
        self.xgs600 = XGS600Driver(port='/dev/ttyUSB2')
        self.psu = UltraHeat(port='/dev/ttyUSB1')

        # SSH Connections - Requires key authentication
        # See:
        # https://www.digitalocean.com/community/tutorials/how-to-configure-ssh-key-based-authentication-on-a-linux-server
        # All scripts used are in the folder magpi
        self.c_magpi003 = Connection('pi@magpi003') # Relay for pressure controller
        self.c_magpi002 = Connection('pi@magpi002') # Pressure Controller

        # Multithread control
        self.threadpool = QtCore.QThreadPool()

        # Timer function should run on its own thread now
        self.update_timer_ms = 2000 # Maybe make interval customizable in GUI
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_values)
        self.timer.start(self.update_timer_ms)

        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(self.update_plot)

        plot_toolbar = NavigationToolbar(self.plot_area.canvas, self)
        self.plot_area.layout().addWidget(plot_toolbar)

        # Setting current date into filename
        self.filename_input.setText(datetime.today().strftime('%Y-%m-%d'))

        # Menubar actions
        self.action_RS232_Settings.triggered.connect(self.open_rs232_options)
        self.rs232options = RS232Options()

        self.actionUpdate_Values.triggered.connect(self.update_control)

        # Checking valve state for valve located before pressure controller (controlled by magpi003)
        result = self.c_magpi003.run("/home/pi/osa/env/bin/python /home/pi/osa/change_relay_state.py r 1") # Directory should be changed to new git folder to get updates
        self.pc_valve.setChecked(result.stdout.strip('\n') == 'True')
        self.pc_valve.clicked.connect(self.switch_pc_valve)

        # Checking valve/relay state for button & make it possible to change valve state.
        for gas_valve in self.gas_valves.values():
            btn, relay = gas_valve['button'], gas_valve['relay']

            # Checks the GPIO to see which valves are opened
            btn.setChecked(not GPIO.input(relay))
            # Open/closes valve on button press
            btn.clicked.connect(lambda checked, relay=relay: self.toggle_valve(checked, relay))

        # Bypass / Reactor shortcut
        self.btn_reactor.clicked.connect(lambda: self.open_valves('reactor'))
        self.btn_bypass.clicked.connect(lambda: self.open_valves('bypass'))

        # Information about mass flow controllers
        for mfc in self.flow_controllers.values():
            addr, info = mfc['addr'], mfc['info']
            info.setText(self.m.information(addr))

        # Setting the flow from input fields
        self.pushButton_set_flows.clicked.connect(self.set_flow)

        # Setting downstream pressure on pressure controller
        self.set_pressure_btn.clicked.connect(self.set_backpressure)

        # Starting measurement
        self.start_measurement_btn.clicked.connect(self.start_measurement)

        # Stopping measurement before time is up
        self.stop_btn.clicked.connect(self.stop)

    def toggle_valve(self, checked, relay):
        if checked:
            GPIO.output(relay, GPIO.LOW)
            self.write_output(f'Opened relay {relay}')
        else:
            GPIO.output(relay, GPIO.HIGH)
            self.write_output(f'Closed relay {relay}')

    def open_valves(self, path):
        if path == 'bypass':
            remainder = 1
        elif path == 'reactor':
            remainder = 0
        else:
            raise Exception('Incorrect gas path')

        for gas_valve in self.gas_valves.keys():
            if 'V' not in gas_valve:
                continue
            btn = self.gas_valves[gas_valve]['button']
            relay = self.gas_valves[gas_valve]['relay']
            if int(gas_valve[-1]) % 2 == remainder:
                GPIO.output(relay, GPIO.LOW)
                btn.setChecked(True)

            else:
                GPIO.output(relay, GPIO.HIGH)
                btn.setChecked(False)

        self.write_output(f'Valves have been opened through {path}')

    def switch_pc_valve(self, checked):
        # Current state - use to check if the state has changed during the runtime of the GUI
        result = self.c_magpi003.run("/home/pi/osa/env/bin/python /home/pi/osa/change_relay_state.py r 1")
        opened = result.stdout.strip('\n') == 'True'

        # It should open the relay if it is checked
        if checked and (not opened):
            self.c_magpi003.run("/home/pi/osa/env/bin/python /home/pi/osa/change_relay_state.py w 1")
            self.write_output('Pressure Control valve opened')

        # Close it otherwise
        elif not checked and opened:
            self.c_magpi003.run("/home/pi/osa/env/bin/python /home/pi/osa/change_relay_state.py w 1")
            self.write_output('Pressure Control valve closed')

    def set_flow(self):
        console_output = 'MFC has been:\n'
        for mfc in self.flow_controllers.values():
            addr, flow_input = mfc['addr'], mfc['flow_input']
            self.m.set_flow(flow_input.value(), addr)
            console_output += f'\t\t{addr} has been set to {flow_input.value()} mL/min\n'

        self.write_output(console_output)

    def set_backpressure(self):
        pressure = self.set_pressure_input.value()
        self.c_magpi002.run(f"/home/pi/VSM-gas-control/venv/bin/python /home/pi/set_pressure_PC.py {pressure}")

        self.write_output(f'Downstream pressure set to {pressure} torr')

    def update_control(self, checked):
        if not checked:
            self.timer.stop()
        else:
            self.timer.start(self.update_timer_ms)

    def update_values(self):
        # Setting up thread and signals
        worker = Worker(self._update_values)

        # Start thread
        self.threadpool.start(worker)

    def _update_values(self):
        # Updating MFC flow values
        for mfc in self.flow_controllers.values():
            addr, flow_read= mfc['addr'], mfc['flow_read']
            flow = self.m.read_flow(addr)
            flow_read.setText('<span style=" font-weight:600; color:#1fa208;">'+f'{flow}'+'</span>')

        # Updating QMS pressure
        p = self.xgs600.read_pressure('I1')
        punit = self.xgs600.read_pressure_unit()

        self.qms_pressure_label.setText(f'{p} {punit}')

        # Update downstream pressure
        result = self.c_magpi002.run("/home/pi/VSM-gas-control/venv/bin/python /home/pi/read_pressure_PC.py")
        pressure = result.stdout.strip('\n')
        if pressure != 'N/A torr':
            self.downstream_pressure_label.setText(f'{pressure}')

        # Update PSU info
        current = self.psu.get_current()
        freq = self.psu.get_frequency()

        self.psu_frequency_label.setText(f'{float(freq)/1000} kHz')
        self.psu_current_label.setText(f'{current} A')

    def exp_done(self):
        # self.exp_running_flag = False
        with open('running_flag', 'w') as f:
            f.write('0')
        self.plot_timer.stop()

    def start_measurement(self):
        with open('running_flag', 'r') as f:
            exp_running_flag = bool(int(f.read()))
        if exp_running_flag:
            self.write_output('Measurement already running', error_flag=True)
            return

        self.plot_timer.start(200)

        # Uses external file to follow if experiment is running
        with open('running_flag', 'w') as f:
            f.write('1')

        # Setting up file
        filename = self.filename_input.text() + '.txt'
        header = 'Time [s]\t'
        #T_header = "\t".join(['T%i [degC]' % i for i in range(len(self.tcs))])
        T_header = "Temperature [degC]"
        with open(filename, 'w') as file:
            file.write(header+T_header + "\n")

        # Parameters

        # Setting up thread and signals
        worker = Worker(measure, filename=filename, tcs=self.tcs)
        worker.signals.result.connect(self.write_output)
        worker.signals.error.connect(
            lambda: self.write_output('Measurement Failed - See print output for more details', error_flag=True))
        worker.signals.finished.connect(self.exp_done)

        # Start thread
        self.threadpool.start(worker)

        self.write_output(f'Measurement <span style="font-weight: 600;">{filename[:-4]}</span> started')

    def stop(self):
        with open('running_flag', 'w') as f:
            f.write('0')

    def write_output(self, line, error_flag=False):
        line = datetime.today().strftime('%Y-%m-%d %H:%M:%S')+'  '+line

        if error_flag:
            line = '<span style=" color:#ff0000;">'+line+'</span>'

        self.console_output.append(line)

    def open_rs232_options(self):
        self.rs232options.show()

    def update_plot(self):
        filename = self.filename_input.text() + '.txt'

        try:
            data = np.loadtxt(filename, delimiter='\t', skiprows=1).T
        except Exception as e:
            print(e)
            return

        ax = self.plot_area.canvas.axes
        ax.clear()

        for i in range(1, data.shape[0]):
            ax.plot(data[0], data[i], label=f'T{i}')

        ax.legend(loc='upper left', bbox_to_anchor=(-0.15, 1))

        self.plot_area.canvas.draw()

class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.
    https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)
class Worker(QtCore.QRunnable):
    """
    Worker thread for longer functions
    """
    def __init__(self, func, *args, **kwargs):
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class RS232Options(QtWidgets.QMainWindow):
    def __init__(self):
        super(RS232Options, self).__init__()
        uic.loadUi("ui/RS232Options.ui", self)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = GasControl()
    main_window.show()
    app.exec_()
