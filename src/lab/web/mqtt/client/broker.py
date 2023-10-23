import paho.mqtt as mqtt

def on_connect(client, userdata, flags, rc):
    print(f'Client connected with result code {str(rc)}')



class MQTTBroker:
    def __init__(self, on_connect, on_subscribe, on_message):
        self.broker =  mqtt.
