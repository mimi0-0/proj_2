from flask import render_template
from testapp import app

# TelloのIPとポート設定
TELLO_IP = "192.168.10.1"  # TelloのIPアドレス
TELLO_PORT = 8889  # Telloが受信するポート番号
LOCAL_PORT = 8890  # ローカルでTelloからの応答を受信するポート

@app.route('/')
def index():
    return render_template("index.html")
@app.route('/test')
def other1():
    return "テストページです！"