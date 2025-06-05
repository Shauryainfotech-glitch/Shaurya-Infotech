/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

class DashboardChart extends Component {
    static template = "day_plan_work_report_ai.DashboardChart";
    
    static props = {
        data: { type: Object },
        type: { type: String },
        style: { type: String, optional: true },
    };
    
    setup() {
        this.chart = null;
    }
    
    mounted() {
        this.renderChart();
    }
    
    willUnmount() {
        if (this.chart) {
            this.chart.destroy();
        }
    }
    
    renderChart() {
        const canvas = this.refs.chart;
        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if any
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Create new chart with provided data
        this.chart = new Chart(ctx, {
            type: this.props.type.replace(/'/g, ''),
            data: this.props.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });
    }
    
    willUpdateProps(nextProps) {
        return this.props.data !== nextProps.data;
    }
    
    willPatch() {
        if (this.chart) {
            this.chart.destroy();
        }
    }
    
    patched() {
        this.renderChart();
    }
}

class NewDashboardClientAction extends Component {
    static template = "day_plan_work_report_ai.NewProductivityDashboard";
    static components = { DashboardChart };
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.actionService = useService("action");
        
        this.state = useState({
            totalPlans: 0,
            plansChange: 0,
            completionRate: 0,
            productivityScore: 0,
            attentionItems: 0,
            chartData: null,
            pieChartData: null,
            lineChartData: null,
            radarChartData: null,
            loading: true
        });
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
        
        onMounted(() => {
            console.log("Dashboard mounted");
        });
    }
    
    async loadDashboardData() {
        try {
            this.state.loading = true;
            
            // Fetch dashboard data from the server
            const data = await this.orm.call(
                "day.plan.dashboard",
                "get_dashboard_data",
                []
            );
            
            // Update the state with fetched data
            this.state.totalPlans = data.total_plans || 0;
            this.state.plansChange = data.plans_change || 0;
            this.state.completionRate = data.completion_rate || 0;
            this.state.productivityScore = data.avg_productivity || 0;
            this.state.attentionItems = data.attention_items || 0;
            
            // Prepare chart data
            this.state.chartData = this.prepareChartData(data.productivity_trend || []);
            this.state.pieChartData = this.preparePieChartData(data.task_status || []);
            this.state.lineChartData = this.prepareLineChartData(data.daily_productivity || []);
            this.state.radarChartData = this.prepareRadarChartData(data.task_priority || []);
            
            this.state.loading = false;
        } catch (error) {
            this.notification.add(_t("Failed to refresh dashboard"), {
                type: "danger",
            });
            console.error("Error refreshing dashboard:", error);
            this.state.loading = false;
        }
    }
    
    async printDashboard() {
        try {
            const result = await this.orm.call(
                "day.plan.dashboard.clean",
                "action_print_dashboard",
                []
            );
            this.actionService.doAction(result);
        } catch (error) {
            this.notification.add(_t("Failed to print dashboard"), {
                type: "danger",
            });
            console.error("Error printing dashboard:", error);
        }
    }
    
    // Helper methods for chart data preparation
    prepareChartData(data) {
        return {
            labels: data.map(item => item.date),
            datasets: [{
                label: 'Productivity',
                data: data.map(item => item.value),
                borderColor: 'rgba(78, 115, 223, 1)',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                borderWidth: 2,
                fill: true,
            }]
        };
    }
    
    preparePieChartData(data) {
        return {
            labels: data.map(item => item.label),
            datasets: [{
                data: data.map(item => item.value),
                backgroundColor: [
                    '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'
                ],
            }]
        };
    }
    
    prepareLineChartData(data) {
        return {
            labels: data.map(item => item.date),
            datasets: [{
                label: 'Daily Productivity',
                data: data.map(item => item.value),
                backgroundColor: 'rgba(28, 200, 138, 0.8)',
            }]
        };
    }
    
    prepareRadarChartData(data) {
        return {
            labels: data.map(item => item.label),
            datasets: [{
                label: 'Task Priority',
                data: data.map(item => item.value),
                backgroundColor: 'rgba(54, 185, 204, 0.5)',
                borderColor: 'rgba(54, 185, 204, 1)',
                borderWidth: 1
            }]
        };
    }
}

// Register the action in the registry
registry.category("actions").add("day_plan_work_report_ai.new_dashboard_action", NewDashboardClientAction);
