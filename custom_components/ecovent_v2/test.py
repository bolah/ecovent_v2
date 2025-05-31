# Replace with your actual fan's details
from ecoventv2 import Fan


ip_address = "192.168.50.80"
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
print("Humidity:", fan.humidity)
print("Airflow:", fan.airflow)

# Example: Turn the fan on
fan.set_state_on()