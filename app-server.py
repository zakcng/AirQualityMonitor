import selectors
import types
import socket
import pickle
selector = selectors.DefaultSelector()


def accept_connection(sock):
    connection, address = sock.accept()
    print(address)
    print('Connection accepted in {}'.format(address))
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
            print(pickle.loads(recv_data))
            # data.outb += recv_data
            # print(data.outb)
        else:
            print('Closing connection in {}'.format(data.addr))
            selector.unregister(sock)
            sock.close()


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 12345
    BUFFER_SIZE = 1024
    # We create a TCP socket
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # We configure the socket in non-blocking mode
    socket_tcp.setblocking(False)
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