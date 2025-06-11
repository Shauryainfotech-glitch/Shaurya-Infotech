from odoo import models, fields

class PortalMixin(models.AbstractModel):
    _name = 'mrp.portal.mixin'
    _description = 'Portal Mixin for Estimations'

    def get_portal_url(self):
        self.ensure_one()
        return "/my/estimations/%s" % self.id

    def get_portal_name(self):
        self.ensure_one()
        return self.name
