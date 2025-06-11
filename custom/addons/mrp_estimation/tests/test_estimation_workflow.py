import unittest
from odoo.tests.common import TransactionCase

class TestEstimationWorkflow(TransactionCase):

    def test_estimation_workflow(self):
        # Create estimation
        estimation = self.env['mrp.estimation'].create({
            'name': 'Test Estimation',
            'product_id': self.env.ref('product.product_product_7').id,
            'quantity': 10,
            'state': 'draft'
        })

        # Test transition from draft to approval
        estimation.action_approve()
        self.assertEqual(estimation.state, 'approved', "Estimation should be approved.")

        # Test submission to customer
        estimation.action_send_to_customer()
        self.assertEqual(estimation.state, 'sent', "Estimation should be sent to customer.")
