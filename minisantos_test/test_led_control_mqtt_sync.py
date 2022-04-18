# This code is adapted from
# https://github.com/RuiSantosdotme/ESP-MicroPython/tree/master/code/MQTT/Node_RED_Client

# Essentially boot.py and main.py are joined for testing purposes in order not to mess up booting.
# This code is just to test the ability to set LED values via MQTT. In the presense of network errors
# it soft-resets to repl.

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

n = 0
while True:
  try:
    client.check_msg()
    if (time.time() - last_sensor_reading) > readings_interval:
      msg = (b'{0:3.1f}'.format(n))
      client.publish(topic_pub, msg)
      last_sensor_reading = time.time()
      n = n + 1
  except OSError as e:
    restart_and_reconnect()
