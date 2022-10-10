import unittest
import httpclient

httpclass = httpclient


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.http = httpclass.HTTPClient()

    def test_parse_response(self):
        test_response = """HTTP/1.1 200 OK
Date: Mon, 27 Jul 2009 12:28:53 GMT
Server: Apache
Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
ETag: "34aa387-d-1568eb00"
Accept-Ranges: bytes
Content-Length: 51
Vary: Accept-Encoding
Content-Type: text/plain

Hello World! My content includes a trailing CRLF."""

        response = self.http.parse_response(test_response)
        self.assertEqual(200, response.code)
        self.assertEqual("Hello World! My content includes a trailing CRLF.", response.body)
        self.assertEqual({
            "Date": "Mon, 27 Jul 2009 12:28:53 GMT",
            "Server": "Apache",
            "Last-Modified": "Wed, 22 Jul 2009 19:15:56 GMT",
            "ETag": "\"34aa387-d-1568eb00\"",
            "Accept-Ranges": "bytes",
            "Content-Length": "51",
            "Vary": "Accept-Encoding",
            "Content-Type": "text/plain",
        }, response.headers)

    if __name__ == '__main__':
        unittest.main()
