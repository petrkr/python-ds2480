from serial import Serial
import ds2480

s = Serial("/dev/ttyACM0", 9600)
ds = ds2480.DS2480(s)


data = ds.reset()
print(data)

data = ds.read_param(ds2480.DS_PARAM_LOAD)
print(data)

