# Program that outputs DHT22 values to SSD1306 on ESP32 (DOIT DEVIT V1 ESP32-WROOM-32).
# The values can also be read via MQTT, 

# The MQTT remote control of the output on GPIO1 does not work!

from mqtt_as import MQTTClient, config
import uasyncio as asyncio
import machine
import dht

from color_setup import ssd
# On a monochrome display Writer is more efficient than CWriter.
from gui.core.writer import Writer
from gui.core.nanogui import refresh
from gui.widgets.label import Label
import gui.fonts.freesans20 as freesans20
#import gui.fonts.arial35 as arial35

PROG_STATE = {}
PROG_STATE['temperature'] = 99
PROG_STATE['humidity'] = 77
PROG_STATE['output1'] = 0

GLOB_PINOUT1 = machine.Pin(1, machine.Pin.OUT)

async def display_outputs():
    global PROG_STATE    

    #ssd.fill(0)
    #refresh(ssd)    
    Writer.set_textpos(ssd, 0, 0)  # In case previous tests have altered it
    
    #wri_val = Writer(ssd, arial35, verbose=False)
    wri_val = Writer(ssd, freesans20, verbose=False)
    wri_val.set_clip(False, False, False)

    wri_aux = Writer(ssd, freesans20, verbose=False)
    wri_aux.set_clip(False, False, False)

    field_val = Label(wri_val, 27, 2, wri_val.stringlen('-23.0C'))
    field_aux = Label(wri_aux, 0, 2, wri_aux.stringlen('Output: 0'))
    
    while True:
        for it in (0,1):
            #refresh(ssd)
            if it == 0:
                field_val.value('{:2.1f}C'.format(PROG_STATE['temperature']))
            elif it==1:
                field_val.value('{:2.1f}%'.format(PROG_STATE['humidity']))
            else:
                field_val.value('{}'.format('Should be unreachable.')) 

            field_aux.value('Output: {}'.format(PROG_STATE['output1']))
            
            await asyncio.sleep_ms(3000)
            refresh(ssd) 
            #ssd.fill(0)  #It is vital to fill with zeros here in this precise order! 



async def measure_dht(sensor):
    global PROG_STATE
    n = 0
    while True:
        #PROG_STATE['temperature'] = n
        #PROG_STATE['humidity'] = n+1      
        
        try:
            sensor.measure() 
            PROG_STATE['temperature'] = sensor.temperature()
            PROG_STATE['humidity'] = sensor.humidity() 
            #PROG_STATE['temperature'] = 55
            #PROG_STATE['humidity'] = 33
            await asyncio.sleep(1) 
        except Exception as ex:
            PROG_STATE['temperature'] = n
            PROG_STATE['humidity'] = n 
            n = n + 1
            await asyncio.sleep(1)
            continue



async def wifi_han(state):
    #print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)


async def conn_han(client):
    
    #await client.subscribe('AAESP32DHT22/#', 1)
    try:
        #await client.subscribe('AAESP32DHT22/temperature', 1)
        #await client.subscribe('AAESP32DHT22/humidity', 1)
        await client.subscribe('AAESP32DHT22/remotectrl/in1', 1)
    except:
        for x in range(3):
            GLOB_PINOUT1.on()
            await asyncio.sleep_ms(500)
            GLOB_PINOUT1.off()
            await asyncio.sleep_ms(500)
        return
    
    
def sub_cb(topic, msg):
    global PROG_STATE

    for x in range(10):
        GLOB_PINOUT1.on()
        await asyncio.sleep_ms(500)
        GLOB_PINOUT1.off()
        await asyncio.sleep_ms(500)
    return

    #if topic == 'AAESP32DHT22/remotectrl/out1':
    #if topic.endswith('remotectrl/in1') or topic == 'AAESP32DHT22/remotectrl/in1' or topic == b'AAESP32DHT22/remotectrl/in1':
    #if (msg == 'on') or (msg == b'on'):
    #    PROG_STATE['output1'] = 1
    if (msg == 1) or (msg == b"1"):
        PROG_STATE['output1'] = 1
    #else:
    #    PROG_STATE['output1'] = 0  
    #else:
    #    pass


#config = {}
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['subs_cb'] = sub_cb
#config['server'] = '192.168.2.100'
config['server'] = '192.168.1.105'
config['ssid'] = 'your wifi name'
config['wifi_pw'] = 'your wifi password'
#config['user'] = ''
#config['password'] = ''
config['port'] = '1883'
config['ssl'] = False

MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)
#client.subscribe('AAESP32DHT22/#', 1)


async def main(client):
    global PROG_STATE
    global GLOB_PINOUT1


    try:
        await client.connect()
    except:
        for x in range(5):
            GLOB_PINOUT1.on()
            await asyncio.sleep_ms(500)
            GLOB_PINOUT1.off()
            await asyncio.sleep_ms(500)
        return

    await asyncio.sleep(2)  # Give broker time
    
    while True:
        
        if PROG_STATE['output1'] == 1:
            GLOB_PINOUT1.on()
        else:
            GLOB_PINOUT1.off()

        # If WiFi is down the following will pause for the duration.
        await client.publish('AAESP32DHT22/temperature', str(PROG_STATE['temperature']), qos = 1)
        await client.publish('AAESP32DHT22/humidity', str(PROG_STATE['humidity']), qos = 1)
        await client.publish('AAESP32DHT22/remotectrl/out1', str(PROG_STATE['output1']), qos = 1)
        
        await asyncio.sleep(20)  # Broker is slow


asyncio.create_task(display_outputs())

d = dht.DHT22(machine.Pin(14))
asyncio.create_task(measure_dht(d))


try:
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()
