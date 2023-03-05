from serial import Serial
import ds2480

def print_bytearray(data):
    for b in data:
        print("0x{:02X}".format(b))


def read_rom(ds):
    print("Read ROM")
    print(ds.write(0x33))

    while True:
        response = ds.read()
        if response == 0xFF:
            break

        print("0x{:02X}".format(response))


s = Serial("/dev/ttyACM0", 9600, timeout=1)
ds = ds2480.DS2480(s)

print(ds.reset())

read_rom(ds)

print("Search ROMs")
devs = ds.search()

for dev in devs:
    print_bytearray(dev)
    print()
