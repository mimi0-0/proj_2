import socket
import threading
import cv2
import time
import numpy as np
from flask import Flask, Response, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORSの設定（異なるドメインからのアクセスを許可）

# TelloのIPアドレスとポート設定
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)
TELLO_CAMERA_ADDRESS = ('0.0.0.0', 11111)

# UDPソケット作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', TELLO_PORT))

def send_to_tello(command):
    """
    ドローンTelloにコマンドを送る関数
    """
    try:
        print(f"Sending command to Tello: {command}")
        sock.sendto(command.encode('utf-8'), (TELLO_IP, TELLO_PORT))
        # 応答を受信（タイムアウトを設定可能）
        sock.settimeout(5.0)  # 5秒でタイムアウト
        response, _ = sock.recvfrom(1024)  # 最大1024バイト受信
        print(f"Response from Tello: {response.decode('utf-8')}")
        return response.decode('utf-8')
    except socket.timeout:
        print("No response from Tello (timeout)")
        return "No response (timeout)"
    except Exception as e:
        print(f"Error sending command to Tello: {e}")
        return f"Error: {str(e)}"

# Telloのコマンドを送信
send_to_tello('command')
send_to_tello('streamon')

# キャプチャオブジェクトの初期化
cap = cv2.VideoCapture(f'udp://@{TELLO_CAMERA_ADDRESS[0]}:{TELLO_CAMERA_ADDRESS[1]}')

if not cap.isOpened():
    cap.open(f'udp://@{TELLO_CAMERA_ADDRESS[0]}:{TELLO_CAMERA_ADDRESS[1]}')

time.sleep(1)

def get_battery():
    return send_to_tello("battery?")

# 時間情報取得
def get_time():
    return send_to_tello("time?")

# ビデオ受信とストリーミングを行う関数
def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # フレームが空でないことを確認
        if frame is None or frame.size == 0:
            continue
        
        # フレームのリサイズ（任意）
        frame_height, frame_width = frame.shape[:2]
        frame = cv2.resize(frame, (int(frame_width / 2), int(frame_height / 2)))

        # JPEGにエンコード
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # HTTPレスポンスとして動画を送信
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Webページに動画をストリーミングするためのエンドポイント
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# コマンドをTelloに送信するエンドポイント
@app.route('/command', methods=['POST'])
def handle_command():
    command = request.json.get('command')
    if command:
        print(f"Received command: {command}")
        send_to_tello(command)  # コマンドをTelloへ送信
        return jsonify({"status": "Command sent", "command": command})
    else:
        return jsonify({"status": "No command received"}), 400

# 音声ファイルをアップロードしてコマンドを予測するエンドポイント(3_DP)
@app.route('/upload3', methods=['POST'])
def handle_upload():
    try:
        # 'audio'フィールドのファイルを取得
        audio_file = request.files['audio']
        
        # 音声ファイルを指定のパスに保存
        save_path = '/Users/abechika/utm_shere/project/DroneAPP/backend/dataset/received_audio.wav'
        audio_file.save(save_path)
        
        print(f"Saved audio file to: {save_path}")

        # データセットのロード
        dataset_dir = '/Users/abechika/utm_shere/project/DroneAPP/backend/dataset/'
        waveforms, labels = load_dataset(dataset_dir)  # load_datasetが2つの値を返すことを仮定

        # 音声ファイルを使ってコマンドを予測
        command_from_audio = DP_ans("received_audio.wav", waveforms, labels)
        
        print(f"Received command from audio: {command_from_audio}")
        # Telloにコマンドを送信
        send_to_tello(command_from_audio)

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error in handle_upload: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/update_data')
def update_data():
    battery = get_battery()
    current_time = get_time()
    return jsonify(battery=battery, time=current_time)

# ホームページのルート
@app.route('/')
def index():
    battery = get_battery()
    current_time = get_time()
    return render_template('index.html', battery=battery, time=current_time)


# サーバーの開始
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
