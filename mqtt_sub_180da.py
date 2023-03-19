import paho.mqtt.client as mqtt

topic = "team6"
HOST = 'localhost'
PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected: " + str(rc))
    client.subscribe(topic)

def on_message(client, userdata, msg):
    cmd = msg.payload.decode()
    print(cmd)

client = mqtt.Client()
client.connect(host, port, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
