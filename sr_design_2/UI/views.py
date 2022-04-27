from django.shortcuts import render
#from UI.camera import VideoCamera
from django.http.response import StreamingHttpResponse
# Create your views here.



#Plotting
from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Scatter
import json



###
import threading
import keyboard
########################################
import paho.mqtt.client as mqtt
from datetime import datetime
import numpy as np
import cv2
import base64
import time
########################################
MQTT_SERVER = "test.mosquitto.org"

CO_PATH = "CO"
ENVIRONMENT_PATH = "ENVIRONMENT"
RADIATION_PATH = "RADIATION"
ELECTROMAGNETIC_PATH = "ELECTROMAGNETIC"
DEPTH_PATH = "DEPTH"
RGB_PATH = "RGB"
DRIVETRAIN_PATH = "DRIVETRAIN"
TOGGLE_DEPTH_PATH = "TOGGLE_DEPTH"
depth_frame = None
rgb_frame = None

toggle_co = 0
toggle_environmental = 0
toggle_radiation = 0
toggle_electromagnetic = 0
toggle_depth = 0
toggle_rgb = 0

radiation_x_data=[]
radiation_y_data=[]

co_x_data = []
co_y_data = []

environmental_x_data = []
temperature_y_data = []
rel_humidity_y_data = []
pressure_y_data = []
altitude_y_data = []

em_x_data = []
em_y_data = []

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
    
def on_publish(client,user_data,mid):
    print("Message "+str(mid)+" published.")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = str(msg.payload)[2:-1]
    global depth_frame
    global rgb_frame
    global radiation_x_data
    global radiation_y_data
    global co_x_data
    global co_y_data
    global environmental_x_data
    global temperature_y_data
    global rel_humidity_y_data
    global pressure_y_data
    global altitude_y_data
    global em_x_data
    global em_y_data
        
        
    if msg.topic == RGB_PATH:

        rgb_frame = base64.b64decode(data)
        img_arr = np.frombuffer(rgb_frame, dtype=np.uint8)
        img = cv2.imdecode(img_arr, flags=cv2.IMREAD_COLOR)
        save_images(img,-1)


    elif msg.topic == DEPTH_PATH:

        depth_frame = base64.b64decode(data)
        #Save Depth Frame as Image
        depth_frame = save_bytes_as_image(depth_frame)
    
    elif msg.topic == RADIATION_PATH:
        data = json.loads(data)
        radiation_x_data.append(data[0])
        radiation_y_data.append(data[1])
        #print(data)
    elif msg.topic==CO_PATH:
        #print(data)
        data = json.loads(data)
        #print(data)
        co_x_data.append(data[0])
        co_y_data.append(data[1])
    elif msg.topic == ENVIRONMENT_PATH:
        #{'seconds': 9, 'temp': 22.184375, 'rel_humidity': 58.30154285447286, 'pressure': 994.4302796413139, 'altitude': 155.1189463091737}
        #print("1",data)
        data=eval(data)
        #print("2",data)

        environmental_x_data.append(data['seconds'])
        temperature_y_data.append(data['temp'])
        rel_humidity_y_data.append(data['rel_humidity'])
        pressure_y_data.append(data['pressure'])
        altitude_y_data.append(data['altitude'])
        
        #print(data)
    
    elif msg.topic == ELECTROMAGNETIC_PATH:
        data = json.loads(data)
        
        em_x_data.append(data[0])
        em_y_data.append(data[1])
        
        #print(data)
        
def publish_data(data_code,data):
    global client
    client.publish(data_code,data)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
def loop_forever():
    global client

    client.connect(MQTT_SERVER, 1883, 60)
    
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

def save_bytes_as_image(img_bytes):
    img_arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_arr, flags=cv2.IMREAD_COLOR)
    detected_image = detect_image(img)
    #convert detected image to bytes
    retval,buffer = cv2.imencode('.jpg',detected_image)
    test = base64.b64encode(buffer)
    test2 = base64.b64decode(test)
    return test2
    #save_images(detected_image)

def detect_image(img):    
    global person_cascade
    objects = person_cascade.detectMultiScale(img,1.4,14)
    color=(255,0,255)
    if len(objects)>0:
        save_images(img,1)
    else:
        save_images(img,0)
    for (x,y,w,h) in objects:


        cv2.rectangle(img,(x,y),(x+w,y+h),color,3)
        cv2.putText(img,"Person",(x,y-5),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,color,2)
        object_image = img[y:y+h,x:x+w]
        print("Object Found")
    return img


count = 0
def save_images(image,posNeg):
    global count
    print("saved image")
    if posNeg==0:
        output_name = "./neg_output/output" + str(count) + ".jpg"

    elif posNeg==-1:
        output_name = "./images/output" + str(count) + ".jpg"
    else:
        output_name = "./pos_output/output" + str(count) + ".jpg"
    
    cv2.imwrite(output_name,image)
    count += 1
#Person Detection#
person_cascade_path="./person_cascade.xml"
person_cascade=cv2.CascadeClassifier(person_cascade_path)

t1 = threading.Thread(target=loop_forever) 
    # start thread 1 
t1.start()

#Resources:
#   Single page django app:
#       https://www.pythonstacks.com/blog/post/create-single-page-application/#:~:text=A%20single%20page%20application%20%28SPA%29%20is%20a%20web,implementing%20a%20very%20simple%20single-page%20application%20using%20Django.
#
#   Video streaming in django:
#       https://www.codershubb.com/live-video-streaming-app-in-django/
def index(request):
    global radiation_x_data
    global radiation_y_data
    global co_x_data
    global co_y_data
    global environmental_x_data
    global temperature_y_data
    global rel_humidity_y_data
    global pressure_y_data
    global altitude_y_data
    global em_x_data
    global em_y_data
    
    global toggle_rgb
    global toggle_depth
    global toggle_co
    global toggle_environmental
    global toggle_radiation
    global toggle_electromagnetic
    TOGGLE_DEPTH_PATH = "TOGGLE_DEPTH"
    TOGGLE_RGB_PATH = "TOGGLE_RGB"
    TOGGLE_CO_PATH = "TOGGLE_CO"
    TOGGLE_ENVIRONMENTAL_PATH = "TOGGLE_ENVIRONMENTAL"
    TOGGLE_RADIATION_PATH = "TOGGLE_RADIATION"
    TOGGLE_ELECTROMAGNETIC_PATH = "TOGGLE_ELECTROMAGNETIC"
    DRIVETRAIN_PATH = "DRIVETRAIN"
    if(request.method == "POST"):
        #Movement
        if request.POST.get("left"):
            print("moving left")
            publish_data(DRIVETRAIN_PATH,"a")
        elif request.POST.get("right"):
            print("moving right")
            publish_data(DRIVETRAIN_PATH,"d")
        elif request.POST.get("forward"):
            print("moving forward")
            publish_data(DRIVETRAIN_PATH,"w")
        elif request.POST.get("backwards"):
            print("moving backward")
            publish_data(DRIVETRAIN_PATH,"s")
        elif request.POST.get("stop_movement"):
            print("stopping movement")
            publish_data(DRIVETRAIN_PATH,"q")
        #Toggle Sensors
        elif request.POST.get("toggle_depth"):
            print("depth toggled")
            if toggle_depth:
                toggle_depth = 0
            else:
                toggle_depth = 1
            publish_data(TOGGLE_DEPTH_PATH,toggle_depth)
        elif request.POST.get("toggle_rgb"):
            print("rgb toggled")
            if toggle_rgb:
                toggle_rgb = 0
            else:
                toggle_rgb = 1
            publish_data(TOGGLE_RGB_PATH,toggle_rgb)
        elif request.POST.get("toggle_co"):
            print("co toggled")
            if toggle_co:
                toggle_co = 0
                co_x_data = []
                co_y_data = []
            else:
                toggle_co = 1
            publish_data(TOGGLE_CO_PATH,toggle_co)
        elif request.POST.get("toggle_environmental"):
            print("environmental toggled")
            if toggle_environmental:
                toggle_environmental=0
                environmental_x_data = []
                temperature_y_data = []
                rel_humidity_y_data = []
                pressure_y_data = []
                altitude_y_data = []
            else:
                toggle_environmental=1
            publish_data(TOGGLE_ENVIRONMENTAL_PATH,toggle_environmental)
        elif request.POST.get("toggle_radiation"):
            print("radiation toggled")
            if toggle_radiation:
                toggle_radiation=0
                radiation_x_data = []
                radiation_y_data = []
            else:
                toggle_radiation=1
            publish_data(TOGGLE_RADIATION_PATH,toggle_radiation)
        elif request.POST.get("toggle_electromagnetic"):
            print("electromagnetic toggled")
            if toggle_electromagnetic:
                toggle_electromagnetic=0
                em_x_data = []
                em_y_data = []
            else:
                toggle_electromagnetic=1
            publish_data(TOGGLE_ELECTROMAGNETIC_PATH,toggle_electromagnetic)
            
        

    radiation_plot_div = plot([Scatter(x=radiation_x_data, y=radiation_y_data,
                            mode='lines', name='test',
                            opacity=0.8, marker_color='green')],
                   output_type='div',include_plotlyjs=False)
    co_plot_div = plot([Scatter(x=co_x_data, y=co_y_data,
                            mode='lines', name='test',
                            opacity=0.8, marker_color='green')],
                   output_type='div',include_plotlyjs=False)
    
    temperature_plot_div = plot([Scatter(x=environmental_x_data, y=temperature_y_data,
                            mode='lines', name='test',
                            opacity=0.8, marker_color='green')],
                   output_type='div',include_plotlyjs=False)
    rel_humidity_plot_div = plot([Scatter(x=environmental_x_data, y=rel_humidity_y_data,
                            mode='lines', name='test',
                            opacity=0.8, marker_color='green')],
                   output_type='div',include_plotlyjs=False)
    pressure_plot_div = plot([Scatter(x=environmental_x_data, y=pressure_y_data,
                            mode='lines', name='test',
                            opacity=0.8, marker_color='green')],
                   output_type='div',include_plotlyjs=False)
    altitude_plot_div = plot([Scatter(x=environmental_x_data, y=altitude_y_data,
                            mode='lines', name='test',
                            opacity=0.8, marker_color='green')],
                   output_type='div',include_plotlyjs=False)
    
    em_plot_div = plot([Scatter(x=em_x_data, y=em_y_data,
                            mode='lines', name='test',
                            opacity=0.8, marker_color='green')],
                   output_type='div',include_plotlyjs=False)    
    


    return render(request,"UI/ui.html", context={'rel_humidity_plot_div':rel_humidity_plot_div,
                                                 'temperature_plot_div':temperature_plot_div,
                                                 'pressure_plot_div':pressure_plot_div,
                                                 'altitude_plot_div':altitude_plot_div,
                                                 'toggle_environmental':toggle_environmental,
                                                 'toggle_electromagnetic':toggle_electromagnetic,
                                                 'em_plot_div':em_plot_div,
                                                 'toggle_depth':toggle_depth,
                                                 'toggle_rgb':toggle_rgb,
                                                 'toggle_radiation':toggle_radiation,
                                                 'radiation_plot_div': radiation_plot_div,
                                                 'toggle_co':toggle_co,
                                                 'co_plot_div':co_plot_div})




def Toggle_Depth():
    global toggle_depth
    if toggle_depth:
        toggle_depth = 0
    else:
        toggle_depth = 1
    publish_data(TOGGLE_DEPTH_PATH,toggle_depth)

def gen_depth():
    global depth_frame
    global toggle_depth
    while True:

        if toggle_depth != 0 and depth_frame != None:
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + depth_frame + b'\r\n\r\n')

def gen_rgb():
    global rgb_frame
    global toggle_rgb
    while True:

        if toggle_rgb != 0 and rgb_frame != None:
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + rgb_frame + b'\r\n\r\n')

def depth_stream(request):
    return StreamingHttpResponse(gen_depth(),
                    content_type='multipart/x-mixed-replace; boundary=frame')
def rgb_stream(request):
    return StreamingHttpResponse(gen_rgb(),
                    content_type='multipart/x-mixed-replace; boundary=frame')