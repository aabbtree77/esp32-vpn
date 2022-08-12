
<table align="center">
    <tr>
    <th align="center"> ESP32 as MQTT Client</th>
    </tr>
    <tr>
    <td>
    <img src="./images/mermaid-diagram-20220402145130.svg"  alt="Device in the Operating Mode)" width="100%" >
    </td>
    </tr>
</table>

## Introduction

This report is about DOIT DEVIT V1 ESP32-WROOM-32 applied for wireless communication inside LAN with MQTT. The MicroPython code achieves resilience w.r.t. a lost Wi-Fi. In the picture above Remmina is supposed to be applied for the connection to LAN from the outside. This demands opening ports which may not always be possible. Instead, one can try this type of a [communication via github](https://github.com/aabbtree77/sendrecv) built in order to avoid opaque 3rd party MQTT brokers and remote desktop software. 


## Some Photos

![gThumb01](./images/esp32-ssd1306-dht22-front.jpg "ESP32 on a custom board: Front.")

![gThumb02](./images/esp32-ssd1306-dht22-back.jpg "ESP32 on a custom board: Back.")


The DOIT DEVIT V1 ESP32-WROOM-32 development board is an inexpensive (sub 10-20$) board with an ambition to perform networking. A combo with MicroPython in a way realizes one's dream of a Lisp machine and brings nostalgia about the golden age of computing around 1980s when activating some device or displaying text/pixels on a monitor required only a few lines of code.

The MicroPython code here is an adaptation of this [github repo by Rui Santos][micropython-Rui-Santos] and does so much with so little.

## Circuit Diagram

- [esp32-30pin] (the 30-pin variant of DOIT DEVIT V1 ESP32-WROOM-32, not 36).

- DHT22.

- Multiple LEDs.

- ~~SSD1306 with in-software I2C.~~ Dropped it, rewind to "the last before revamp" commit if interested.

- Capacitive Soil Moisture Sensor v1.2.

See boot.py for the exact connectivity/pin numbers.

## Commands

- Ubuntu PC:

  ```console
  sudo apt-get install python3-pip
  sudo pip3 install esptool
  sudo pip3 install rshell
  ```

- USB connection:

  ```console
  ls /dev/ttyUSB*
  dmesg | grep ttyUSB
  ```

- Flashing/reflashing [MicroPython firmware][MicroPython firmware] via USB:

  ```console
  sudo esptool.py --port /dev/ttyUSB0 flash_id
  sudo esptool.py --port /dev/ttyUSB0 erase_flash
  sudo esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-ota-20220618-v1.19.1.bin
  ```  

- Release: 

  ```console
  rshell --buffer-size=30 -p /dev/ttyUSB0 -a
  boards
  ls /pyboard
  cp main.py /pyboard
  cp umqttsimple.py /pyboard
  cp boot.py /pyboard
  ```

  Disconnect the device from USB and use only a power supply.

- MQTT:

  ```console
  sudo apt install mosquitto mosquitto-clients
  hostname -I
  ifconfig -a | grep inet
  ```

  The hostname/ifconfig command will provide the local IP address assigned by the router to a computer (PC1) which runs the MQTT broker (Moscquitto), such as '192.168.1.107'. It will have to be entered in boot.py manually/explicitly. 


  The Mosquitto broker always runs on Ubuntu by default once the OS starts. However, depending on the exact Ubuntu and Mosquitto versions one may need some additional minimal configuration.
  Since Mosquitto version 2.0, one needs to create a custom config file and place it somewhere, say at /home/sara/esp32/custom_mosquitto.conf, with this minimal content:

  ```console
  listener 1883
  allow_anonymous true
  ```
  
  Then start the MQTT broker with this config:

  ```console
  mosquitto -c /home/sara/esp32/custom_mosquitto.conf
  ```

  Sometimes you may get "Error: Address already in use". That means you are starting another Mosquitto broker on the same machine. Kill one or the other with
    
  ```console
  ps -ef | grep mosquitto
  sudo kill 1234
  ```
    
  One should get the console message indicating the connected MicroPython MQTT client with its local IP address such as 192.168.1.108, the latter may change 
  with each device reboot, it is assigned by a router.

  Read the sensor data from the device:
 
  ```console
  mosquitto_sub -d -h 192.168.1.107 -t "testincr"
  ```

  Publish the messages "on" or "off" to control the LED output:

  ```console
  mosquitto_pub -d -h 192.168.1.107 -t "output" -m "on" -q 1
  mosquitto_pub -d -h 192.168.1.107 -t "output" -m "off" -q 1
  ```

## Remote Desktop Control

Remote desktop control splits into two main camps: (i) the one that relies on router port forwarding and does not need any external "rendezvous server", and (ii) mostly SAAS solutions which do hole punching (TeamViewer, AnyDesk, RustDesk). Remmina is of the first type and it does not get through every network. The problem is that certain wireless ISPs may put one behind their [NAT](https://en.wikipedia.org/wiki/NAT_traversal) in such a way that no port forwarding is possible, which can always be checked by using

[SO](https://stackoverflow.com/questions/54878001/cannot-get-mosquitto-to-allow-connection-from-outside-local-network)

[www.yougetsignal.com](https://www.yougetsignal.com/tools/open-ports/)

[canyouseeme.org](https://canyouseeme.org/)

Hole punching solves the problem, but demands another external server or an entire commercial service. An interesting option is [RustDesk](https://github.com/rustdesk/rustdesk) which automates everything openly, for free, for now. Running and configuring such software is a complex endeavor however.

Yet another way is to rely on a 3rd party MQTT broker. CloudMQTT has removed its only free plan. HiveMQ allows a free setup, but I am getting "Server closed connection without DISCONNECT" already in a simple test setup when switching a computer yet using the same credentials from their CLI interface. Such services seem to be good for big commercial apps as they introduce the need for some consultancy with the provider.

A decent way out of these problems could be the ESP RainMaker cloud which solves most of the problems of connecting ESP32 chips globally, for free. The problem here is a heavy dependence on the cloud built by Espressif Systems, with a still evolving C++ API. 

As a middle ground, I could suggest one [sending commands via github](https://github.com/aabbtree77/sendrecv), which I have tested. We are not able to send simple text messages/UDP/MQTT packets directly from PC to PC based on their MAC addresses, but at least we have access to a few reliable and largely free services such as gmail or github. They can be used to send and receive commands from PC to PC globally and achieve remote control independence from complex proprietary/open source software. The downside of this approach is that it is very raw/primitive yet and Github tracks each file update and thus the size of the repository grows which may exceed a quota.

## Some Observations

- When the DHT sensor is detached from the chip's pin, executing the line "dht_sensor.measure()" or "dht_sensor.start()" 
  in the MicroPython REPL will reboot the device with a "useful" error message:

  ```console
  >>> import mainx
  ets Jun  8 2016 00:22:57

  rst:0x8 (TG1WDT_SYS_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
  configsip: 0, SPIWP:0xee
  clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
  mode:DIO, clock div:2
  load:0x3fff0030,len:4540
  ho 0 tail 12 room 4
  load:0x40078000,len:12448
  load:0x40080400,len:4124
  entry 0x40080680
  W (57) boot.esp32: PRO CPU has been reset by WDT.
  W (58) boot.esp32: WDT reset info: PRO CPU PC=0x400803c0
  W (59) boot.esp32: WDT reset info: APP CPU PC=0x40093cb2
  MicroPython v1.17 on 2022-01-10; 4MB/OTA module with ESP32
  Type "help()" for more information.
  >>> 
  ```

- ESP12 has a pathetic amount of RAM, but ESP32 is no cake either. Importing the font arial35 from Peter Hinch's ssd1306 lib along with freesans20 
  is still possible when running the DHT measurement with the display without the networking stack. Adding the async networking and the MQTT libs exposes an 
  insufficient RAM: "MemoryError: memory allocation failed, allocating 6632 bytes" (breaks at "#import gui.fonts.arial35 as arial35").

- Despite all the amazing work by Peter Hinch, I do not recommend using displays with ESP32 and the async codes which I could not get to receive the MQTT messages, but the device could send them.

- Capacitive Soil Moisture Sensor v1.2 works, but its voltage/ADC value range between dry and wet soil leaves space for improvements.
  Most of the existing solutions based on the electrical resistance are worse due to the corrosion of the electrodes. Personal attempts to make soil-moisture sensitive resistors out of cheap construction-site gypsum did not meet success.

- The problem of global connectivity has no answers, only choices. What a pity that we cannot simply send a UDP packet to a MAC address and instead have to deal with so many layers of IT crapola.

- Ditch this whole approach in favour of the ESP Rainmaker cloud with the Arduino IDE and C++ API?!

## References

My great respect to the MicroPython community, esp. Peter Hinch and Rui and Sara Santos whose code is worth checking out.

Essential:

- [Getting started]
- [MicroPython firmware]
- [micropython-Rui-Santos]
- [umqtt.simple]
- [esp32-30pin]

Optional:

- [micropython-mqtt-async]
- [micropython-nano-gui]
- [umqtt.robust]
- [umqtt.robust dies when MQTT broker gets restarted #102]
- [umqtt.simple socket behaviour when WiFi is degraded #103]
- [umqtt.robust: Resubscribe to topics after doing reconnect. #186]
- [can't await mqtt.simple publish method #357]
- [unstable MQTT on ESP8266 (4+ days) #2568]
- [umqtt cannot import MQTTClient #250]


[Getting Started]: https://www.youtube.com/watch?v=_vcQTyLU1WY&list=PLKGiH5V9SS1hUz5Jh_35oTFM4wPZYA4sT&index=2
[MicroPython firmware]: https://micropython.org/download/esp32-ota/
[micropython-mqtt-async]: https://github.com/peterhinch/micropython-mqtt/tree/master/mqtt_as
[micropython-nano-gui]: https://github.com/peterhinch/micropython-nano-gui
[micropython-Rui-Santos]: https://github.com/RuiSantosdotme/ESP-MicroPython/tree/master/code/MQTT/Node_RED_Client
[umqtt.simple]: https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/example_sub_led.py
[esp32-30pin]:https://www.mischianti.org/wp-content/uploads/2020/11/ESP32-DOIT-DEV-KIT-v1-pinout-mischianti.png
[umqtt.robust]: https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.robust/example_sub_robust.py
[umqtt.robust dies when MQTT broker gets restarted #102]: https://github.com/micropython/micropython-lib/issues/102
[umqtt.robust: Resubscribe to topics after doing reconnect. #186]: https://github.com/micropython/micropython-lib/pull/186
[can't await mqtt.simple publish method #357]: https://github.com/micropython/micropython-lib/issues/357
[umqtt.simple socket behaviour when WiFi is degraded #103]: https://github.com/micropython/micropython-lib/issues/103
[unstable MQTT on ESP8266 (4+ days) #2568]: https://github.com/micropython/micropython/issues/2568
[umqtt cannot import MQTTClient #250]: https://github.com/micropython/micropython-lib/issues/250
