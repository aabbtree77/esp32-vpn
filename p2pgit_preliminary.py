import subprocess

#subprocess.check_output(cmd)

cmd = "git pull"
subprocess.call(cmd, shell=True)

cmd = "mosquitto_sub -C 1 -h 192.168.1.10 -t \"testincr\" > temp.txt"
subprocess.call(cmd, shell=True)

cmd = "mv temp.txt newtest.txt"
subprocess.call(cmd, shell=True)

with open('newest.txt', 'w') as f:
    MQTT_result = f.read()

print("MQTT result:{0}".format(MQTT_result))


