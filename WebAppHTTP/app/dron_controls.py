import json
from dronLink.Dron import Dron
import random
import paho.mqtt.client as mqtt

def conectar_broker ():
    global client
    print('empezamos')
    telemetry_info = None
    # preparo la conexión al broker con el que me comunicaré con el demoDash
    clientName = "mobileFlask" + str(random.randint(1000, 9000))
    client = mqtt.Client(clientName, transport="websockets")

    broker_address = "dronseetac.upc.edu"
    # broker_address = 'broker.hivemq.com'
    broker_port = 8000

    client.username_pw_set(
        'dronsEETAC', 'mimara1456.'
    )

    client.on_message = on_message
    client.on_connect = on_connect
    print('me voy a conectar al broker')
    client.connect(broker_address, broker_port)
    print('Conectado a dronseetac.upc.edu:8000')

    # me subscribo a cualquier mensaje  que venga del demoDash
    client.subscribe('demoDash/mobileFlask/#')
    client.loop_start()
    print('Esperando publicaciones del demoDash')


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK Returned code=", rc)
    else:
        print("Bad connection Returned code=", rc)

# aqui recibimos las publicaciones que hace el demoDash
def on_message(client, userdata, message):
        global telemetry_info
        # el formato del topic siempre será:
        # demoDash/mobileFlask/comando
        parts = message.topic.split ('/')
        command = parts[2]
        # en realidad del demoDash solo espero que me envíe los datos de telemetría guardarlos
        # y tenerlos disponibles cuando los pida el navegador
        if command == 'telemetryInfo':
            telemetry_info = json.loads(message.payload)



def conectar_dron():
    print ('vamos a conectar')
    client.publish('mobileFlask/demoDash/connect')
    return {"estado": "success"}


def despegar_dron(metros):
    client.publish('mobileFlask/demoDash/arm_takeOff', metros)
    return {"estado": "success"}

def aterrizar_dron():
    client.publish('mobileFlask/demoDash/Land')
    return {'estado': 'success', 'message': 'Dron aterrizando'}
    
def mover_dron(direccion):
    client.publish('mobileFlask/demoDash/go', direccion)
    return {'estado': 'success', 'message': 'Dron moviendose al '+direccion}

# cuando me pidan los datos de telemetría entrego los valores que tengo para esos datos
def obtener_datos_telemetria():
    global telemetry_info
    if telemetry_info:
        datos_telemetria = {
                    "lat": telemetry_info['lat'],
                    "lon": telemetry_info['lon'],
                    "alt": telemetry_info['alt'],
                    "velocidad": telemetry_info['groundSpeed'],
                    "direccion": telemetry_info['heading'],
                    "estado": telemetry_info['state']
        }
        return {"estado": "success", "data": datos_telemetria}
    else:
        return {"estado": "fail", "message": 'aun no hay datos de telemetria'}


