import random

class TC():
    """
    Class that handles the SPI driven thermocouple amplifier from Adafruit (MAX 31856)
    """
    def __init__(self, CS_PINS, tc_type='N'):
        print(f'Initialized TC on pin {CS_PINS}')

        self.tcs = [CS_PIN for CS_PIN in CS_PINS]
    def __len__(self):
        return len(self.tcs)

    def initiate(self):
        pass

    def get_T(self):
        # [tc.initiate_one_shot_measurement() for tc in self.tcs]

        # while self.tcs[-1].oneshot_pending:
            # pass

        # print(self.tcs[0].fault)

        return [random.random()*100 for _ in range(self.tcs)]

    def set_type(self, tc_type='N'):
        print(f'Type set to {tc_type}')