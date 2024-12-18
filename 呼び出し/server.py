from flask import Flask, request, jsonify
from flask_cors import CORS
import socket  # Telloに送るためにsocketを使用
from dpmatch01 import DP_ans, load_dataset 
import os
from CTC_yobidashi import CTC

app = Flask(__name__)
CORS(app)

# TelloのIPとポート設定
TELLO_IP = "192.168.10.1"  # TelloのIPアドレス
TELLO_PORT = 8889  # Telloが受信するポート番号
LOCAL_PORT = 8890  # ローカルでTelloからの応答を受信するポート

# UDPソケットのセットアップ
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', LOCAL_PORT))

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

'''
def get_tello_data():
    command = "command"  # Telloへのコマンド
    sock.sendto(command.encode('utf-8'), (TELLO_IP, TELLO_PORT))
    sock.settimeout(5.0)
    try:
        response, _ = sock.recvfrom(1024)
        return response.decode('utf-8')
    except socket.timeout:
        return "Telloからの応答がありません"

def parse_tello_data(data):
    fields = data.split(';')
    data_dict = {}
    for field in fields:
        if field:
            key, value = field.split(':')
            data_dict[key] = value
    return data_dict

@app.route('/')
def index():
    data = get_tello_data()
    data_dict = parse_tello_data(data)
    jsonify(data_dict)  
    print(jsonify(data_dict))
'''
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
        #dataset_dir = '/Users/abechika/utm_shere/project/DroneAPP/backend/dataset/'
        #waveforms, labels = load_dataset(dataset_dir)  # load_datasetが2つの値を返すことを仮定

        # 音声ファイルを使ってコマンドを予測
        #command_from_audio = DP_ans("received_audio.wav",waveforms, labels)
        unit = "kana"
        token_list = "/app/backend/token_list"
        mean_std = "/app/backend/kana_model_ctc/mean_std.txt"
        model = "/app/backend/kana_model_ctc/best_model.pt"
        config = "/app/backend/kana_model_ctc/config.json"
        recording_path = "/app"

        command_from_audio = CTC(unit,save_path,token_list,mean_std,model,config,recording_path)



        print(f"Received command from audio: {command_from_audio}")
        # Telloにコマンドを送信
        send_to_tello(command_from_audio)

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error in handle_upload: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)