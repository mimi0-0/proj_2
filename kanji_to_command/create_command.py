import socket
import time
from analyze import load_ipadic_dict, morphological_analysis

# 文字列と数値の対応を辞書で定義
kanji_to_number = {
    "ひゃく": 100
}

# IPAdic辞書の読み込み（ディレクトリパスを指定）
ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"
dictionary = load_ipadic_dict(ipadic_dir_path)

# Create a UDP socket
tello_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)

# command-mode : 'command'
tello_socket.sendto('command'.encode('utf-8'), tello_address)
print('Entering command mode..')
time.sleep(5)  # 少し待機して応答を確認する

#離陸
tello_socket.sendto('takeoff'.encode('utf-8'),tello_address)
print ('takeoff')
time.sleep(5)#5秒間待機

def create_command(text):
    # 入力が空の場合は関数を終了
    if not text:
        print('Error: command is empty.')
        return
    
    
    # ノードの品詞を見るための変数
    nodecmd = ''
    jp_far = ''
    far = 0

    # コマンドを解析する
    node = morphological_analysis(text, dictionary)
    #node = t.parseToNode(command)
    
    if node:
        for word, pos in node:
            print(f'{word} ({pos})')
    else:
        print("No morphological analysis result found.")
    
    for word, pos in node:
        if pos == '数詞':
            jp_far = word  # 数詞を取得
            far = kanji_to_number.get(jp_far, 0)  # 対応する数値が見つからない場合は0を返す
            
        # 名詞
        elif pos == '名詞':
            if word == '前':
                nodecmd = 'forward'
            elif word == '後ろ':
                nodecmd = 'back'
            elif word == '右':
                nodecmd = 'right'
            elif word == '左':
                nodecmd = 'left'
            elif word == 'ちゃく':
                node = node.next
                if word == 'りく':
                    nodecmd = 'land'
        else:
            if word == 'り':
                node = node.next
                if word == 'りく':
                    nodecmd = 'takeoff'
        #node = node.next
    print(nodecmd)

    # 移動コマンドが生成されているかチェック
    if nodecmd or (far != 0 or nodecmd == 'land' or nodecmd == 'takeoff'): #　離陸、着陸をする場合は1個目のorをandに
        # コマンドを結合
        if nodecmd == 'land':  # landコマンドは距離を伴わない
            cmd = nodecmd
            print('Created command: ' + cmd)
            tello_socket.sendto(cmd.encode('utf-8'), tello_address)
            return
        elif nodecmd == 'takeoff':  # takeoffコマンドは距離を伴わない
            cmd = nodecmd
        else:
            cmd = nodecmd # + ' ' + str(far)
        print('Created command: ' + cmd)
    else:
        print('Error: command not found.')
        return
    

    # コマンドを実行
    cmd = cmd + ' 100' # 距離は100がデフォ
    print('Get command: ' + cmd)
    tello_socket.sendto(cmd.encode('utf-8'), tello_address)
    time.sleep(5)

    #着陸
    tello_socket.sendto('land'.encode('utf-8'), tello_address)
    time.sleep(5)
    print('land…')  
    
    print('We hope to see you again soon.')

# Example command
#create_command('まえに100')  # ここに任意のコマンドを渡すことができます



