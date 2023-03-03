__author__ = "Petr Kracik"
__version__ = "0.0.1"
__license__ = "MIT"


DS_DATA_MODE = 0xE1
DS_CMD_MODE = 0xE3

DS_PULSE_TERM = 0xF1
DS_RESET = b'\xC1'

DS_RES_ONEW_SHORT = 0xCC
DS_RES_ONEW_PRESC = 0xCD
DS_RES_ONEW_ALPRS = 0xCE
DS_RES_ONEW_NOPRS = 0xCF

# Parameter codes
DS_PARAM_PDSRC = 0b001
DS_PARAM_PPD   = 0b010
DS_PARAM_SPUD  = 0b011
DS_PARAM_W1LT  = 0b100
DS_PARAM_DSO   = 0b101
DS_PARAM_LOAD  = 0b110
DS_PARAM_RBR   = 0b111

# Configuration parameter operations
DS_PARAM_BIT     = 0x01
DS_PARAM_READ    = 0x01
DS_PARAM_WRRITE  = 0x04


class DS2480():
    def __init__(self, serial):
        self._serial = serial


    def reset(self):
        # DS will not reply on first reset after power-up, so send two
        self._serial.write(DS_RESET+DS_RESET)
        return self._serial.read()

    def read_param(self, param):
        data = bytearray(1)
        data[0] = DS_PARAM_BIT | (param << DS_PARAM_READ)
        self._serial.write(data)

        return self._serial.read()
