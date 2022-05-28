# This code is adapted from
# https://github.com/RuiSantosdotme/ESP-MicroPython/tree/master/code/MQTT/Node_RED_Client


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
      
      msg = b't={0:3.1f}C, h={1:3.1f}%, soil={2:4d}.'.format(temp, hum, soil_ADC)
      client.publish(topic_pub, msg)
      last_sensor_reading = time.time()
  except OSError as e:
    restart_and_reconnect()
