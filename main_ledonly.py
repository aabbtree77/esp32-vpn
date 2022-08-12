# This code is adapted from
# https://github.com/RuiSantosdotme/ESP-MicroPython/tree/master/code/MQTT/Node_RED_Client

def sub_cb(topic, msg):
 
  if msg == b'led0on':
    led0.value(1)
  elif msg == b'led0off':
    led0.value(0)


def connect_and_subscribe(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_passwd, topic_sub):
  client = MQTTClient(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_passwd)
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
  client = connect_and_subscribe(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_passwd, topic_sub)
  #client = connect_and_subscribe(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_passwd, topic_sub)
except OSError as e:
  restart_and_reconnect()

last_sensor_reading = 0
while True:
  try:
    client.check_msg()
    if (time.time() - last_sensor_reading) > readings_interval:    
      msg = b'led0={0:1d}.'.format(led0.value())
      client.publish(topic_pub, msg)
      last_sensor_reading = time.time()   
  except OSError as e:
    restart_and_reconnect()
