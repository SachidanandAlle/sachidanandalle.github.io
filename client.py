import os.path
import pathlib
import socketserver
from http.server import SimpleHTTPRequestHandler
from urllib.request import urlopen, Request

PORT = 9097


class MyProxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        url = self.path[1:]
        # print(f"GET: {self.path} => {url}")

        self.send_response(200)
        self.end_headers()

        if not url:
            url = "index.html"

        if url in ["index.html", "vista3dNIM.js", "vista3dNIM.js.map", "favicon.ico"]:
            p = pathlib.Path(os.path.abspath(f'./{url}'))
            if url in ["vista3dNIM.js", "vista3dNIM.js.map"]:
                with open(url, "rb") as f:
                    c = f.read().replace(b"const NIM_PROXY_URL = '';", b"const NIM_PROXY_URL = '/';")
                    self.wfile.write(c)
                return

            url = p.as_uri()

        self.copyfile(urlopen(url), self.wfile)

    def do_POST(self):
        url = self.path[1:]
        # print(f"POST: {self.path} => {url}")

        self.send_response(200)
        self.end_headers()

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        # print(f"Post Data: {post_data}")
        # print(f"Post Headers: {self.headers}")

        req = Request(url, method='POST', data=post_data, headers={k: v for k, v in self.headers.items()})
        self.copyfile(urlopen(req), self.wfile)


httpd = socketserver.ThreadingTCPServer(('', PORT), MyProxy)
print("Now serving at: http://localhost:" + str(PORT))
httpd.serve_forever()
