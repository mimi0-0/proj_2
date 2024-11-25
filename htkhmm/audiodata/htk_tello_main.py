import socket
import time
import MeCab
import subprocess
#以下自作ライブラリ
import reco

# 文字列と数値の対応を辞書で定義
kanji_to_number = {
    "ひゃく": 100
}


#Create a UDP socket
tello_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1' , 8889)

#command-mode : 'command'
tello_socket.sendto('command'.encode('utf-8'),tello_address)
print ('Entering command mode..')
time.sleep(5)  # 少し待機して応答を確認する

tello_socket.sendto('takeoff'.encode('utf-8'),tello_address)
print ('takeoff')#離陸
time.sleep(10)#5秒間待機

while True:
    #コマンドを標準入力
    reco.run_hvite()
    # reco.mlfファイルのパスを指定
    mlf_file_path = 'reco.mlf'
    # ファイルを読み込む
    commands = reco.read_mlf_file(mlf_file_path)
    # 入力が空の場合はループを続ける
    if not commands:
        print('Error: command is empty.')
        continue

    #ノードの品詞を見る
    for node in commands:
        if node == 'sil':
            time.sleep(0.1)
        else:
            if node == 'mae':
                nodecmd = 'forward'
            elif node == 'ushiro':
                nodecmd = 'back'
            elif node == 'migi':
                nodecmd = 'right'
            elif node == 'hidari':
                nodecmd = 'left'
            else:
                print('Error: command not found.')
                nodecmd = None
                break
            cmd = nodecmd + ' 100'
    
    #コマンドを実行
    #100cm前進するためのコマンド:socket.sendto('forward 100'.encode('utf-8'),tello_address)
    print('Get command: ' + cmd)
    tello_socket.sendto(cmd.encode('utf-8'),tello_address)
    time.sleep(10)#5秒間待機
    
    tello_socket.sendto('land'.encode('utf-8'),tello_address)
    print ('land')#離陸
    time.sleep(5)#5秒間待機


print('We hope to see you again soon.')
#tello_socket.sendto('land'.encode('utf-8'),tello_address)
#time.sleep(5)#5秒間待機
#print ('land…')#着陸