import socket
import time
import threading
from filler_to_newtext import load_ipadic_dict
from split_verb import process_text
from frame_processor import stream_on

# Create a UDP socket
tello_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)

# command-mode : 'command'
tello_socket.sendto('command'.encode('utf-8'), tello_address)
print('Entering command mode..')
time.sleep(5)  # 少し待機して応答を確認する

def carry_command(arg_command):
    for com_split in arg_command.split(' /'):
        if com_split != '':
            # コマンドを実行
            print('Get command: ' + com_split)
            tello_socket.sendto(com_split.encode('utf-8'), tello_address)
        time.sleep(5)  # 5秒間待機



if __name__ == "__main__":
    ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"
    my_address = ('192.168.10.2', 11111)
    # 辞書を読み込む
    dictionary = load_ipadic_dict(ipadic_dir_path)
    
    # 入力テキスト
    text = "前に200cm進んで"

    # テキスト処理
    command, verbs, verb_dependents = process_text(text, dictionary)

    # 結果を出力
    print("\n生成されたコマンド:")
    print(command)
    print("\n動詞リスト:")
    print(verbs)
    print("\n動詞依存語リスト:")
    print(verb_dependents)
    
    #離陸
    carry_command('takeoff')
        
    thread1 = carry_command(command)
    thread2 = stream_on(my_address)
    
    # スレッドの開始
    thread1.start()
    thread2.start()

    # 両方のスレッドが終了するのを待つ
    thread1.join()
    thread2.join()
    
    #着陸
    carry_command('land')
    
    print('We hope to see you again soon.')
    
    
    