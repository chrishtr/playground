import socket
import time
import urllib.parse

def handle_connection(conx):
    req = conx.makefile("b")
    reqline = req.readline().decode('utf8')
    print('handle_connection:')
    if len(reqline) == 0:
        return
    method, url, version = reqline.split(" ", 2)
    assert method in ["GET", "POST"]
    headers = {}
    while True:
        line = req.readline().decode('utf8')
        if line == '\r\n': break
        header, value = line.split(":", 1)
        headers[header.casefold()] = value.strip()
    if 'content-length' in headers:
        length = int(headers['content-length'])
        body = req.read(length).decode('utf8')
    else:
        body = None

    status, body = do_request(method, url, headers, body)
    response = "HTTP/1.0 {}\r\n".format(status)
    response += "Content-Length: {}\r\n".format(
        len(body.encode("utf8")))
    response += "\r\n" + body
    conx.send(response.encode('utf8'))
    conx.close()

def do_request(method, url, headers, body):
    if method == "GET" and url == "/popover":
        return "200 OK", show_popover()
    elif method == "POST" and url == "/form":
        return "200 OK", show_form()
    elif method == "GET" and url == "/popover-example.html":
        with open("popover-example.html") as f:
            return "200 OK", f.read()
    elif method == "GET" and url == "/popover-example-react.html":
        with open("popover-example-react.html") as f:
            return "200 OK", f.read()
    
    return "404 Not Found", not_found(url, method)

def show_popover():
    time.sleep(3)
    return "popover contents"

def show_form():
    time.sleep(3)
    return "Form submitted"

def not_found(url, method):
    out = "<!doctype html>"
    out += "<h1>{} {} not found!</h1>".format(method, url)
    return out

if __name__ == "__main__":
    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP,
    )
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 8000))
    s.listen()
    
    while True:
        conx, addr = s.accept()
        print("Received connection from", addr)
        handle_connection(conx)
