/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

class GuaranteedChartDashboard extends Component {
    static template = "day_plan_work_report_ai.GuaranteedChartDashboard";
    static components = { Layout };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.actionService = useService("action");

        this.state = useState({
            loading: true,
            error: null,
            chartData: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Productivity',
                    data: [65, 70, 75, 80, 75, 68, 72],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
            pieChartData: {
                labels: ['Completed', 'In Progress', 'Pending', 'Cancelled'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: [
                        '#28a745',
                        '#ffc107',
                        '#17a2b8',
                        '#dc3545'
                    ],
                    borderWidth: 2
                }]
            },
            barChartData: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Tasks Completed',
                    data: [12, 19, 15, 25],
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            }
        });

        this.chartRefs = {
            line: useRef("lineChart"),
            pie: useRef("pieChart"),
            bar: useRef("barChart")
        };

        this.charts = {};

        onMounted(async () => {
            try {
                console.log("GuaranteedChartDashboard mounted");
                await this._loadChartJS();
                await this._loadDashboardData();
                this._renderAllCharts();
                this.state.loading = false;
            } catch (error) {
                console.error("Failed to initialize dashboard:", error);
                this.state.error = error.message;
                this.state.loading = false;
            }
        });
    }

    async _loadChartJS() {
        if (typeof Chart !== 'undefined') {
            console.log("Chart.js already loaded");
            return Promise.resolve();
        }

        console.log("Loading Chart.js...");
        return loadJS("/web/static/lib/Chart/Chart.js");
    }

    async _loadDashboardData() {
        try {
            console.log("Loading dashboard data...");

            // Call the backend to get real data
            const result = await this.orm.call(
                "day.plan.dashboard.clean",
                "_get_default_dashboard",
                []
            );

            if (result && result.chart_data) {
                // Parse the chart data from backend
                const chartData = JSON.parse(result.chart_data);
                if (chartData.line_chart) {
                    this.state.chartData = chartData.line_chart;
                }
                if (chartData.pie_chart) {
                    this.state.pieChartData = chartData.pie_chart;
                }
                if (chartData.bar_chart) {
                    this.state.barChartData = chartData.bar_chart;
                }
            }

            console.log("Dashboard data loaded successfully");
        } catch (error) {
            console.log("Using default chart data:", error.message);
            // Continue with default data if backend call fails
        }
    }

    _renderAllCharts() {
        console.log("Rendering all charts...");

        // Render Line Chart
        this._renderChart('line', this.state.chartData, {
            type: 'line',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Weekly Productivity Trend'
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        // Render Pie Chart
        this._renderChart('pie', this.state.pieChartData, {
            type: 'pie',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Task Distribution'
                    },
                }
            }
        });

        // Render Bar Chart
        this._renderChart('bar', this.state.barChartData, {
            type: 'bar',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Monthly Performance'
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    _renderChart(type, data, config) {
        const chartRef = this.chartRefs[type];

        if (!chartRef.el) {
            console.error(`Chart canvas element not found for ${type} chart`);
            return;
        }

        const ctx = chartRef.el.getContext('2d');
        if (!ctx) {
            console.error(`Failed to get 2D context for ${type} chart`);
            return;
        }

        // Destroy existing chart if it exists
        if (this.charts[type]) {
            this.charts[type].destroy();
        }

        console.log(`Creating ${type} chart with data:`, data);

        this.charts[type] = new Chart(ctx, {
            ...config,
            data: data
        });

        console.log(`${type} chart created successfully`);
    }

    async refreshDashboard() {
        try {
            this.state.loading = true;
            await this._loadDashboardData();
            this._renderAllCharts();

            this.notification.add("Dashboard refreshed successfully", {
                type: "success",
            });
        } catch (error) {
            this.notification.add("Failed to refresh dashboard", {
                type: "danger",
            });
            console.error("Error refreshing dashboard:", error);
        } finally {
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
            this.notification.add("Failed to print dashboard", {
                type: "danger",
            });
            console.error("Error printing dashboard:", error);
        }
    }
}

// Register the client action - FIXED: Register component directly
registry.category("actions").add("day_plan_work_report_ai.guaranteed_chart_dashboard", GuaranteedChartDashboard);

export { GuaranteedChartDashboard };