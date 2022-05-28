# This code is adapted from
# https://github.com/RuiSantosdotme/ESP-MicroPython/tree/master/code/MQTT/Node_RED_Client

from umqttsimple import MQTTClient
import time
import ubinascii
import machine
import micropython
import network
import dht

ssid = 'your wifi name'
password = 'your wifi password'
mqtt_server = '192.168.1.107'

client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'output'
topic_pub = b'testincr'

last_sensor_reading = 0
readings_interval = 5 #seconds

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())


led = machine.Pin(1, machine.Pin.OUT, value=0)

sensor = dht.DHT22(machine.Pin(14))

soil = machine.ADC(machine.Pin(36))
soil.atten(machine.ADC.ATTN_11DB) #Full range: 3.3v
soil.width(machine.ADC.WIDTH_10BIT)

def read_DHT():
  temp = 1.0
  hum = 0.1

  try:
    sensor.measure() 
    temp = sensor.temperature()
    hum = sensor.humidity()
  except Exception as ex:
    temp = 99.0
    hum = 88.0
  
  return (temp, hum)


def sub_cb(topic, msg):
  print((topic, msg))
  if msg == b'on':
    led.value(1)
  elif msg == b'off':
    led.value(0)


def connect_and_subscribe(client_id, mqtt_server, topic_sub):
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client


def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe(client_id, mqtt_server, topic_sub)
except OSError as e:
  restart_and_reconnect()


while True:
  try:
    client.check_msg()
    if (time.time() - last_sensor_reading) > readings_interval:
      temp, hum = read_DHT()
      soil_ADC = soil.read()
      #soil_ADC = soil.read()
      msg = b't={0:3.1f}C, h={1:3.1f}%, soil={2:4d}.'.format(temp, hum, soil_ADC)
      client.publish(topic_pub, msg)
      last_sensor_reading = time.time()
  except OSError as e:
    restart_and_reconnect()
