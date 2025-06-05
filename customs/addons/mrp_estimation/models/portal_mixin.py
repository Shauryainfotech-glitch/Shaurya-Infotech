from odoo import models, fields, api

class PortalMixin(models.AbstractModel):
    _name = 'estimation.portal.mixin'
    _description = 'Portal Mixin for Estimation'

    portal_access = fields.Boolean('Portal Access', default=False)
    portal_visible = fields.Boolean('Visible in Portal', default=True)
    portal_message = fields.Text('Portal Message')

    def action_grant_portal_access(self):
        self.portal_access = True
        return True

    def action_revoke_portal_access(self):
        self.portal_access = False
        return True 