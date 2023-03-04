__author__ = "Petr Kracik"
__version__ = "0.0.1"
__license__ = "MIT"


DS_DATA_MODE = 0xE1
DS_CMD_MODE  = 0xE3

DS_PULSE_TERM = 0xF1
DS_RESET      = 0xC1

DS_WRITE_0_BIT = 0x81
DS_WRITE_1_BIT = 0x91

DS_SEARCH_ACCEL_OFF = 0xA1
DS_SEARCH_ACCEL_ON  = 0xB1

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

# Taken from dallas
DS_CRC_TABLE = [
    0, 94,188,226, 97, 63,221,131,194,156,126, 32,163,253, 31, 65,
    157,195, 33,127,252,162, 64, 30, 95,  1,227,189, 62, 96,130,220,
    35,125,159,193, 66, 28,254,160,225,191, 93,  3,128,222, 60, 98,
    190,224,  2, 92,223,129, 99, 61,124, 34,192,158, 29, 67,161,255,
    70, 24,250,164, 39,121,155,197,132,218, 56,102,229,187, 89,  7,
    219,133,103, 57,186,228,  6, 88, 25, 71,165,251,120, 38,196,154,
    101, 59,217,135,  4, 90,184,230,167,249, 27, 69,198,152,122, 36,
    248,166, 68, 26,153,199, 37,123, 58,100,134,216, 91,  5,231,185,
    140,210, 48,110,237,179, 81, 15, 78, 16,242,172, 47,113,147,205,
    17, 79,173,243,112, 46,204,146,211,141,111, 49,178,236, 14, 80,
    175,241, 19, 77,206,144,114, 44,109, 51,209,143, 12, 82,176,238,
    50,108,142,208, 83, 13,239,177,240,174, 76, 18,145,207, 45,115,
    202,148,118, 40,171,245, 23, 73,  8, 86,180,234,105, 55,213,139,
    87,  9,235,181, 54,104,138,212,149,203, 41,119,244,170, 72, 22,
    233,183, 85, 11,136,214, 52,106, 43,117,151,201, 74, 20,246,168,
    116, 42,200,150, 21, 75,169,247,182,232, 10, 84,215,137,107, 53]

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
        self._serial.timeout = 1
        self._mode = None
        self.reset()


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
        if self._mode == mode:
            return

        print("Switch mode to: {}".format("CMD" if mode == DS_CMD_MODE else "DATA"))
        self._write_byte(mode)
        self._mode = mode


    def _check_crc_8(self, data):
        crc = 0
        for c in data:
            crc = DS_CRC_TABLE[crc ^ c]

        return crc == 0


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
        # If we know, we are in DATA mode, switch to CMD first
        if self._mode == DS_DATA_MODE:
            self._set_mode(DS_CMD_MODE)

        self._write_byte(DS_RESET)
        res = self._read_byte()

        # DS will not reply on first reset after power-up, so send second
        if not res:
            print("Power on? Reset twice")
            self._write_byte(DS_RESET)
            res = self._read_byte()

        if not res:
            raise DS2480Exception("No response from DS2480, is it connected?")

        if (res & 0b1100_1100) != 0b1100_1100:
            print("Bad response, try switch to CMD mode and reset again")
            self._set_mode(DS_CMD_MODE)
            return self.reset()


        return DS2480ResetResponse(res & 0b000000_11)


    def search_accel(self, status):
        self._set_mode(DS_CMD_MODE)
        self._write_byte(DS_SEARCH_ACCEL_ON if status else DS_SEARCH_ACCEL_OFF)


    # Write byte to one wire bus
    def write(self, byte):
        self._set_mode(DS_DATA_MODE)
        self._write_byte(byte)

        # For those bytes we need transmit twice
        if byte in [DS_CMD_MODE, DS_DATA_MODE, DS_PULSE_TERM]:
            self._write_byte(byte)

        return self._read_byte()


    def read(self):
        self._set_mode(DS_DATA_MODE)
        return self.write(0xFF)
