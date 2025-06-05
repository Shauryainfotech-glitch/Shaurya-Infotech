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
        
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'standard_price': 100.0,
        })
        
        self.material = self.env['product.product'].create({
            'name': 'Test Material',
            'type': 'product',
            'standard_price': 50.0,
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
        self.assertEqual(estimation.state, 'draft')
        self.assertEqual(estimation.version, 1.0)
        self.assertTrue(estimation.estimation_date)

    def test_estimation_lines(self):
        """Test estimation lines functionality"""
        estimation = self.env['mrp.estimation'].create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 10.0,
            'product_uom_id': self.product.uom_id.id,
        })
        
        # Create estimation line
        line = self.env['mrp.estimation.line'].create({
            'estimation_id': estimation.id,
            'product_id': self.material.id,
            'product_qty': 5.0,
            'product_uom_id': self.material.uom_id.id,
            'product_cost': 50.0,
            'markup_percentage': 10.0,
        })
        
        # Test computed fields
        self.assertEqual(line.marked_up_cost, 55.0)  # 50 + 10%
        self.assertEqual(line.subtotal, 275.0)  # 5 * 55
        self.assertEqual(estimation.material_total, 275.0)

    def test_estimation_costs(self):
        """Test estimation costs functionality"""
        estimation = self.env['mrp.estimation'].create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 10.0,
            'product_uom_id': self.product.uom_id.id,
        })
        
        # Create labor cost
        cost = self.env['mrp.estimation.cost'].create({
            'estimation_id': estimation.id,
            'name': 'Test Labor',
            'cost_type': 'labor',
            'labor_hours': 10.0,
            'labor_rate': 25.0,
            'labor_overhead': 20.0,
        })
        
        # Test computed total cost
        expected_cost = (10.0 * 25.0) + (10.0 * 25.0 * 0.20)  # base + overhead
        self.assertEqual(cost.total_cost, expected_cost)
        self.assertEqual(estimation.cost_total, expected_cost)

    def test_estimation_workflow(self):
        """Test estimation workflow states"""
        estimation = self.env['mrp.estimation'].create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 10.0,
            'product_uom_id': self.product.uom_id.id,
        })
        
        # Add a line to allow submission
        self.env['mrp.estimation.line'].create({
            'estimation_id': estimation.id,
            'product_id': self.material.id,
            'product_qty': 5.0,
            'product_uom_id': self.material.uom_id.id,
            'product_cost': 50.0,
        })
        
        # Test workflow transitions
        estimation.action_submit_for_approval()
        self.assertEqual(estimation.state, 'waiting_approval')
        
        estimation.action_approve()
        self.assertEqual(estimation.state, 'approved')
        
        estimation.action_send_estimation()
        self.assertEqual(estimation.state, 'sent')
        
        estimation.action_confirm()
        self.assertEqual(estimation.state, 'confirmed')

    def test_estimation_validation(self):
        """Test estimation validation constraints"""
        # Test negative quantity validation
        with self.assertRaises(ValidationError):
            self.env['mrp.estimation'].create({
                'partner_id': self.partner.id,
                'product_id': self.product.id,
                'product_qty': -1.0,
                'product_uom_id': self.product.uom_id.id,
            })

    def test_estimation_totals(self):
        """Test estimation total calculations with markup"""
        estimation = self.env['mrp.estimation'].create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 10.0,
            'product_uom_id': self.product.uom_id.id,
            'material_markup_type': 'percentage',
            'material_markup_value': 10.0,
            'cost_markup_type': 'percentage',
            'cost_markup_value': 15.0,
        })
        
        # Add material line
        self.env['mrp.estimation.line'].create({
            'estimation_id': estimation.id,
            'product_id': self.material.id,
            'product_qty': 5.0,
            'product_uom_id': self.material.uom_id.id,
            'product_cost': 50.0,
        })
        
        # Add cost
        self.env['mrp.estimation.cost'].create({
            'estimation_id': estimation.id,
            'name': 'Test Cost',
            'cost_type': 'misc',
            'unit_cost': 100.0,
            'quantity': 1.0,
        })
        
        # Test total calculations
        material_total = 250.0  # 5 * 50
        cost_total = 100.0
        material_markup = material_total * 0.10  # 25.0
        cost_markup = cost_total * 0.15  # 15.0
        expected_total = material_total + cost_total + material_markup + cost_markup
        
        self.assertEqual(estimation.material_total, material_total)
        self.assertEqual(estimation.cost_total, cost_total)
        self.assertEqual(estimation.markup_total, material_markup + cost_markup)
        self.assertEqual(estimation.estimation_total, expected_total)

    def test_version_creation(self):
        """Test version control functionality"""
        estimation = self.env['mrp.estimation'].create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 10.0,
            'product_uom_id': self.product.uom_id.id,
        })
        
        # Create new version
        new_estimation = estimation.action_create_version()
        
        # Check version increment
        self.assertEqual(estimation.version, 1.0)
        # Note: The new estimation would have version 1.1 based on default increment

    def test_mrp_costing(self):
        """Test manufacturing costing functionality"""
        # Create a manufacturing order first (simplified)
        mo = self.env['mrp.production'].create({
            'product_id': self.product.id,
            'product_qty': 10.0,
            'product_uom_id': self.product.uom_id.id,
        })
        
        # Create costing record
        costing = self.env['mrp.costing'].create({
            'mo_id': mo.id,
            'planned_cost': 1000.0,
            'raw_material_cost': 500.0,
            'labor_cost_actual': 300.0,
            'overhead_cost': 150.0,
            'machine_cost': 100.0,
            'quality_cost': 50.0,
        })
        
        # Test computed fields
        expected_actual = 500.0 + 300.0 + 150.0 + 100.0 + 50.0  # 1100.0
        expected_variance = expected_actual - 1000.0  # 100.0
        expected_percentage = (100.0 / 1000.0) * 100  # 10.0%
        
        self.assertEqual(costing.actual_cost, expected_actual)
        self.assertEqual(costing.cost_variance, expected_variance)
        self.assertEqual(costing.cost_variance_percentage, expected_percentage)

    def test_config_settings(self):
        """Test configuration settings"""
        settings = self.env['res.config.settings'].create({
            'estimation_sequence_prefix': 'TEST',
            'auto_markup_enabled': True,
            'default_material_markup': 15.0,
            'default_cost_markup': 20.0,
        })
        
        settings.execute()
        
        # Verify settings are saved
        prefix = self.env['ir.config_parameter'].get_param('mrp_estimation.sequence_prefix')
        self.assertEqual(prefix, 'TEST')

    def test_estimation_copy(self):
        """Test estimation copy functionality"""
        estimation = self.env['mrp.estimation'].create({
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'product_qty': 10.0,
            'product_uom_id': self.product.uom_id.id,
            'state': 'approved',
        })
        
        copied = estimation.copy()
        
        # Check copy behavior
        self.assertEqual(copied.state, 'draft')
        self.assertEqual(copied.version, 1.0)
        self.assertTrue('Copy of' in copied.name)
