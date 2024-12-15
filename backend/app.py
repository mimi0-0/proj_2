from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def flask_app():
    return 'おめでとう成功だ!!!'
def hello():
    name = "who"
    #return name
    return render_template('hello.html', title='hello2', name=name)

if __name__ == "__main__":
    app.run(debug=True, port=5001, threaded=True)  
