import selectors
import types
import socket
import pickle
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import dbm

selector = selectors.DefaultSelector()


def accept_connection(sock):
    connection, address = sock.accept()
    print(address)
    print('Connection accepted: {}'.format(address))
    # We put the socket in non-blocking mode
    connection.setblocking(False)
    data = types.SimpleNamespace(addr=address, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(connection, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(BUFFER_SIZE)
        if recv_data:
            # Functional
            node_data = pickle.loads(recv_data)
            # Time received
            dt = datetime.datetime.now().isoformat()
            dbm.insert_quality_record(node_data, dt)
            detect_alert_requirement(node_data, dt)
        else:
            print('Closing connection: {}'.format(data.addr))
            selector.unregister(sock)
            sock.close()


def detect_alert_requirement(node_data, dt):
    alerts = dbm.return_all_alerts(node_data[0])

    if alerts:
        for alert in alerts:
            if alert['measurement'] == 0:  # Temperature
                if alert['state'] == '<':
                    if node_data[1] < alert['value']:
                        send_alert(alert, node_data[1], dt)
                elif alert['state'] == '==':
                    if node_data[1] == alert['value']:
                        send_alert(alert, node_data[1], dt)
                elif alert['state'] == '>':
                    if node_data[1] > alert['value']:
                        send_alert(alert, node_data[1], dt)
            elif alert['measurement'] == 1:  # Humidity
                if alert['state'] == '<':
                    if node_data[2] < alert['value']:
                        send_alert(alert, node_data[2], dt)
                elif alert['state'] == '==':
                    if node_data[2] == alert['value']:
                        send_alert(alert, node_data[2], dt)
                elif alert['state'] == '>':
                    if node_data[2] > alert['value']:
                        send_alert(alert, node_data[2], dt)
            elif alert['measurement'] == 2:  # Barometric Pressure
                if alert['state'] == '<':
                    if node_data[3] < alert['value']:
                        send_alert(alert, node_data[3], dt)
                elif alert['state'] == '==':
                    if node_data[3] == alert['value']:
                        send_alert(alert, node_data[3], dt)
                elif alert['state'] == '>':
                    if node_data[3] > alert['value']:
                        send_alert(alert, node_data[3], dt)
            elif alert['measurement'] == 3:  # PM2.5
                if alert['state'] == '<':
                    if node_data[4] < alert['value']:
                        send_alert(alert, node_data[4], dt)
                elif alert['state'] == '==':
                    if node_data[4] == alert['value']:
                        send_alert(alert, node_data[4], dt)
                elif alert['state'] == '>':
                    if node_data[4] > alert['value']:
                        send_alert(alert, node_data[4], dt)
            elif alert['measurement'] == 4:  # PM10
                if alert['state'] == '<':
                    if node_data[5] < alert['value']:
                        send_alert(alert, node_data[5], dt)
                elif alert['state'] == '==':
                    if node_data[5] == alert['value']:
                        send_alert(alert, node_data[5], dt)
                elif alert['state'] == '>':
                    if node_data[5] > alert['value']:
                        send_alert(alert, node_data[5], dt)


def send_alert(alert, node_data, dt):
    user_record = dbm.get_account_email_by_account_id(alert['account_id'])

    if alert['measurement'] == 0:
        measurement = 'Temperature'
    elif alert['measurement'] == 1:
        measurement = 'Humidity'
    elif alert['measurement'] == 2:
        measurement = 'Barometric Pressure'
    elif alert['measurement'] == 3:
        measurement = 'PM2.5'
    elif alert['measurement'] == 4:
        measurement = 'PM10'

    message = Mail(
        from_email='AQMBot@airqualitymonitor.com',
        to_emails=user_record['email'],
        subject='Alert: Air Quality Value Exceeded',
        html_content=f"""
        Hi {user_record['username']}, your air quality alert has been raised! <br>
        You set an alert regarding {measurement} {alert['state']} {alert['value']} <br>
        The reported value from the node was {node_data} for {measurement}
        """
    )

    with open('AQM/sendgrid.key') as f:
        key = f.readline()

    sg = SendGridAPIClient(key)
    response = sg.send(message)

    print(response.status_code)
    print(f"Alert sent to {user_record['email']}")

    # Record time to database.
    dbm.insert_alert_triggered_time(alert['alert_id'], dt)
    # Disable alert
    dbm.change_alert_state(alert['alert_id'], 0)


if __name__ == '__main__':
    # Determine if database needs setup
    dbm.db_exists()

    host = '127.0.0.1'
    # host = '169.254.58.5'
    port = 12345
    BUFFER_SIZE = 1024

    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket
    socket_tcp.setblocking(False)  # Configure socket non-blocking
    socket_tcp.bind((host, port))
    socket_tcp.listen()
    print('Opened socket for listening connections on {} {}'.format(host, port))
    socket_tcp.setblocking(False)
    # We register the socket to be monitored by the selector functions
    selector.register(socket_tcp, selectors.EVENT_READ, data=None)
    while socket_tcp:
        events = selector.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                (service_connection(key, mask))

    socket_tcp.close()
    print('Connection finished.')
