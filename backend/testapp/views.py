from flask import render_template, request, jsonify
from testapp import app
#import speech_recognition as sr
import socket  # Telloに送るためにsocketを使用
from dpmatch01 import DP_ans, load_dataset 
import os

# TelloのIPとポート設定
TELLO_IP = "192.168.10.1"  # TelloのIPアドレス
TELLO_PORT = 8889  # Telloが受信するポート番号
LOCAL_PORT = 8890  # ローカルでTelloからの応答を受信するポート

# UDPソケットのセットアップ
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(('', LOCAL_PORT))

@app.route('/')
def index():
    return render_template('/index3.html')

@app.route('/command', methods=['POST', 'OPTIONS'])
def handle_command():
    if request.method == 'OPTIONS':  # OPTIONSリクエストへの対応
        response = jsonify({})
        response.status_code = 200
        return response
    # 通常のPOST処理
    command = request.json.get('command')
    if command:
        print(f"Received command: {command}")
        send_to_tello(command)  # コマンドをTelloへ送信
        return jsonify({"status": "Command sent", "command": command})
    else:
        return jsonify({"status": "No command received"}), 400

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'Audio file not provided'}), 400

    audio_file = request.files['audio']
    recognizer = sr.Recognizer()
    try:
        # SpeechRecognition用の形式に変換
        audio_data = sr.AudioFile(io.BytesIO(audio_file.read()))
        with audio_data as source:
            audio = recognizer.record(source)
        transcription = recognizer.recognize_google(audio, language='ja-JP')
        return jsonify({'transcription': transcription})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def other1():
    return "テストページです！!!!gghjk"
@app.route('/sampleform')
def sample_form():
    return render_template('/sampleform.html')
@app.route('/sampleform-post', methods=['POST'])
def sample_form_temp():
    print('POSTデータ受け取ったので処理します')
    req1 = request.form['data1']
    return f'POST受け取ったよ: {req1}'




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


