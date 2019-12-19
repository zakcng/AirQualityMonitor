from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Air Quality Monitor'


app.run('127.0.0.1', port=8000, debug=True)