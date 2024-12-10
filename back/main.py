from flask import Flask

app = Flask(__name__)

@app.route('/')
def flask_app():
    return 'おめでとう成功だ!'
if __name__ == '__main__':
    main.run(host='0.0.0.0', port=5000)