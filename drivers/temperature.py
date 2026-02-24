import board
import busio
import adafruit_mcp9600
from micropython import const


class TC:
    """
    Class that handles the I2C driven thermocouple amplifier from Groove Seed (MCP9600)
    """
    def __init__(self):
        #addresses = [const(0x60), const(0x63), const(0x67)]
        addresses = [const(0x60)]
        tctypes = ['N']

        i2c = busio.I2C(board.SCL, board.SDA)
        self.mcps = [adafruit_mcp9600.MCP9600(i2c, address=addresses[i], tctype=tctypes[i]) for i in range(len(tctypes))]
    
    def __len__(self):
        return len(self.mcps)
    
    def get_T(self):
        return [mcp.temperature for mcp in self.mcps]

if __name__ == '__main__':
    tc = TC()
    print(tc.get_T())