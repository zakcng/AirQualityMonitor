'''
Database management module
https://docs.python.org/3/library/sqlite3.html#row-objects
https://stackoverflow.com/questions/2854011/get-a-list-of-field-values-from-pythons-sqlite3-not-tuples-representing-rows
'''

import os
import sqlite3
import datetime
from AQM import server_config

# Default path for db file
db_path = server_config.db_path

# Create globals
db_con = None
cursor = None


def db_exists():
    global db_con
    global cursor

    # Determine if database needs creating
    if os.path.exists(db_path):
        db_con = sqlite3.connect(db_path, check_same_thread=False)
        db_con.set_trace_callback(print)
        cursor = db_con.cursor()
        return True
    else:
        # Create globals
        db_con = sqlite3.connect(db_path)
        cursor = db_con.cursor()
        db_setup()
        return False


def db_setup():
    quality_records_sql = '''
    CREATE TABLE quality_records (
        id INTEGER PRIMARY KEY, 
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
        email TEXT NOT NULL UNIQUE
    );
    '''

    # Build tables
    cursor.execute(quality_records_sql)
    cursor.execute(nodes_sql)
    cursor.execute(accounts_sql)

    # Add admin
    # admin:admin
    cursor.execute('''INSERT INTO accounts(account_id, user_type, username, password, email)
                          VALUES(null,?,?,?,?)''', (
        0, "admin", "$2b$12$yZNLO93MQ9E1bkCdkowVLe3C/0SieARNigJFZ/0d85buWJ.M5om6m", "admin@admin.com"))

    # Commit changes
    db_con.commit()


def insert_quality_record(node_data):
    dt = datetime.datetime.now().isoformat()

    # Calculate node id from token
    token = str(node_data[0])
    find_node_sql = cursor.execute("SELECT * FROM nodes WHERE token=?", (token,)).fetchone()
    node_id = find_node_sql[0]

    cursor.execute('''INSERT INTO quality_records(id, node_id, time, temp, humidity, barometric_pressure, pm_25, pm_10)
                      VALUES(null,?,?,?,?,?,?,?)''',
                   (node_id, dt, node_data[1], node_data[2], node_data[3], node_data[4], node_data[5]))

    db_con.commit()


def insert_node(nodeName, nodeLocation, nodeToken):
    cursor.execute('''INSERT INTO nodes(node_id, name, location, token) VALUES(null,?,?,?)''',
                   (str(nodeName), str(nodeLocation), str(nodeToken)))

    db_con.commit()


def insert_user(username, password, email):
    # Creates a standard permission user account
    cursor.execute(
        '''INSERT INTO accounts(account_id, user_type, username, password, email) VALUES(null,1,?,?,?)''', (
            str(username), str(password), str(email)))

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
    cursor.execute("DELETE FROM nodes where name=?", (node_name,))

    # TODO: Remove quality_records as required once implemented.

    db_con.commit()


def get_node_names():
    db_con.row_factory = lambda cursor, row: row[0]
    c = db_con.cursor()
    names = c.execute("SELECT name FROM 'nodes'").fetchall()

    return names


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


def db_execute(sql_query):
    cursor.execute(sql_query)
    db_con.commit()

    return cursor.fetchall()


if __name__ == '__main__':
    db_exists()
