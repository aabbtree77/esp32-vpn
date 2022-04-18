# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Ramunas Girdziusas

# Program that outputs DHT22 values to SSD1306 on ESP32 (DOIT DEVIT V1 ESP32-WROOM-32).
# The values can also be read via MQTT, there is also MQTT control of the output on GPIO1.

import uasyncio as asyncio
import machine
import dht

from color_setup import ssd
# On a monochrome display Writer is more efficient than CWriter.
from gui.core.writer import Writer
from gui.core.nanogui import refresh
from gui.widgets.label import Label
import gui.fonts.freesans20 as freesans20
import gui.fonts.arial35 as arial35

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
    
    wri_val = Writer(ssd, arial35, verbose=False)
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



async def report_dht_data(sensor):
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


async def main():
    global GLOB_PINOUT1
    global PROG_STATE
    while True:
        GLOB_PINOUT1.on()
        PROG_STATE['output1'] = 1 
        await asyncio.sleep(1)
        GLOB_PINOUT1.off()
        PROG_STATE['output1'] = 0 
        await asyncio.sleep(1)


asyncio.create_task(display_outputs())

d = dht.DHT22(machine.Pin(14))
asyncio.create_task(report_dht_data(d))


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
