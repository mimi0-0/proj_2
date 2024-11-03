import socket
import time
import MeCab
import ipadic
import dpmatch01

# 文字列と数値の対応を辞書で定義
kanji_to_number = {
    "ひゃく": 100
}

t = MeCab.Tagger()



#Create a UDP socket
tello_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1' , 8889)

#command-mode : 'command'
tello_socket.sendto('command'.encode('utf-8'),tello_address)
print ('Entering command mode..')
time.sleep(5)  # 少し待機して応答を確認する


#tello_socket.sendto('takeoff'.encode('utf-8'),tello_address)
#print ('takeoff')#離陸
#time.sleep(5)#5秒間待機

while True:
    #コマンドを標準入力
    command = DP_ans(audiofile + "にひゃく")
    node = t.parseToNode(command)
    
    # 入力が空の場合はループを続ける
    if not command:
        print('Error: command is empty.')
        continue
    
    #ノードの品詞を見るための変数
    nodecmd = ''
    jp_far = ''
    far = 0

    #ノードの品詞を見る
    while node:
        #node.featureで品詞や活用形にアクセスできる
        f = node.feature
        p1 = f.split(',')[0]
        p2 = f.split(',')[1]
        if p1 == '名詞' and p2== '数詞':
            jp_far = node.surface # 数詞を取得
            far = number = kanji_to_number.get(jp_far, 0) #対応する数値が見つからない場合は0を返す
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
        else:
            if node.surface == 'り':
                node = node.next
                if node.surface == 'りく':
                    nodecmd = 'takeoff'
        node = node.next

    #移動コマンドが生成されているかチェック
    if nodecmd and (far != 0 or nodecmd == 'land' or nodecmd == 'takeoff'):
        # コマンドを結合
        if nodecmd == 'land':  # landコマンドは距離を伴わない
            cmd = nodecmd
            print('Created command: ' + cmd)
            tello_socket.sendto(cmd.encode('utf-8'),tello_address)
            break
        elif nodecmd == 'takeoff':  # takeoffコマンドは距離を伴わない
            cmd = nodecmd
        else:
            cmd = nodecmd + ' ' + str(far)
        print('Created command: ' + cmd)
    else:
        print('Error: command not found.')
        cmd = None
        break

    #コマンドを実行
    #100cm前進するためのコマンド:socket.sendto('forward 100'.encode('utf-8'),tello_address)
    print('Get command: ' + cmd)
    tello_socket.sendto(cmd.encode('utf-8'),tello_address)
    time.sleep(5)#5秒間待機


print('We hope to see you again soon.')
#tello_socket.sendto('land'.encode('utf-8'),tello_address)
#time.sleep(5)#5秒間待機
#print ('land…')#着陸