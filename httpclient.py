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
    USER_AGENT = "curl/7.68.0"

    def __init__(self):
        self.host_name = None
        self.netloc = None
        self.path = None
        self.params = None
        self.query = None
        self.fragment = None

    def get_remote_ip(self, host) -> str:
        try:
            remote_ip = socket.gethostbyname(host)
        except socket.gaierror:
            print('Hostname could not be resolved. Exiting')
            sys.exit()

        print(f'Ip address of {host} is {remote_ip}')
        return remote_ip

    def get_host_port(self, url) -> int:
        url_split = url.split(":")
        if len(url_split) < 3:
            raise Exception("Missing colon (:) indicating port area")

        port_str = url_split[2]
        end_index = port_str.find("/")
        if end_index < 0:
            raise Exception("Missing slash (/) indicating port end")
        port_str = port_str[:end_index]

        return int(port_str)

    def connect(self, host, port) -> None:
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
        return self.do_command(url, "GET", args)

    def POST(self, url, args=None):
        return self.do_command(url, "POST", args)

    def do_command(self, url, command="GET", args=None):
        self.raw_connect(url)
        req = self.create_request(command, args)
        self.sendall(req)
        full_data = self.recvall(self.socket)
        print(full_data)
        resp = self.parse_response(full_data)
        self.close()
        return resp

    def command(self, url, command="GET", args=None):
        return self.do_command(url, command, args)

    def raw_connect(self, url):
        _, self.netloc, self.path, self.params, self.query, self.fragment = urllib.parse.urlparse(url)
        netloc_split = self.netloc.split(":")
        if len(netloc_split) < 2:
            port = 80
        else:
            port = int(netloc_split[1])
        self.host_name = netloc_split[0]
        host = self.get_remote_ip(self.host_name)
        self.connect(host, port)

    # Reference: https://en.wikipedia.org/wiki/Percent-encoding#Reserved_characters
    SPECIAL_CHARACTERS = "\r\n !#$%&'()*+,/:;=?@[]%"
    # magic number from https://stackoverflow.com/a/196392/17836168
    MAX_ASCII = 128
    SPECIAL_MATCH = [("\\", "%"), ("r'", "0D"), ("n'", "0A")]

    def percent_encode_string(self, old_string):
        new_string = ""
        for character in old_string:
            # check if need to encode
            if character not in HTTPClient.SPECIAL_CHARACTERS and ord(character) < 128:
                new_string += character
                continue

            # encode
            encoded = str(character.encode("utf-8"))
            encoded = encoded[2:]
            for old, new in HTTPClient.SPECIAL_MATCH:
                encoded = encoded.replace(old, new)
            new_string += encoded
        return new_string

    def create_request(self, command_string, args=None):
        # Reference: https://www.rfc-editor.org/rfc/rfc9110.html#section-3.9
        path = self.path if self.path is not None and self.path != "" else "/"
        contents = [f"{command_string} {path} HTTP/1.1",
                    f"Host: {self.host_name}",
                    f"User-Agent: {HTTPClient.USER_AGENT}",
                    "Connection: close",  # https://uofa-cmput404.github.io/cmput404-slides/05-More-HTTP.html#/61
                    "Accept: */*"]
        body = ""
        if command_string == "POST":
            if args is not None or self.params != "":
                raw_entry = []
                if args is not None:
                    for k, v in args.items():
                        raw_entry.append(f"{self.percent_encode_string(k)}={self.percent_encode_string(v)}")
                if self.params != "":
                    raw_entry.append(self.params)
                body = "&".join(raw_entry)
                contents.append("Content-type: application/x-www-form-urlencoded")

            # from: https://stackoverflow.com/a/30686735/17836168
            content_length = len(body.encode("utf-8"))
            contents.append(f"Content-Length: {content_length}")

        contents.append("")
        contents.append(body)
        contents.append("")

        return "\r\n".join(contents)

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
                break

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
