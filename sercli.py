# usage:
# ./sercli
#     --server/client --tcp/udp --port 10086
#     --username cowsay --password 123456
import socket
import sys
from collections import deque
import json


def parse_arguments(argv):
    default_config = {
        'type': 'server',
        'protocol': 'tcp',
        'port': 10086,
        'username': 'cowsay',
        'password': '123456',
    }
    config = dict(default_config)
    arguments = deque(argv[1:])
    while len(arguments) != 0:
        next_arg = arguments.popleft()
        try:
            if next_arg == '--server':
                config['type'] = 'server'
            elif next_arg == '--client':
                config['type'] = 'client'
            elif next_arg == '--tcp':
                config['protocol'] = 'tcp'
            elif next_arg == '--udp':
                config['protocol'] = 'udp'
            elif next_arg == '--port':
                next_arg = arguments.popleft()
                config['port'] = int(next_arg)
            elif next_arg == '--username':
                next_arg = arguments.popleft()
                config['username'] = next_arg
            elif next_arg == '--password':
                next_arg = arguments.popleft()
                config['password'] = next_arg
            else:
                raise Exception(f'unknown argument: {next_arg}')
        except Exception:
            raise Exception('cannot parse arguments')
    return config


def start_server(config):
    if config['protocol'] == 'tcp':
        socket_type = socket.SOCK_STREAM
    else:  # 'udp'
        socket_type = socket.SOCK_DGRAM
    skt = socket.socket(socket.AF_INET, socket_type)
    skt.bind(('localhost', config['port']))
    if config['protocol'] == 'tcp':
        skt.listen(1)
    while True:
        try:
            if config['protocol'] == 'tcp':
                conn, addr = skt.accept()
                print(f'recived connection from {addr}')
                # assume 4096 is large enough for single request
                data = conn.recv(4096)
                print(f'recived data: {data}')
            else:
                data, addr = skt.recvfrom(4096)
                print(f'recived from {addr}: {data}')
        except KeyboardInterrupt:
            skt.close()
            print('server closed')
            return
        try:
            message = json.loads(data.decode())
            # a little silly here for readablity
            if message['username'] == config['username'] and \
                    message['password'] == config['password']:
                reply_message = {'ok': True, 'message': 'ok'}
            else:
                reply_message = {'ok': False, 'message': 'auth fail'}
        except Exception:
            reply_message = {'ok': False, 'message': 'invalid request'}
        if config['protocol'] == 'tcp':
            conn.send(json.dumps(reply_message).encode())
            conn.close()
        else:
            skt.sendto(json.dumps(reply_message).encode(), addr)


def send_request(config):
    if config['protocol'] == 'tcp':
        socket_type = socket.SOCK_STREAM
    else:  # 'udp'
        socket_type = socket.SOCK_DGRAM
    skt = socket.socket(socket.AF_INET, socket_type)
    message = {'username': config['username'], 'password': config['password']}

    if config['protocol'] == 'tcp':
        skt.connect(('localhost', config['port']))
        skt.send(json.dumps(message).encode())
        data = b''
        while True:
            part = skt.recv(4096)
            if not part:
                break
            data += part
        skt.close()
    else:
        skt.sendto(json.dumps(message).encode(), ('localhost', config['port']))
        data, _addr = skt.recvfrom(4096)
    print(f'received data: {data}')


if __name__ == '__main__':
    config = parse_arguments(sys.argv)
    if config['type'] == 'server':
        start_server(config)
    else:
        send_request(config)
