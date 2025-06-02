class DemoApp:
    def http_response_methods(self, url):
        return {
            "status_code": 500,
            "allowed_methods": ["GET", "POST", "PUT", "DELETE"]
        }

    def http_reponse_body(self, url):
        return {
            "body": "Hello, World!",
            "content_type": "text/html",
            "content_length": 13
        }

    def http_get_client_ip(self, url):
        return {
            "status_code": 200,
            "Headers": {
                "X-Forwarded-For": "75.14.155.201"
            }
        }
    
    def http_check_cors(self, url):
        return {
            "status_code": 200,
            "Headers": {
                "X-Frame-Options": "SAMEORIGIN"
            }
        }