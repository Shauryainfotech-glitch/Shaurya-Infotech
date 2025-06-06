from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class TestMrpEstimation(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Estimation = self.env['mrp.estimation']
        self.Product = self.env['product.product']
        self.Partner = self.env['res.partner']

        # Create test company
        self.company = self.env['res.company'].create({
            'name': 'Test Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create test partner
        self.partner = self.Partner.create({
            'name': 'Test Customer',
            'is_company': True,
        })
        
        # Create test product
        self.product = self.Product.create({
            'name': 'Test Product',
            'type': 'product',
            'standard_price': 100.0,
        })

    def test_estimation_validation(self):
        """Test estimation validation constraints"""
        # Create estimation
        estimation = self.Estimation.create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 1.0,
            'product_uom_id': self.product.uom_id.id,
            'company_id': self.company.id,
        })
        
        # Test product quantity validation
        with self.assertRaises(ValidationError):
            estimation.product_qty = 0.0
        
        # Test markup validation
        estimation.material_markup_type = 'percentage'
        with self.assertRaises(ValidationError):
            estimation.material_markup_value = -101.0
            
        estimation.material_markup_type = 'fixed'
        with self.assertRaises(ValidationError):
            estimation.material_markup_value = -1.0
            
        estimation.cost_markup_type = 'percentage'
        with self.assertRaises(ValidationError):
            estimation.cost_markup_value = -101.0
            
        estimation.cost_markup_type = 'fixed'
        with self.assertRaises(ValidationError):
            estimation.cost_markup_value = -1.0
            
        # Test version validation
        with self.assertRaises(ValidationError):
            estimation.version = 0.0

    def test_estimation_line_validation(self):
        """Test estimation line validation constraints"""
        estimation = self.Estimation.create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 1.0,
            'product_uom_id': self.product.uom_id.id,
            'company_id': self.company.id,
        })
        
        # Create estimation line
        line = self.env['mrp.estimation.line'].create({
            'estimation_id': estimation.id,
            'product_id': self.product.id,
            'product_qty': 1.0,
            'product_uom_id': self.product.uom_id.id,
            'product_cost': 100.0,
        })
        
        # Test quantity validation
        with self.assertRaises(ValidationError):
            line.product_qty = 0.0
            
        # Test cost validation
        with self.assertRaises(ValidationError):
            line.product_cost = -1.0
            
        # Test markup validation
        with self.assertRaises(ValidationError):
            line.markup_percentage = -101.0
            
        # Test lead time validation
        with self.assertRaises(ValidationError):
            line.lead_time = -1.0

    def test_multi_company_security(self):
        """Test multi-company security rules"""
        # Create second company
        company2 = self.env['res.company'].create({
            'name': 'Second Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create estimation for first company
        estimation1 = self.Estimation.create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 1.0,
            'product_uom_id': self.product.uom_id.id,
            'company_id': self.company.id,
        })
        
        # Create estimation for second company
        estimation2 = self.Estimation.create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 1.0,
            'product_uom_id': self.product.uom_id.id,
            'company_id': company2.id,
        })
        
        # Switch to company 2 user
        self.env.user.company_id = company2
        
        # Should only see company 2 estimations
        estimations = self.Estimation.search([])
        self.assertEqual(len(estimations), 1)
        self.assertEqual(estimations[0].id, estimation2.id)

    def test_pdf_generation(self):
        """Test PDF report generation"""
        estimation = self.Estimation.create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 1.0,
            'product_uom_id': self.product.uom_id.id,
            'company_id': self.company.id,
        })
        
        # Generate PDF report
        report = self.env.ref('mrp_estimation.action_report_estimation')
        pdf_content, content_type = report._render_qweb_pdf([estimation.id])
        
        # Verify PDF content
        self.assertTrue(pdf_content)
        self.assertEqual(content_type, 'application/pdf')

    def test_01_create_estimation(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        self.assertEqual(estimation.name, 'Test Estimation')
        self.assertEqual(estimation.state, 'draft')

    def test_02_estimation_approval(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        estimation.action_approve()
        self.assertEqual(estimation.state, 'approved')

    def test_03_estimation_rejection(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        estimation.action_reject()
        self.assertEqual(estimation.state, 'rejected')

    def test_04_estimation_cost_calculation(self):
        estimation = self.Estimation.create({
            'name': 'Test Estimation',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
        })
        self.assertEqual(estimation.total_cost, 100.0)
