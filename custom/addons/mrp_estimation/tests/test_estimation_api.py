import unittest
import requests


class TestEstimationAPI(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://localhost:8069/api/v1/estimations"
        self.headers = {'Content-Type': 'application/json'}

    def test_create_estimation(self):
        data = {
            "name": "Test Estimation",
            "product_id": 1,
            "quantity": 10,
            "cost": 100.0
        }
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json())
