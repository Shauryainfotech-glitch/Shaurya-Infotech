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

        # Prepare additional data for the report
        report_data = {
            'doc_ids': docids,
            'doc_model': 'mrp.estimation',
            'docs': docs,
            'data': data,
        }

        # Add computed values for each estimation
        for doc in docs:
            # Calculate totals if not already computed
            if not doc.material_total:
                doc._compute_totals()

            # Add any additional report-specific calculations here
            report_data.update({
                'company': self.env.company,
                'currency': doc.currency_id,
                'print_date': fields.Datetime.now(),
            })

        return report_data