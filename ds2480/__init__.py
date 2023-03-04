__author__ = "Petr Kracik"
__version__ = "0.0.1"
__license__ = "MIT"


DS_DATA_MODE = 0xE1
DS_CMD_MODE  = 0xE3

DS_PULSE_TERM = 0xF1
DS_RESET      = 0xC1

DS_WRITE_0_BIT = 0x81
DS_WRITE_1_BIT = 0x91

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


class DS2480Parameter():
    def __init__(self, response):
        self._res = response

    @property
    def response(self):
        return self._res


class DS2480ParameterLOAD(DS2480Parameter):
    LOAD={
        0b000: 1.8,
        0b001: 2.1,
        0b010: 2.4,
        0b011: 2.7,
        0b100: 3.0,
        0b101: 3.3,
        0b110: 3.6,
        0b111: 3.9}


    def __str__(self):
        return "Load: {}mA".format(self.LOAD[self._res])


class DS2480():
    def __init__(self, serial):
        self._serial = serial


    def _write_byte(self, byte):
        return self._serial.write(byte.to_bytes(1, 'little'))


    def _read_byte(self):
        res = self._serial.read()
        return res[0] if res else None


    def _read_param(self, param):
        self._write_byte(DS_PARAM_BIT | (param << DS_PARAM_READ))
        response = self._read_byte()

        if response & 0b1000_0001 != 0b0000_0000:
            raise DS2480Exception("Bad response", response)

        return response >> 1


    def _set_mode(self, mode):
        if self._mode != mode:
            print("Switch mode to: {}".format("CMD" if mode == DS_CMD_MODE else "DATA"))
            self._write_byte(mode)
            self._mode = mode


    @property
    def load_sensor_threshold(self):
        res = self._read_param(DS_PARAM_LOAD)
        return DS2480ParameterLOAD(res)


    def write_bit(self, bit):
        self._set_mode(DS_CMD_MODE)
        self._write_byte(DS_WRITE_1_BIT if bit else DS_WRITE_0_BIT)
        res = self._read_byte()
        return res & 1


    def read_bit(self):
        return self.write_bit(1)


    def reset(self):
        # DS will not reply on first reset after power-up, so send two
        self._write_byte(DS_RESET)
        self._write_byte(DS_RESET)
        res = self._read_byte()

        if len(response) != 1:
            raise DS2480Exception("Bad response", response)

        if (response[0] & 0b1100_1100) != 0b1100_1100:
            raise DS2480Exception("Bad response", response)

        return DS2480ResetResponse(response[0] & 0b000000_11)
