import datetime
import serial
import time
import re

error_dict = {'01': 'Checksum error',
              '10': 'Syntax error',
              '11': 'Data length error',
              '12': 'Invalid data',
              '13': 'Invalid operating mode',
              '14': 'Invalid action',
              '15': 'Invalid gas',
              '16': 'Invalid control mode',
              '17': 'Invalid command',
              '24': 'Calibration error',
              '25': 'Flow too large',
              '27': 'Too many gases in gas table',
              '28': 'Flow cal error; valve not open',
              '98': 'Internal device error',
              '99': 'Internal device error'}

class MFC():
    def __init__(self, port='/dev/ttyUSB0', baud=9600):
        self.ser = serial.Serial(port, baud)

    def timestamp(self):
        current_time = datetime.datetime.now(tz=None)
        return current_time.strftime("%Y-%m-%d %H:%M:%S")

    def log(self, log_str, error=False):
        with open('mfc.log', 'a') as f:
            if error:
                f.write("ERROR " + self.timestamp() + " -- " + log_str+"\n")
            else:
                f.write(self.timestamp() + " -- " + log_str+"\n")

    def checksum(self, msg):
        decimal = sum([ord(s) for s in msg])

        return hex(decimal)[-2:].upper()

    def comm(self, cmd, addr):

        msg = "@" + str(addr).zfill(3) + cmd + ';'
        check = self.checksum(msg)

        final_msg = "@@" + msg + check
        self.ser.write(final_msg.encode('utf-8'))
        self.log(final_msg)

        time.sleep(.1)
        reply = self.retrieve_reply(addr)

        return reply

    def retrieve_reply(self, addr):
        reply = self.ser.read(self.ser.inWaiting()).decode('utf-8', errors='ignore')

        if reply == '':
            self.log("No device found on address %i" %addr, error=True)
            return 'N/A'


        if 'NAK' in reply:
            error_code = re.search("NAK(.*);", reply).group(1).strip()
            return error_dict[error_code]

        else:
            return re.search("ACK(.*);", reply).group(1).strip()

    def information(self, addr):
        FS = self.comm('FS?', addr=addr)
        U = self.comm('U?', addr=addr)
        SN = self.comm('SN?', addr=addr)

        return "Serial No: #%s\nScale: 0-%s %s" %(SN, FS, U)

    def set_flow(self, flow, addr):
        """
        Sets flow to specified value in flow controller
        Maybe add validation with 'SX?'
        """
        upper_limit = float(self.comm('FS?', addr))
        flow = round(flow, 2)

        if 0 <= flow <= upper_limit:
            self.comm('SX!%f' %flow, addr)

        else:
            self.log("Flow of %f is out of range" %flow, error=True)

    def read_flow(self, addr):
        flow = self.comm('FX?', addr)
        return float(flow)


