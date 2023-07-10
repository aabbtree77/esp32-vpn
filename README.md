> “An operating system is a collection of things that don't fit into a language. <br>
There shouldn't be one.”<br> &ndash; Dan Ingalls


> “...the bullshit piled up so fast... you needed wings to stay above it.”<br> &ndash; Apocalypse Now, 1979

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

[DOIT DEvKit V1 ESP32-WROOM-32](https://en.wikipedia.org/wiki/ESP32) is an inexpensive (15 euro) microcontroller board with Wi-Fi, the BLE and ESP-NOW. One can connect it to [a lot of sensors](https://esphome.io/#sensor-components) with ready-made drivers. The challenge is to control such a board globally, via the internet.

Initially, the goal was to use the ESP32 board for remote plant watering. This goal was achieved. However, we also found code-free solutions based on the Clas Ohlson WiFi Smart Plug which could be operated with their mobile app. The latter are cheap (10-20 euro) and easy to use, but one must rely on the Clas Ohlson servers. The smart plugs are also very limited in that they do not provide any feedback, one presses "on"/"off" with the hope it all works on the other end.

Eventually this little project transformed into my personal research on global ways to connect things, which I keep updating from time to time here. My ideal is a reliable coder-friendly Linux-centric global communication whose tech-stack one can completely own/dissect and whose parts are replaceable/customizable like lego blocks.

## ESP32 and IoT

There are several different ways to connect the ESP32 boards globally:

1. Cloud services: [ESP RainMaker](https://github.com/espressif/esp-rainmaker/issues/96), [Firebase](https://randomnerdtutorials.com/firebase-control-esp32-gpios/), [Blynk](https://blynk.io/blog/esp32-blynk-iot-platform-for-your-connected-product), [Arduino IoT Cloud](https://www.youtube.com/watch?v=rcCxGcRwCVk), [Yaler.net](https://yaler.net/), [Amazon API Gateway with Websocket API](https://www.youtube.com/watch?v=z53MkVFOnIo), [Amazon API Gateway with RESTful API](https://aws.amazon.com/blogs/compute/building-an-aws-iot-core-device-using-aws-serverless-and-an-esp32/), [Husarnet](https://husarnet.com/docs/tutorial-esp32-platformio), [CloudMQTT](https://www.cloudmqtt.com/blog/cloudmqtt-cute-cat-free-plan-out-of-stock.html), [HiveMQ](https://community.hivemq.com/t/connection-fail-in-hivemq-cloud/579/4), [RemoteXY](https://www.youtube.com/watch?v=dyEnOyQS1w8&t=1s), [Google Cloud IoT](https://www.elementzonline.com/blog/Connecting-ESP32-to-Google-Cloud-IoT), Viper/Zerynth: [1](https://zerynth.com/blog/python-on-esp32-getting-started/), [2](https://lemariva.com/blog/2021/12/zerynth-esp32-google-iot-core-part-1-sending-data-to-the-cloud), [3](https://zerynth.com/customers/case-studies/zerynth-powered-smart-iot-display/)... 

    There is so much choice with all sorts of pros and cons that would take ages to enumerate. A few remarks:
    
    - Google IoT Core [will be discontinued on August 16, 2023](https://news.ycombinator.com/item?id=32475298).
    
    - [Free plans come and go](https://twitter.com/heroku/status/1562817050565054469).
    
    - Husarnet is the only one from the listed above which provides [its open source code](https://husarnet.com/business/open-source). I also like a lot its approach/philosophy about being a thin VPN (connection as a service) which is also programmer-centric. Contrast this to the Arduino IoT Cloud which is a complete platform with all these drag and drop GUI and remote code editors, prompts for Wi-Fi credentials that include your Wi-Fi password (!) to make the ESP32 code OTA updates. 
    
2. Making and hosting a classical web app which will communicate with the ESP32 via the HTTP requests: [1](https://randomnerdtutorials.com/control-esp32-esp8266-gpios-from-anywhere/), [2](https://randomnerdtutorials.com/esp32-esp8266-mysql-database-php/). Notice that the board needs to know the URL or the IP address of the web app to send GET/POST requests, but the web app does not need to know the address of the board.

3. Something similar, but with the MQTT replacing the HTTP. Again, only the board needs to know the URL or the IP address of the "MQTT app". I prefer the MQTT for two reasons.

    Firstly, in my experience, the MQTT client libs are more reliable than their HTTP counterparts in the ESP32 world. I never had to deal with crashes and hangings with the MQTT messaging in MicroPython, but my HTTP codes had to be littered with a lot of exceptions, though these were the ESP8266 times. However, I could not get the async MQTT codes of Peter Hinch to work, so it depends.

    Secondly, there is no need to write a web app to send and receive data to the board. One can simply run the Mosquitto broker as an "MQTT app" and use "mosquitto_pub/sub" commands w.r.t. the MQTT topics that the board will pub/sub to.

4. Connecting the ESP32 to the Linux PC over Wi-Fi that runs the MQTT broker within its LAN, thus delegating the problem of global connectivity effectively to the PC space.

The last option is my choice. It is the most reliable one, but it demands an extra PC/Linux board (PC-1 shown in the figure above). 

One can run the MQTT broker on a router, e.g. with [OpenWrt Linux](https://cgomesu.com/blog/Mesh-networking-openwrt-batman/): [1](https://www.onetransistor.eu/2019/05/run-local-mqtt-broker-on-openwrt-router.html), [2](https://esp8266.ru/esp8266-openwrt-mosquitto-mqttwarn-thingspeak-email-android-ios-twitter-cloudmqtt/) or [RutOS](https://teltonika-networks.com/lt/resursai/webinarai/rutos-an-extensive-introduction), but these router OSes (6-8MB .bin image size) are too limiting.

In order to establish remote PC connections, I have tested [Hyprspace](https://github.com/hyprspace/hyprspace/issues/94) and [EdgeVPN](https://github.com/mudler/edgevpn/issues/25). Both of them are FOSS (written in Go) based on the MIT-licensed stack called [go-libp2p](https://github.com/libp2p/go-libp2p). This stack provides [NAT](https://discuss.libp2p.io/t/how-nat-traversal-and-hole-punching-work-in-ipfs/1422) [traversal](https://github.com/ipfs/camp/blob/master/DEEP_DIVES/40-better-nat-traversal-so-that-relay-servers-are-a-last-not-first-resort.md) without an external 3rd party service or static IP. It is very useful for the ability to ssh into any remote computer!

Do these tools always work though, are they equally good? EdgeVPN may have an [edge](https://github.com/mudler/edgevpn/issues/25).

## Some Other Things To Think About

- EdgeVPN solves the problem of external connections without a public IP/3rd party. However, the connection will typically be slow, albeit fast enough to establish an ssh connection, run Linux commands, monitor messages. In a long run, is it better to have a more solid VPN, preferably with a static public IP?

- There are a lot of cloud services which connect Linux boards and PCs: ShellHub, RemoteIoT, DataPlicity, PiTunnel, SocketXP, Tunnel In... This number could be sufficiently large to start using their free plans for hobby purposes, hopping on a new platform every time user/device list expands or a free plan disappears ;).

- Remmina, Chrome Remote Desktop, TeamViewer, AnyDesk, RustDesk, Screego... Remmina demands port forwarding which is very limited and unreliable. "UbuntuDesk" with a solid NAT punching, please.

- [Parsec, Rainway, Steam Remote Play](https://news.ycombinator.com/item?id=29479503) and other game streaming services might provide the most responsive VPNs.

- The role of the Wireguard VPN: [1](https://github.com/ciniml/WireGuard-ESP32-Arduino), [2](https://github.com/trombik/esp_wireguard), [3](https://github.com/esphome/feature-requests/issues/1444) in the IoT remains unclear to me. Can Wireguard make the ESP32 completely independent global network node on par to Linux boards? Is this for something special like remote OTA firmware updates?

    Some Linux Wireguard helpers to bookmark: [pivpn](https://github.com/pivpn/pivpn), [wg-easy](https://github.com/wg-easy/wg-easy), [firezone](https://github.com/firezone/firezone), youtube: [1](https://www.youtube.com/watch?v=5Aql0V-ta8A), [2](https://www.youtube.com/watch?v=_hiYI7ABnQI).

- Tailscale, Nebula, NetBird, Netmaker, headscale, innernet, [ZeroTier](https://www.youtube.com/watch?v=sA55fcuJSQQ), tinc, [Hamachi](https://news.ycombinator.com/item?id=29479503)... A long list of "[overlay](https://github.com/search?l=Go&o=desc&q=wireguard&s=stars&type=Repositories) [mesh](https://github.com/cedrickchee/awesome-wireguard) [network](https://wiki.nikiv.dev/networking/vpn/wireguard)" software built on top of Wireguard, mostly, but not always. Quite a few services with free plans.

- [NetFoundry](https://netfoundry.io/edge-and-iot-zero-trust-networking/). "The SaaS is free forever for up to 10 endpoints, so you can get started immediately with the SaaS or open source." It positions itself as a [more secure Tailscale](https://netfoundry.io/networking-alternative-compare-tailscale-netfoundry/), which is even further away from NAT punching layers. Too much to figure out what is what and run something simple [at the first glance](https://www.reddit.com/r/openziti/comments/xpe01b/need_some_guidance/).

- ngrok, frp, localtunnel.me, gotunnelme, boringproxy, rathole. So called "reverse proxy/tunneling", which is kind of a synonym to the VPN. These tools help to expose a machine behind a NAT when you already have a VPS with a static IP, just like Wireguard? Some are [TCP only](https://github.com/fatedier/frp/issues/3009), some may result in a [much faster VPN](https://github.com/fatedier/frp/issues/2911). 

- The Onion Router: [1](https://www.maths.tcd.ie/~fionn/misc/ssh_hidden_service/), [2](https://www.techjail.net/raspberry-iotlinux-devices.html), [3](https://golb.hplar.ch/2019/01/expose-server-tor.html), [4](https://community.torproject.org/onion-services/setup/), [5](https://www.reddit.com/r/Freenet/comments/9w4do9/demo_public_darknet_on_the_tor_onioncat_ipv6/), [6](https://null-byte.wonderhowto.com/how-to/host-your-own-tor-hidden-service-with-custom-onion-address-0180159/), [7](https://opensource.com/article/19/8/how-create-vanity-tor-onion-address), [8](https://shufflingbytes.com/posts/ripping-off-professional-criminals-by-fermenting-onions-phishing-darknet-users-for-bitcoins/).
 
  "It's easier to setup a Tor hidden service than it is to set up a server with a domain. You don't have to know anything about DNS or firewalls. I'm surprised that they aren't more common."

- [Yggdrasil](https://news.ycombinator.com/item?id=27580995), [CJDNS](https://news.ycombinator.com/item?id=16135341)/Hyperboria, ZeroNet, I2P, Scuttlebutt and other global p2p networks. I have little initiative to try these networks out as the libp2p network (with EdgeVPN) solves the problem, but it is worth noting that p2p networks are ideal for low MQTT traffic, they are totally free to use and do not demand a public static IP. [This 2022 report](https://cheapskatesguide.org/articles/yggdrasil.html) delves deeper into Yggdrasil and provides some interesting details, e.g. the number of public peers in the US.

- [Freifunk, FunkFeuer, NYC Mesh](https://github.com/redecentralize/alternative-internet#networking) and other local community/city/country-wide radio p2p networks. [B.A.T.M.A.N.](https://en.wikipedia.org/wiki/B.A.T.M.A.N.) [routing](https://cgomesu.com/blog/Mesh-networking-openwrt-batman/) at the OSI layer 2 (Data link) rather than 3 (Network). [This will be relevant to the world after nuclear war](https://www.youtube.com/watch?v=DrXJ9_ezSy4). The free internet built with only "line of sight" devices, mostly routers with OpenWrt. Tools to mesh WLANs and LANs, BATMAN-based and traditional, with certain [use cases](https://youtu.be/t4A0kfg2olo?t=134).

- [Meshtastic](https://www.youtube.com/watch?v=TY6m6fS8bxU) is like Freifunk, but focused on the LoRa radio communication. Its main use seems to be in remote rural areas: Crowded rock festivals and other animal tracking ;). LoRa (LoRaWAN) alternatives include [NB-IoT, Sigfox, and Wi-Fi HaLow](https://www.hackster.io/news/the-ttgo-t-beam-an-esp32-lora-board-d44b08f18628).

- [v2ray](https://www.quora.com/How-do-I-bypass-the-GFW-of-China-without-a-VPN): [1](https://www.reddit.com/r/dumbclub/comments/106aomk/how_to_install_and_setup_v2ray/), [2](https://www.reddit.com/r/dumbclub/comments/ydfpr7/why_v2ray_doesnt_work_on_games/), [3](https://www.reddit.com/r/dumbclub/comments/11q8nhn/v2ray_xray_vps/), [4](https://www.reddit.com/r/dumbclub/comments/100g8ei/best_v2ray_config_for_gaming/), and [the Great Firewall of China](https://en.wikipedia.org/wiki/Great_Firewall):

  "the developer of shadowsocksR being asked to police station,the code on github was deleted by unimagable mean. so v2ray come out in the world. Which is stronger than shadowsocks (or in another way v2ray contains shadowsocks),the establish method is same with shadowsocks.U can search 一键搭建v2ray on YouTube..."

- "v2ray" and "Shadowsocks" related software that helps to get through firewalls: [Outline VPN](https://www.youtube.com/watch?v=O9jGg6tE7nY), [udp2raw](https://github.com/wangyu-/udp2raw), [hysteria](https://github.com/apernet/hysteria), [trojan](https://github.com/trojan-gfw/trojan), [clash](https://github.com/Dreamacro/clash), [gost](https://github.com/ginuerzh/gost/blob/master/README_en.md), [naiveproxy](https://github.com/klzgrad/naiveproxy), [pi-hole](https://github.com/pi-hole/pi-hole). Outline VPN needs to be installed as a server on DigitalOcean/Hostinger, and it is free just like Wireguard, but it might have stronger hole-punching properties. The other tools mentioned here are less clear to me.

- Discussions around the VPN concept may go [on](https://news.ycombinator.com/item?id=24893615) and [on](https://news.ycombinator.com/item?id=27672715) and [on](https://github.com/anderspitman/awesome-tunneling) and [on](https://changelog.complete.org/archives/10231-recovering-our-lost-free-will-online-tools-and-techniques-that-are-available-now)... with some phishing attacks to consider: [1](https://news.drweb.com/show/?i=14451), [2](https://www.reddit.com/r/crowdstrike/comments/tjh602/query_hunt_for_reverse_proxy_tunnel_tools/), [3](https://thestack.technology/ransomware-attack-bitlocker/), [4](https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/ipfs-the-new-hotbed-of-phishing/), [5](https://shufflingbytes.com/posts/ripping-off-professional-criminals-by-fermenting-onions-phishing-darknet-users-for-bitcoins/)...

- There exist tools built to attack your own IoT networks for testing purposes: [1](https://github.com/ElectronicCats/CatSniffer), [2](https://github.com/SpacehuhnTech/esp8266_deauther), [3](https://www.youtube.com/watch?v=I0N2KpwGETI).

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

- [EdgeVPN](https://github.com/mudler/edgevpn):

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
  
  It may take several minutes for the node to join the EdgeVPN network which is the libp2p network under the hood. I do not recommend using the [Linux desktop GUI](https://github.com/mudler/edgevpn-gui) as it is totally unnecessary.
  
  If everything is fine, you should be able to connect to any Linux computer within the EdgeVPN network, e.g.
  
  ```console
  ssh username@10.1.0.8
  ...
  ```
  
  The broker becomes visible as if EdgeVPN were a LAN, so you can run mosquitto_pub/sub commands directly even without ssh-ing to the machine that runs the MQTT broker. 
  
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
  
- Despite all the amazing work by Peter Hinch, I could not make the async codes receive my MQTT messages, the device could only send them.

- After a long search and disappointment I could finally reach resilience w.r.t. the Wi-Fi loss thanks to this [code by Rui and Sara Santos][micropython-Rui-Santos].
  
## Conclusions

- DOIT DEvKit V1 ESP32-WROOM-32 is roughly an ATmega board, only with a slightly longer reach to its sensors, minus economy and reliability. The [ESP32](https://en.wikipedia.org/wiki/ESP32) is much better than [Atmega with ENC28J60](http://tuxgraphics.org/electronics/200606/article06061.shtml), but still, tiny RAM = obscure software. I would not use ESP32s for anything other than transmitting sensor values/control within a LAN, via MQTT. Bail out to the PC space ASAP.
  
- The [ESP32](https://en.wikipedia.org/wiki/ESP32) niche could be massive LANs of "Wi-Fi-enabled" sensors, where node failures are not critical, e.g. [waste bin level sensors](https://www.ecubelabs.com/bin-level-sensors-5-reasons-why-every-city-should-track-their-waste-bins-remotely/). Contrary to popular belief, these chips are very suboptimal for hobby networking, compared to, say, Raspberry Pi Zero W. I would look more into the types of [ESP32-ready sensors](https://esphome.io/#sensor-components) and think of distributing them in the LAN.

- Consider economics: DOIT DEVIT V1 ESP32-WROOM-32 vs Raspberry Pi Zero W bought on, say, anodas.lt in Vilnius, May 23rd, 2023. The former costs 12.70€, while the latter is 23.90€ plus a 32GB MicroSD card sold as low as 4.90€. A typical hobbyist will only need a dozen of such devices in a life time, and the cost of 2-4x higher priced Raspberry Pi Zero W will be negligible compared to the pain one will experience with scarce network software and tiny kilobyte RAM of ESP32. [Andreas Spiess](https://www.youtube.com/watch?v=rXc_zGRYhLo&t=389s) even suggests getting an old used laptop on ebay instead of a new Raspberry Pi.  

- A bus card reader? We used to have some early low RAM devices here in Vilnius for about 5-10 years. They would produce occasional errors and that is how I know that their memory was kilobytes, it would be displayed in the error message on the screen. This year (2023) the bus card readers got replaced with Estonian Ridango devices which, I suspect, run Linux. 

- The [ESP32](https://en.wikipedia.org/wiki/ESP32) provides small distance communication via the BLE and ESP-NOW protocols. In theory, this could be used to implement electronic bike shifting, remove low power electric control wires whenever possible. "But hold on a second, did you know that you never need to update the firmware on a mechanical derailleur?" 

- The combo of the [ESP32](https://en.wikipedia.org/wiki/ESP32) with MicroPython achieves a hassle-free ADC to measure analogue voltage values. An easy ROM address scanning (whenever one needs to pin a lot of temperature sensors on a single wire input) is also a solid achievement. This is a lot messier in the ATmega world. There is no need to deal with the fuse bits, makefiles and C shenanigans. This is only a convenience issue though. Fundamentally, MicroPython eats up precious RAM and dynamic typing is very prone to typos and all sorts of hidden bugs, which is a huge problem.

- Wi-Fi is limited to 10-40m without repeaters. [LoRa](https://en.wikipedia.org/wiki/LoRa) (via e.g. the [LILYGO TTGO T-Beam ESP32 board](https://www.youtube.com/watch?v=TY6m6fS8bxU)) may reach [1-166km](https://meshtastic.discourse.group/t/practical-range-test-results/692/47?page=2). The ESP32 seems to be suboptimal regarding its power consumption, which is critical in [mobile p2p radio networking](https://meshtastic.discourse.group/t/real-world-use-cases/175).

- [EdgeVPN](https://github.com/mudler/edgevpn/issues/25) is a remarkable FOSS VPN which could be used to ssh globally to any computer behind NAT without any 3rd party service and static IP. The connection may be slow, but it is free and works as long as the libp2p network has any connected peers. According to [Max Inden, 2022](https://archive.fosdem.org/2022/schedule/event/libp2p/attachments/audio/4917/export/events/attachments/libp2p/audio/4917/slides.pdf), the libp2p network "powers the IPFS, Ethereum 2, Filecoin and Polkadot network and there are ~100K libp2p based nodes online at any given time".

- [Wireguard](https://www.youtube.com/watch?v=5Aql0V-ta8A) is another remarkable FOSS VPN. It may produce faster than EdgeVPN connections, but it demands a public static IP, which means monthly payments, dependency on 3rd party services. Web2 philosophy.

- Useful ESP32 applications may not require the global internet connectivity, see e.g. this NAT router: [1](https://github.com/martin-ger/esp32_nat_router/tree/master), [2](https://github.com/dchristl/esp32_nat_router_extended/tree/master/src), or [the GPS Tracker](https://how2electronics.com/esp32-gps-tracker-using-l86-gps-module-oled-display/).

## References

The ESP32 Essentials:

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

"All your stupid ideals <br> 
  You've got your head in the clouds" <br> 
  &#8211; [Depeche Mode - Useless](https://www.youtube.com/watch?v=U2Kyu4XURaE) 


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
