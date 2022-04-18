# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Ramunas Girdziusas

# Testing DHT22, the synchronous case. 
# DOIT DEVIT V1 ESP32-WROOM-32, 30-pin version.
# DHT22 on GPIO14, blinking LED on GPIO1. 

import dht
import machine
import time

from color_setup import ssd
# On a monochrome display Writer is more efficient than CWriter.
from gui.core.writer import Writer
from gui.core.nanogui import refresh
from gui.widgets.label import Label
import gui.fonts.freesans20 as freesans20
import gui.fonts.arial35 as arial35


def display_outputs(temp, hum, out):

    #ssd.fill(0)
    #refresh(ssd)    
    Writer.set_textpos(ssd, 0, 0)  # In case previous tests have altered it
    
    wri_val = Writer(ssd, arial35, verbose=False)
    wri_val.set_clip(False, False, False)

    wri_aux = Writer(ssd, freesans20, verbose=False)
    wri_aux.set_clip(False, False, False)

    field_val = Label(wri_val, 27, 2, wri_val.stringlen('-23.0C'))
    field_aux = Label(wri_aux, 0, 2, wri_aux.stringlen('Output: 0'))
    

    for it in (0,1):
        #refresh(ssd)
        if it == 0:
            field_val.value('{:2.1f}C'.format(temp))
        elif it==1:
            field_val.value('{:2.1f}%'.format(hum))
        else:
            field_val.value('{}'.format('Should be unreachable.')) 

        field_aux.value('Output: {}'.format(out))
        
        
        refresh(ssd) 
        time.sleep_ms(2000) 


sensor = dht.DHT22(machine.Pin(14))
output_ctrl = machine.Pin(1, machine.Pin.OUT)

while True:
    
    #Some irrelevant initial values
    temp = 1.0
    hum = 0.1
 
    try:
        sensor.measure() 
        temp = sensor.temperature()
        hum = sensor.humidity()
    except Exception as ex:
        #print("error: {}".format(ex))
        temp = 99
        hum = 77
        continue

    output_ctrl.on()
    display_outputs(temp, hum, 1)    

    output_ctrl.off()
    display_outputs(temp, hum, 0)    

