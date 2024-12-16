from testapp import app

@app.route('/')
def index():
    return 'Hellow World!'
