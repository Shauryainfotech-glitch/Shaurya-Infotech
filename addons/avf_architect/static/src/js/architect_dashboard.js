
/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class ArchitectDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            projects: {
                total: 0,
                active: 0,
                completed: 0,
                overdue: 0
            },
            compliance: {
                pending: 0,
                approved: 0,
                rejected: 0,
                overdue: 0
            },
            dpr: {
                draft: 0,
                under_review: 0,
                approved: 0
            },
            recent_projects: [],
            pending_approvals: [],
            ai_insights: []
        });

        onMounted(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            // Load project statistics
            const projectStats = await this.orm.call(
                "architect.project",
                "get_dashboard_stats",
                []
            );
            
            // Load compliance statistics
            const complianceStats = await this.orm.call(
                "architect.compliance",
                "get_dashboard_stats",
                []
            );
            
            // Load DPR statistics
            const dprStats = await this.orm.call(
                "architect.dpr",
                "get_dashboard_stats",
                []
            );
            
            // Load recent projects
            const recentProjects = await this.orm.searchRead(
                "architect.project",
                [],
                ["name", "code", "partner_id", "progress", "state"],
                { limit: 5, order: "create_date desc" }
            );
            
            // Load pending approvals
            const pendingApprovals = await this.orm.searchRead(
                "architect.compliance",
                [["state", "=", "submitted"]],
                ["name", "project_id", "deadline"],
                { limit: 5, order: "deadline asc" }
            );

            this.state.projects = projectStats;
            this.state.compliance = complianceStats;
            this.state.dpr = dprStats;
            this.state.recent_projects = recentProjects;
            this.state.pending_approvals = pendingApprovals;
            this.state.ai_insights = await this.generateAIInsights();
            
        } catch (error) {
            console.error("Error loading dashboard data:", error);
        }
    }

    async generateAIInsights() {
        // Placeholder for AI insights generation
        return [
            {
                type: "recommendation",
                title: "Energy Efficiency Opportunity",
                message: "Consider implementing renewable energy solutions in upcoming projects to improve sustainability scores.",
                priority: "medium"
            },
            {
                type: "alert",
                title: "Compliance Deadline Approaching",
                message: "3 compliance items are due within the next 7 days. Review and take action.",
                priority: "high"
            },
            {
                type: "insight",
                title: "Project Performance",
                message: "Projects are running 5% ahead of schedule on average this quarter.",
                priority: "low"
            }
        ];
    }

    openProjectKanban() {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: "Projects",
            res_model: "architect.project",
            view_mode: "kanban,tree,form",
            views: [[false, "kanban"], [false, "tree"], [false, "form"]],
        });
    }

    openComplianceList() {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: "Compliance Tracking",
            res_model: "architect.compliance",
            view_mode: "tree,form",
            domain: [["state", "!=", "approved"]],
        });
    }

    openDPRList() {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: "DPR Management",
            res_model: "architect.dpr",
            view_mode: "tree,form",
        });
    }

    async refreshDashboard() {
        await this.loadDashboardData();
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount);
    }

    getProgressBarClass(progress) {
        if (progress < 30) return "bg-danger";
        if (progress < 70) return "bg-warning";
        return "bg-success";
    }

    getPriorityClass(priority) {
        const classes = {
            low: "text-info",
            medium: "text-warning",
            high: "text-danger"
        };
        return classes[priority] || "text-muted";
    }

    getInsightIcon(type) {
        const icons = {
            recommendation: "fa-lightbulb-o",
            alert: "fa-exclamation-triangle",
            insight: "fa-bar-chart"
        };
        return icons[type] || "fa-info-circle";
    }
}

ArchitectDashboard.template = "avf_architect.DashboardTemplate";

registry.category("actions").add("architect_dashboard", ArchitectDashboard);

export default ArchitectDashboard;
