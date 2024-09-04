import serial
import time
import re

class PC():
    def __init__(self, port='/dev/ttyUSB0', baud=9600):
        self.ser = serial.Serial(port, baud)
    def checksum(self, msg):
        decimal = sum([ord(s) for s in msg])

        return hex(decimal)[-2:].upper()

    def comm(self, cmd, addr):
        msg = "@" + str(addr).zfill(3) + cmd + ';'
        check = self.checksum(msg)

        final_msg = "@@" + msg + check
        self.ser.write(final_msg.encode('utf-8'))

        time.sleep(.1)
        reply = self.retrieve_reply(addr)

        return reply

    def retrieve_reply(self, addr):
        reply = self.ser.read(self.ser.inWaiting()).decode('utf-8', errors='ignore')

        if 'NAK' in reply:
            error_code = re.search("NAK(.*);", reply).group(1).strip()
            return error_code

        try:
            return re.search("ACK(.*);", reply).group(1).strip()

        except AttributeError:
            return 'N/A'


if __name__ == '__main__':
    p = PC()
    pressure = p.comm('PX?', 250)
    print(f'{pressure} torr')