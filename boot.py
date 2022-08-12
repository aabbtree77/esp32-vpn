# This code is adapted from
# https://github.com/RuiSantosdotme/ESP-MicroPython/tree/master/code/MQTT/Node_RED_Client


from umqttsimple import MQTTClient
import time
import ubinascii
import machine
import micropython
import network
import dht


ssid = 'Wi-Fi name'
password = 'Wi-FI password'
mqtt_server = 'Local IP address of a PC that runs the Mosquitto broker'

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


led0 = machine.Pin(1, machine.Pin.OUT, value=0)
led1 = machine.Pin(18, machine.Pin.OUT, value=0)

sensor = dht.DHT22(machine.Pin(13))

soil0 = machine.ADC(machine.Pin(36))
soil0.atten(machine.ADC.ATTN_11DB) #Full range: 3.3v
soil0.width(machine.ADC.WIDTH_12BIT)

soil1 = machine.ADC(machine.Pin(39))
soil1.atten(machine.ADC.ATTN_11DB) #Full range: 3.3v
soil1.width(machine.ADC.WIDTH_12BIT)

soil2 = machine.ADC(machine.Pin(34))
soil2.atten(machine.ADC.ATTN_11DB) #Full range: 3.3v
soil2.width(machine.ADC.WIDTH_12BIT)

