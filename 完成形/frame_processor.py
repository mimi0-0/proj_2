# tello操作用
import socket
import time
import cv2
def stream_on(my_address):

    # 通信用のソケットを作成
    # ※アドレスファミリ：AF_INET（IPv4）、ソケットタイプ：SOCK_DGRAM（UDP）
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # ローカル変数の名前をsockに変更
    sock.connect(my_address)

    print("ストリーミング開始")

    # ビデオストリーミングを取得して、ウィンドウに表示
    capture = cv2.VideoCapture('udp://@0.0.0.0:11111')
    while True:
        ret, frame = capture.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    capture.release()
    cv2.destroyAllWindows()