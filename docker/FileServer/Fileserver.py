import http.server
import socketserver


def FileServer():
    PORT = 4321
    httpd = socketserver.TCPServer(
        ("", PORT), http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    FileServer()
