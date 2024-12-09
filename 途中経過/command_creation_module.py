import socket
import time
import MeCab

# 文字列と数値の対応を辞書で定義
kanji_to_number = {
    "ひゃく": 100
}

t = MeCab.Tagger()

# Create a UDP socket
tello_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)

# command-mode : 'command'
tello_socket.sendto('command'.encode('utf-8'), tello_address)
print('Entering command mode..')
time.sleep(5)  # 少し待機して応答を確認する


tello_socket.sendto('takeoff'.encode('utf-8'),tello_address)
print ('takeoff')#離陸
time.sleep(5)#5秒間待機

def create_command(command):
    # 入力が空の場合は関数を終了
    if not command:
        print('Error: command is empty.')
        return
    

    # ノードの品詞を見るための変数
    nodecmd = ''
    jp_far = ''
    far = 0

    # コマンドを解析する
    node = t.parseToNode(command)
    
    while node:
        # node.featureで品詞や活用形にアクセスできる
        f = node.feature
        p1 = f.split(',')[0]
        p2 = f.split(',')[1]
        
        if p1 == '名詞' and p2 == '数詞':
            jp_far = node.surface  # 数詞を取得
            far = kanji_to_number.get(jp_far, 0)  # 対応する数値が見つからない場合は0を返す
            
        # 名詞
        elif p1 == '名詞' and p2 != '数詞':
            if node.surface == 'まえ':
                nodecmd = 'forward'
            elif node.surface == 'うしろ':
                nodecmd = 'back'
            elif node.surface == 'みぎ':
                nodecmd = 'right'
            elif node.surface == 'ひだり':
                nodecmd = 'left'
            elif node.surface == 'ちゃく':
                node = node.next
                if node.surface == 'りく':
                    nodecmd = 'land'
            elif node.surface == '反転':
                nodecmd = 'flip r'
        else:
            if node.surface == 'り':
                node = node.next
                if node.surface == 'りく':
                    nodecmd = 'takeoff'
        node = node.next

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
            if nodecmd != 'flip r':
                cmd = nodecmd + ' ' + str(far)
            else:
                cmd = nodecmd
        print('Created command: ' + cmd)
    else:
        print('Error: command not found.')
        return
    

    # コマンドを実行
    print('Get command: ' + cmd)
    tello_socket.sendto(cmd.encode('utf-8'), tello_address)
    time.sleep(5)  # 5秒間待機

    tello_socket.sendto('land'.encode('utf-8'), tello_address)
    time.sleep(5)  # 5秒間待機
    print('land…')  # 着陸
    
    print('We hope to see you again soon.')

# Example command
#create_command('まえに100')  # ここに任意のコマンドを渡すことができます



