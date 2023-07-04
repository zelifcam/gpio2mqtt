#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import random
import sys
import json
from paho.mqtt import client as mqtt_client
from time import sleep

GPIO.setmode(GPIO.BCM)
PREVIOUS = "null"
BROKER = '192.168.0.10'
USER = "mqtt-user"
PASSWORD = "mqtt-password"
PORT = 1883
DELAY = .75
CLIENT_ID = f'pi-sensor-{random.randint(0, 1000)}'

def print_to_stdout(*a):
    jjj=0
    #print(*a, file = sys.stdout)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print_to_stdout("Connected to MQTT Broker!")
        else:
            print_to_stdout("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(CLIENT_ID)
    client.username_pw_set(username="mqtt-user",password="mqtt-user")
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    return client

def publish(client):
    while True:
        sensor = 16
        time.sleep(DELAY)
        result_json={}
        while sensor >= 0:

            topic = "pisensor/gpio-" + str(sensor)
            pi_gpio = sensor
	
            GPIO.setup(pi_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            state = GPIO.input(pi_gpio)

            if state == False and PREVIOUS == "open" or state == False and PREVIOUS == "null":
                print_to_stdout(str(pi_gpio) + " open")
                msg = 0
            if state != False and PREVIOUS == "closed" or state != False and PREVIOUS == "null":
                print_to_stdout(str(pi_gpio) + " closed")
                msg = 1
            
            #print(topic,msg)
            result_json[str(pi_gpio)]=str(msg)
            result = client.publish(topic, msg)

            # result: [0, 1]

            status = result[0]
            if status != 0:
                print_to_stdout(f"Failed to send message to topic {topic}")

            GPIO.cleanup(pi_gpio)

            topic=''
            pi_gpio=''

            sensor += -1
        now_ns = time.time_ns()
        result_json["time"]=str(now_ns)
        json_status = client.publish('pisensor/data', json.dumps(result_json))
        if json_status[0] != 0:
              print_to_stdout(f"Failed to send message to topic {topic}")
        print_to_stdout('--------------------------')

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()

