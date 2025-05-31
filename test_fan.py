# Replace with your actual fan's details
from ecoventv2 import Fan

#ip_address = "192.168.50.25"
ip_address = "192.168.50.80" # furdo
password = "1111"
device_id = "DEFAULT_DEVICEID"
name = "Test Fan"
port = 4000

fan = Fan(ip_address, password, device_id, name, port)
fan.init_device()

print("Fan ID:", fan.id)
print("Fan Name:", fan.name)
print("Current State:", fan.state)
print("Current Speed:", fan.speed)
print("Battery Voltage (raw):", fan.battery_voltage)
print("Battery Voltage type:", type(fan.battery_voltage))
print("Boost status:", fan.boost_time)


# Try to turn on the fan
#print("\nTrying to turn on the fan...")
#fan.set_param("state", "on")
#print("Fan state after turn on:", fan.state)