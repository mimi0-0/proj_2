from flask import Flask, request, jsonify
from flask_cors import CORS
import socket  # Telloに送るためにsocketを使用
#from dpmatch01 import DP_ans, load_dataset 
import os

app = Flask(__name__)
CORS(app)

"""
# TelloのIPとポート設定
TELLO_IP = "192.168.10.1"  # TelloのIPアドレス
TELLO_PORT = 8889  # Telloが受信するポート番号

# UDPソケットのセットアップ
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(("",5555)) 
"""
def send_to_tello(command):
    """
    ドローンTelloにコマンドを送る関数
    """
    try:
        print(f"Sending command to Tello: {command}")
        #sock.sendto(command.encode('utf-8'), (TELLO_IP, TELLO_PORT))
    except Exception as e:
        print(f"Error sending command to Tello: {e}")


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
        """
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
        command_from_audio = DP_ans("received_audio.wav",waveforms, labels)
        """
        send_to_client = "右に曲がる前に速度を上げて後ろに200cm進む"
        print(f"Sending command to client: {send_to_client}")
        
        # 初回リクエストか判定
        command_from_client = request.json.get('response_command')
        if not command_from_client:
            # 初回リクエストの場合はここで終了
            response = jsonify({"status": "success", "sent_to_client": send_to_client})
            response.status_code = 200
            return response
        
        print(f"Received command from client: {command_from_client}")
        
        # Telloにコマンドを送信
        send_to_tello(command_from_client)

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error in handle_upload: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)
