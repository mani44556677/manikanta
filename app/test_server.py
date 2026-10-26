import json
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError
from app.server import Handler


class APITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_health(self):
        with urlopen(self.url + "/healthz") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_version(self):
        os.environ["APP_VERSION"] = "test-sha"
        try:
            with urlopen(self.url + "/") as response:
                self.assertEqual(json.load(response)["version"], "test-sha")
        finally:
            os.environ.pop("APP_VERSION", None)

    def test_missing(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(self.url + "/missing")
        self.assertEqual(error.exception.code, 404)
        self.assertEqual(json.load(error.exception), {"error": "not found"})
