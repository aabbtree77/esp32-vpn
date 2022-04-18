# This code is adapted from
# https://github.com/RuiSantosdotme/ESP-MicroPython/tree/master/code/MQTT/Node_RED_Client

from umqttsimple import MQTTClient
import time
import ubinascii
import machine
import micropython
import network


ssid = 'your wifi name'
password = 'your wifi password'
mqtt_server = '192.168.1.107'

client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'output'
topic_pub = b'testincr'

last_sensor_reading = 0
readings_interval = 5

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())


led = machine.Pin(1, machine.Pin.OUT, value=0)
