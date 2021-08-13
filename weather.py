#import library
import requests
from bs4 import BeautifulSoup
import time
import json
import random
import paho.mqtt.client as mqtt

#readings from sensors(currenty using random values)
def read_data():
    air = random.randint(55,60)
    light = random.randint(100,180)
    return air,light

#thingsboard credentials
broker_name = 'demo.thingsboard.io'
access_token = 'jkujxAO3D7azYmJhxN0N'
topic1='v1/devices/me/telemetry'
topic2='v1/devices/me/attributes'


#sending request to google for weather report
city=input("Enter City: ")
url = "https://www.google.com/search?q="+"weather"+city
page = requests.get(url)
soup = BeautifulSoup(page.content,'html.parser')

#method to request temperature,Time,sky,wind,humidity
def request_data():
    #temperature_data
    temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
    temp=temp[0:2]
    
    #Time & sky data
    data1 = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
    data = data1.split('\n')
    Time = data[0]
    sky = data[1]

    #Wind & Humidity data
    wind_hum = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
    wind = wind_hum[1].text
    hum=wind_hum[8].text
    pos1 = hum.find('Humidity')
    pos = wind.find('Wind')
    wind = wind[pos:]
    humidity = hum[pos1+8:pos1+10]
    return temp,Time,sky,wind,humidity

#dictionary to store all the data
data = {'temperature' :0,'humidity':0,'air_quality':0,'light_intensity':0,'time':"",'wind':"",'sky':""}
#connecting to thingsboard platform
next_reading = time.time()
client = mqtt.Client()
client.username_pw_set(access_token)
client.connect(broker_name,1883,1)
#loop starts
client.loop_start()

try:
    while True:
        #calling methods
        air,light = read_data()
        temperature,Time,sky,wind,humidity=request_data()
        #printing data
        print("Time: ", Time)
        print("temperature:",temperature, chr(176) + "C")
        print("Humidity:", humidity,"%")
        print("Air Quality:", air,"%")
        print("Light Intensity:",   light,"lux")
        print("Sky:",sky)
        #storing data in dictionary
        data['temperature'] = temperature
        data['humidity'] = humidity
        data['air_quality'] = air
        data['light_intensity'] = light
        data['sky'] = sky
        data['wind'] = wind
        data['time'] = Time

        #sending to thingsboard
        client.publish(topic1,json.dumps(data),1)
        client.publish(topic2,json.dumps(data),1)
        #setting sleepTime and readingTime
        next_reading += 5
        sleep_time = next_reading-time.time()
        if sleep_time >0:
            time.sleep(sleep_time)

except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()


