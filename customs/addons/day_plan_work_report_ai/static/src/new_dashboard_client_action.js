/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { Component, useState, useRef, onMounted, onWillStart, onPatched } from "@odoo/owl";

/**
 * Chart Component - NO TEMPLATE REGISTRATION HERE
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
            // Ensure Chart.js is available
            if (!window.Chart) {
                console.error("Chart.js not loaded");
                throw new Error("Chart.js library not available");
            }
        });

        onMounted(() => {
            // Add delay to ensure DOM is ready
            setTimeout(() => this.renderChart(), 100);
        });

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
                try {
                    chartData = JSON.parse(this.props.data);
                } catch (e) {
                    console.error("Invalid chart data JSON:", e);
                    return;
                }
            } else {
                chartData = this.props.data || this.getDefaultData();
            }

            // Default options
            const options = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    }
                }
            };

            // Create chart
            this.chart = new window.Chart(ctx, {
                type: this.props.type || "bar",
                data: chartData,
                options: options,
            });

            console.log("Chart rendered successfully:", this.props.type);
        } catch (error) {
            console.error("Error rendering chart:", error);
        }
    }

    getDefaultData() {
        return {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            datasets: [{
                label: 'Sample Data',
                data: [12, 19, 3, 5, 2],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        };
    }

    updateChart() {
        if (this.chart) {
            this.chart.destroy();
            setTimeout(() => this.renderChart(), 50);
        }
    }

    willUnmount() {
        if (this.chart) {
            this.chart.destroy();
        }
    }
}

/**
 * Main Dashboard Client Action
 */
export class ProductivityDashboard extends Component {
    static template = "day_plan_work_report_ai.NewProductivityDashboard";
    static components = { DashboardChart };
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
        updateActionState: { type: Function, optional: true },
    };

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
            chartData: JSON.stringify(this.getDefaultChartData()),
            pieChartData: JSON.stringify(this.getDefaultPieData()),
            lineChartData: JSON.stringify(this.getDefaultLineData()),
            loading: true,
            error: null
        });

        onMounted(() => {
            // Add small delay to ensure all components are ready
            setTimeout(() => this.loadDashboardData(), 200);
        });
    }

    getDefaultChartData() {
        return {
            labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            datasets: [{
                label: 'Tasks Completed',
                data: [5, 8, 6, 9, 7],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2
            }]
        };
    }

    getDefaultPieData() {
        return {
            labels: ['Completed', 'In Progress', 'Pending'],
            datasets: [{
                data: [60, 30, 10],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ]
            }]
        };
    }

    getDefaultLineData() {
        return {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Productivity Score',
                data: [65, 75, 80, 85],
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4
            }]
        };
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            this.state.error = null;

            console.log("Starting dashboard data load");

            // Load dashboard data
            const dashboardData = await this.orm.call(
                "day.plan.dashboard",
                "get_dashboard_data",
                [],
                { context: {} }
            );

            if (dashboardData) {
                // Update state with real data
                Object.assign(this.state, {
                    totalPlans: dashboardData.total_plans || 0,
                    completionRate: dashboardData.completion_rate || 0,
                    productivityScore: dashboardData.productivity_score || 0,
                    attentionItems: dashboardData.attention_items || 0,
                    chartData: JSON.stringify(dashboardData.chart_data || this.getDefaultChartData()),
                    pieChartData: JSON.stringify(dashboardData.pie_chart_data || this.getDefaultPieData()),
                    lineChartData: JSON.stringify(dashboardData.line_chart_data || this.getDefaultLineData()),
                });
            }

            console.log("Dashboard data loaded successfully");

        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.error = "Error loading dashboard data: " + error.message;
            this.notification.add(_t("Failed to load dashboard data"), {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }

    async refreshDashboard() {
        await this.loadDashboardData();
        this.notification.add(_t("Dashboard refreshed successfully"), {
            type: "success",
        });
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

// Register the action - SINGLE REGISTRATION
registry.category("actions").add("day_plan_work_report_ai.dashboard_action", {
    Component: ProductivityDashboard,
});