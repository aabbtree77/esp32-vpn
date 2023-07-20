
> “...the bullshit piled up so fast... you needed wings to stay above it.”<br> &ndash; Apocalypse Now, 1979

<table align="center">
    <tr>
    <th align="center"> Towards Reliable IoT</th>
    </tr>
    <tr>
    <td>
    <img src="./images/mermaid-diagram-2023-07-20-162627.png"  alt="ESP32 in the Operating Mode)" width="100%" >
    </td>
    </tr>
</table>

## Introduction

[DOIT DEvKit V1 ESP32-WROOM-32](https://en.wikipedia.org/wiki/ESP32) is an inexpensive (15 euro) microcontroller board with Wi-Fi, Bluetooth LE, and ESP-NOW. One can connect it to [a lot of sensors](https://esphome.io/#sensor-components) with ready-made drivers. The challenge is to control such a board globally, via the internet.

Initially, the goal was to use the ESP32 board for remote plant watering. This goal was achieved. However, we also found code-free solutions based on the Clas Ohlson WiFi Smart Plug which could be dissected and controlled with their mobile app. The latter are cheap (10-20 euro) and easy to use, but one must rely on the Clas Ohlson servers. Smart plugs are limited: It is a one way communication from a mobile phone to an electrical relay via 3rd party servers.

The ideal is reliable developer-friendly Linux-centric global open free communication.

## ESP32 and IoT

There are several ways to connect the ESP32 globally:

1. Cloud services: [ESP RainMaker](https://github.com/espressif/esp-rainmaker/issues/96), [Firebase](https://randomnerdtutorials.com/firebase-control-esp32-gpios/), [Blynk](https://blynk.io/blog/esp32-blynk-iot-platform-for-your-connected-product), [Arduino IoT Cloud](https://www.youtube.com/watch?v=rcCxGcRwCVk), [Yaler.net](https://yaler.net/), [Amazon API Gateway with Websocket API](https://www.youtube.com/watch?v=z53MkVFOnIo), [Amazon API Gateway with RESTful API](https://aws.amazon.com/blogs/compute/building-an-aws-iot-core-device-using-aws-serverless-and-an-esp32/), [Husarnet](https://husarnet.com/docs/tutorial-esp32-platformio), [CloudMQTT](https://www.cloudmqtt.com/blog/cloudmqtt-cute-cat-free-plan-out-of-stock.html), [HiveMQ](https://community.hivemq.com/t/connection-fail-in-hivemq-cloud/579/4), [RemoteXY](https://www.youtube.com/watch?v=dyEnOyQS1w8&t=1s), [Google Cloud IoT](https://www.elementzonline.com/blog/Connecting-ESP32-to-Google-Cloud-IoT), Viper/Zerynth: [1](https://zerynth.com/blog/python-on-esp32-getting-started/), [2](https://lemariva.com/blog/2021/12/zerynth-esp32-google-iot-core-part-1-sending-data-to-the-cloud), [3](https://zerynth.com/customers/case-studies/zerynth-powered-smart-iot-display/)... 

    Google IoT Core [will be discontinued on August 16, 2023](https://news.ycombinator.com/item?id=32475298). [Free plans come and go](https://twitter.com/heroku/status/1562817050565054469). Husarnet is the only one from the listed above which provides [its open source code](https://husarnet.com/business/open-source).
    
2. Classical web apps which will communicate with the ESP32 via the HTTP requests: [1](https://randomnerdtutorials.com/control-esp32-esp8266-gpios-from-anywhere/), [2](https://randomnerdtutorials.com/esp32-esp8266-mysql-database-php/). Notice that the board needs to know the URL or the IP address of the web app to send GET/POST requests, but the web app does not need to know the address of the board.

3. Something similar, but with the MQTT replacing the HTTP. Again, only the board needs to know the URL or the IP address of the "MQTT app". The MQTT is preferable for two reasons: (i) the MQTT client libs are more reliable than their HTTP counterparts in the ESP world, and (ii) there is no need to write a web app to send/receive data. One can simply run the Mosquitto broker as an "MQTT app" and use "mosquitto_pub/sub" commands w.r.t. the MQTT topics that the board will pub/sub to.

4. Wireguard on the ESP32: [1](https://github.com/ciniml/WireGuard-ESP32-Arduino), [2](https://github.com/trombik/esp_wireguard), [3](https://github.com/esphome/feature-requests/issues/1444). This is for some overly optimistic uses where the ESP32 becomes an independent node on a par with Linux boards. Wireguard still needs a public static IP.

5. Connecting the ESP32 to the Linux PC over Wi-Fi that runs the MQTT broker within its LAN, thus delegating the problem of global connectivity effectively to the PC space.

The last option is my choice. It is the most reliable one, but it demands an extra PC/Linux board (PC-1 shown in the figure above). 

One can run the MQTT broker on a router, e.g. with [OpenWrt Linux](https://cgomesu.com/blog/Mesh-networking-openwrt-batman/): [1](https://www.onetransistor.eu/2019/05/run-local-mqtt-broker-on-openwrt-router.html), [2](https://esp8266.ru/esp8266-openwrt-mosquitto-mqttwarn-thingspeak-email-android-ios-twitter-cloudmqtt/) or [RutOS](https://teltonika-networks.com/lt/resursai/webinarai/rutos-an-extensive-introduction), but these router OSes (6-8MB .bin image size) are too limiting.

In order to establish remote PC connections, we have tested [Hyprspace](https://github.com/hyprspace/hyprspace/issues/94), [EdgeVPN](https://github.com/mudler/edgevpn/issues/25), and [awl](https://github.com/anywherelan/awl). All of them are built on top of [go-libp2p](https://github.com/libp2p/go-libp2p) which is both, the FOSS code, and the actual running network with the focus on a [NAT](https://discuss.libp2p.io/t/how-nat-traversal-and-hole-punching-work-in-ipfs/1422) [traversal](https://github.com/ipfs/camp/blob/master/DEEP_DIVES/40-better-nat-traversal-so-that-relay-servers-are-a-last-not-first-resort.md). This stack is very useful for the ability to ssh into a remote computer without a public static IP.

According to [Max Inden, 2022](https://archive.fosdem.org/2022/schedule/event/libp2p/attachments/audio/4917/export/events/attachments/libp2p/audio/4917/slides.pdf), the libp2p network "powers the IPFS, [Ethereum 2](https://blog.libp2p.io/libp2p-and-ethereum/#how-ethereum-beacon-nodes-use-libp2p-%F0%9F%94%8D), Filecoin and Polkadot network and there are ~100K libp2p based nodes online at any given time".

Do these tools always work though, are they equally good? 

  [hyprspace](https://github.com/hyprspace/hyprspace): 895 LOC of Go. Minimal, but weaker hole punching.
  
  [awl](https://github.com/anywherelan/awl): 6.5 KLOC of Go. Just about right.
  
  [EdgeVPN](https://github.com/mudler/edgevpn): 7.5 KLOC of Go. Solid punching, but problems with 24/7 runs. No Android support. 

  [go-libp2p](https://github.com/libp2p/go-libp2p): 67 KLOC of Go. The base layer for the three above.
  
  [Syncthing](https://github.com/syncthing/syncthing/tree/main): 110 KLOC of Go, 37.5 KLOC of Js, 10.6 KLOC of CSS. Irrelevant here, but this is what it takes to sync a folder.


EdgeVPN may have an [edge](https://github.com/mudler/edgevpn/issues/25) over Hyprspace, but there is [a problem with longer runs](https://github.com/mudler/edgevpn/issues/137). [awl](https://github.com/anywherelan/awl) is more reliable and also more convenient (desktop browser GUI for one-click handshakes, runs on Android), but not always. If for some reason one has to reinstall the Android app, the latter generates a new peer id which then needs to be confirmed again on the other end. EdgeVPN simply shares the same secret file and has no handshakes.

## Some Photos

This hobby/demo hardware has been assembled and soldered by Saulius Rakauskas (InfoVega).

![gThumb01](./images/esp32-ssd1306-dht22-front.jpg "ESP32 on a custom board: Front.")

![gThumb02](./images/esp32-ssd1306-dht22-back.jpg "ESP32 on a custom board: Back.")

## Circuit Diagram

- [esp32-30pin] (the 30-pin variant of DOIT DEVIT V1 ESP32-WROOM-32, not 36).

- DHT22, Multiple LEDs, Capacitive Soil Moisture Sensor v1.2, see boot.py.

- ~~SSD1306 with in-software I2C.~~ Dropped it, rewind to "the last before revamp" commit if interested.

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

  The hostname/ifconfig command will provide the local IP address assigned by the router to a computer (PC-1) which runs the MQTT broker (Moscquitto), such as '192.168.1.107'. It will have to be entered in boot.py manually/explicitly. 


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

- EdgeVPN:

  Download the latest edgevpn executable for your OS, e.g. [edgevpn-v0.23.1-Linux-x86_64.tar.gz](https://github.com/mudler/edgevpn/releases/tag/v0.23.1). 
  
  Use the same release version on all the computers that will be connected into a VPN, otherwise there might be conflicts as some versions have changed the way the keys are stored and decoded.
  
  cd into extracted folder and generate config.yaml:
  
  ```console
  ./edgevpn -g > config.yaml
  ```

  Distribute it on all the machines that will be connected to EdgeVPN (manually by carrying a USB stick, via email, etc.).
  
  Assuming the machine runs Ubuntu, place the executable with config.yaml in the same folder and run
  
  ```console
  sudo IFACE=edgevpn0 ADDRESS=10.1.0.7/24 EDGEVPNCONFIG=config.yaml ./edgevpn --log-level debug
  ```
  
  The command assigns a virtual IP address 10.1.0.7 to the machine on which it is executed. Assign a different address to each machine that you connect to EdgeVPN, i.e. 10.1.0.1.. 10.1.0.254. but use the same config.yaml in each case.
  
  It may take several minutes for the node to join the EdgeVPN network which is the libp2p network under the hood. [The Linux desktop GUI](https://github.com/mudler/edgevpn-gui) is totally unnecessary.
  
  If everything is fine, you should be able to connect to any Linux computer of your VPN, e.g.
  
  ```console
  ssh username@10.1.0.8
  username@10.1.0.8's password: 
  Last login: Mon Jul 10 15:13:34 2023 from 10.1.0.4
  
  ...
  
  exit
  logout
  Connection to 10.1.0.8 closed.
  ```
    
  When you are able to connect from A to B, A's ./edgevpn --log-level debug will show a lot of information including the following lines:
  
  ```
  {"level":"DEBUG","time":"2023-07-11T14:44:39.455+0300","caller":"discovery/dht.go:204","message":" Announcing ourselves..."}
  {"level":"DEBUG","time":"2023-07-11T14:44:56.542+0300","caller":"discovery/dht.go:207","message":" Successfully announced!"}
  {"level":"DEBUG","time":"2023-07-11T14:44:56.542+0300","caller":"discovery/dht.go:210","message":" Searching for other peers..."}
  {"level":"DEBUG","time":"2023-07-11T14:44:56.583+0300","caller":"discovery/dht.go:230","message":" Known peer (already connected):
  ```
  
  followed by the list of so called multiaddresses of known/connected peers which will include global or local IPv4. While being on the A side, you should be able to see the local LAN IPv4 address of B assigned to B by its encompassing router on the B side!
  
- awl:
  
  There is [one unsolved issue](https://github.com/mudler/edgevpn/issues/137) with edgevpn that occurs on the 24/7 runs, so we switched to [awl](https://github.com/anywherelan/awl) which seems to be more reliable. 
  
  Download the [awl-tray binary](https://github.com/anywherelan/awl/releases) and run it, see [1](https://github.com/anywherelan/awl#desktopandroid) and [2](https://github.com/anywherelan/awl#desktop-awl-tray) for more details.
  
  awl is nice in that once you start it on Android, you can then run an SSH app such as [JuiceSSH](https://play.google.com/store/apps/details?id=com.sonelli.juicessh&hl=en&gl=US) and get the remote access to your Linux terminal. Make sure the VPN by awl has no overlapping/duplicated addresses and delete all the previous connections on JuiceSSH before connecting. awl is not very polished yet so you can sometimes mess up virtual addresses with many-to-one connections or loops, but these situations are avoidable more or less.
   
## ESP32 and MicroPython

- **Hardware errors.** When the DHT sensor is detached from the chip's pin, executing the line "dht_sensor.measure()" or "dht_sensor.start()" 
  in the MicroPython REPL will reboot the device with a "useful" error message:

  ```console
  >>> import main
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
- **Too little RAM.** ESP12e/ESP8266 has a [pathetic amount of RAM](https://github.com/espressif/esp-rainmaker/issues/8), but ESP32 is no cake either. Importing the font arial35 from Peter Hinch's ssd1306 lib along with freesans20 
  is still possible when running the DHT measurement with the display without the networking stack. Adding the async networking and the MQTT libs exposes an 
  insufficient RAM: 
  
  ```console
  "MemoryError: memory allocation failed, allocating 6632 bytes" (breaks at "#import gui.fonts.arial35 as arial35").
  ```
- **Low quality sensors**, see e.g. this [discussion](https://www.youtube.com/watch?v=IGP38bz-K48) of Capacitive Soil Moisture Sensor v1.2.
  The solutions based on the electrical resistance are worse due to a rapid corrosion of the electrodes. Contrary to some existing recommendations, submerging them into a cheap construction-site gypsum does not work as this kills their moisture sensitivity.
  
- Monitoring soil moisture is a much harder problem than sensing air humidity. Perhaps the best way is to set up a camera and observe the ground surface. It is doubtful whether the ESP32 could be a good platform for capturing and sending images.     
  
- Despite all the amazing work by Peter Hinch, the device could only send the MQTT messages, the receiving did not work.

- After a long search and disappointment the resilience w.r.t. the Wi-Fi loss was reached thanks to this [code by Rui and Sara Santos][micropython-Rui-Santos].
  
## Final Remarks

- The [ESP32](https://en.wikipedia.org/wiki/ESP32) is better than sending UDP packets with [Atmega and the ENC28J60](http://tuxgraphics.org/electronics/200606/article06061.shtml). 15 years bring some progress. One can even reach a certain Wi-Fi resilience and distribute the [ESP32-ready sensors](https://esphome.io/#sensor-components) within a LAN with some mild confidence. However, tiny RAM = very limited software, esp. very limited global connectivity options. With some painful acrobatics one may run "Wireguard" on the ESP32, but the go-libp2p apps are beyond the reach of these boards.
    
- All this gigantic Web2 VPN service activity exists mostly because A and B do not have proper addresses. We cannot use MAC, we do not have the IPv6. So how does one send a message to a board/PC? It is a mess as one must deal with the OSI model, overlay mesh networks, proxies and reverse proxies, [tunneling and self-hosting](https://github.com/anderspitman/awesome-tunneling), STUN/TURN/ICE, TCP meltdown, CGNAT, SOCKS5, ARP, ICMP, subnet masks, CIDR, gateways, port forwarding, host names, DNS and mDNS, DHCP, virtual interfaces, firewalls, Linux kernel routes, routers and routing... Good luck with Remmina...

- The new Web3 (p2p) way is remarkable in that the tools such as Hyprspace, EdgeVPN, [awl](https://github.com/anywherelan/awl), Syncthing: [1](https://www.reddit.com/r/Syncthing/comments/1324xrm/how_reliable_is_synthing/), [2](https://forum.syncthing.net/t/how-syncthing-communicates-with-my-server-when-im-in-a-public-network/20437/2) solve the global connectivity problem without a need to rent the VPS with a static IP.

- Either way, some pretty basic services are so complex underneath. 70 KLOC of go-libp2p just to give your computer a global address, mostly. Syncing a folder? Double these seventy thousand lines of code. Humanity has not yet automated elections, and no doubt the solution is going to be [quite an architecture](https://hackmd.io/@juincc/B1QV5NN5S).

## Some ESP32 References

Essentials:

- [MicroPython firmware]
- [micropython-Rui-Santos]
- [umqtt.simple]
- [esp32-30pin]

Optional (problems to be aware of):

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

## Appendix: Useful Applications to Consider

1. [Waste bin level detectors based on ultrasonic distance sensors](https://www.ecubelabs.com/bin-level-sensors-5-reasons-why-every-city-should-track-their-waste-bins-remotely/)?

2. A bus card reader? We used to have some early low RAM devices here in Vilnius for about 5-10 years. This year (2023) the bus card readers got replaced with Estonian Ridango devices which, I suspect, run Linux.
    
3. Mapping out minefields? See [1](https://youtu.be/suxLa6kWsrw?t=2000) and [2](https://cepdnaclk.github.io/e17-3yp-Landmine-Detector/) for two completely different systems. The first one presents a radar mounted on a drone, while the second one is a Colpitts oscillator-based metal detector on a four-wheel robot. 

4. [The GPS Tracker](https://how2electronics.com/esp32-gps-tracker-using-l86-gps-module-oled-display/).

5. Non-invasive blood glucose and hemoglobin monitoring: [1](https://ijrpr.com/uploads/V2ISSUE9/IJRPR1274.pdf), [2](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8230267/), [3](https://www.mdpi.com/1424-8220/22/13/4855).
 
6. [A smart walking cane for the blind](https://github.com/manishmeganathan/smartwalkingcane). 
