import board
import digitalio
import adafruit_max31856

# class TC():
    # """
    # Class that handles the SPI driven thermocouple amplifier from Adafruit (MAX 31856)
    # """
    # def __init__(self, CS_PINS, tc_type='N'):
        # self.CS_PINS = CS_PINS

        # spi = board.SPI()

        # cs = [digitalio.DigitalInOut(getattr(board, pin)) for pin in self.CS_PINS]
        # for c in cs:
            # c.direction = digitalio.Direction.OUTPUT

        # self.tcs = [adafruit_max31856.MAX31856(spi, c, thermocouple_type=getattr(adafruit_max31856.ThermocoupleType, tc_type)) for c in cs]
        # for tc in self.tcs:
             # tc.noise_rejection = 50


    # def __len__(self):
        # return len(self.tcs)

    # def initiate(self):
        # [tc.initiate_one_shot_measurement() for tc in self.tcs]

    # def get_T(self):
        # # [tc.initiate_one_shot_measurement() for tc in self.tcs]

        # # while self.tcs[-1].oneshot_pending:
            # # pass

        # print(self.tcs[0].fault)


        # if self.tcs[0].oneshot_pending:
            # raise Exception('Temperature not initialised!')
        # return [tc.unpack_temperature() for tc in self.tcs]

    # def set_type(self, tc_type='N'):
        # thermocouple_type = getattr(adafruit_max31856.ThermocoupleType, tc_type)
        # [tc._set_thermocouple_type(thermocouple_type) for tc in self.tcs]

class TC():
    """
    Class that handles the SPI driven thermocouple amplifier from Adafruit (MAX 31856)
    """
    def __init__(self):
        spi = board.SPI()
        cs = digitalio.DigitalInOut(getattr(board, 'D24'))
        cs.direction = digitalio.Direction.OUTPUT
        self.thermocouple = adafruit_max31856.MAX31856(spi, cs, thermocouple_type=getattr(adafruit_max31856.ThermocoupleType, 'N'))
        self.thermocouple.noise_rejection = 50
        
    def initiate(self):
        self.thermocouple.initiate_one_shot_measurement()

    def get_T(self):
    
        output = self.thermocouple.unpack_temperature()
        
        print(self.thermocouple.fault)
        print(output)
        return [output]