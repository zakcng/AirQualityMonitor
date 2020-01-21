from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import login_user
from flask_bcrypt import Bcrypt
from forms import LoginForm, RegistrationForm, RegisterNode
import uuid
import dbm
import server_config

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '132dec296c809a27ef4433940f343108'
bcrypt = Bcrypt(app)


@app.route('/')
@app.route('/home')
def index():
    rows = dbm.db_execute("SELECT * FROM 'quality_records' LIMIT 0,30")

    return render_template('index.html', rows=rows)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = dbm.return_user(form.username.data)

            if user and bcrypt.check_password_hash(user['password'], form.password.data):
                login_user(user, remember=True)
                return redirect(url_for('index'))
            else:
                flash(f'• Login attempt unsuccessful. Please check credentials and try again!', 'danger')
        else:
            flash(f'• Login attempt unsuccessful. Please check credentials and try again!', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            dbm.insert_user(form.username.data, hashed_pass, form.email.data)

            flash(f'• Welcome {form.username.data}, your account has been registered successfully!', 'success')

            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


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


if __name__ == '__main__':
    dbm.db_exists()
    app.run(debug=True)
