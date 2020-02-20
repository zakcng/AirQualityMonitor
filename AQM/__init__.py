from flask import Flask, render_template, flash, request, redirect, url_for, current_app, session, g
from flask_paginate import Pagination, get_page_args
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from AQM.forms import LoginForm, RegistrationForm, RegisterNode, EmailForm, PasswordForm, AlertForm
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# Util
import csv
import time
import os
import operator
import uuid
# Database
import dbm
import sqlite3
# Graphing
import plotly
import plotly.graph_objects as go
import json
import pandas as pd

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '132dec296c809a27ef4433940f343108'
app.config['SERVE'] = os.getcwd()
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
from AQM.models import User


@app.before_request
def before_request():
    g.conn = sqlite3.connect('database.sqlite3')
    g.conn.row_factory = sqlite3.Row
    g.cur = g.conn.cursor()


@app.teardown_request
def teardown(error):
    if hasattr(g, 'conn'):
        g.conn.close()


@login_manager.user_loader
def load_user(userid):
    try:
        user_record = dbm.return_user_by_id(userid)

        user = User(user_record['account_id'], user_record['user_type'], user_record['unit_preference'],
                    user_record['username'], user_record['password'], user_record['email'])
        return user
    except AttributeError:
        # Attempt to fix an issue with an deleted database and an active user session
        session.clear()


@app.route('/')
@app.route('/home')
def index():
    g.cur.execute('select count(*) from quality_records')
    total = g.cur.fetchone()[0]

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 5
    offset = (page - 1) * per_page

    sql = 'select id, name, time, temp, humidity, barometric_pressure, pm_25, pm_10 from quality_records INNER JOIN ' \
          'nodes ON quality_records.node_id=nodes.node_id order by id desc  limit {}, {}' \
        .format(offset, per_page)
    g.cur.execute(sql)
    rows = g.cur.fetchall()

    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='rows',
                                format_total=True,
                                format_number=True,
                                )

    names = dbm.get_live_node_names()

    return render_template('index.html', rows=rows, page=page,
                           per_page=per_page,
                           pagination=pagination, names=names)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/nodes')
def nodes():
    g.cur.execute('select count(*) from nodes')
    total = g.cur.fetchone()[0]

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 3
    offset = (page - 1) * per_page

    # Left join
    sql = 'SELECT * FROM nodes LEFT JOIN quality_records on quality_records.node_id = nodes.node_id GROUP BY ' \
          'nodes.node_id ORDER BY time DESC limit {}, {}' \
        .format(offset, per_page)
    g.cur.execute(sql)
    nodes = g.cur.fetchall()

    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='nodes',
                                format_total=True,
                                format_number=True,
                                )

    return render_template('nodes.html', nodes=nodes, page=page,
                           per_page=per_page,
                           pagination=pagination)


@app.route('/node/<int:node_id>', methods=['GET', 'POST'])
def node(node_id):
    form = AlertForm()
    node_exists = dbm.node_exists(node_id)

    if node_exists:
        node = dbm.return_node_by_id(node_id)
        last_node_record = dbm.return_latest_quality_record_by_node_id(node_id)

        g.cur.execute("select count(*) FROM 'quality_records' WHERE node_id={}".format(node_id))
        total = g.cur.fetchone()[0]

        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')

        sql = "SELECT id, time, temp, humidity, barometric_pressure, pm_25, pm_10 FROM 'quality_records' WHERE node_id={} ORDER BY time DESC limit {}, {}".format(
            node_id, offset, per_page)
        g.cur.execute(sql)
        rows = g.cur.fetchall()

        pagination = get_pagination(page=page,
                                    per_page=per_page,
                                    total=total,
                                    record_name='rows',
                                    format_total=True,
                                    format_number=True,
                                    )

        # Plot
        graph_json = plot(False)

        if request.method == "POST":
            if current_user.is_authenticated:
                if form.validate_on_submit():
                    alert = dbm.alert_exists(current_user.get_id(), node_id, request.form.get('measurement'),
                                             request.form.get('state'),
                                             request.form.get('value'))

                    if not alert:
                        dbm.insert_alert(current_user.get_id(), node_id, request.form.get('measurement'),
                                         request.form.get('state'),
                                         request.form.get('value'))
                        flash(f'• Successfully added alert!', 'success')
                    else:
                        flash(f'• Alert already exists for this node!', 'danger')

        return render_template('node.html', node=node, last_node_record=last_node_record, rows=rows, page=page,
                               per_page=per_page,
                               pagination=pagination, graph_json=graph_json, form=form)
    else:
        return redirect(url_for('index'))


@app.route('/plot', methods=['GET', 'POST'])
def plot(dynamic=True):
    if dynamic:
        measurement = int(request.args.get('measurement'))
    else:
        measurement = 0

    def dynamic_json(rows, measurement):
        rows = [dict(row) for row in rows]

        df = pd.DataFrame(rows)
        del df['id']  # Remove redundant record id

        fig = go.Figure()

        measurement_dict = {
            0: ["temp", "Temperature"],
            1: ["humidity", "Humidity"],
            2: ["barometric_pressure", "Barometric Pressure"],
            3: ["pm_25", "PM2.5"],
            4: ["pm_10", "PM10"]
        }

        fig.add_trace(go.Scatter(x=df['time'], y=df[measurement_dict[measurement][0]]))
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title=measurement_dict[measurement][1],
        )

        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return graph_json

    sql = "SELECT id, time, temp, humidity, barometric_pressure, pm_25, pm_10 FROM 'quality_records' WHERE node_id={} ORDER BY time DESC".format(
        1)
    g.cur.execute(sql)
    rows = g.cur.fetchall()

    graphJSON = dynamic_json(rows, measurement)

    return graphJSON


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        if form.validate_on_submit():
            user_record = dbm.return_user_by_username(form.username.data)
            if user_record and bcrypt.check_password_hash(user_record['password'], form.password.data):
                user = User(user_record['account_id'], user_record['user_type'], user_record['unit_preference'],
                            user_record['username'], user_record['password'], user_record['email'])

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


@app.route("/request-reset", methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = EmailForm()

    if request.method == "POST":
        if form.validate_on_submit():
            user_record = dbm.return_user_by_email(form.email.data)
            if user_record:
                user = User(user_record['account_id'], user_record['user_type'], user_record['username'],
                            user_record['password'], user_record['email'])

                token = user.get_reset_token()

                message = Mail(
                    from_email='AQMBot@airqualitymonitor.com',
                    to_emails=user_record['email'],
                    subject='Password Reset',
                    html_content=f"""
                    To reset your password, use the following link:<br>
                    {url_for('reset_password', token=token, _external=True)}<br>
                    If you did not submit this reset request, please ignore this email. 
                    """
                )

                with open('sendgrid.key') as f:
                    key = f.readline()

                sg = SendGridAPIClient(key)
                response = sg.send(message)

                print(response)

            flash("• If an account with that email exists a reset email has been sent!", "warning")

    return render_template('request-reset.html', title='Reset Password', form=form)


@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user_id = User.verify_reset_token(token)

    if user_id is None:
        flash('• The token provided is either invalid or expired', 'warning')
        return redirect(url_for('request_reset'))

    form = PasswordForm()

    if request.method == "POST":
        if form.validate_on_submit():
            hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            dbm.change_user_pass(user_id, hashed_pass)

            flash('• Your password has been changed! ', 'success')
            return redirect(url_for('login'))

    return render_template('reset-password.html', title='Reset Password', form=form)


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


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    alerts = dbm.get_alerts_by_user_id(current_user.get_id())

    # Workaround for SQLite row not allowing assignment
    dict_rows = [dict(row) for row in alerts]

    # Convert back to human readable

    def get_alert_current_value(node_id, selector):
        return dbm.get_latest_value_node(node_id, selector)

    def get_alert_colour_cell(value, state, latest_value):
        # Returns the colour used to display current value against the alert
        # 0 Green
        # 1 Red
        # 2 Warning

        print(alert['value'], alert['state'], alert['latest_value'])

        if value == latest_value:
            if state == '==':
                return 0
            return 2

        ops = {'>': operator.gt,
               '<': operator.lt,
               '==': operator.eq}
        print(str(latest_value) + state + str(value))
        comp = ops[state](latest_value, value)

        if comp:
            return 1
        elif not comp:
            return 0

    for alert in dict_rows:
        if alert['measurement'] == 0:
            alert['measurement'] = 'Temperature'
            alert['latest_value'] = get_alert_current_value(alert['node_id'], 'temp')
            alert['colour'] = get_alert_colour_cell(alert['value'], alert['state'], alert['latest_value'])
        elif alert['measurement'] == 1:
            alert['measurement'] = 'Humidity'
            alert['latest_value'] = get_alert_current_value(alert['node_id'], 'humidity')
            alert['colour'] = get_alert_colour_cell(alert['value'], alert['state'], alert['latest_value'])
        elif alert['measurement'] == 2:
            alert['measurement'] = 'Barometric Pressure'
            alert['latest_value'] = get_alert_current_value(alert['node_id'], 'barometric_pressure')
            alert['colour'] = get_alert_colour_cell(alert['value'], alert['state'], alert['latest_value'])
        elif alert['measurement'] == 3:
            alert['measurement'] = 'PM2.5'
            alert['latest_value'] = get_alert_current_value(alert['node_id'], 'pm_25')
            alert['colour'] = get_alert_colour_cell(alert['value'], alert['state'], alert['latest_value'])
        elif alert['measurement'] == 4:
            alert['measurement'] = 'PM10'
            alert['latest_value'] = get_alert_current_value(alert['node_id'], 'pm10')
            alert['colour'] = get_alert_colour_cell(alert['value'], alert['state'], alert['latest_value'])

    if request.method == "POST":
        if request.form.get('remove_alert'):
            dbm.remove_alert_by_id(request.form.get('remove_alert'))

            flash(f'• Alert removed', 'success')

            return redirect(url_for('account'))
        elif request.form.get('enable_alert'):
            dbm.change_alert_state(request.form.get('enable_alert'), 1)
            return redirect(url_for('account'))
        elif request.form.get('disable_alert'):
            dbm.change_alert_state(request.form.get('disable_alert'), 0)
            return redirect(url_for('account'))
        elif request.form.get('set_units'):
            unit_type = request.form.get('unit_type')
            dbm.change_user_unit_preference(current_user.get_id(), unit_type)
            flash(f'• Updated unit preferences', 'success')

    return render_template('account.html', title='Account Management', alerts=dict_rows)


@app.route('/admin-cp', methods=['GET', 'POST'])
@login_required
def admin_cp():
    if current_user.is_authenticated and current_user.get_user_type() == 0:
        node_names = dbm.get_node_names()
        usernames = dbm.get_usernames()

        register_node_form = RegisterNode()

        if request.method == "POST":
            if register_node_form.nodeAdd.data:
                if register_node_form.validate_on_submit():
                    nodeName = register_node_form.nodeName.data
                    nodeLocation = register_node_form.nodeLocation.data
                    nodeToken = generate_node_token()

                    dbm.insert_node(nodeName, nodeLocation, nodeToken)

                    flash(f'• Node created', 'success')
                    flash(f'• Use the following token to register the node: {nodeToken}', 'info')

                    return redirect(url_for('admin_cp'))
                else:
                    flash('• Node creation unsuccessful. Please check name and location', 'danger')
            elif request.form.get('remove_user'):
                username = request.form.get('account_name')

                if username is not "Select user:":
                    dbm.remove_user_by_name(username)
                    flash(f'• Removed user {username} successfully', 'success')
                else:
                    flash(f'• Please select a user to remove', 'danger')

                return redirect(url_for('admin_cp'))

        return render_template('admin-cp.html', title='Admin Control Panel', register_node_form=register_node_form,
                               node_names=node_names, usernames=usernames)
    else:
        return redirect(url_for('index'))


@app.route("/node_management", methods=['GET', 'POST'])
@login_required
def node_management():
    if current_user.is_authenticated and current_user.get_user_type() == 0:
        if request.method == "POST":
            node_name = request.form.get('node_name')

            if node_name == "Select node:":
                flash('• Please select a node!', 'danger')
                return redirect(url_for('admin_cp'))
            else:
                if request.form.get('nodeView'):
                    token = dbm.get_node_token_by_name(node_name)
                    flash(f'• Node {node_name} unique connection token is: {token}', 'success')
                else:
                    # If node remove selected and confirmed
                    dbm.remove_node_by_name(node_name)
                    flash(f'• Node {node_name} has been deleted', 'success')

        return redirect(url_for('admin_cp'))
    else:
        return redirect(url_for('home'))


@app.route("/node/<int:node_id>/download", methods=['GET', 'POST'])
def node_download(node_id):
    node_name = dbm.get_node_name_by_id(node_id)
    init_row = "record_no, date/time, temperature, humidity, barometric_pressure, pm2.5, pm10"
    records = dbm.return_all_quality_records_by_node_id(node_id)
    create_time = time.time()

    path = app.config['SERVE'] + os.path.sep + str(node_name) + '-' + str(create_time)
    filename = "%s-%s.csv" % (str(node_name), str(create_time))

    with open(path, 'w') as file:
        file.write(init_row + "\n")

    with open(path, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in records:
            writer.writerow(row)

    def generate():
        with open(path) as f:
            yield from f

        os.remove(path)

    r = current_app.response_class(generate(), mimetype='text/csv')
    r.headers.set('Content-Disposition', 'attachment', filename=filename)

    return r


def convert_temp_f(c):
    # Converts temperature from Celsius to Fahrenheit
    result = c * (9 / 5) + 32
    return "{0:.1f}".format(result)


def generate_node_token():
    # Produces unique id according to RFC 4122
    return uuid.uuid4()


def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap4')


def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')


def get_alignment():
    return current_app.config.get('LINK_ALIGNMENT', '')


def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework=get_css_framework(),
                      link_size=get_link_size(),
                      alignment=get_alignment(),
                      show_single_page=show_single_page_or_not(),
                      **kwargs
                      )


# Jinja functions
app.jinja_env.globals.update(convert_temp_f=convert_temp_f)

if __name__ == '__main__':
    dbm.db_exists()
    app.run(debug=True)
