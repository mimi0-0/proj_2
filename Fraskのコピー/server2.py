import socket
import cv2
import time
from flask import Flask, Response, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Tello 設定
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)
TELLO_CAMERA_ADDRESS = ('0.0.0.0', 11111)

# UDPソケット作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', TELLO_PORT))

# Telloにコマンド送信
def send_to_tello(command):
    try:
        print(f"Sending command to Tello: {command}")
        sock.sendto(command.encode('utf-8'), TELLO_ADDRESS)
        sock.settimeout(5.0)
        response, _ = sock.recvfrom(1024)
        return response.decode('utf-8')
    except socket.timeout:
        return "No response (timeout)"
    except Exception as e:
        return f"Error: {str(e)}"

# ビデオストリーミング
cap = cv2.VideoCapture(f'udp://@{TELLO_CAMERA_ADDRESS[0]}:{TELLO_CAMERA_ADDRESS[1]}')

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# バッテリー情報取得
def get_battery():
    return send_to_tello("battery?")

# 時間情報取得
def get_time():
    return send_to_tello("time?")

# ホームページ表示
@app.route('/')
def index():
    battery = get_battery()
    current_time = get_time()
    return render_template('index.html', battery=battery, time=current_time)

# 状態取得API
@app.route('/get_status')
def get_status():
    battery = get_battery()
    current_time = get_time()
    return jsonify({"battery": battery, "time": current_time})

# コマンド送信API
@app.route('/command', methods=['POST'])
def handle_command():
    command = request.json.get('command')
    if not command:
        return jsonify({"status": "No command received"}), 400
    response = send_to_tello(command)
    return jsonify({"status": "Command sent", "response": response})

# サーバー開始
if __name__ == '__main__':
    send_to_tello('command')  # コマンドモード有効化
    send_to_tello('streamon')  # ストリーミング有効化
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
