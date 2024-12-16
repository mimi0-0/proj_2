from flask import render_template, request
from testapp import app

# TelloのIPとポート設定
TELLO_IP = "192.168.10.1"  # TelloのIPアドレス
TELLO_PORT = 8889  # Telloが受信するポート番号
LOCAL_PORT = 8890  # ローカルでTelloからの応答を受信するポート

@app.route('/')
def index():
    return render_template('/index.html')
@app.route('/test')
def other1():
    return "テストページです！!!!gghjk"
@app.route('/sampleform')
def sample_form():
    return render_template('/sampleform.html')
@app.route('/sampleform-post', methods=['POST'])
def sample_form_temp():
    print('POSTデータ受け取ったので処理します')
    req1 = request.form['data1']

    return f'POST受け取ったよ: {req1}'


