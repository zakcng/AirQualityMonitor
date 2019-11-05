#!/usr/bin/env python3

import socket
import selectors
import types
import time
import random
import pickle

selector = selectors.DefaultSelector()


def get_temp():
    temp = str(random.randint(19, 32))
    return temp


def get_sensor_readings():
    readings_list = [get_temp()]

    return readings_list


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
            data.outb = pickle.dumps("Test")
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
    # Arguments
    host = '127.0.0.1'
    port = 12345
    BUFFER_SIZE = 1024
    TICK_RATE = 1
    UID = 0  # Will be MAC address

    # sensorData = ['28']
    sensorData = get_sensor_readings()

    send_data(host, port)
    time.sleep(TICK_RATE)
