from serial import Serial
import ds2480

s = Serial("/dev/ttyACM0", 9600, timeout=1)
ds = ds2480.DS2480(s)

print(ds.reset())

print("Write")
print(ds.write(0x33))

while True:
    response = ds.read()
    if response == 0xFF:
        break

    print("0x{:02X}".format(response))

print(ds.reset())
