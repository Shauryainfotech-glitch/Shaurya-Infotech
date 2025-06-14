from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class TestMrpEstimation(TransactionCase):

    def setUp(self):
        super().setUp()

        # Create test data
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'is_company': True,
            'customer_rank': 1,
        })

        # Ensure the correct UOM and Product Category are created
        uom = self.env['uom.uom'].create({
            'name': 'Unit',
            'category_id': self.env.ref('product.product_uom_categ_unit').id,
            'uom_type': 'reference',
        })

        product_category = self.env['product.category'].create({
            'name': 'Test Category'
        })

        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'standard_price': 100.0,
            'uom_id': uom.id,
            'categ_id': product_category.id,
        })

        self.material = self.env['product.product'].create({
            'name': 'Test Material',
            'type': 'product',
            'standard_price': 50.0,
            'uom_id': uom.id,
            'categ_id': product_category.id,
        })

        # Create test user groups
        self.estimation_user = self.env['res.users'].create({
            'name': 'Test Estimation User',
            'login': 'estimation_user',
            'email': 'estimation_user@test.com',
            'groups_id': [(6, 0, [self.env.ref('mrp_estimation.group_estimation_user').id])]
        })

        self.estimation_manager = self.env['res.users'].create({
            'name': 'Test Estimation Manager',
            'login': 'estimation_manager',
            'email': 'estimation_manager@test.com',
            'groups_id': [(6, 0, [self.env.ref('mrp_estimation.group_estimation_manager').id])]
        })

    def test_estimation_creation(self):
        """Test basic estimation creation"""
        estimation = self.env['mrp.estimation'].create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 10.0,
            'product_uom_id': self.product.uom_id.id,
        })

        self.assertTrue(estimation.name)
        self.assertNotEqual(estimation.name, 'New')
        self.assertEqual(estimation.state, 'draft')
        self.assertEqual(estimation.version, 1.0)
        self.assertTrue(estimation.estimation_date)
        self.assertTrue(estimation.access_token)
