import unittest


class TestHealth(unittest.TestCase):
    def test_health_endpoint(self):
        from fastapi.testclient import TestClient
        from proxy import app
        client = TestClient(app)
        resp = client.get('/health')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
