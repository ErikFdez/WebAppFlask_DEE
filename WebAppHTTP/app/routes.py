from flask import Blueprint, render_template, jsonify, request, Response

from .dron_controls import conectar_dron, despegar_dron, aterrizar_dron, mover_dron, obtener_datos_telemetria, conectar_broker

main = Blueprint('main', __name__)

# Este código se ejecuta en el servidor, que debe atender las peticiones http que haga el navegador
# Aqui se especifica lo que hay que hacer en cada petición
# para ello llamaremos a las funciones que envían las ordenes al dron,
# que están en dron_controls.py y devolvemos al navegador el resultado

# Cuando el navegador se conecte le enviamos el fichero html
@main.route('/')
def index():
    return render_template('control.html')


@main.route('/conexion_dron', methods=['POST'])
def conexion_dron():
    print ('recibo conexion 1')
    conectar_broker()
    resultado = conectar_dron()
    return jsonify(resultado), 200 if resultado["estado"] == "success" else 500


@main.route('/despegar', methods=['POST'])
def despegar():
    # la altura a alcanzar en el despegue viene como datos en la petición POST
    data = request.get_json()
    metros = data.get('metros')
    if not metros:
        return jsonify({"estado": "error"}), 400
    resultado = despegar_dron(metros)
    return jsonify(resultado), 200 if resultado["estado"] == "success" else 400

@main.route('/aterrizar', methods=['POST'])
def aterrizar():
    resultado = aterrizar_dron()
    return jsonify(resultado), 200 if resultado["estado"] == "success" else 400


@main.route('/mover', methods=['POST'])
def start_movement():
    # la dirección en la que hay que moverse viene en los datos del POST
    data = request.get_json()
    direction = data.get('direction')
    if not direction:
        return jsonify({'estado': 'error', 'message': 'Dirección no especificada'}), 400
    resultado = mover_dron(direction)
    return jsonify(resultado), 200 if resultado["estado"] == "success" else 400


@main.route('/telemetria', methods=['GET'])
def obtener_telemetria():
    resultado = obtener_datos_telemetria()
    return jsonify(resultado), 200 if resultado["estado"] == "success" else 500

