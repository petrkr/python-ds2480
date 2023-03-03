__author__ = "Petr Kracik"
__version__ = "0.0.1"
__license__ = "MIT"


DS_DATA_MODE = 0xE1
DS_CMD_MODE  = 0xE3

DS_PULSE_TERM = 0xF1
DS_RESET      = 0xC1

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


class DS2480Exception(Exception):
    pass


class DS2480Response():
    def __init__(self, response):
        self._res = response

    @property
    def response(self):
        return self._res


class DS2480ResetResponse(DS2480Response):
    BUS_SHORTED             = 0b00
    PRESENCE_PULSE          = 0b01
    ALARMING_PRESENCE_PULSE = 0b10
    NO_PRESENCE_PULSE       = 0b11

    def __str__(self):
        if self._res == self.BUS_SHORTED:
            return "Bus shorted"
        if self._res == self.PRESENCE_PULSE:
            return "Presence pulse"
        if self._res == self.ALARMING_PRESENCE_PULSE:
            return "Alarming presence pulse"
        if self._res == self.NO_PRESENCE_PULSE:
            return "No presence pulse"


class DS2480():
    def __init__(self, serial):
        self._serial = serial


    def _write_byte(self, byte):
        return self._serial.write(byte.to_bytes(1, 'little'))


    def reset(self):
        # DS will not reply on first reset after power-up, so send two
        self._write_byte(DS_RESET)
        self._write_byte(DS_RESET)
        response = self._serial.read()

        if len(response) != 1:
            raise DS2480Exception("Bad response", response)

        if (response[0] & 0b1100_1100) != 0b1100_1100:
            raise DS2480Exception("Bad response", response)

        return DS2480ResetResponse(response[0] & 0b000000_11)


    def read_param(self, param):
        self._write_byte(DS_PARAM_BIT | (param << DS_PARAM_READ))
        return self._serial.read()
