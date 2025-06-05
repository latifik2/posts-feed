import unittest
from demo_app import DemoApp

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = DemoApp()

    def test_reponse_methods(self):
        self.assertEqual(
            self.app.http_response_methods('http://localhost'),
            {
                "status_code": 200,
                "allowed_methods": ["GET", "POST", "PUT", "DELETE"]
            }
        )

    def test_response_body(self):
        self.assertEqual(
            self.app.http_reponse_body('http://localhost'),
            {
                "body": "Hello, World!",
                "content_type": "text/html",
                "content_length": 13   
            }
        )

    def test_client_ip(self):
        self.assertEqual(
            self.app.http_get_client_ip('http://localhost')['Headers']['X-Forwarded-For'],
            '75.14.155.201'
        )
    
    def test_cors(self):
        self.assertEqual(
            self.app.http_check_cors('http://localhost')['Headers']['X-Frame-Options'],
            'SAMEORIGIN'
        )

if __name__ == '__main__':
    unittest.main()