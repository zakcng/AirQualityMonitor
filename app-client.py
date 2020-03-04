import socket
import selectors
import types
import time
import random
import pickle
import argparse

selector = selectors.DefaultSelector()


def get_sds011():
    serial_device = glob.glob("/dev/ttyUSB*")[0]
    return serial_device


def get_temp():
    if emulate:
        #temp = (random.randint(20, 23))
        temp = 23
        return temp
    else:
        temp = round(sense.get_temperature(), 2)
        return temp


def get_humidity():
    if emulate:
        return 29
    else:
        humidity = round(sense.get_humidity(), 2)
        return humidity


def get_barometric_pressure():
    if emulate:
        return 32.2
    else:
        pressure = round(sense.get_pressure(), 2)
        return pressure


def get_particulate_matter():
    if emulate:
        return 200, 11
    else:
        sds011.sleep(sleep=False)
        time.sleep(30)
        pm_readings = sds011.query()
        sds011.sleep()
        return pm_readings


def package_data(token):
    pm_readings = get_particulate_matter()
    data = [token, get_temp(), get_humidity(), get_barometric_pressure(), pm_readings[0], pm_readings[1]]
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
        import glob
        from SDS011 import SDS011

        sense = SenseHat()

        # Detect SDS011 on Raspberry Pi.
        usb = get_sds011()
        sds011 = SDS011(usb, use_query_mode=True)

    start_time = time.time()
    while True:
        node_data = package_data(token)
        print(node_data)
        send_data(host, port)
        time.sleep(TICK_RATE - ((time.time() - start_time) % TICK_RATE))
