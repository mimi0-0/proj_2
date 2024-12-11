from flask import Flask

main = Flask(__name__)

@main.route('/')
def flask_app():
    return 'おめでとう成功だ!'
if __name__ == '__main__':
    main.run(host='0.0.0.0', port=5000)