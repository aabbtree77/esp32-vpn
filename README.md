
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

This report is about DOIT DEVIT V1 ESP32-WROOM-32 applied to wireless communication inside LAN via MQTT, mostly. The MicroPython code achieves resilience w.r.t. a lost Wi-Fi. 

The Remmina part shown above is for the global connectivity over the internet and it is just an idea. It demands opening ports which may not always be possible. Instead, one could add another LAN node to the same PC which runs LAN's MQTT broker. That node would have two purposes: (i) it would run a regular Python with its paho-mqtt library to control the ESP32 MQTT via the broker, and (ii) it would manage a communication via the internet by means of IFPS. However, all that is still a "web2" tech stack, needing the whole server/broker just to communicate with ESP32 when ideally ESP32 should act directly as an IFPS node without PC1 shown in the picture above, and even without MQTT.

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

This path is not recommended. Instead, one could communicate with ESP32 as indicated in the introduction or even by [sending commands via github](https://github.com/aabbtree77/sendrecv) which I used before not knowing about the existence of IFPS.

## Observations about ESP32 and MicroPython

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

- ESP32 and MicroPython is ideal for projects within a LAN. In the case of the global connectivity this combo is no longer adequate as one needs an external MQTT broker with all the configuration shenanigans of "web2". Instead, one could opt for the ESP Rainmaker cloud with the Arduino IDE and its C++ API which is also highly suboptimal.

- The best way would be to treat any ESP32 as an IPFS node, but solid codes do not exist there yet, and definitely not in MicroPython. As an example, kubo, the implementation of IPFS in Go, takes more than 60MB as a Linux package, and it is recommended "running it on a machine with at least 2 GB of RAM and 2 CPU cores (kubo is highly parallel). On systems with less memory, it may not be completely stable."

- Therefore, ESP32 and MicroPython is still not there, but it leads to an interesting challenge of implementing IFPS on such low RAM devices.

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
