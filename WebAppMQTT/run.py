# IMPORTANTE: Interprete Pyhton 3.9 e instalar Flask, Flask-SocketIO, mediapipe
import base64
from app import create_app
from flask_socketio import SocketIO
import cv2
import numpy as np
import mediapipe as mp
import traceback

# Inicializa MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('video_frame')
def handle_video_frame(data):
    # aqui recibimmos los frames que nos envía la estación de tierra por el websocket
    # enviamos el frame al navegador
    print ("Recibo frame")
    socketio.emit('stream_frame', data)

@socketio.on("frame_from_camera")
def handle_video(data):
    processed_frame = process_frame_hands (data)
    # Enviar frame  al navegador y a la estación de tierra
    socketio.emit("processed_frame", f"data:image/jpeg;base64,{processed_frame}")

# Procesa el video que se recibe de la cámara del móvil
def process_frame_hands(data):
    try:
        img_data = base64.b64decode(data.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Convertir a RGB para MediaPipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = frame.shape

        # Mostrar la chuleta de texto con los gestos
        debug_text = "Gestos: Pulgar arriba=Sur, Pulgar abajo=Norte,"
        cv2.putText(frame, debug_text, (10, height - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        debug_text2 = "Pulgar izq=Oeste, Pulgar der=Este, 5 dedos=Stop,"
        cv2.putText(frame, debug_text2, (10, height - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 1)
        debug_text3 = "OK=Despegar, Pulgar+Indice=Aterrizar"
        cv2.putText(frame, debug_text3, (10, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        with mp_hands.Hands(static_image_mode=False,
                            max_num_hands=2,
                            min_detection_confidence=0.6,
                            min_tracking_confidence=0.6) as hands:

            results = hands.process(image_rgb)

            command = None

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Dibuja los puntos y líneas de la mano detectada
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Extraer landmarks de la mano
                    landmarks = {}
                    for point_id, landmark in enumerate(hand_landmarks.landmark):
                        landmarks[point_id] = (int(landmark.x * width), int(landmark.y * height), landmark.z)

                    # Calcular vectores direccionales para una mejor detección
                    # Vectores de la muñeca a las puntas de los dedos
                    wrist = landmarks[0]
                    thumb_tip = landmarks[4]
                    index_tip = landmarks[8]
                    middle_tip = landmarks[12]
                    ring_tip = landmarks[16]
                    pinky_tip = landmarks[20]

                    # Centro de la palma
                    palm_center = landmarks[0]  # Usar la muñeca como referencia para el centro de la palma

                    # Nudillos (MCP) de los dedos
                    thumb_mcp = landmarks[2]
                    index_mcp = landmarks[5]
                    middle_mcp = landmarks[9]
                    ring_mcp = landmarks[13]
                    pinky_mcp = landmarks[17]

                    # Base de los dedos (PIP, segunda articulación)
                    index_pip = landmarks[6]
                    middle_pip = landmarks[10]
                    ring_pip = landmarks[14]
                    pinky_pip = landmarks[18]

                    def distance(p1, p2):
                        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

                    # Verificar si un dedo está extendido usando la distancia
                    # Un dedo está extendido si la punta está significativamente más lejos de la muñeca que su base
                    thumb_extended = distance(thumb_tip, wrist) > distance(thumb_mcp, wrist) * 1.2
                    index_extended = distance(index_tip, wrist) > distance(index_pip, wrist) * 1.3
                    middle_extended = distance(middle_tip, wrist) > distance(middle_pip, wrist) * 1.3
                    ring_extended = distance(ring_tip, wrist) > distance(ring_pip, wrist) * 1.3
                    pinky_extended = distance(pinky_tip, wrist) > distance(pinky_pip, wrist) * 1.3

                    fingers_extended = [thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended]

                    # Verificar dirección del pulgar (para ir a: norte, sur, este, oeste)
                    thumb_direction_x = thumb_tip[0] - wrist[0]
                    thumb_direction_y = thumb_tip[1] - wrist[1]

                    # Determinar la dirección del pulgar basado en los ángulos
                    angle_rad = np.arctan2(thumb_direction_y, thumb_direction_x)
                    angle_deg = np.degrees(angle_rad)

                    # Verificar posturas y asignar comandos

                    # Todos los 5 dedos extendidos - STOP (exactamente 5 dedos)
                    if all(fingers_extended):
                        command = "STOP"
                        command_go = "Stop"
                        socketio.emit("go", command_go)

                    # Gesto OK (pulgar e índice formando círculo) - DESPEGAR
                    # Comprobamos que la distancia entre la punta del pulgar y del índice es muy pequeña
                    elif distance(thumb_tip, index_tip) < width * 0.05:
                        # Verificamos que los otros dedos estén extendidos
                        if middle_extended and ring_extended and pinky_extended:
                            command = "DESPEGAR"
                            socketio.emit("arm_takeOff", 5)

                    # Solo pulgar extendido
                    elif thumb_extended and sum(fingers_extended[1:]) == 0:
                        # Determinar dirección basado en el ángulo
                        if -45 <= angle_deg <= 45:  # Pulgar a la izquierda (OESTE)
                            command = "OESTE"
                            command_go = "West"
                            socketio.emit("go", command_go)
                        elif 45 < angle_deg <= 135:  # Pulgar abajo (SUR)
                            command = "SUR"
                            command_go = "South"
                            socketio.emit("go", command_go)
                        elif -135 <= angle_deg < -45:  # Pulgar arriba (NORTE)
                            command = "NORTE"
                            command_go = "North"
                            socketio.emit("go", command_go)
                        elif abs(angle_deg) > 135:  # Pulgar a la derecha (ESTE)
                            command = "ESTE"
                            command_go = "East"
                            socketio.emit("go", command_go)

                    # Solo pulgar e índice extendidos - LAND
                    elif thumb_extended and index_extended and not middle_extended and not ring_extended and not pinky_extended:
                        command = "LAND"
                        socketio.emit("Land")

            # Mostrar el comando en el frame
            if command:
                print(f"Comando detectado: {command}")
                cv2.putText(frame, f"Orden: {command}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Codificar el frame procesado a base64
        _, buffer = cv2.imencode(".jpg", frame)
        processed_frame = base64.b64encode(buffer).decode("utf-8")
        return processed_frame

    except Exception as e:
        print(f"Error al procesar el frame: {e}")
        traceback.print_exc()
        return None

if __name__ == '__main__':
    print('WebApp MQTT y WebSockets')
    #app.run(debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True) #para movil
    #app.run(host='0.0.0.0', port=5000, ssl_context=('openssl/cert.pem', 'openssl/key.pem'))

    # hay que poner en marcha el servidor flask, al que se conectarán el navegador, y el websocket al que se conectará la estación de tierra
    from threading import Thread

    # Pongo en marcha el servidor flask en un hilo separado
    # Uso el el puerto 5000 para el servidor en desarrollo
    # y el puerto 8104 para el servidor en producción (que es uno de los puertos abiertos en dronseetac.upc.edu)
    #flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False))

    # Thread con certificados para el uso de https
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5004, debug=True, ssl_context=("public_certificate.pem", "private_key.pem"),use_reloader=False))
    flask_thread.start()

    # Pongo en marcha el websocket
    # Uso  el puerto 8766 para el servidor en desarrollo
    # y el puerto 8106 para el servidor en producción (que es uno de los puertos abiertos en dronseetac.upc.edu)
    socketio.run(app, host='0.0.0.0', port=8766, allow_unsafe_werkzeug=True)
