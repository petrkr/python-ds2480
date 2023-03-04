from serial import Serial
import ds2480

s = Serial("/dev/ttyACM0", 9600)
ds = ds2480.DS2480(s)


data = ds.reset()
print(data)
print(data.response)

print(ds.load_sensor_threshold)
