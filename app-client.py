import socket
import selectors
import types
import time
import random
import pickle
import argparse
import datetime

emulate = None

selector = selectors.DefaultSelector()


def get_temp():
    if emulate:
        temp = (random.randint(19, 32))
        return temp
    else:
        return None


def get_humidity():
    if emulate:
        return 32.2
    else:
        return None


def get_barometric_pressure():
    if emulate:
        return 32.2
    else:
        return None


def get_pm_25():
    if emulate:
        return 9
    else:
        return None


def get_pm_10():
    if emulate:
        return 11.1
    else:
        return None


def package_data(token):

    data = [token, get_temp(), get_humidity(), get_barometric_pressure(), get_pm_25(), get_pm_10()]

    return data


def send_data(host, port):
    server_address = (host, port)
    print('Starting connection towards {}'.format(server_address))
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # We connect using connect_ex () instead of connect ()
    socket_tcp.connect_ex(server_address)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(uid=0,
                                 outb=b'')
    selector.register(socket_tcp, events, data=data)
    events = selector.select()
    for key, mask in events:
        service_connection(key, mask)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_WRITE:
        if not data.outb:
            data.outb = pickle.dumps(node_data)
            # data.outb = "Test".encode()
        if data.outb:
            print('Sending {} to {}'.format(repr(data.outb), host))
            sent = sock.send(data.outb)
            sock.shutdown(socket.SHUT_WR)
            data.outb = data.outb[sent:]

        print('Closing connection')
        selector.unregister(sock)
        sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitoring Client')
    parser.add_argument('-t', '--token', help='Unique connection token', required=True)
    args = vars(parser.parse_args())
    print(args)

    # Arguments
    host = '127.0.0.1'
    port = 12345
    BUFFER_SIZE = 1024
    TICK_RATE = 1
    UID = 0  # Will be MAC address

    emulate = True
    node_data = package_data(args['token'])

    send_data(host, port)
    time.sleep(TICK_RATE)

# Argarse emulate -e to emulate if no sensors are present