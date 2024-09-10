import serial
import time

def CRC(msg):
    CRC = 0
    for l in msg:
        CRC -= ord(l)
        
    return hex(CRC % (2**8))[2:].upper()

class UltraHeat():
    def __init__(self, port='/dev/ttyUSB2'):
        self.ser = serial.Serial(port, baudrate=9600)
        
        self.start_char = 'S'
        self.end_char = 'K'
        
    # Used for debugging. It prints the final msg and return the full
    # unhandled reply.
    def raw_comm(self, cmd):
        msg = self.start_char + cmd
        msg = msg + CRC(msg)
        msg = msg + self.end_char

        print(msg)
        self.ser.write(msg.encode('utf-8'))
        
        time.sleep(.1)
        
        return self.ser.read(self.ser.inWaiting())

    def comm(self, cmd):
        msg = self.start_char + cmd
        msg = msg + CRC(msg)
        msg = msg + self.end_char

        self.ser.write(msg.encode('ascii'))
        
        time.sleep(.2)
        
        reply = self.retrieve_reply()
        
        return reply
        
    def retrieve_reply(self):
        reply = self.ser.read(self.ser.inWaiting()).decode('ascii')
        
        # Removing start_char, address, command, CRC and endchar
        reply = reply[3:-3]
        
        # Converting the hexadecimal value to decimal 
        return int(reply, 16)

    def get_current(self):
        return self.comm('3i')/10

    def get_frequency(self):
        return self.comm('3f')

        
if __name__ == '__main__':
    ps = UltraHeat()
    
    # All examples are address 3
    print(ps.comm('3E'))