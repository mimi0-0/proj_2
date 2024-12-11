# Telloにコマンドを送信し応答を確認するテストコード
TELLO_IP = "192.168.10.1"
TELLO_PORT = 8889
LOCAL_PORT = 8890

import socket

# ソケットのセットアップ
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', LOCAL_PORT))

def test_tello_connection(command):
    try:
        print(f"Sending command: {command}")
        sock.sendto(command.encode('utf-8'), (TELLO_IP, TELLO_PORT))
        sock.settimeout(5.0)  # 5秒のタイムアウト
        response, _ = sock.recvfrom(1024)  # 応答を受信
        print(f"Response: {response.decode('utf-8')}")
    except socket.timeout:
        print("No response from Tello (timeout)")
    except Exception as e:
        print(f"Error: {e}")

# Telloにコマンドモードを送信
test_tello_connection("command")
