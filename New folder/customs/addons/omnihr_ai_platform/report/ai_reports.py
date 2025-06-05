from odoo import models, api

class AIReportParser(models.AbstractModel):
    _name = 'report.omnihr_ai_platform.ai_analysis_report'
    _description = 'AI Analysis Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values for AI analysis"""
        docs = self.env['hr.employee.intelligence'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee.intelligence',
            'docs': docs,
            'data': data,
        } 