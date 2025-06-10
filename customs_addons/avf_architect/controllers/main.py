
# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
import json
import base64
from datetime import datetime, timedelta

class ArchitectController(http.Controller):

    @http.route('/architect/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kwargs):
        """Main dashboard for architect module"""
        return request.render('avf_architect.dashboard_template', {
            'page_name': 'dashboard',
        })

    @http.route('/architect/api/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        """API endpoint for dashboard data"""
        try:
            # Project statistics
            project_env = request.env['architect.project']
            projects_total = project_env.search_count([])
            projects_active = project_env.search_count([('state', 'in', ['confirmed', 'in_progress'])])
            projects_completed = project_env.search_count([('state', '=', 'completed')])
            projects_overdue = project_env.search_count([
                ('deadline', '<', datetime.now().date()),
                ('state', 'not in', ['completed', 'cancelled'])
            ])

            # Compliance statistics
            compliance_env = request.env['architect.compliance']
            compliance_pending = compliance_env.search_count([('state', '=', 'pending')])
            compliance_approved = compliance_env.search_count([('state', '=', 'approved')])
            compliance_rejected = compliance_env.search_count([('state', '=', 'rejected')])
            compliance_overdue = compliance_env.search_count([
                ('deadline', '<', datetime.now().date()),
                ('state', 'not in', ['approved', 'not_applicable'])
            ])

            # DPR statistics
            dpr_env = request.env['architect.dpr']
            dpr_draft = dpr_env.search_count([('state', '=', 'draft')])
            dpr_under_review = dpr_env.search_count([('state', '=', 'under_review')])
            dpr_approved = dpr_env.search_count([('state', '=', 'approved')])

            # Recent projects
            recent_projects = project_env.search([
                ('user_id' , '=', request.env.user.id)
            ], limit=5, order='write_date desc')

            return {
                'success': True,
                'data': {
                    'projects': {
                        'total': projects_total,
                        'active': projects_active,
                        'completed': projects_completed,
                        'overdue': projects_overdue
                    },
                    'compliance': {
                        'pending': compliance_pending,
                        'approved': compliance_approved,
                        'rejected': compliance_rejected,
                        'overdue': compliance_overdue
                    },
                    'dpr': {
                        'draft': dpr_draft,
                        'under_review': dpr_under_review,
                        'approved': dpr_approved
                    },
                    'recent_projects': [{
                        'id': p.id,
                        'name': p.name,
                        'code': p.code,
                        'progress': p.progress,
                        'state': p.state,
                        'partner_name': p.partner_id.name
                    } for p in recent_projects]
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/architect/api/ai_recommendations', type='json', auth='user')
    def get_ai_recommendations(self, project_id=None, **kwargs):
        """Get AI recommendations for a project or general recommendations"""
        try:
            recommendations = []
            
            if project_id:
                project = request.env['architect.project'].browse(project_id)
                if project.exists():
                    # Project-specific recommendations
                    recommendations = self._generate_project_recommendations(project)
            else:
                # General recommendations
                recommendations = self._generate_general_recommendations()

            return {
                'success': True,
                'recommendations': recommendations
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_project_recommendations(self, project):
        """Generate AI recommendations for a specific project"""
        recommendations = []
        
        # Environmental compliance recommendations
        if project.category in ['eco_tourism', 'infrastructure']:
            recommendations.append({
                'type': 'environmental',
                'title': 'Environmental Impact Assessment',
                'description': 'Consider conducting detailed environmental impact assessment for this project type.',
                'priority': 'high',
                'action': 'Create EIA compliance item'
            })
        
        # Budget optimization
        if project.estimated_cost > project.budget:
            recommendations.append({
                'type': 'financial',
                'title': 'Budget Optimization',
                'description': f'Estimated cost exceeds budget by {((project.estimated_cost - project.budget) / project.budget * 100):.1f}%. Review scope or increase budget.',
                'priority': 'high',
                'action': 'Review project scope'
            })
        
        # Timeline recommendations
        if project.deadline and (project.deadline - datetime.now().date()).days < 30:
            recommendations.append({
                'type': 'timeline',
                'title': 'Timeline Alert',
                'description': 'Project deadline is approaching. Consider resource optimization.',
                'priority': 'medium',
                'action': 'Review project timeline'
            })
        
        #    Sustainability recommendations
        recommendations.append({
            'type': 'sustainability',
            'title': 'Green Building Standards',
            'description': 'Consider implementing LEED/GRIHA standards for better sustainability score.',
            'priority': 'medium',
            'action': 'Add sustainability compliance'
        })
        
        return recommendations

    def _generate_general_recommendations(self):
        """Generate general AI recommendations"""
        return [
            {
                'type': 'process',
                'title': 'Digital Documentation',
                'description': 'Migrate to digital-first documentation for better efficiency and compliance tracking.',
                'priority': 'medium',
                'action': 'Setup digital workflows'
            },
            {
                'type': 'compliance',
                'title': 'Proactive Compliance',
                'description': 'Set up automated compliance reminders to avoid deadline misses.',
                'priority': 'high',
                'action': 'Configure compliance alerts'
            },
            {
                'type': 'innovation',
                'title': 'BIM Integration',
                'description': 'Consider Building Information Modeling for better project visualization and coordination.',
                'priority': 'low',
                'action': 'Explore BIM tools'
            }
        ]

    @http.route('/architect/api/compliance_check', type='json', auth='user')
    def automated_compliance_check(self, project_id, **kwargs):
        """Automated compliance checking for a project"""
        try:
            project = request.env['architect.project'].browse(project_id)
            if not project.exists():
                return {'success': False, 'error': 'Project not found'}

            compliance_items = request.env['architect.compliance'].search([
                ('project_id', '=', project_id)
            ])

            results = []
            for item in compliance_items:
                status = self._check_compliance_status(item)
                results.append({
                    'compliance_id': item.id,
                    'name': item.name,
                    'status': status['status'],
                    'message': status['message'],
                    'recommendations': status.get('recommendations', [])
                })

            return {
                'success': True,
                'results': results,
                'summary': self._generate_compliance_summary(results)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _check_compliance_status(self, compliance_item):
        """Check the status of a compliance item"""
        # This is a simplified version - in practice, this would integrate with external APIs
        # or use more sophisticated checking mechanisms
        
        days_to_deadline = (compliance_item.deadline - datetime.now().date()).days if compliance_item.deadline else None
        
        if compliance_item.state == 'approved':
            return {
                'status': 'compliant',
                'message': 'Compliance approved and up to date'
            }
        elif compliance_item.state == 'rejected':
            return {
                'status': 'non_compliant',
                'message': 'Compliance rejected - action required',
                'recommendations': ['Review rejection reasons', 'Prepare revised submission']
            }
        elif days_to_deadline and days_to_deadline <= 7:
            return {
                'status': 'urgent',
                'message': f'Deadline in {days_to_deadline} days - immediate action required',
                'recommendations': ['Prioritize this compliance item', 'Gather required documents']
            }
        elif days_to_deadline and days_to_deadline <= 30:
            return {
                'status': 'attention',
                'message': f'Deadline in {days_to_deadline} days - plan action',
                'recommendations': ['Schedule compliance activities', 'Review requirements']
            }
        else:
            return {
                'status': 'on_track',
                'message': 'Compliance on track'
            }

    def _generate_compliance_summary(self, results):
        """Generate summary of compliance check results"""
        total = len(results)
        compliant = len([r for r in results if r['status'] == 'compliant'])
        urgent = len([r for r in results if r['status'] == 'urgent'])
        non_compliant = len([r for r in results if r['status'] == 'non_compliant'])
        
        return {
            'total_items': total,
            'compliant': compliant,
            'urgent': urgent,
            'non_compliant': non_compliant,
            'compliance_rate': (compliant / total * 100) if total > 0 else 0
        }

    @http.route('/architect/parivesh/integration', type='http', auth='user')
    def parivesh_integration(self, **kwargs):
        """PARIVESH portal integration endpoint"""
        # This would handle PARIVESH portal integration
        # For now, redirect to PARIVESH website
        return request.redirect('https://parivesh.nic.in/')

    @http.route('/architect/api/rate_analysis', type='json', auth='user')
    def rate_analysis(self, estimation_id, **kwargs):
        """Perform rate analysis for estimation"""
        try:
            estimation = request.env['architect.estimation'].browse(estimation_id)
            if not estimation.exists():
                return {'success': False, 'error': 'Estimation not found'}

            analysis = {
                'total_variance': 0,
                'line_analysis': [],
                'recommendations': []
            }

            for line in estimation.estimation_line_ids:
                if line.rate_item_id.market_rate > 0:
                    variance = ((line.unit_rate - line.rate_item_id.market_rate) / line.rate_item_id.market_rate) * 100
                    analysis['line_analysis'].append({
                        'item': line.description,
                        'dsr_rate': line.unit_rate,
                        'market_rate': line.rate_item_id.market_rate,
                        'variance': variance,
                        'impact': line.total_amount * (variance / 100)
                    })

            # Generate recommendations based on analysis
            high_variance_items = [item for item in analysis['line_analysis'] if abs(item['variance']) > 20]
            if high_variance_items:
                analysis['recommendations'].append({
                    'type': 'cost_optimization',
                    'message': f'{len(high_variance_items)} items have significant rate variance. Consider market rate verification.',
                    'items': [item['item'] for item in high_variance_items[:3]]
                })

            return {
                'success': True,
                'analysis': analysis
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
