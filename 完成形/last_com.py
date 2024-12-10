import socket
import time
from filler_to_newtext import load_ipadic_dict
from split_verb import process_text

# Create a UDP socket
tello_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)

# command-mode : 'command'
tello_socket.sendto('command'.encode('utf-8'), tello_address)
print('Entering command mode..')
time.sleep(5)  # 少し待機して応答を確認する

def carry_command(arg_command):
    if arg_command != '':
        # コマンドを実行
        print('Get command: ' + arg_command)
        tello_socket.sendto(arg_command.encode('utf-8'), tello_address)
        time.sleep(5)  # 5秒間待機



if __name__ == "__main__":
    ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"
    
    # 辞書を読み込む
    dictionary = load_ipadic_dict(ipadic_dir_path)
    
    # 入力テキスト
    text = "上昇する前に回転して"

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
    
    #テキスト
    for com_split in command.split(' /'):
        carry_command(com_split)
    
    #着陸
    carry_command('land')
    print('We hope to see you again soon.')
    
    