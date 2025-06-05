/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { Component, useState, useRef, onMounted, onWillStart, onPatched } from "@odoo/owl";

/**
 * Chart Component
 */
class DashboardChart extends Component {
    static template = "day_plan_work_report_ai.DashboardChart";
    static props = {
        data: { type: String, optional: true },
        type: { type: String, optional: true },
        style: { type: String, optional: true },
    };

    setup() {
        this.chartRef = useRef("chart");
        this.chart = null;
        
        onWillStart(async () => {
            // Chart.js is now loaded from local assets
            console.log("Using local Chart.js from assets");
        });
        
        onMounted(() => this.renderChart());
        onPatched(() => this.updateChart());
    }
    
    renderChart() {
        if (!window.Chart) {
            console.error("Chart.js not loaded");
            return;
        }
        
        if (!this.chartRef.el) {
            console.error("Chart canvas element not found");
            return;
        }
        
        try {
            const ctx = this.chartRef.el.getContext("2d");
            let chartData;
            
            // Parse data if it's a string
            if (typeof this.props.data === "string") {
                chartData = JSON.parse(this.props.data);
            } else {
                chartData = this.props.data;
            }
            
            // Default options
            const options = {
                responsive: true,
                maintainAspectRatio: false,
            };
            
            // Create chart
            this.chart = new window.Chart(ctx, {
                type: this.props.type || "bar",
                data: chartData,
                options: options,
            });
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
 * Main Dashboard Client Action
 */
export class DashboardClientAction extends Component {
    static template = "day_plan_work_report_ai.ProductivityDashboard";
    static components = { DashboardChart };
    static props = {
        // Standard Odoo client action props
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
        updateActionState: { type: Function, optional: true },
        // Any additional props specific to this component
        message: { type: String, optional: true }
    }
    
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
        
        onMounted(() => this.loadDashboardData());
    }
    
    async loadDashboardData() {
        try {
            this.state.loading = true;
            console.log("Starting dashboard data load");
            
            // First, ensure a dashboard record exists
            try {
                console.log("Ensuring dashboard exists...");
                await this.orm.call(
                    "day.plan.dashboard.clean",
                    "_ensure_dashboard_exists",
                    []
                );
            } catch (e) {
                console.error("Failed to ensure dashboard exists:", e);
            }
            
            // Now try to get the dashboard data
            console.log("Fetching dashboard data...");
            const dashboardData = await this.orm.call(
                "day.plan.dashboard.clean",
                "_get_default_dashboard",
                []
            );
            
            console.log("Got dashboard record:", dashboardData);
            
            if (dashboardData && dashboardData.id) {
                // Get the computed data fields
                const dashboardFields = await this.orm.read(
                    "day.plan.dashboard.clean", 
                    [dashboardData.id],
                    [
                        "total_plans", "plans_change", "completion_rate", 
                        "productivity_score", "attention_items",
                        "chart_data", "pie_chart_data", "line_chart_data", "radar_chart_data"
                    ]
                );
                
                console.log("Dashboard data received:", dashboardFields);
                
                if (dashboardFields && dashboardFields.length > 0) {
                    const data = dashboardFields[0];
                    
                    this.state.totalPlans = data.total_plans || 0;
                    this.state.plansChange = data.plans_change || 0;
                    this.state.completionRate = data.completion_rate || 0;
                    this.state.productivityScore = data.productivity_score || 0;
                    this.state.attentionItems = data.attention_items || 0;
                    
                    // Parse JSON strings if they exist
                    try {
                        this.state.chartData = data.chart_data ? JSON.parse(data.chart_data) : null;
                        this.state.pieChartData = data.pie_chart_data ? JSON.parse(data.pie_chart_data) : null;
                        this.state.lineChartData = data.line_chart_data ? JSON.parse(data.line_chart_data) : null;
                        this.state.radarChartData = data.radar_chart_data ? JSON.parse(data.radar_chart_data) : null;
                        console.log("Chart data parsed successfully");
                    } catch (parseError) {
                        console.error("Error parsing chart data:", parseError);
                        this.state.error = "Error parsing chart data: " + parseError.message;
                    }
                    
                    console.log("Dashboard data loaded successfully");
                } else {
                    console.error("No dashboard field data found");
                    this.state.error = "No dashboard field data found";
                }
            } else {
                console.error("No dashboard data found");
                this.state.error = "No dashboard data found";
            }
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.error = `Error loading dashboard data: ${error.name}`;
        } finally {
            this.state.loading = false;
        }
    }
    
    async refreshDashboard() {
        try {
            await this.orm.call(
                "day.plan.dashboard.clean",
                "action_refresh_dashboard",
                []
            );
            this.notification.add(_t("Dashboard refreshed successfully"), {
                type: "success",
            });
            
            // Reload dashboard data
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
}

// Register client action
registry.category("actions").add("day_plan_work_report_ai.dashboard_action", DashboardClientAction);
