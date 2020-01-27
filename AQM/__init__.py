from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from AQM.forms import LoginForm, RegistrationForm, RegisterNode
import uuid
import dbm

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '132dec296c809a27ef4433940f343108'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
from AQM.models import User


@login_manager.user_loader
def load_user(userid):
    user_record = dbm.return_user_by_id(userid)
    user = User(user_record['account_id'], user_record['user_type'], user_record['username'],
                user_record['password'], user_record['email'])
    return user


@app.route('/')
@app.route('/home')
def index():
    rows = dbm.db_execute("SELECT * FROM 'quality_records' LIMIT 0,30")

    return render_template('index.html', rows=rows)


@app.route('/nodes')
def nodes():

    return render_template('nodes.html')


@app.route('/node/<int:node_id>', methods=['GET', 'POST'])
def node(node_id):
    node_exists = dbm.node_exists(node_id)
    last_node_record = dbm.return_latest_quality_record_by_node_id(node_id)
    rows = dbm.return_all_quality_records_by_node_id(node_id)

    if not last_node_record:
        # Created dictionary with null values
        pass

    if node_exists:
        node = dbm.return_node_by_id(node_id)
        for n in node:
            print(n)
        return render_template('node.html', node=node, last_node_record=last_node_record, rows=rows)
    else:
        return redirect(url_for('index'))


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        if form.validate_on_submit():
            user_record = dbm.return_user_by_username(form.username.data)
            if user_record and bcrypt.check_password_hash(user_record['password'], form.password.data):
                user = User(user_record['account_id'], user_record['user_type'], user_record['username'],
                            user_record['password'], user_record['email'])

                login_user(user)
                return redirect(url_for('index'))
            else:
                flash(f'• Login attempt unsuccessful. Please check credentials and try again!', 'danger')
        else:
            flash(f'• Login attempt unsuccessful. Please check credentials and try again!', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            dbm.insert_user(form.username.data, hashed_pass, form.email.data)

            flash(f'• Welcome {form.username.data}, your account has been registered successfully!', 'success')

            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/admin-cp', methods=['GET', 'POST'])
@login_required
def admin_cp():
    if current_user.is_authenticated and current_user.get_user_type() == 0:
        node_names = dbm.get_node_names()
        form = RegisterNode()

        if request.method == "POST":
            if form.nodeAdd.data:
                if form.validate_on_submit():
                    nodeName = form.nodeName.data
                    nodeLocation = form.nodeLocation.data
                    nodeToken = generate_node_token()

                    dbm.insert_node(nodeName, nodeLocation, nodeToken)

                    flash(f'• Node created', 'success')
                    flash(f'• Use the following token to register the node: {nodeToken}', 'info')

                    return redirect(url_for('admin_cp'))
                else:
                    flash('• Node creation unsuccessful. Please check name and location', 'danger')
            elif form.nodeView.data:
                print("View")
            elif form.nodeRemove.data:
                print("Remove")
        return render_template('admin-cp.html', title='Admin Control Panel', form=form, node_names=node_names)
    else:
        print("Unauth")
        return redirect(url_for('index'))


@app.route("/node_management", methods=['GET', 'POST'])
@login_required
def node_management():
    if current_user.is_authenticated and current_user.get_user_type() == 0:
        if request.method == "POST":
            if request.form.get('nodeView'):
                # If view token selected
                node_name = request.form.get('node_name')

                if node_name is not "Select node:":
                    token = dbm.get_node_token_by_name(node_name)
                    flash(f'• Node {node_name} unique connection token is: {token}', 'success')
            else:
                # If node remove selected and confirmed
                dbm.remove_node_by_name(request.form.get('node_name'))
                flash('Node has been deleted!', 'success')

        return redirect(url_for('admin_cp'))
    else:
        return redirect(url_for('home'))


def generate_node_token():
    # Produces unique id according to RFC 4122
    return uuid.uuid4()


if __name__ == '__main__':
    dbm.db_exists()
    app.run(debug=True)
