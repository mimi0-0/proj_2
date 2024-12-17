from flask import render_template, request, jsonify, Response
import pyaudio
import wave
import requests
import time
from datetime import datetime
import cv2
from testapp import app
import speech_recognition as sr
import numpy as np
import socket  # Telloに送るためにsocketを使用
import threading
from dpmatch01 import DP_ans, load_dataset 
import os

TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)
TELLO_CAMERA_ADDRESS = ('0.0.0.0', 11111)


# UDPソケットのセットアップ
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(('', LOCAL_PORT))

# ホームページのルート
@app.route('/')
def index():
    battery = get_battery()
    current_time = get_time()
    return render_template('index3.html', battery=battery, time=current_time)


# Webページに動画をストリーミングするためのエンドポイント
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 音声ファイルをアップロードしてコマンドを予測するエンドポイント
@app.route('/upload', methods=['POST'])
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
# 音声ファイルをアップロードしてコマンドを予測するエンドポイント
@app.route('/keitaiso', methods=['POST'])
def handle_upload():
    try:
        # サーバーに最初のPOSTリクエストを送信してsent_to_clientを取得
        response = requests.post(server_url, json={})
        response_data = response.json()

        if response.status_code == 200:
            # サーバーから送信されたテキストコマンドを取得
            text = response_data.get('sent_to_client', '')
            print(f"Command from server: {text}")

            if text:
                # 辞書を読み込む
                ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"
                dictionary = load_ipadic_dict(ipadic_dir_path)

                # テキスト処理
                command, verbs, verb_dependents = process_text(text, dictionary)

                # 結果を出力
                print("\n生成されたコマンド:")
                print(command)
                print("\n動詞リスト:")
                print(verbs)
                print("\n動詞依存語リスト:")
                print(verb_dependents)

                command = 'takeoff /' + command + 'land'
                # サーバーにコマンドを送り返す
                for com_split in command.split(' /'):
                    if com_split.strip():
                        request_payload = {"response_command": com_split.strip()}
                        print(f"Sending to server: {request_payload}")  # デバッグ用に送信内容を表示
                        confirm_response = requests.post(server_url, json=request_payload)

                        if confirm_response.status_code == 200:
                            print(f"Server confirmation: {confirm_response.json()}")
                        else:
                            print(f"Error from server: {confirm_response.text}")
                        #time.sleep(5)  # 5秒間待機
        else:
            print(f"Error from server: {response_data}")
    
    except Exception as e:
        print(f"Error connecting to server: {e}")

@app.route('/update_data')
def update_data():
    battery = get_battery()
    current_time = get_time()
    return jsonify(battery=battery, time=current_time)

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
#send_to_tello('command')
#send_to_tello('streamon')

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
