# from temperature import TC
from emulators.temperature import TC

import time

def measure(filename):
    print('Starting measurement')

    for i in range(10):
        print(i)
        time.sleep(0.5)


