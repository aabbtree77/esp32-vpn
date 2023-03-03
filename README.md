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

DOIT DEVIT V1 ESP32-WROOM-32 is an inexpensive (10-20$) MCU board with the Wi-Fi connectivity. The challenge is to access such a board from anywhere, via the internet.

There are several ways to establish global connections to an ESP32:

- Using 3rd party services: [ESP RainMaker](https://github.com/espressif/esp-rainmaker/issues/96), [Amazon API Gateway with Websockets](https://www.youtube.com/watch?v=z53MkVFOnIo), [Google IoT Core](https://news.ycombinator.com/item?id=32475298), [CloudMQTT](https://www.cloudmqtt.com/blog/cloudmqtt-cute-cat-free-plan-out-of-stock.html), [HiveMQ](https://community.hivemq.com/t/connection-fail-in-hivemq-cloud/579/4)... Vendor lock-in, phased-out plans or entire cloud services, registration layers, pricing...

- [Wireguard for ESP-IDF](https://github.com/trombik/esp_wireguard). This is a raw low level library with unclear stability and NAT punching. Its user base is too tiny to trust it.

- Connecting an ESP32 board to a local Linux machine first, e.g. via an MQTT broker, thus delegating the problem of global connectivity effectively to the PC space. 

This memo documents some details about the third way. It is the least opaque and the most reliable, but it demands an extra PC/Linux board (PC-1 shown in the figure above).

## Congratulations, You Had a Problem and Now You Have Two

With the Linux PC one can send to and receive messages from an ESP32 via an MQTT broker. How does one connect to the Linux PC outside of LAN? Surprisingly, there is no good solution to this problem in the year 2023, and here are some of the options I have been considering:

- Coding some ESP32 control panel and hosting it as a web app on, say, [Heroku](https://twitter.com/heroku/status/1562817050565054469) which has no longer any free plans. 
Emulating a 3rd party service with yet another 3rd party service... No.

- Remmina, Chrome Remote Desktop, TeamViewer, AnyDesk, RustDesk, Screego... Hell no. "UbuntuDesk" with a solid NAT punching, please.

- ShellHub, RemoteIoT, DataPlicity, PiTunnel, SocketXP, Tunnel In... Mostly Raspberry Pi related IoT clouds with very limited free plans and steep prices.

- Wireguard: Requires an [endpoint](https://wiki.archlinux.org/title/WireGuard#Endpoint_with_changing_IP) [public IP](https://github.com/pirate/wireguard-docs#NAT-to-NAT-Connections), is too low level, but it may run everywhere including [ESP-IDF](https://github.com/trombik/esp_wireguard), which is something to think about, or not.

- [wireguard-p2p](https://github.com/manuels/wireguard-p2p/issues/5): A layer on top of Wireguard with Rust and C++ compilation issues.

- Nebula, NetBird, Netmaker, Tailscale, headscale, innernet, ZeroTier, tinc, [Yggdrasil](https://news.ycombinator.com/item?id=27580995), [Hamachi](https://news.ycombinator.com/item?id=29479503)... A long list of "[overlay](https://github.com/search?l=Go&o=desc&q=wireguard&s=stars&type=Repositories) [mesh](https://github.com/cedrickchee/awesome-wireguard) [network](https://wiki.nikiv.dev/networking/vpn/wireguard)" software built on top of Wireguard, mostly, but not always. Quite a few services with free plans, but how long will they stay that way? Outside the service mode there is always the need for a static IP here.

- [NetFoundry](https://netfoundry.io/edge-and-iot-zero-trust-networking/) cloud. "The SaaS is free forever for up to 10 endpoints, so you can get started immediately with the SaaS or open source." It positions itself as a [more secure Tailscale](https://netfoundry.io/networking-alternative-compare-tailscale-netfoundry/), which is even further away from a raw connectivity problem. Too much to figure out what is what and run something simple [at the first glance](https://www.reddit.com/r/openziti/comments/xpe01b/need_some_guidance/).

- ngrok, frp, localtunnel.me, gotunnelme, boringproxy, rathole. So called "reverse proxy tools" to expose a machine behind a NAT when you already have a VPS with a static IP. Some are [TCP only](https://github.com/fatedier/frp/issues/3009), some may result in a [much faster VPN](https://github.com/fatedier/frp/issues/2911). ngrok's free plan is fairly limited to testing as the public urls disappear/change when one restarts the self-hosting machine. 
   
- The show must go [on](https://news.ycombinator.com/item?id=24893615) and [on](https://news.ycombinator.com/item?id=27672715) and [on](https://github.com/anderspitman/awesome-tunneling) and [on](https://changelog.complete.org/archives/10231-recovering-our-lost-free-will-online-tools-and-techniques-that-are-available-now)... with some phishing attacks to consider: [1](https://news.drweb.com/show/?i=14451), [2](https://www.reddit.com/r/crowdstrike/comments/tjh602/query_hunt_for_reverse_proxy_tunnel_tools/), [3](https://thestack.technology/ransomware-attack-bitlocker/), [4](https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/ipfs-the-new-hotbed-of-phishing/)...

- [Sharing a file](https://github.com/aabbtree77/sendrecv) via github.com does the job if you only need to send and receive an occasional message. It is very slow and limited.

- The Onion Router: [1](https://www.maths.tcd.ie/~fionn/misc/ssh_hidden_service/), [2](https://www.techjail.net/raspberry-iotlinux-devices.html), [3](https://golb.hplar.ch/2019/01/expose-server-tor.html), [4](https://community.torproject.org/onion-services/setup/), [5](https://www.reddit.com/r/Freenet/comments/9w4do9/demo_public_darknet_on_the_tor_onioncat_ipv6/), [6](https://null-byte.wonderhowto.com/how-to/host-your-own-tor-hidden-service-with-custom-onion-address-0180159/), [7](https://opensource.com/article/19/8/how-create-vanity-tor-onion-address).
 
  "It's easier to setup a Tor hidden service than it is to set up a server with a domain. You don't have to know anything about DNS or firewalls. I'm surprised that they aren't more common."

So what is the decision finally? I have tested [Hyprspace](https://github.com/hyprspace/hyprspace/issues/94) and [EdgeVPN](https://github.com/mudler/edgevpn/issues/25). Both of them are OSS (written in Go!) based on the MIT-licensed stack called [go-libp2p](https://github.com/libp2p/go-libp2p) which stems from [kubo](https://github.com/ipfs/kubo) (go-ipfs). This stack has a decent focus on the [NAT](https://discuss.libp2p.io/t/how-nat-traversal-and-hole-punching-work-in-ipfs/1422) [traversal](https://github.com/ipfs/camp/blob/master/DEEP_DIVES/40-better-nat-traversal-so-that-relay-servers-are-a-last-not-first-resort.md) without an external service or static IP junk. It is very useful for the ability to ssh into a remote computer.

Do these tools always work though, are they equally good? EdgeVPN may have an [edge](https://github.com/mudler/edgevpn/issues/25).

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

- After a long search and disappointment I could finally have a resilience w.r.t. the Wi-Fi loss thanks to this [code by Rui and Sara Santos][micropython-Rui-Santos].
  
## Reservations about Networking with ESP32
   
- ESP32 with MicroPython is a somewhat resilient Wi-Fi client to be controlled from a PC within a LAN via MQTT. It is not a self-sufficient global network node.

- ESP32, global connectivity, no 3rd party/extra broker: Pick any two.

- **Embedded Linux is the way**.

## Major Discovery

[EdgeVPN](https://github.com/mudler/edgevpn/issues/25) is a remarkable tool to ssh globally to any computer behind NAT.

## References

ESP32 Essentials:

- [MicroPython firmware]
- [micropython-Rui-Santos]
- [umqtt.simple]
- [esp32-30pin]

Optional (Places not to go to, only to be aware of):

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
