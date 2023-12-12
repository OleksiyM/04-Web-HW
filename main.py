import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse


class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        # print(url.query)
        match url.path:
            case '/':
                self.return_html_file('index.html')
            case '/message':
                self.return_html_file('message.html')
            case _:
                file_exists = Path().joinpath(url.path[1:]).exists()
                self.return_static_file() if file_exists else self.return_html_file('error.html', 404)
        # if url.path == '/':
        #     self.return_html_file('index.html')
        # elif url.path == '/message':
        #     self.return_html_file('message.html')
        # else:
        #     file_exists = Path().joinpath(url.path[1:]).exists()
        #     self.return_static_file() if file_exists else self.return_html_file('error.html', 404)

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
        pass


def main(server_class=HTTPServer, handler_class=MyHTTPHandler):
    server_address = ('', 3000)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == '__main__':
    main()
