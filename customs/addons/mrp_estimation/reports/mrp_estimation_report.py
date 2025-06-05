
from odoo import api, models

class MrpEstimationReport(models.AbstractModel):
    _name = 'report.mrp_estimation.report_estimation'
    _description = 'Manufacturing Estimation Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Prepare the report data.
        :param docids: List of estimation IDs
        :param data: Additional data (if any)
        :return: Dictionary containing report data
        """
        docs = self.env['mrp.estimation'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.estimation',
            'docs': docs,
            'data': data,
        }