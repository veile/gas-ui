import random
class XGS600Driver:
    """Emulator for XGS600 gauge controller"""

    def __init__(self, port='/dev/ttyUSB1'):
        pass

    def read_pressure(self, gauge):
        print(f'Read pressure for gauge {gauge}')
        return f'{random.random()*1e-8:.3E}'

    def read_pressure_unit(self):
        print('Getting pressure unit')
        return 'mBar'