/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { Component, useState, useRef, onMounted, onWillStart, onPatched } from "@odoo/owl";

/**
 * Chart.js Dashboard Graph Component
 * Renders various chart types based on provided data
 */
export class DashboardGraph extends Component {
    static template = "day_plan_work_report_ai.DashboardGraph";
    static props = {
        data: { type: String, optional: true },
        graphType: { type: String, optional: true },
        style: { type: String, optional: true },
    };

    setup() {
        this.chartRef = useRef("chart");
        this.chart = null;

        onWillStart(async () => {
            try {
                await loadJS("https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js");
                console.log("Chart.js loaded successfully");
            } catch (error) {
                console.error("Error loading Chart.js:", error);
            }
        });

        onMounted(() => this.renderChart());
        onPatched(() => this.updateChart());
    }

    renderChart() {
        if (!window.Chart) {
            console.log("Cannot render chart: Chart.js not loaded");
            return;
        }
        
        // Make sure the element is in the DOM
        if (!this.chartRef.el) {
            console.log("Chart canvas element not found");
            return;
        }
        
        const ctx = this.chartRef.el.getContext("2d");
        let chartData = {};
        let chartOptions = {};
        
        try {
            // Parse chart data if it's a string
            if (typeof this.props.data === 'string') {
                chartData = JSON.parse(this.props.data);
            } else if (typeof this.props.data === 'object') {
                chartData = this.props.data;
            }
            
            // Default chart type is bar
            const graphType = this.props.graphType || 'bar';
            
            // Configure chart options based on type
            switch (graphType) {
                case 'pie':
                    chartOptions = {
                        plugins: {
                            legend: { position: 'right' }
                        },
                        maintainAspectRatio: false,
                        responsive: true
                    };
                    break;
                case 'bar':
                    chartOptions = {
                        plugins: {
                            legend: { position: 'top' }
                        },
                        scales: {
                            y: { beginAtZero: true }
                        },
                        maintainAspectRatio: false,
                        responsive: true
                    };
                    break;
                case 'line':
                    chartOptions = {
                        plugins: {
                            legend: { position: 'top' }
                        },
                        scales: {
                            y: { beginAtZero: true }
                        },
                        maintainAspectRatio: false,
                        responsive: true
                    };
                    break;
                case 'radar':
                    chartOptions = {
                        plugins: {
                            legend: { position: 'top' }
                        },
                        scales: {
                            r: {
                                min: 0,
                                max: 100,
                                ticks: { stepSize: 20 }
                            }
                        },
                        maintainAspectRatio: false,
                        responsive: true
                    };
                    break;
                default:
                    chartOptions = {
                        maintainAspectRatio: false,
                        responsive: true
                    };
            }
            
            // Create the chart
            this.chart = new window.Chart(ctx, {
                type: graphType,
                data: chartData,
                options: chartOptions
            });
            
            console.log(`${graphType} chart rendered successfully`);
        } catch (error) {
            console.error("Error rendering chart:", error);
        }
    }
    
    updateChart() {
        if (this.chart) {
            this.chart.destroy();
            this.renderChart();
        }
    }
}

/**
 * Main Dashboard Component
 * Displays the productivity dashboard with charts and KPIs
 */
export class ProductivityDashboard extends Component {
    static template = "day_plan_work_report_ai.ProductivityDashboard";
    static components = { DashboardGraph };

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
            loading: true,
            error: null
        });

        // Load dashboard data on component mount
        onMounted(() => this.loadDashboardData());
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            // Get dashboard data from the server
            const dashboardData = await this.orm.searchRead(
                "day.plan.dashboard",
                [],
                [
                    "total_plans", "plans_change", "completion_rate", 
                    "productivity_score", "attention_items",
                    "chart_data", "pie_chart_data", "line_chart_data", "radar_chart_data"
                ],
                { limit: 1 }
            );
            
            if (dashboardData && dashboardData.length > 0) {
                const data = dashboardData[0];
                
                // Update state with the retrieved data
                this.state.totalPlans = data.total_plans || 0;
                this.state.plansChange = data.plans_change || 0;
                this.state.completionRate = data.completion_rate || 0;
                this.state.productivityScore = data.productivity_score || 0;
                this.state.attentionItems = data.attention_items || 0;
                
                // Set chart data
                this.state.chartData = data.chart_data || null;
                this.state.pieChartData = data.pie_chart_data || null;
                this.state.lineChartData = data.line_chart_data || null;
                this.state.radarChartData = data.radar_chart_data || null;
                
                console.log("Dashboard data loaded successfully");
            } else {
                console.error("No dashboard data found");
                this.state.error = "No dashboard data found";
            }
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.error = "Error loading dashboard data";
            this.notification.add(_t("Failed to load dashboard data"), {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }
    
    async refreshDashboard() {
        try {
            await this.orm.call(
                "day.plan.dashboard",
                "action_refresh_dashboard",
                []
            );
            this.notification.add(_t("Dashboard refreshed successfully"), {
                type: "success",
            });
            
            // Reload the dashboard data
            await this.loadDashboardData();
        } catch (error) {
            this.notification.add(_t("Failed to refresh dashboard"), {
                type: "danger",
            });
            console.error("Error refreshing dashboard:", error);
        }
    }
    
    async printDashboard() {
        try {
            const result = await this.orm.call(
                "day.plan.dashboard",
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
}

// Register the Owl templates
registry.category("view_templates").add("day_plan_work_report_ai.DashboardGraph", `
    <div class="chart-container" t-att-style="props.style || 'height: 300px;'">
        <canvas t-ref="chart"/>
    </div>
`);

// Register the client action directly
registry.category("actions").add("day_plan_work_report_ai.dashboard_action", ProductivityDashboard);
