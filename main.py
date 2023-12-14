import json
import logging
import mimetypes
import socket
import urllib
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

ROOT_DIR = Path()
STORAGE_DIR = ROOT_DIR.joinpath('storage')
STORAGE_DATA_FILE = STORAGE_DIR.joinpath('data.json')
HTTP_HOST = '0.0.0.0'
HTTP_PORT = 3000
SOCKETS_HOST = '127.0.0.1'
SOCKETS_PORT = 5000
SOCKETS_BUFFER = 1024


class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        match url.path:
            case '/':
                self.return_html_file('index.html')
            case '/message':
                self.return_html_file('message.html')
            case _:
                file_exists = ROOT_DIR.joinpath(url.path[1:]).exists()
                self.return_static_file() if file_exists else self.return_html_file('error.html', 404)

    def return_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as f:
            return self.wfile.write(f.read())

    def return_static_file(self, status=200):
        self.send_response(status)
        myme_type = mimetypes.guess_type(self.path)
        self.send_header(
            'Content-type', myme_type[0]) if myme_type else self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as f:
            self.wfile.write(f.read())

    def do_POST(self):
        server_address = (SOCKETS_HOST, SOCKETS_PORT)
        data_size = int(self.headers['Content-Length'])
        data = self.rfile.read(data_size)
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_client.sendto(data, server_address)
        socket_client.close()
        logging.debug(f'Send data from client: {data}')

        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()


def start_http_server(host, port):
    server_address = (host, port)
    httpd = HTTPServer(server_address, MyHTTPHandler)
    logging.info('Starting httpd...')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.info('Closing httpd...')
        httpd.server_close()


def save_data_to_file(data):
    parsed_data = urllib.parse.unquote_plus(data.decode('utf-8'))
    try:
        parsed_dict_message = {key: value for key, value in [elem.split('=') for elem in parsed_data.split('&')]}

        logging.debug(f'Parsed data: {parsed_dict_message}')

        with open(STORAGE_DATA_FILE, 'r', encoding='UTF-8') as f:
            data = json.load(f)
            data.update({str(datetime.now()): parsed_dict_message})

        with open(STORAGE_DATA_FILE, 'w', encoding='UTF-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.debug(f'Data saved to file: {STORAGE_DATA_FILE}')
    except Exception as e:
        logging.error(f'Error while parsing data: {e}')
        raise e


def create_storage_dir(storage_dir, data_file):
    if not storage_dir.exists():
        storage_dir.mkdir()
    if not data_file.exists():
        # data_file.touch()
        with open(STORAGE_DATA_FILE, 'w') as f:
            f.write('{}')
    return data_file


def start_sockets_server(host, port):
    server_address = (host, port)
    # socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_server.bind(server_address)
    logging.info('Starting socket server...')
    try:
        while True:
            data, address = socket_server.recvfrom(SOCKETS_BUFFER)
            logging.debug(f'Received data from {address}: {data}')
            # socket_server.sendto(data, address)
            save_data_to_file(data)
    except KeyboardInterrupt:
        pass
    finally:
        logging.info('Closing socket server...')
        socket_server.shutdown(socket.SHUT_RDWR)
        socket_server.close()


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(threadName)s - %(message)s')

    create_storage_dir(STORAGE_DIR, STORAGE_DATA_FILE)

    http_server = Thread(target=start_http_server, args=(HTTP_HOST, HTTP_PORT))
    http_server.start()

    socket_server = Thread(target=start_sockets_server, args=(SOCKETS_HOST, SOCKETS_PORT))
    socket_server.start()


if __name__ == '__main__':
    main()
