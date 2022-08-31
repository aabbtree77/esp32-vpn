
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

DOIT DEVIT V1 ESP32-WROOM-32 is an inexpensive (sub 10-20$) MCU board with an ambition to perform Linux-free networking. I will share here a reliable setup without any 3rd party services. It is not hassle-free, but the chosen network stack is ubiquitous and solid/well tested.

A global picture shown above is still a "Web2" way as one needs an additional Linux machine to run along with ESP32. The machine consumes electricity and needs to be configured.
We do not really need this link, and neither MQTT is that important. In the ideal "Web3" world we would have an ESP32 acting as an IPFS node which could share a file with its IPNS link. The latter effectively being its "message board", punching through NATs in the P2P way. This could already be a reality with the embedded Linux SBCs, but with ESP32 we still need that additional link.

## Congratulations, You Had a Problem and Now You Have Two

The most challenging part is connecting to a LAN/device via the internet from anywhere. One can find a bewildering number of SaaS/3rd party services for the deliberation, but real life shows it is too dangerous/pricey to give up freedom for convenience. Let's discuss this a bit: 

- [ESP RainMaker](https://github.com/espressif/esp-rainmaker/issues/96), [Google IoT Core](https://news.ycombinator.com/item?id=32475298), [Heroku](https://twitter.com/heroku/status/1562817050565054469)... No.

- [CloudMQTT](https://www.cloudmqtt.com/blog/cloudmqtt-cute-cat-free-plan-out-of-stock.html), [HiveMQ](https://community.hivemq.com/t/connection-fail-in-hivemq-cloud/579/4)...

- Remmina, Chrome Remote Desktop, TeamViewer, AnyDesk, RustDesk... Where is "UbuntuDesk"?!

- ShellHub, RemoteIoT, DataPlicity, PiTunnel, SocketXP, Tunnel In... Mostly Raspberry Pi related IoT clouds with very limited free plans and steep prices.

- Wireguard: Requires an [endpoint](https://wiki.archlinux.org/title/WireGuard#Endpoint_with_changing_IP) [public IP](https://github.com/pirate/wireguard-docs#NAT-to-NAT-Connections), is too low level, but it may run everywhere including [ESP-IDF](https://github.com/trombik/esp_wireguard), which is something to think about.

- [wireguard-p2p](https://github.com/manuels/wireguard-p2p/issues/5): A layer on top of Wireguard with Rust and C++ compilation issues.

- Nebula, NetBird, Netmaker, Tailscale, headscale, innernet, ZeroTier, tinc, Hamachi... A long list of "[overlay](https://github.com/search?l=Go&o=desc&q=wireguard&s=stars&type=Repositories) [mesh](https://github.com/cedrickchee/awesome-wireguard) [network](https://wiki.nikiv.dev/networking/vpn/wireguard)" software built on top of Wireguard, mostly. Quite a few services with shaky free plans to punch through NAT, server-oriented "Web2" stuff.

- ngrok, frp, localtunnel.me, gotunnelme, boringproxy, rathole. Most of them are good "reverse proxy tools" to expose a machine behind a NAT when you already have a VPS with a static IP. Some are [TCP only](https://github.com/fatedier/frp/issues/3009), some may result in a [much faster VPN](https://github.com/fatedier/frp/issues/2911). ngrok's free plan is fairly limited to testing as the plan allows only a temporal public url which becomes invalid as soon as one restarts the ngrok process. ngrok, frp and many other such tunneling/VPN tools have been used in phishing attacks, see e.g. [1](https://news.drweb.com/show/?i=14451), [2](https://www.reddit.com/r/crowdstrike/comments/tjh602/query_hunt_for_reverse_proxy_tunnel_tools/), [3](https://thestack.technology/ransomware-attack-bitlocker/)...
   
- The show must go [on](https://news.ycombinator.com/item?id=24893615) and [on](https://news.ycombinator.com/item?id=27672715) and [on](https://github.com/anderspitman/awesome-tunneling)...

- Could [Tor (The Onion Router)](https://www.techjail.net/raspberry-iotlinux-devices.html) be the answer to the way out of this mess?! Generate a hidden onion service link with "echalot" and then access your computer with "torify ssh"?

- IPFS: [1](https://docs.ipfs.tech/how-to/websites-on-ipfs/multipage-website/#publish-to-ipns), [2](https://www.atnnn.com/p/ipfs-hosting/), [3](https://push32.com/post/blogging-on-ipfs/), [4](https://pawelurbanek.com/ipfs-ethereum-blog). Its subsystem called [IPNS](https://hackernoon.com/understanding-ipfs-in-depth-3-6-what-is-interplanetary-naming-system-ipns-9aca71e4c13b) is [too slow](https://github.com/ipfs/kubo/issues/3860) and [confusing](https://discuss.ipfs.tech/t/confusion-about-ipns/1414), [if it works at all](https://macwright.com/2019/06/08/ipfs-again.html). There is also Dat: [1](https://macwright.com/2017/08/09/decentralize-ipfs.html), [2](https://hannuhartikainen.fi/blog/dat-site/)...

At some point one becomes so desperate that [sharing a file](https://github.com/aabbtree77/sendrecv) via github.com becomes viable. At least this works for testing purposes as long as github.com is available. This is a very slow and limited way to communicate globally, but it does the job.

Great ideas come in pairs, and one gets lucky to locate [Hyprspace](https://github.com/hyprspace/hyprspace/issues/94) and [EdgeVPN](https://github.com/mudler/edgevpn/issues/25). They focus on the ability to tap into a remote PC under NAT layers without an external server/service. They rely on the MIT-licensed stack called [go-libp2p](https://github.com/libp2p/go-libp2p). The way this magic works is that the connection gets established through the [bootstrap peers](https://news.ycombinator.com/item?id=27461354) of the global IPFS network which is, in a way, a torrent network that treats VPN computers as its new nodes. 

Do they always work though, are they equally good? EdgeVPN may have an [edge](https://github.com/mudler/edgevpn/issues/25).

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
  
- Despite all the amazing work by Peter Hinch, I could not make the async codes receive my MQTT messages, the device could only send them.

- After a long search and disappointment I could finally have a resilience w.r.t. the Wi-Fi loss thanks to this [code by Rui and Sara Santos][micropython-Rui-Santos].
  
## Reservations about Networking with ESP32
   
- ESP32 with MicroPython is a solid Wi-Fi client to be controlled from a PC within a LAN via MQTT. Despite many existing attempts, it is not a self-sufficient minicomputer or network node.

- One could opt for the [Espressif](https://github.com/espressif/esp-idf/issues) [Rainmaker](https://github.com/espressif/esp-rainmaker/issues) cloud, which makes ESP32 globally accessible to any Android device, but this is a 3rd party service, a huge opaque dependency that runs on AWS inside of it.  

- Ideally, some day ESP32 would become a global IPFS/IPNS "Web3" node with a "hole punching" capacity. It is not clear if the amount of RAM available in ESP32 chips can make this goal/challenge viable. As an example, [kubo](https://github.com/ipfs/kubo), the implementation of IPFS in Go, takes more than 60MB as a Linux package, and it is recommended "running it on a machine with at least 2 GB of RAM."

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
