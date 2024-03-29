'''
Database management module
https://docs.python.org/3/library/sqlite3.html#row-objects
https://stackoverflow.com/questions/2854011/get-a-list-of-field-values-from-pythons-sqlite3-not-tuples-representing-rows
'''

import os
import sqlite3

# Default path for db file
db_path = None

# Create globals
db_con = None
cursor = None


def db_exists():
    global db_con
    global cursor

    # Determine if database needs creating
    if os.path.exists(db_path):
        db_con = sqlite3.connect(db_path, check_same_thread=False)
        cursor = db_con.cursor()
        return True
    else:
        # Create globals
        db_con = sqlite3.connect(db_path, check_same_thread=False)
        cursor = db_con.cursor()
        db_setup()
        return False


def db_setup():
    quality_records_sql = '''
    CREATE TABLE quality_records (
        record_id INTEGER PRIMARY KEY, 
        node_id INTEGER NOT NULL,
        time TEXT NOT NULL,
        temp REAL NOT NULL,
        humidity REAL NOT NULL,
        barometric_pressure REAL NOT NULL,
        pm_25 REAL NOT NULL, 
        pm_10 REAL NOT NULL,
        FOREIGN KEY (node_id)
            REFERENCES nodes (node_id)
    );
    '''
    nodes_sql = '''
    CREATE TABLE nodes ( 
        node_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        location TEXT NOT NULL,
        token TEXT NOT NULL UNIQUE
    );
    '''

    accounts_sql = '''
    CREATE TABLE accounts (
        account_id INTEGER PRIMARY KEY,
        user_type INTEGER NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        unit_preference INTEGER NOT NULL DEFAULT 0
    );
    '''

    alerts_sql = '''
    CREATE TABLE alerts (
        alert_id INTEGER PRIMARY KEY,
        account_id INTEGER NOT NULL,
        node_id INTEGER NOT NULL,
        measurement INTEGER NOT NULL,
        state TEXT NOT NULL,
        value REAL NOT NULL,
        time_triggered TEXT,
        enabled INTEGER NOT NULL,
        FOREIGN KEY (account_id)
            REFERENCES accounts (account_id)
        );
    '''

    # Build tables
    cursor.execute(quality_records_sql)
    cursor.execute(nodes_sql)
    cursor.execute(accounts_sql)
    cursor.execute(alerts_sql)

    # Add admin
    # admin:admin
    cursor.execute('''INSERT INTO accounts(account_id, user_type, username, password, email)
                          VALUES(null,?,?,?,?)''', (
        0, "admin", "$2b$12$yZNLO93MQ9E1bkCdkowVLe3C/0SieARNigJFZ/0d85buWJ.M5om6m", "admin@admin.com"))

    # Commit changes
    db_con.commit()


def drop_all():
    # Drop all tables used during testing
    cursor.execute('DELETE FROM quality_records')
    cursor.execute('DELETE FROM nodes')
    cursor.execute('DELETE FROM accounts')
    cursor.execute('DELETE FROM alerts')

    db_con.commit()


def set_debug(b=True):
    if b:
        db_con.set_trace_callback(print)
    else:
        db_con.set_trace_callback(False)


def insert_quality_record(node_data, dt):
    # Calculate node id from token
    token = str(node_data[0])
    node_id = get_node_id_by_token(token)

    if node_id:
        cursor.execute('''INSERT INTO quality_records(record_id, node_id, time, temp, humidity, barometric_pressure, pm_25, pm_10)
                          VALUES(null,?,?,?,?,?,?,?)''',
                       (node_id, dt, node_data[1], node_data[2], node_data[3], node_data[4], node_data[5]))

        db_con.commit()

        return True
    else:
        return False


def insert_node(nodeName, nodeLocation, nodeToken):
    cursor.execute('''INSERT INTO nodes(node_id, name, location, token) VALUES(null,?,?,?)''',
                   (str(nodeName), str(nodeLocation), str(nodeToken)))

    db_con.commit()


def insert_user(username, password, email, user_type=1):
    # Insert a user into the database default user type is standard user
    cursor.execute(
        '''INSERT INTO accounts(account_id, user_type, username, password, email) VALUES(null,?,?,?,?)''',
        (str(user_type), str(username), str(password), str(email)))

    db_con.commit()


def insert_alert(account_id, node_id, measurement, state, value):
    # Creates a standard permission user account
    cursor.execute(
        '''INSERT INTO alerts(alert_id, account_id, node_id, measurement, state, value, enabled) VALUES(null,?,?,?,?,?,?)''',
        (account_id, node_id,
         measurement,
         state, value, 1))

    db_con.commit()


def insert_alert_triggered_time(alert_id, dt):
    # Updates the triggered time of an alert
    cursor.execute(
        '''UPDATE alerts SET time_triggered = ? WHERE alert_id = ?''', (dt, alert_id))

    db_con.commit()


def change_user_pass(user_id, hashed_pass):
    # Changes the users password after a valid reset
    cursor.execute(
        '''UPDATE accounts SET password = ? WHERE account_id = ?''', (hashed_pass, user_id))

    db_con.commit()


def change_user_unit_preference(user_id, unit_preference):
    # Changes the users unit preference
    cursor.execute(
        '''UPDATE accounts SET unit_preference = ? WHERE account_id = ?''', (unit_preference, user_id))

    db_con.commit()


def node_exists_by_id(node_id):
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT * FROM nodes WHERE node_id=?", (node_id,))
    node = cust_cursor.fetchone()

    if node:
        return True
    else:
        return False


def node_exists_by_name(node_name):
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT * FROM nodes WHERE name=?", (node_name,))
    node = cust_cursor.fetchone()

    if node:
        return True
    else:
        return False


def alert_exists(account_id, node_id, measurement, state, value):
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute(
        "SELECT * FROM alerts WHERE account_id=? AND node_id=? AND measurement=? AND state=? and value=?",
        (account_id, node_id, measurement, state, value))
    exists = cust_cursor.fetchone()

    if exists:
        return True
    else:
        return False


def change_alert_state(alert_id, enabled):
    cursor.execute(
        '''UPDATE alerts SET enabled = ? WHERE alert_id = ?''', (enabled, alert_id))

    db_con.commit()


def get_node_token_by_name(node_name):
    # Return the node token identified by node name
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT token FROM nodes WHERE name=?", (node_name,))

    token = cust_cursor.fetchone()[0]
    return token


def remove_node_by_name(node_name):
    # Removes a node identified by node name
    id = get_node_id_by_name(node_name)

    cursor.execute("DELETE FROM nodes where name=?", (node_name,))
    cursor.execute("DELETE FROM quality_records where node_id=?", (id,))
    cursor.execute("DELETE FROM alerts where node_id=?", (id,))

    db_con.commit()


def remove_user_by_name(username):
    # Removes a node identified by node name
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT account_id FROM accounts WHERE username=?", (username,))

    user_id = cust_cursor.fetchone()[0]

    cursor.execute("DELETE FROM accounts where username=?", (username,))
    cursor.execute("DELETE FROM alerts where account_id=?", (user_id,))

    db_con.commit()


def remove_alert_by_id(alert_id):
    # Remove an alert by alert_id
    cursor.execute("DELETE FROM alerts where alert_id=?", (alert_id,))

    db_con.commit()


def get_node_names():
    db_con.row_factory = lambda cursor, row: row[0]
    c = db_con.cursor()
    names = c.execute("SELECT name FROM 'nodes'").fetchall()

    return names


def get_usernames():
    db_con.row_factory = lambda cursor, row: row[0]
    c = db_con.cursor()
    names = c.execute("SELECT username FROM 'accounts' WHERE user_type = 1").fetchall()

    return names


def get_node_id_by_token(token):
    # Calculate node id from token
    find_node_sql = cursor.execute("SELECT * FROM nodes WHERE token=?", (token,)).fetchone()

    if find_node_sql:
        node_id = find_node_sql[0]

        if node_id:
            return node_id
        else:
            return None
    else:
        return None


def get_node_id_by_name(name):
    # Calculate node id from name
    find_node_sql = cursor.execute("SELECT * FROM nodes WHERE name=?", (name,)).fetchone()
    name = find_node_sql[0]

    if name:
        return name
    else:
        return None


def get_node_name_by_id(node_id):
    # Return the node name identified by node id
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT name FROM nodes WHERE node_id=?", (node_id,))

    token = cust_cursor.fetchone()[0]

    return token


def get_live_node_names():
    # Return the node name of records_submitted within 5 minutes
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()

    cust_cursor.execute('''
    SELECT quality_records.time, nodes.name, nodes.node_id 
    FROM quality_records 
    INNER JOIN nodes on quality_records.node_id=nodes.node_id 
    WHERE datetime(time) >=datetime('now', '-5 Minute') 
    GROUP BY nodes.node_id
    ORDER BY time DESC
    LIMIT 5
    ''')

    names = cust_cursor.fetchall()

    return names


def get_latest_value_node(node_id, selector):
    # Returns the current value from a node
    # Return the username and email using the account_id
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute(
        "SELECT {}, time FROM 'quality_records' where node_id=? ORDER BY time desc".format(selector),
        (node_id,))
    value = cust_cursor.fetchone()

    if value:
        return value[0]
    else:
        return None

def get_alerts_by_user_id(user_id):
    # Return alerts given a users id
    # Join for node_name
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()

    cust_cursor.execute(
        "SELECT alert_id, account_id, alerts.node_id, measurement, state, value, time_triggered, enabled, name FROM alerts INNER JOIN nodes on alerts.node_id=nodes.node_id WHERE account_id = ?",
        (user_id,))

    alerts = cust_cursor.fetchall()

    return alerts


def get_account_email_by_account_id(account_id):
    # Return the username and email using the account_id
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT username, email FROM 'accounts' WHERE account_id=?", (account_id,))

    account_details = cust_cursor.fetchone()

    return account_details


def return_node_by_id(node_id):
    # Returns the user record by username
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT * FROM nodes WHERE node_id= ?", (node_id,))
    record = cust_cursor.fetchone()

    if record:
        return record
    else:
        return None


def return_user_by_username(username):
    # Returns the user record by username
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT * FROM accounts WHERE username = ?", (username,))
    record = cust_cursor.fetchone()

    if record:
        return record
    else:
        return None


def return_user_by_id(account_id):
    # Returns the user record by account_id
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,))
    record = cust_cursor.fetchone()

    if record:
        return record
    else:
        return None


def return_user_by_email(email):
    # Returns the user record by email
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute("SELECT * FROM accounts WHERE email = ?", (email,))
    record = cust_cursor.fetchone()

    if record:
        return record
    else:
        return None


def return_latest_quality_record_by_node_id(node_id):
    # Returns the most recent quality record from a node
    # If no quality records are present returns None
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute(
        "SELECT * FROM 'quality_records' WHERE node_id=? ORDER BY time DESC LIMIT 1",
        (node_id,))
    record = cust_cursor.fetchone()

    if record:
        return record
    else:
        return None


def return_pm_data_24_hours_by_node_id(node_id):
    # Return the node name of records_submitted within 5 minutes
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()

    cust_cursor.execute(
        "SELECT node_id,pm_25,pm_10 FROM quality_records WHERE datetime(time) >=datetime('now', '-1 Day') AND node_id=?"
        , (node_id,))

    records = cust_cursor.fetchall()

    if records:
        return records
    else:
        return None


def return_all_quality_records_by_node_id(node_id):
    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute(
        "SELECT record_id, time, temp, humidity, barometric_pressure, pm_25, pm_10 FROM 'quality_records' WHERE node_id=? ORDER BY time DESC",
        (node_id,))
    record = cust_cursor.fetchall()

    if record:
        return record
    else:
        return None


def return_all_alerts(token):
    # Returns all alerts related to that node_id accessed via the token

    node_id = get_node_id_by_token(token)

    db_con.row_factory = sqlite3.Row
    cust_cursor = db_con.cursor()
    cust_cursor.execute(
        "SELECT * FROM alerts WHERE node_id={}".format(node_id))

    record = cust_cursor.fetchall()

    return record


def db_execute(sql_query):
    cursor.execute(sql_query)
    db_con.commit()

    return cursor.fetchall()
