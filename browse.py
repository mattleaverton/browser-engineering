import socket
import ssl
import tkinter as tk
import tkinter.font

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


class Browser(object):
    def __init__(self):
        self.window = tk.Tk()
        self.canvas = tk.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        # self.canvas.pack()
        self.text = ""
        self.display_list = []
        self.scroll = 0
        self.font_size = 12

        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.scrollwheel)
        self.window.bind("<Configure>", self.resize)

    def load(self, url=""):
        headers, body = self.request(url)
        # self.text = self.lex(body)
        # self.display_list = self.layout(self.text)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        font = tkinter.font.Font(size=self.font_size)
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c, font=font, anchor="nw")

        font1 = tkinter.font.Font(family="Times", size=32)
        font2 = tkinter.font.Font(family="Times", size=32, slant="italic")
        x, y = 200, 200
        self.canvas.create_text(x, y, text="Hello, ", font=font1, anchor="nw")
        x += font1.measure("Hello, ")
        self.canvas.create_text(x, y, text="chrysanthemum!", font=font2, anchor="nw")

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        if self.scroll < 0:
            self.scroll = 0
        self.draw()

    def scrollwheel(self, e):
        self.scroll -= e.delta
        if self.scroll < 0:
            self.scroll = 0
        self.draw()

    def resize(self, e):
        global WIDTH, HEIGHT
        WIDTH = e.width
        HEIGHT = e.height
        self.display_list = self.layout(self.text)
        self.draw()

    @staticmethod
    def layout(text):
        display_list = []
        cursor_x, cursor_y = HSTEP, VSTEP
        for word in text.split():
            display_list.append((cursor_x, cursor_y, c))
            cursor_x += HSTEP
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP
        return display_list

    @staticmethod
    def lex(body):
        text = ""
        in_angle = False
        for c in body:
            if c == "<":
                in_angle = True
            elif c == ">":
                in_angle = False
            elif not in_angle:
                text += c
        return text

    @staticmethod
    def request(url):
        scheme, url = url.split("://", 1)
        assert scheme in ["http", "https"], f"Unknown scheme: {scheme}"
        port = 80 if scheme == "http" else 443
        host, path = url.split("/", 1)
        path = "/" + path

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        if scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=host)

        s.connect((host, port))
        connect = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: test_browser\r\n\r\n"
        s.send(connect.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        assert status == "200", f"{status}: {explanation}"

        headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            headers[header.lower()] = value.strip()

        body = response.read()
        s.close()

        return headers, body


if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    # Browser().load()
    tk.mainloop()
