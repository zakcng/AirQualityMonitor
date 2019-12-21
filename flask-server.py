from flask import Flask, render_template, flash, request
from forms import RegisterNode
import uuid
import dbm
import server_config

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '132dec296c809a27ef4433940f343108'


@app.route('/')
@app.route('/home')
def index():
    rows = dbm.db_execute("SELECT * FROM 'quality_records' LIMIT 0,30")

    return render_template('index.html', rows=rows)


@app.route('/about')
def about():
    return "About"


@app.route('/register-node', methods=['GET', 'POST'])
def register_node():
    form = RegisterNode()
    if request.method == "POST":
        if form.validate_on_submit():
            nodeName = form.nodeName.data
            nodeLocation = form.nodeLocation.data
            nodeToken = generate_node_token()

            dbm.insert_node(nodeName, nodeLocation, nodeToken)

            flash(f'• Node created', 'success')
            flash(f'• Use the following token to register the node: {nodeToken}', 'info')
        else:
            flash('• Node creation unsuccessful. Please check name and location', 'danger')
    return render_template('register-node.html', title='Register Node', form=form)


def generate_node_token():
    # Produces unique id according to RFC 4122
    return uuid.uuid4()


dbm.db_exists()
app.run('127.0.0.1', port=8000, debug=True)
