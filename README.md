> “An operating system is a collection of things that don't fit into a language. <br>
There shouldn't be one.”<br> &ndash; Dan Ingalls

<table align="center">
    <tr>
    <th align="center"> ESP32 as an MQTT Client in the Context of IoT</th>
    </tr>
    <tr>
    <td>
    <img src="./images/mermaid-diagram-2022-08-20-161912.png"  alt="ESP32 in the Operating Mode)" width="100%" >
    </td>
    </tr>
</table>

## Introduction

[DOIT DEvKit V1 ESP32-WROOM-32](https://en.wikipedia.org/wiki/ESP32) is an inexpensive (15 euro) microcontroller board with Wi-Fi. The challenge is to connect it to the IoT.

Initially, our goal was to use the ESP32 board for remote plant watering. This goal was achieved. However, we also found code-free solutions based on some remote light switches which could be operated with a mobile app. The latter are cheap, easy to use, and do not cost much, but they rely on unknown servers. The light switches also do not provide feedback, one presses "on"/"off" with the hope it all works on the other end (the actual control plant).

Eventually this little project transformed into my personal research on various global ways to connect PCs, which I keep updating from time to time here.

## ESP32 and IoT

There are a lot of ways to set up this Espressif MCU, but nothing too impressive to be honest:

1. ESP32-specific cloud called [ESP RainMaker](https://github.com/espressif/esp-rainmaker/issues/96). Vendor lock-in, still young/unclear stability, steep pricing. AWS-based, so it is 3rd party on top of another 3rd party. In the year 2023 one hardly wants yet another "customer service". I want a one-time payment board with global p2p-like connectivity. Please provide the board with an IP address, not a rental fee. 

2. 3rd party MQTT brokers and ESP32 MQTT clients. [CloudMQTT](https://www.cloudmqtt.com/blog/cloudmqtt-cute-cat-free-plan-out-of-stock.html), [HiveMQ](https://community.hivemq.com/t/connection-fail-in-hivemq-cloud/579/4)... Vendor lock-in, phased-out plans, issues.

3. [Amazon API Gateway with Websockets](https://www.youtube.com/watch?v=z53MkVFOnIo). Vendor lock-in. Most likely one of the better services out there, but it is not free.

4. [Wireguard for ESP-IDF](https://github.com/trombik/esp_wireguard). Wireguard is a very solid FOSS VPN, but it needs a public static IP. The properties of this specific ESP32 client library remain unlear (Wi-Fi resilience? NAT punching?). The user base is too tiny to trust it, there might be some [low level magic](https://github.com/esphome/feature-requests/issues/1444) needed to get it working.

5. Connecting an ESP32 device to a PC/Linux board over Wi-Fi that runs an MQTT broker within its LAN, thus delegating the problem of global connectivity effectively to the PC space.

6. Similar to option No.5, except running the MQTT broker on the router, thus removing an extra Linux PC. This looks very economic at the first glance, one needs to upgrade, say, the TP-Link firmware with the [OpenWrt Linux](https://esp8266.ru/esp8266-openwrt-mosquitto-mqttwarn-thingspeak-email-android-ios-twitter-cloudmqtt/) whose .bin image will barely be 6-8Mb. However, such a Linux server is very limited and rebooting it will mean rebooting the router, which can easily mess up the whole network.

The fifth option is my choice. It is the most reliable, but it demands an extra PC/Linux board (PC-1 shown in the figure above). This is not ideal if one simply wants to fire up a mobile phone app to control an ESP32 globally from anywhere, directly. However, I just do not want to deal with Wireguard on ESP32 or the ESP RainMaker cloud when the connectivity errors start to appear. Running the MQTT broker on [OpenWrt](https://cgomesu.com/blog/Mesh-networking-openwrt-batman/) or [RutOS](https://teltonika-networks.com/lt/resursai/webinarai/rutos-an-extensive-introduction) is also not the option as I do not want to touch a router unless I absolutely have to.

In order to establish remote PC connections, I have tested [Hyprspace](https://github.com/hyprspace/hyprspace/issues/94) and [EdgeVPN](https://github.com/mudler/edgevpn/issues/25). Both of them are FOSS (written in Go) based on the MIT-licensed stack called [go-libp2p](https://github.com/libp2p/go-libp2p) which stems from [kubo](https://github.com/ipfs/kubo) (go-ipfs). This stack provides [NAT](https://discuss.libp2p.io/t/how-nat-traversal-and-hole-punching-work-in-ipfs/1422) [traversal](https://github.com/ipfs/camp/blob/master/DEEP_DIVES/40-better-nat-traversal-so-that-relay-servers-are-a-last-not-first-resort.md) without an external 3rd party service or static IP. It is very useful for the ability to ssh into almost any remote computer.

Do these tools always work though, are they equally good? EdgeVPN may have an [edge](https://github.com/mudler/edgevpn/issues/25).

## The Wild World of Computer Networks

EdgeVPN solves the problem of external connections without a public IP/3rd party. However, the connection will typically be very slow. It is fast enough to establish an ssh connection, exchange MQTT messages between the broker and ESP32 within a LAN, and logout. However, the solution is not ideal. In a long run, it is better to have a more solid VPN, preferably with a static public IP. Numerous options exist, though nothing too exciting:

- [Google IoT Core](https://news.ycombinator.com/item?id=32475298) is being retired. AWS IoT, ShellHub, RemoteIoT, DataPlicity, PiTunnel, SocketXP, Tunnel In, Zerynth Cloud Core...  

  "All your stupid ideals You've got your head in the clouds" - Depeche Mode, Useless, 1997

- [Heroku](https://twitter.com/heroku/status/1562817050565054469) has no free plans anymore.

- Remmina, Chrome Remote Desktop, TeamViewer, AnyDesk, RustDesk, Screego... Remmina demands port forwarding which is very limited and unreliable. "UbuntuDesk" with a solid NAT punching, please.

- [Parsec, Rainway, Steam Remote Play](https://news.ycombinator.com/item?id=29479503) game streaming services provide responsive VPNs, but they are not free.

- Getting a VPS on, say, Hostinger, and setting up [Wireguard](https://www.youtube.com/watch?v=5Aql0V-ta8A). A solid option that also gets one a public IP, but it involves a monthly fee. Wireguard helpers: [pivpn](https://github.com/pivpn/pivpn), [wg-easy](https://github.com/wg-easy/wg-easy), [firezone](https://github.com/firezone/firezone)...

- Tailscale, Nebula, NetBird, Netmaker, headscale, innernet, [ZeroTier](https://www.youtube.com/watch?v=sA55fcuJSQQ), tinc, [Hamachi](https://news.ycombinator.com/item?id=29479503)... A long list of "[overlay](https://github.com/search?l=Go&o=desc&q=wireguard&s=stars&type=Repositories) [mesh](https://github.com/cedrickchee/awesome-wireguard) [network](https://wiki.nikiv.dev/networking/vpn/wireguard)" software built on top of Wireguard, mostly, but not always. Quite a few services with free plans, but how long will they stay that way?

- [NetFoundry](https://netfoundry.io/edge-and-iot-zero-trust-networking/). "The SaaS is free forever for up to 10 endpoints, so you can get started immediately with the SaaS or open source." It positions itself as a [more secure Tailscale](https://netfoundry.io/networking-alternative-compare-tailscale-netfoundry/), which is even further away from NAT punching layers. Too much to figure out what is what and run something simple [at the first glance](https://www.reddit.com/r/openziti/comments/xpe01b/need_some_guidance/).

- ngrok, frp, localtunnel.me, gotunnelme, boringproxy, rathole. So called "reverse proxy/tunneling", which is kind of a synonym to VPN. These tools help to expose a machine behind a NAT when you already have a VPS with a static IP. Some are [TCP only](https://github.com/fatedier/frp/issues/3009), some may result in a [much faster VPN](https://github.com/fatedier/frp/issues/2911). 

- The Onion Router: [1](https://www.maths.tcd.ie/~fionn/misc/ssh_hidden_service/), [2](https://www.techjail.net/raspberry-iotlinux-devices.html), [3](https://golb.hplar.ch/2019/01/expose-server-tor.html), [4](https://community.torproject.org/onion-services/setup/), [5](https://www.reddit.com/r/Freenet/comments/9w4do9/demo_public_darknet_on_the_tor_onioncat_ipv6/), [6](https://null-byte.wonderhowto.com/how-to/host-your-own-tor-hidden-service-with-custom-onion-address-0180159/), [7](https://opensource.com/article/19/8/how-create-vanity-tor-onion-address), [8](https://shufflingbytes.com/posts/ripping-off-professional-criminals-by-fermenting-onions-phishing-darknet-users-for-bitcoins/).
 
  "It's easier to setup a Tor hidden service than it is to set up a server with a domain. You don't have to know anything about DNS or firewalls. I'm surprised that they aren't more common."

- [Yggdrasil](https://news.ycombinator.com/item?id=27580995), [CJDNS](https://news.ycombinator.com/item?id=16135341)/Hyperboria, ZeroNet, I2P, Scuttlebutt and other global p2p networks. I have little initiative to try these networks out as the libp2p network (with EdgeVPN) solves the problem, but it is worth noting that p2p networks are ideal for low MQTT traffic, they are totally free to use and do not demand a public static IP. [This 2022 report](https://cheapskatesguide.org/articles/yggdrasil.html) delves deeper into Yggdrasil and provides some interesting details, e.g. the number of public peers in the US.

- [Freifunk, FunkFeuer, NYC Mesh](https://github.com/redecentralize/alternative-internet#networking) and other local community/city/country-wide radio p2p networks. [B.A.T.M.A.N.](https://en.wikipedia.org/wiki/B.A.T.M.A.N.) [routing](https://cgomesu.com/blog/Mesh-networking-openwrt-batman/) at the OSI layer 2 (Data link) rather than 3 (Network). [This is actually very interesting](https://www.youtube.com/watch?v=DrXJ9_ezSy4). The free internet built with only "line of sight" devices, mostly routers with OpenWrt. Tools to mesh WLANs and LANs, BATMAN-based and traditional, with certain [use cases](https://youtu.be/t4A0kfg2olo?t=134).

- [Meshtastic](https://www.youtube.com/watch?v=TY6m6fS8bxU) is like Freifunk, but limited to/focused on the LoRa radio communication. Its main use seems to be remote rural areas, crowded rock festivals, animal tracking, where telecom operators do not work well and satellite services are too expensive. LoRa (LoRaWAN) alternatives include [NB-IoT, Sigfox, and Wi-Fi HaLow](https://www.hackster.io/news/the-ttgo-t-beam-an-esp32-lora-board-d44b08f18628).

- [v2ray](https://www.quora.com/How-do-I-bypass-the-GFW-of-China-without-a-VPN): [1](https://www.reddit.com/r/dumbclub/comments/106aomk/how_to_install_and_setup_v2ray/), [2](https://www.reddit.com/r/dumbclub/comments/ydfpr7/why_v2ray_doesnt_work_on_games/), [3](https://www.reddit.com/r/dumbclub/comments/11q8nhn/v2ray_xray_vps/), [4](https://www.reddit.com/r/dumbclub/comments/100g8ei/best_v2ray_config_for_gaming/), and [the Great Firewall of China](https://en.wikipedia.org/wiki/Great_Firewall):

  "the developer of shadowsocksR being asked to police station,the code on github was deleted by unimagable mean. so v2ray come out in the world. Which is stronger than shadowsocks (or in another way v2ray contains shadowsocks),the establish method is same with shadowsocks.U can search 一键搭建v2ray on YouTube..."

- "v2ray" and "Shadowsocks" related software that helps to get through firewalls: [Outline VPN](https://www.youtube.com/watch?v=O9jGg6tE7nY), [udp2raw](https://github.com/wangyu-/udp2raw), [hysteria](https://github.com/apernet/hysteria), [trojan](https://github.com/trojan-gfw/trojan), [clash](https://github.com/Dreamacro/clash), [gost](https://github.com/ginuerzh/gost/blob/master/README_en.md), [naiveproxy](https://github.com/klzgrad/naiveproxy), [pi-hole](https://github.com/pi-hole/pi-hole). Outline VPN needs to be installed as a server on DigitalOcean/Hostinger, and it is free just like Wireguard, but it might have stronger hole-punching properties. The other tools mentioned here are less clear to me.

- The list may go [on](https://news.ycombinator.com/item?id=24893615) and [on](https://news.ycombinator.com/item?id=27672715) and [on](https://github.com/anderspitman/awesome-tunneling) and [on](https://changelog.complete.org/archives/10231-recovering-our-lost-free-will-online-tools-and-techniques-that-are-available-now)... with some phishing attacks to consider: [1](https://news.drweb.com/show/?i=14451), [2](https://www.reddit.com/r/crowdstrike/comments/tjh602/query_hunt_for_reverse_proxy_tunnel_tools/), [3](https://thestack.technology/ransomware-attack-bitlocker/), [4](https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/ipfs-the-new-hotbed-of-phishing/)...

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
  
## Observations about ESP32 and MicroPython

- **Hardware is tough.** When the DHT sensor is detached from the chip's pin, executing the line "dht_sensor.measure()" or "dht_sensor.start()" 
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
- **Too little RAM.** ESP12 has a pathetic amount of RAM and is a [disaster](https://github.com/espressif/esp-rainmaker/issues/8), but ESP32 is no cake either. Importing the font arial35 from Peter Hinch's ssd1306 lib along with freesans20 
  is still possible when running the DHT measurement with the display without the networking stack. Adding the async networking and the MQTT libs exposes an 
  insufficient RAM: 
  
  ```console
  "MemoryError: memory allocation failed, allocating 6632 bytes" (breaks at "#import gui.fonts.arial35 as arial35").
  ```
- **Low quality sensors**, see e.g. this [discussion](https://www.youtube.com/watch?v=IGP38bz-K48) of Capacitive Soil Moisture Sensor v1.2.
  The solutions based on the electrical resistance are worse due to a rapid corrosion of the electrodes. Contrary to some existing recommendations, submerging them into a cheap construction-site gypsum does not work as this kills their moisture sensitivity.
  
- Monitoring soil moisture is a much harder problem than sensing air humidity. Perhaps the best way is to set up a camera and observe the ground surface. It is doubtful whether ESP32 could be a good platform for capturing and sending images.     
  
- Despite all the amazing work by Peter Hinch, I could not make the async codes receive my MQTT messages, the device could only send them.

- After a long search and disappointment I could finally reach a certain resilience w.r.t. the Wi-Fi loss thanks to this [code by Rui and Sara Santos][micropython-Rui-Santos].
  
## Conclusions

- DOIT DEvKit V1 ESP32-WROOM-32 is roughly an ATmega board, only with a longer reach to its sensors, minus reliability.
   
- It is unlikely that [ESP32](https://en.wikipedia.org/wiki/ESP32) boards will displace embedded Linux. The elephant in the room is tiny ESP32 RAM which is on the scale of kilobytes. Tiny RAM = nonexistent or custom incomplete network libs, similar to the case of [Atmega with ENC28J60](http://tuxgraphics.org/electronics/200606/article06061.shtml). They can be made to be autonomous, but I would not use them alone to build, say, a complete remote Wi-Fi trail camera/heating/plant watering, industrial/automotive/drone control.

- A bus card reader? We used to have some early low RAM devices here in Vilnius for about 5-10 years. They would produce occasional errors and that is how I know that their memory was kilobytes, it would be displayed in the error message on the screen :). This year (2023) the bus card readers got replaced with Ridango devices. They support several public city transport cards and a QR-code based mobile payment option. This evolution shows that ESP32 is not ideal for such applications.
  
- The [ESP32](https://en.wikipedia.org/wiki/ESP32) niche could be massive LANs with nodes connected to a Linux broker via MQTT, where each node failure is non-critical: Wi-Fi-capable [bin level sensors](https://www.ecubelabs.com/bin-level-sensors-5-reasons-why-every-city-should-track-their-waste-bins-remotely/), robotic toys. Contrary to popular belief, these chips are very suboptimal for hobby networking, compared to, say, Raspberry Pi Zero W. I would look more into the types of [ESP32-ready sensors](https://esphome.io/#sensor-components) and think of distributing them within a LAN.

- [ESP32](https://en.wikipedia.org/wiki/ESP32) has a direct small distance p2p communication capacity via BLE and ESP-NOW protocols, which I have not explored. In theory, this could be used to implement electronic bike shifting, remove low power electric control wires whenever possible. "But hold on a second, did you know that you never need to update the firmware on a mechanical derailleur?" 

- The combo of [ESP32](https://en.wikipedia.org/wiki/ESP32) with MicroPython achieves a hassle-free ADC to measure analogue voltage values. An easy ROM address scanning (whenever one needs to pin a lot of temperature sensors on a single wire input) is also a solid achievement. This is a lot messier in the ATmega world. There is no need to deal with the fuse bits, makefiles and C shenanigans. On the other hand, MicroPython eats up some precious RAM and Python coding is very prone to typos, which is a huge problem.

- Wi-Fi is limited to 10-40m without repeaters. Consider [LILYGO TTGO T-Beam ESP32 board](https://www.youtube.com/watch?v=TY6m6fS8bxU) for LoRa radio communication which may reach [1-166km](https://meshtastic.discourse.group/t/practical-range-test-results/692/47?page=2). ESP32 is suboptimal regarding its power consumption, which is critical in [mobile p2p radio networking](https://meshtastic.discourse.group/t/real-world-use-cases/175).

- [EdgeVPN](https://github.com/mudler/edgevpn/issues/25) is a remarkable FOSS VPN which could be used to ssh globally to any computer behind NAT without any 3rd party service and static IP. The connection is likely to be slow, but this is ideal for mild messaging. One can setup an MQTT broker on one node of this VPN and use it to deliver messages to any other node, build all sorts of "actors", "workers", "microservices", without having to worry about public IPs and NAT. It would be interesting to experiment more with this tool and the whole libp2p network.

- [Wireguard](https://www.youtube.com/watch?v=5Aql0V-ta8A) is another remarkable FOSS VPN. It can be a lot faster than EdgeVPN, but it demands a public static IP, which means a monthly payment, dependency on 3rd party services, a Web2 philosophy.

- Consider economics. DOIT DEVIT V1 ESP32-WROOM-32 vs Raspberry Pi Zero W bought on, say, anodas.lt in Vilnius, May 23rd, 2023. The former costs 12.70€, while the latter is 23.90€ plus a 32GB MicroSD card sold as low as 4.90€. A typical hobbyist will only need a dozen of such devices in a life time, and the cost of 2-4x higher priced Raspberry Pi Zero W will be negligible compared to the pain one will experience with scarce network software and tiny kilobyte RAM of ESP32. [Andreas Spiess](https://www.youtube.com/watch?v=rXc_zGRYhLo&t=389s) suggests getting an old used laptop on ebay instead of a new Raspberry Pi.

- [Freifunk](https://youtu.be/t4A0kfg2olo?t=134) and this whole OneMarcFifty channel deserves a closer look. TBC... 

## References

ESP32 Essentials:

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

[Depeche Mode - Useless](https://www.youtube.com/watch?v=U2Kyu4XURaE) 

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
