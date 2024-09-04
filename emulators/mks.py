import random

class MFC:
    def __init__(self, port):
        pass

    def checksum(self, msg):
        decimal = sum([ord(s) for s in msg])

        return hex(decimal)[-2:].upper()

    def comm(self, cmd, addr):

        msg = "@" + str(addr).zfill(3) + cmd + ';'
        check = self.checksum(msg)

        final_msg = "@@" + msg + check

        print(f'{addr}:\t{final_msg}')

    def set_flow(self, flow, addr):
        """
        Sets flow to specified value in flow controller
        Maybe add validation with 'SX?'
        """

        self.comm('SX!%f' % flow, addr)

    def read_flow(self, addr):
        self.comm('FX?', addr)
        return f'{random.random()*10:.2f}'

    def information(self, addr):
        return f'Random info about {addr}'