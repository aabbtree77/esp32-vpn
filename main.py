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


led1on_start_time = 0

def sub_cb(topic, msg):
  global led1on_start_time
  print((topic, msg))
  if msg == b'led0on':
    led0.value(1)
  elif msg == b'led0off':
    led0.value(0)
    
  if msg == b'led1on':
    led1.value(1)
    led1on_start_time = time.time()
  elif msg == b'led1off':
    led1.value(0)  


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

last_sensor_reading = 0
while True:
  try:
    client.check_msg()
    if (time.time() - last_sensor_reading) > readings_interval:
      temp, hum = read_DHT()
      soil_ADC0 = soil0.read()
      soil_ADC1 = soil1.read()
      soil_ADC2 = soil2.read()
      #soil_ADC = 555
      msg = b't={0:3.1f}C, h={1:3.1f}%, s0={2:4d}, s1={3:4d}, s2={4:4d}, led0={5:1d}, led1={6:1d}, led1ontime={7:4d}s, time={8:4d}s.'.format(
      temp, hum, soil_ADC0, soil_ADC1, soil_ADC2, led0.value(), led1.value(), led1on_start_time, time.time())
      client.publish(topic_pub, msg)
      last_sensor_reading = time.time()
    if (((time.time() - led1on_start_time) > 60) and (led1on_start_time != 0)):
      led1.value(0) 
      led1on_start_time = 0     
  except OSError as e:
    restart_and_reconnect()
