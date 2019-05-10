from flask import Flask,jsonify
from flask import send_file
import requests
import os
import code1
import json
from datetime import datetime
import time
import simplejson
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)  # set board mode to Broadcom

GPIO.setup(2, GPIO.OUT) 
GPIO.setup(3, GPIO.OUT)

app = Flask(__name__, static_url_path='')

@app.route("/measure", methods=['GET', 'POST'])
def hello():
    body = checkstatus()
    r = requests.post("http://172.20.10.10/account/measurefrombody", data=body)
    return body

def checkstatus():
    r = requests.get("http://172.20.10.10/home/sliderstatus")
    json_response = json.loads(r.text)
    status = json_response['status']
    if status == True:
        GPIO.output(2, 0)
        time.sleep(20)
        GPIO.output(2, 0)
        measuring = measure()    
        return measuring
    else:
        checkstatus()

def measure():
    result = code1.start()
    r = requests.get('http://172.20.10.10:80/home/sliderstatus')
    json_response = json.loads(r.text)
    customer = json_response['customer']
    cust = str(customer)
    now = datetime.fromtimestamp(time.time()).strftime("%d-%m-%Y_%H.%M.%S")
    measurement_json = json.dumps({"coin_number": result[0], "timestamp": now, "coin_values": "32.74", "coin_radii": [(result[1])], "image": result[2], "user_id": cust})
    GPIO.output(3, 0)
    r = requests.get('http://172.20.10.10:80/home/sliderstatusreset')
    return measurement_json

app.run(host='0.0.0.0', port='5000')
