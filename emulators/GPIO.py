def setmode(input):
    print(f'Set mode to {input}')

def setup(pins, mode):
    print(f'Setup pins {pins} to {mode}')

def output(pins, level):
    print(f'Pins {pins} set to {level}')

def input(pin):
    return True

LOW = 0
HIGH = 1
