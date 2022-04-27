import paho.mqtt.client as mqtt
from datetime import datetime
import numpy as np
import cv2
import base64
MQTT_SERVER = "test.mosquitto.org"

CO_PATH = "CO"
ENVIRONMENT_PATH = "ENVIRONMENT"
RADIATION_PATH = "RADIATION"
ELECTROMAGNETIC_PATH = "ELECTROMAGNETIC"
DEPTH_PATH = "DEPTH"
RGB_PATH = "RGB"
LATENCY_PATH = "LATENCY"

# The callback for when the client receives a connect response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe(CO_PATH)
    client.subscribe(ENVIRONMENT_PATH)
    client.subscribe(RADIATION_PATH)
    client.subscribe(ELECTROMAGNETIC_PATH)
    client.subscribe(DEPTH_PATH)
    client.subscribe(RGB_PATH)
    client.subscribe(LATENCY_PATH)
    


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = str(msg.payload)[2:-1]
    
    if msg.topic==LATENCY_PATH:
        reciever_time = datetime.now()
        print(data)
        print(reciever_time)
        
        
        
    elif msg.topic == RGB_PATH:
        jpg_original = base64.b64decode(data)
        jpg_as_np = np.frombuffer(jpg_original,dtype = np.uint8)

        image_buffer = cv2.imdecode(jpg_as_np,flags=0)
        cv2.imshow("image",image_buffer)

        print(image_buffer)

    elif msg.topic == DEPTH_PATH:
        jpg_original = base64.b64decode(data)
        jpg_as_np = np.frombuffer(jpg_original,dtype = np.uint8)

        image_buffer = cv2.imdecode(jpg_as_np,flags=1)
        cv2.imshow("image",image_buffer)

        print(image_buffer)        

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()