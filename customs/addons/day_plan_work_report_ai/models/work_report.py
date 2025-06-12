from odoo import models, fields, api

class WorkReport(models.Model):
    _name = "work.report"
    _description = "End of Day Work Report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"

    day_plan_id = fields.Many2one('day.plan', string="Day Plan", required=True, tracking=True)
    
    # Accomplishments section
    accomplishments = fields.Text(string="Accomplishments", 
                                 help="Document completed tasks and achievements")
    
    # Challenges & Solutions section
    challenges = fields.Text(string="Challenges", 
                            help="Record obstacles encountered during work")
    solutions = fields.Text(string="Solutions", 
                           help="Document implemented fixes for challenges")
    
    # Self-Assessment section
    self_assessment_productivity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Productivity Rating", tracking=True, 
       help="Rate your productivity level for the day")
    
    self_assessment_quality = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Quality Rating", tracking=True,
       help="Rate the quality of your work for the day")
    
    self_assessment_satisfaction = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Satisfaction Rating", tracking=True,
       help="Rate your overall satisfaction with the day's work")
    
    # Learnings & Next Steps section
    learnings = fields.Text(string="Learnings", 
                           help="Document insights gained during the day")
    next_steps = fields.Text(string="Next Steps",
                            help="Document future priorities and action items")
    
    # Manager review fields
    manager_review_comments = fields.Text(string="Manager Review Comments")
    manager_review_rating = fields.Selection([
        ('approved', 'Approved'),
        ('needs_revision', 'Needs Revision')
    ], string="Review Rating", tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('analyzed', 'Analyzed'),
        ('approved', 'Approved')
    ], string="Status", default='draft', tracking=True)

    def action_submit(self):
        self.write({'state': 'submitted'})
        return True

    def action_analyze(self):
        self.write({'state': 'analyzed'})
        return True

    def action_approve(self):
        self.write({'state': 'approved'})
        return True

    def action_print_report(self):
        # This method will be implemented for PDF generation
        return True
