'''
Database management module

'''

import os
import sqlite3
import datetime

# Default path for db file
db_path = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

# Create globals
db_con = None
cursor = None


def db_exists():
    global db_con
    global cursor

    # Determine if database needs creating
    if os.path.exists(db_path):
        db_con = sqlite3.connect(db_path)
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
        pm_10 REAL NOT NULL
    );
    '''

    # Execute SQL
    cursor.execute(quality_records_sql)

    # Commit changes
    db_con.commit()


def insert_quality_record(node_data):
    dt = datetime.datetime.now().isoformat()
    cursor.execute('''INSERT INTO quality_records(id, node_id, time, temp, humidity, barometric_pressure, pm_25, pm_10)
                      VALUES(null,?,?,?,?,?,?,?)''',
                   (node_data[0], dt, node_data[1], node_data[2], node_data[3], node_data[4], node_data[5]))

    db_con.commit()


if __name__ == '__main__':
    db_exists()
