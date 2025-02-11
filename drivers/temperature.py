import board
import busio
import adafruit_mcp9600
from micropython import const


class TC:
    """
    Class that handles the SPI driven thermocouple amplifier from Adafruit (MAX 31856)
    """
    def __init__(self):
        addresses = [const(0x60), const(0x63), const(0x67)]

        i2c = busio.I2C(board.SCL, board.SDA)
        self.mcps = [adafruit_mcp9600.MCP9600(i2c, address=address, tctype='N') for address in addresses]

    def get_T(self):
        return [mcp.temperature for mcp in self.mcps]

