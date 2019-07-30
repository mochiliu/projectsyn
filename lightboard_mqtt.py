import paho.mqtt.client as paho
import sys, time#, json, struct
import numpy as np
import RPi.GPIO as GPIO
from enum import Enum
from display import LEDdisplay
from GameOfLife import GameOfLife
import threading

    

broker="192.168.1.170"
port=1883

#ret= client.publish("linknodeR4bedroom/cmnd/Power1","TOGGLE")                   #publish for linknode

topics = [("board/#",0)] #QOS 0

frame_rate = 10 #10 Hz           
           
class light_states(Enum):
    PowerOff = 0
    ConstantDisplay = 1
    CyclingSampleDisplay = 2
    PlayingGameOfLife = 3

light_state = light_states.PowerOff
current_color = np.array([255., 255., 255.]) # store color as a normalized unit vector
current_brightness = np.max(current_color)
current_color = current_color / np.max(current_color)
disp = LEDdisplay()


def real_color(color, brightness):
    r_color = brightness * color
    int_r_color = r_color.astype(int)
    return int_r_color

def set_color(color):
    global current_color, current_brightness
    color = np.array([min(max(color[0], 0.), 255.), min(max(color[1], 0.), 255.), min(max(color[2], 0.), 255.)])
    current_brightness = np.max(color)
    current_color = color / current_brightness
    display_single_color(color)
    
def set_brightness(brightness):
    global current_color
    set_color(real_color(current_color, brightness))
#    
#def status_json_payload():
#    global light_state, current_color, current_brightness
#    if light_state == light_states.PowerOff:
#        on_off_state = 'OFF'
#    else:
#        on_off_state = 'ON'
#    return {'state': on_off_state, 'brightness': current_brightness, 'rgb': current_color}

def display_single_color(color):
    global disp
    single_color_linear_array = np.tile(color, 900)
    disp.set_from_array(single_color_linear_array)

def set_power_state(powerstate):
    # set the power state of the light panel, to save energy and reduce excess noise
    global current_color, current_brightness, disp
    GPIO.setmode(GPIO.BCM)
    powersupplypin = 2
    GPIO.setup(powersupplypin,GPIO.OUT)
    if powerstate == light_states.PowerOff:
        GPIO.output(powersupplypin,0)     
    else:
        GPIO.output(powersupplypin,1)     
    pass
           
def publish_update(client):
    global light_state, current_color, current_brightness
#    client.publish('lightboard/status', json.dumps(status_json_payload()))
    if light_state == light_states.PowerOff:
        client.publish('board/status', 'OFF')
        client.publish('board/effect/status', 'Uniform')
    elif light_state == light_states.ConstantDisplay:
        client.publish('board/status', 'ON')
        client.publish('board/effect/status', 'Uniform')
    elif light_state == light_states.PlayingGameOfLife:
        client.publish('board/status', 'ON')
        client.publish('board/effect/status', 'Game of Life')
        
    client.publish('board/brightness/status', int(current_brightness))

    scaled_color = real_color(current_color, current_brightness)
    client.publish('board/rgb/status', str(scaled_color[0])+','+str(scaled_color[1])+','+str(scaled_color[2]))
    
      
    
def on_connect(client, userdata, flags, rc):
    global light_state, current_color, current_brightness

    print("Connected with result code "+str(rc))
    print("subscribing " + str(topics))

    for t in topics:
        try:
            r=client.subscribe(t)
            if r[0]==0:
                print("subscribed to " + str(t[0]))
#                topic_ack.append([t[0], r[1], 0]) #keep track
            else:
                print("error on subscribing" + str(r))
                client.loop_stop()
                sys.exit(1)
        except Exception as e:
            print(str(e))
            client.loop_stop()
            sys.exit(1)       
    
    #after connecting, reset everything to off
    #gpio off
    
    light_state = light_states.PowerOff
    set_power_state(light_state)
    publish_update(client)

    
        
def on_publish(client,userdata,result):             #create function for callback
#    print("data published: " + str(userdata))
    pass

def on_subscribe(client, userdata, mid, granted_qos):             #create function for callback
#    print("Subscribed: "+str(mid)+" "+str(granted_qos))
    pass

def on_message(client, userdata, msg):
    global light_state, current_color, current_brightness
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "board/switch":
        #lightboard on / off
        if msg.payload == b'ON':
            light_state = light_states.ConstantDisplay
            set_power_state(light_state)
            set_color(real_color(current_color, current_brightness))
        elif msg.payload == b'OFF':
            light_state = light_states.PowerOff
            set_power_state(light_state)
        publish_update(client)
            
    elif msg.topic == "board/brightness/set":
        # set the brightness
        decoded_payload = int(msg.payload.decode())
        set_brightness(decoded_payload)
        publish_update(client)

    elif msg.topic == "board/rgb/set":
        # set the color
        decoded_payload = msg.payload.decode()
        decoded_payload = decoded_payload.split(',')
        color = (int(decoded_payload[0]), int(decoded_payload[1]), int(decoded_payload[2]))
        set_color(color)
        publish_update(client)

    elif msg.topic == "board/effect/set":
        # set the effect
        decoded_payload = msg.payload.decode()
        if msg.payload == b'Uniform':
            light_state = light_states.ConstantDisplay
            set_power_state(light_state)
            set_color(real_color(current_color, current_brightness))
        elif msg.payload == b'Game of LIfe':
            # start playing game of life
            light_state = light_states.PlayingGameOfLife

            
        publish_update(client)
        
        
client= paho.Client("board")                           #create client 
client.username_pw_set('hassio', 'projectsyn')

client.on_connect = on_connect
client.on_publish = on_publish                          #assign function to callback
client.on_subscribe = on_subscribe
client.on_message = on_message



try:
    client.connect(broker,port)                                 #establish connection
except:
    print("can't connect")
    sys.exit(1)
    
client.loop_start() #start loop in background thread

running = threading.Event()
background_thread = None
last_light_state = light_state

while True:
    #main loop, waiting until esc key press
    #keep checking if we swiched light states
    if last_light_state != light_state: 
        # transitioning states
        if light_state == light_states.PlayingGameOfLife:
            print('starting game of life')
            game_of_life = GameOfLife(disp, frame_rate)
            running.set()
            background_thread = threading.Thread(target=game_of_life.start_game, args=[running])
            background_thread.daemon = True
            background_thread.start()
        elif last_light_state == light_states.PlayingGameOfLife:
            print('stopping game of life')
            running.clear()
            time.sleep(1)
            set_power_state(light_state)
            set_color(real_color(current_color, current_brightness))
        last_light_state = light_state


#client.loop_forever()
client.disconnect()
