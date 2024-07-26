# ------------------------------------------------------
# ---------------------- main.py -----------------------
# ------------------------------------------------------
from PyQt5 import QtWidgets, uic, QtCore
import ui.rsc
import os
import numpy as np
import time

# Initalize GPIO pins on raspberry pi
try:
    import RPi.GPIO as GPIO
    from mks import MFC

    GPIO.setmode(GPIO.BCM)
    pins = [i for i in range(2, 12)]
    GPIO.setup(pins, GPIO.OUT)
    
except:
    import emulators.GPIO as GPIO
    from emulators.mks import MFC

class GasControl(QtWidgets.QMainWindow):
    def __init__(self):
        super(GasControl, self).__init__()

        # Load the UI Page - added path too
        # ui_path = os.path.dirname(os.path.abspath(__file__))
        # uic.loadUi(os.path.join(ui_path, "ui/gas-UI.ui"), self)
        uic.loadUi("ui/gas-UI.ui", self)
        
        # Which gas connected to which (GPIO Pin)/(Relay-1) .
        self.gas_valves = {
            'Ar': {'relay': 2, 'button': self.ar_valve},
            'H2': {'relay': 3, 'button': self.h2_valve},
            'N2': {'relay': 4, 'button': self.n2_valve},
            'NH3': {'relay': 5, 'button': self.nh3_valve},
            'CO': {'relay': 6, 'button': self.co_valve},
            'V1': {'relay': 7, 'button': self.valve1},
            'V2': {'relay': 8, 'button': self.valve2},
            'V3': {'relay': 9, 'button': self.valve3},
            'V4': {'relay': 10, 'button': self.valve4}
        }

        # Mass Flow controller settings
        self.flow_controllers ={
            'Ar': {'addr': 230, 'flow_input': self.ar_flow_input, 'info': self.ar_info},
            'H2': {'addr': 231, 'flow_input': self.h2_flow_input, 'info': self.h2_info},
            'N2': {'addr': 232, 'flow_input': self.n2_flow_input, 'info': self.n2_info},
            'NH3': {'addr': 233, 'flow_input': self.nh3_flow_input, 'info': self.nh3_info},
            'CO': {'addr': 234, 'flow_input': self.co_flow_input, 'info': self.co_info},
        }

        self.m = MFC()

        # Multithread control
        self.threadpool = QtCore.QThreadPool()

        # self.setWindowTitle("In-situ VSM Gas Control")

        # Menubar actions
        self.action_RS232_Settings.triggered.connect(self.open_rs232_options)
        self.rs232options = RS232Options()

        # Plot actions
        # self.pushButton_set_flows.clicked.connect(self.update_plot)

        # Button test
        self.pushButton_1.clicked.connect(self.bt1)
        self.pushButton_2.clicked.connect(self.bt2)

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

    def toggle_valve(self, checked, relay):
        if checked:
            GPIO.output(relay, GPIO.LOW)
            print(f'Opened relay {relay}')
        else:
            GPIO.output(relay, GPIO.HIGH)
            print(f'Closed relay {relay}')

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

    def set_flow(self):
        for mfc in self.flow_controllers.values():
            addr, flow_input = mfc['addr'], mfc['flow_input']
            self.m.set_flow(flow_input.value(), addr)

    def btclick(self, btno):
        print(f'bt{btno} started')
        time.sleep(5)
        print(f'bt{btno} ended')

    def bt1(self):
        worker = Worker(self.btclick, 1)
        self.threadpool.start(worker)

    def bt2(self):
        worker = Worker(self.btclick, 2)
        self.threadpool.start(worker)

    def open_rs232_options(self):
        self.rs232options.show()

    def update_plot(self):
        ax = self.plot_area.canvas.axes
        ax.clear()
        ax.plot(np.arange(5), np.arange(5), 'o:')

        self.plot_area.canvas.draw()


class Worker(QtCore.QRunnable):
    """
    Worker thread for longer functions
    """
    def __init__(self, func, *args, **kwargs):
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @QtCore.pyqtSlot()
    def run(self):
        self.func(*self.args, **self.kwargs)


class RS232Options(QtWidgets.QMainWindow):
    def __init__(self):
        super(RS232Options, self).__init__()
        uic.loadUi("ui/RS232Options.ui", self)


app = QtWidgets.QApplication([])
main_window = GasControl()
main_window.show()
app.exec_()
