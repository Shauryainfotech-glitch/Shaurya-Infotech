
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

# Custom project stages model removed to avoid conflicts with standard Odoo project stages
# Using project.task.type for project stage management instead
# This follows Odoo best practices and avoids foreign key conflicts

class ProjectTaskTypeExtended(models.Model):
    _inherit = 'project.task.type'
    
    # Add architect-specific fields to existing task types
    is_milestone = fields.Boolean(string='Is Milestone', default=False)
    requires_approval = fields.Boolean(string='Requires Approval', default=False)
    compliance_required = fields.Boolean(string='Compliance Check Required', default=False)
    description = fields.Text(string='Stage Description')
