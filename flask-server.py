from flask import Flask, render_template
import dbm
import config

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
@app.route('/home')
def index():
    rows = dbm.db_execute("SELECT * FROM 'quality_records' LIMIT 0,30")

    return render_template('index.html', rows=rows)


@app.route('/about')
def about():
    return "About"


dbm.db_exists()
app.run('127.0.0.1', port=8000, debug=True)
