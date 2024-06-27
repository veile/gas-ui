# ------------------------------------------------------
# ---------------------- main.py -----------------------
# ------------------------------------------------------
from PyQt5 import QtWidgets, uic, QtCore
import ui.rsc
import numpy as np
import time


class GasControl(QtWidgets.QMainWindow):
    def __init__(self):
        super(GasControl, self).__init__()

        uic.loadUi("ui/gas-UI.ui", self)

        # Multithread control
        self.threadpool = QtCore.QThreadPool()

        # self.setWindowTitle("In-situ VSM Gas Control")

        # Menubar actions
        self.action_RS232_Settings.triggered.connect(self.open_rs232_options)
        self.rs232options = RS232Options()

        # Plot actions
        self.pushButton_set_flows.clicked.connect(self.update_plot)

        # Button test
        self.pushButton_1.clicked.connect(self.bt1)
        self.pushButton_2.clicked.connect(self.bt2)

        self.ar_valve.clicked.connect(lambda: self.toggle_valve('Ar'))
        self.h_valve.clicked.connect(lambda: self.toggle_valve('H2'))
        self.n_valve.clicked.connect(lambda: self.toggle_valve('N2'))
        self.nh3_valve.clicked.connect(lambda: self.toggle_valve('NH3'))
        self.co_valve.clicked.connect(lambda: self.toggle_valve('CO'))

    def toggle_valve(self, gas, *args, **kwargs):
        if self.ar_valve.isChecked():
            print(f'Opened valve for {gas}')
        else:
            print(f'Closed valve for {gas}')

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
