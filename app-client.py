import socket
import selectors
import types
import time
import random
import pickle
import argparse

selector = selectors.DefaultSelector()


def get_temp():
    if emulate:
        #temp = (random.randint(19, 32))
        temp = 23
        return temp
    else:
        temp = round(sense.get_temperature(), 2)
        return temp


def get_humidity():
    if emulate:
        return 32.2
    else:
        humidity = round(sense.get_humidity(), 2)
        return humidity


def get_barometric_pressure():
    if emulate:
        return 32.2
    else:
        pressure = round(sense.get_pressure(), 2)
        return pressure


def get_pm_25():
    if emulate:
        return 9
    else:
        return 9


def get_pm_10():
    if emulate:
        return 11.1
    else:
        return 9


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
    parser.add_argument('-e', '--emulate', help='Emulate sensors',
                        action='store_true')
    args = parser.parse_args()

    if args.token is not None:
        token = args.token
    if args.emulate is not None:
        emulate = args.emulate

    print("Token: " + token)
    print("Emulate: " + str(emulate))

    # Arguments
    host = '127.0.0.1'
    # host = '169.254.58.5'
    port = 12345
    BUFFER_SIZE = 1024
    TICK_RATE = 60

    if not emulate:
        from sense_hat import SenseHat

        sense = SenseHat()

    start_time = time.time()
    while True:
        node_data = package_data(token)

        send_data(host, port)
        time.sleep(TICK_RATE - ((time.time() - start_time) % TICK_RATE))
