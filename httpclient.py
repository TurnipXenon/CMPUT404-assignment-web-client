#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# Some code based on lab1

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
        self.headers = {}


class HTTPClient(object):
    BUFFER_SIZE = 4096
    USER_AGENT = "curl/7.64.1"  # todo(turnip): change

    def get_remote_ip(self, host: str) -> str:
        try:
            remote_ip = socket.gethostbyname(host)
        except socket.gaierror:
            print('Hostname could not be resolved. Exiting')
            sys.exit()

        print(f'Ip address of {host} is {remote_ip}')
        return remote_ip

    def get_host_port(self, url: str) -> int:
        url_split = url.split(":")
        if len(url_split) < 3:
            raise Exception("Missing colon (:) indicating port area")

        port_str = url_split[2]
        end_index = port_str.find("/")
        if end_index < 0:
            raise Exception("Missing slash (/) indicating port end")
        port_str = port_str[:end_index]

        return int(port_str)

    def connect(self, host: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        _, netloc, path, params, query, fragment = urllib.parse.urlparse(url)
        netloc_split = netloc.split(":")
        if len(netloc_split) < 2:
            raise AssertionError("Should not happen!")
        host_name = netloc_split[0]
        port = int(netloc_split[1])
        host = self.get_remote_ip(host_name)
        self.connect(host, port)
        # Reference: https://www.rfc-editor.org/rfc/rfc9110.html#section-3.9
        self.sendall(f"""GET / HTTP/1.1
User-Agent: {HTTPClient.USER_AGENT}
Host: {host_name}
Accept-Language: en-us""")
        full_data = self.recvall(self.socket)
        self.parse_response(full_data)
        code = 404
        body = ""
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # todo(turnip)
        host = self.get_remote_ip(url)
        port = self.get_host_port(url)
        self.connect(host, port)
        self.socket.sendall("POST / HTTP/1.1".encode("utf-8"))
        full_data = b""
        while True:
            data = self.socket.recv(HTTPClient.BUFFER_SIZE)
            if not data:
                break
            full_data += data
        print(full_data)
        code = 404
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

    def parse_response(self, full_data):
        response = HTTPResponse()

        # split the data
        lines = full_data.splitlines()
        line_1 = lines[0].split(" ")
        lines.pop(0)  # remove the first line

        raw_headers = []
        for ind in range(len(lines)):
            if lines[ind].strip() == "":
                raw_headers = lines[:ind:]

                raw_body = lines[ind:]
                if len(raw_body) > 1:
                    response.body = "\n".join(raw_body[1:])

        # understand the data
        response.code = int(line_1[1])
        for raw_entry in raw_headers:
            entry = raw_entry.split(": ", 1)
            response.headers[entry[0]] = entry[1]
        return response


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
