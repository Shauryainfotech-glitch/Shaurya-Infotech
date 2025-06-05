from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestEstimationWorkflow(TransactionCase):
    def setUp(self):
        super(TestEstimationWorkflow, self).setUp()
        self.Estimation = self.env['mrp.estimation']
        self.Product = self.env['product.product']
        self.Partner = self.env['res.partner']
        self.User = self.env['res.users']

        # Create test data
        self.product = self.Product.create({
            'name': 'Test Product',
            'type': 'product',
            'standard_price': 100.0,
        })
        self.partner = self.Partner.create({
            'name': 'Test Partner',
        })
        self.user = self.User.create({
            'name': 'Test User',
            'login': 'test@example.com',
            'email': 'test@example.com',
        })

    def test_01_workflow_draft_to_pending(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        estimation.action_submit()
        self.assertEqual(estimation.state, 'pending')

    def test_02_workflow_pending_to_approved(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        estimation.action_submit()
        estimation.action_approve()
        self.assertEqual(estimation.state, 'approved')

    def test_03_workflow_pending_to_rejected(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        estimation.action_submit()
        estimation.action_reject()
        self.assertEqual(estimation.state, 'rejected')

    def test_04_workflow_approved_to_draft(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        estimation.action_submit()
        estimation.action_approve()
        estimation.action_reset_to_draft()
        self.assertEqual(estimation.state, 'draft')

    def test_05_workflow_rejected_to_draft(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        estimation.action_submit()
        estimation.action_reject()
        estimation.action_reset_to_draft()
        self.assertEqual(estimation.state, 'draft') 