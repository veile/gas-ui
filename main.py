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
        self.valve_relay_dict = {'Ar': 2, 'H2': 3, 'N2': 4, 'NH3': 5, 'CO': 6}
        self.mfc_addr = {'Ar': 230, 'H2': 231, 'N2': 232, 'NH3': 233, 'CO': 234} # Check these values in lab
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


        # Checks the GPIO to see which valves are opened
        self.ar_valve.setChecked(not GPIO.input(self.valve_relay_dict['Ar']))
        self.h2_valve.setChecked(not GPIO.input(self.valve_relay_dict['H2']))
        self.n2_valve.setChecked(not GPIO.input(self.valve_relay_dict['N2']))
        self.nh3_valve.setChecked(not GPIO.input(self.valve_relay_dict['NH3']))
        self.co_valve.setChecked(not GPIO.input(self.valve_relay_dict['CO']))

        # Opening/Closing Valves upstream of mass flow controllers
        self.ar_valve.clicked.connect(lambda checked: self.toggle_valve(checked, 'Ar'))
        self.h2_valve.clicked.connect(lambda checked: self.toggle_valve(checked, 'H2'))
        self.n2_valve.clicked.connect(lambda checked: self.toggle_valve(checked, 'N2'))
        self.nh3_valve.clicked.connect(lambda checked: self.toggle_valve(checked, 'NH3'))
        self.co_valve.clicked.connect(lambda checked: self.toggle_valve(checked, 'CO'))


        # Information about mass flow controllers
        self.ar_info.setText(self.m.information(self.mfc_addr['Ar']))
        self.h2_info.setText(self.m.information(self.mfc_addr['H2']))
        self.n2_info.setText(self.m.information(self.mfc_addr['N2']))
        self.nh3_info.setText(self.m.information(self.mfc_addr['NH3']))
        self.co_info.setText(self.m.information(self.mfc_addr['CO']))

        # Setting the flow from input fields
        self.pushButton_set_flows.clicked.connect(self.set_flow)

    def toggle_valve(self, checked, gas):
        if checked:
            GPIO.output(self.valve_relay_dict[gas], GPIO.LOW)
            print(f'Opened valve for {gas}')
        else:
            GPIO.output(self.valve_relay_dict[gas], GPIO.HIGH)
            print(f'Closed valve for {gas}')

    def set_flow(self):
        self.m.set_flow(self.ar_flow_input.value(), self.mfc_addr['Ar'])
        self.m.set_flow(self.h2_flow_input.value(), self.mfc_addr['H2'])
        self.m.set_flow(self.n2_flow_input.value(), self.mfc_addr['N2'])
        self.m.set_flow(self.nh3_flow_input.value(), self.mfc_addr['NH3'])
        self.m.set_flow(self.co_flow_input.value(), self.mfc_addr['CO'])

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
