from flask import Flask

app = Flask(__name__)

@app.route('/')
def flask_app():
    return 'おめでとう成功だ!!'


if __name__ == "__main__":
    app.run(debug=True, port=5001, threaded=True)  
