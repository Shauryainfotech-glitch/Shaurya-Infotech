from odoo.tests.common import HttpCase
import json

class TestEstimationAPI(HttpCase):
    def setUp(self):
        super(TestEstimationAPI, self).setUp()
        self.Estimation = self.env['mrp.estimation']
        self.Product = self.env['product.product']
        self.Partner = self.env['res.partner']

        # Create test data
        self.product = self.Product.create({
            'name': 'Test Product',
            'type': 'product',
            'standard_price': 100.0,
        })
        self.partner = self.Partner.create({
            'name': 'Test Partner',
        })

    def test_01_api_create_estimation(self):
        url = '/api/estimation/create'
        data = {
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        }
        response = self.url_open(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['estimation_id'])

    def test_02_api_get_estimation(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        url = f'/api/estimation/{estimation.id}'
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data'][0]['name'], 'Test Estimation')

    def test_03_api_invalid_estimation(self):
        url = '/api/estimation/999999'
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'Estimation not found') 