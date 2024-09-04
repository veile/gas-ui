import random

class UltraHeat():
    def __init__(self, port):
        pass

    def get_current(self):
        return f'{random.random()*24:.1f}'

    def get_frequency(self):
        return f'{random.random()*5000 + 400000:.0f}'