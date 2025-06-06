# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    # Architecture firm specific fields
    architect_license_number = fields.Char(string='Architect License Number')
    architect_license_authority = fields.Char(string='License Authority')
    architect_license_expiry = fields.Date(string='License Expiry Date')

    # Professional memberships
    professional_memberships = fields.Text(string='Professional Memberships')

    # Company capabilities
    service_areas = fields.Many2many('architect.service.area', string='Service Areas')
    specializations = fields.Many2many('architect.specialization', string='Specializations')

    # Certifications
    iso_certified = fields.Boolean(string='ISO Certified')
    iso_certification_number = fields.Char(string='ISO Certification Number')
    green_building_certified = fields.Boolean(string='Green Building Certified')

    # Digital signature
    digital_signature = fields.Binary(string='Digital Signature')
    stamp_image = fields.Binary(string='Company Stamp')
from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    # Architecture firm specific fields
    architect_license_number = fields.Char(string='Architect License Number')
    architect_license_authority = fields.Char(string='License Authority')
    architect_license_expiry = fields.Date(string='License Expiry Date')

    # Professional memberships
    professional_memberships = fields.Text(string='Professional Memberships')

    # Company capabilities
    service_areas = fields.Many2many('architect.service.area', string='Service Areas')
    specializations = fields.Many2many('architect.specialization', string='Specializations')

    # Certifications
    iso_certified = fields.Boolean(string='ISO Certified')
    iso_certification_number = fields.Char(string='ISO Certification Number')
    green_building_certified = fields.Boolean(string='Green Building Certified')

    # Digital signature
    digital_signature = fields.Binary(string='Digital Signature')
    stamp_image = fields.Binary(string='Company Stamp')
