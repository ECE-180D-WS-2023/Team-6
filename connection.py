import paho.mqtt.client as mqtt
import numpy as np
from datetime import datetime

class connection():
  def __init__(self, on_message, id) -> None:
    def on_connect(client, userdata, flags, rc):
      client.subscribe("ece180d/A412", qos=1)
    # def on_message(msg):
    #   print('rcv: ',msg)

    self.id = id
    self.client = mqtt.Client()
    self.client.on_connect = on_connect
    # self.client.on_disconnect = on_disconnect
    self.client.on_message = on_message
    self.client.connect_async('mqtt.eclipseprojects.io')
    self.client.loop_start()
    #print('Publishing...')
    #client.publish("ece180d/test/A412", 'P2,50,50', qos=1)
    #client.loop_stop()
    #client.disconnect()   


      # print("Connection returned result: " + str(rc))
    # def on_disconnect(client, userdata, rc):
    #   if rc != 0:
    #     print('Unexpected Disconnect')
    #   else:
    #     print('Expected Disconnect')
  
  def publish(self, msg: str):
    msg = str(self.id) + ',' + msg
    print('sending msg: ', msg)
    self.client.publish('ece180d/A412', msg, qos=1)
