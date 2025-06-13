/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { Component, useState, onMounted, useRef, onWillUnmount } from "@odoo/owl";
import { loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

class GuaranteedChartDashboard extends Component {
    static template = 'day_plan_work_report_ai.GuaranteedChartDashboard';
    static components = { Layout };

    setup() {
        this.notification = useService("notification");
        this.actionService = useService("action");

        this.state = useState({
            loading: true,
            error: null,
            chartData: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Productivity Score',
                    data: [65, 70, 75, 80, 75, 68, 72],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    fill: false
                }]
            }
        });

        // Chart references
        this.lineChartRef = useRef("lineChart");
        this.pieChartRef = useRef("pieChart");
        this.barChartRef = useRef("barChart");

        // Chart instances
        this.lineChart = null;
        this.pieChart = null;
        this.barChart = null;

        onMounted(async () => {
            try {
                console.log("GuaranteedChartDashboard mounted");
                await this._loadChartJS();
                await this._initializeCharts();
                this.state.loading = false;
            } catch (error) {
                console.error("Failed to initialize dashboard:", error);
                this.state.error = error.message || "Failed to load dashboard";
                this.state.loading = false;
            }
        });

        onWillUnmount(() => {
            this._destroyCharts();
        });
    }

    async _loadChartJS() {
        if (typeof Chart !== 'undefined') {
            console.log("Chart.js already loaded");
            return Promise.resolve();
        }

        console.log("Loading Chart.js...");
        try {
            // Try loading from Odoo's static assets first
            await loadJS("/web/static/lib/Chart/Chart.js");
        } catch (error) {
            console.log("Fallback to CDN Chart.js");
            await loadJS("https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js");
        }
    }

    async _initializeCharts() {
        console.log("Initializing charts...");

        // Wait a bit for DOM to be ready
        await new Promise(resolve => setTimeout(resolve, 100));

        try {
            await this._renderLineChart();
            await this._renderPieChart();
            await this._renderBarChart();
        } catch (error) {
            console.error("Error rendering charts:", error);
            throw error;
        }
    }

    async _renderLineChart() {
        if (!this.lineChartRef.el) {
            console.error("Line chart canvas element not found");
            return;
        }

        const ctx = this.lineChartRef.el.getContext('2d');
        if (!ctx) {
            console.error("Failed to get 2D context for line chart");
            return;
        }

        this.lineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
                datasets: [{
                    label: 'Productivity Trend',
                    data: [65, 70, 75, 80, 82, 85],
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Target',
                    data: [70, 70, 70, 70, 70, 70],
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Weekly Productivity Analysis'
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

        console.log("Line chart created successfully");
    }

    async _renderPieChart() {
        if (!this.pieChartRef.el) {
            console.error("Pie chart canvas element not found");
            return;
        }

        const ctx = this.pieChartRef.el.getContext('2d');
        if (!ctx) {
            console.error("Failed to get 2D context for pie chart");
            return;
        }

        this.pieChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Pending', 'Cancelled'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(23, 162, 184, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(23, 162, 184, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Task Status Distribution'
                    },
                }
            }
        });

        console.log("Pie chart created successfully");
    }

    async _renderBarChart() {
        if (!this.barChartRef.el) {
            console.error("Bar chart canvas element not found");
            return;
        }

        const ctx = this.barChartRef.el.getContext('2d');
        if (!ctx) {
            console.error("Failed to get 2D context for bar chart");
            return;
        }

        this.barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Tasks Completed',
                    data: [12, 15, 18, 20],
                    backgroundColor: 'rgba(40, 167, 69, 0.6)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 1
                }, {
                    label: 'Tasks Created',
                    data: [15, 18, 22, 25],
                    backgroundColor: 'rgba(23, 162, 184, 0.6)',
                    borderColor: 'rgba(23, 162, 184, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Monthly Task Overview'
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        console.log("Bar chart created successfully");
    }

    _destroyCharts() {
        if (this.lineChart) {
            this.lineChart.destroy();
            this.lineChart = null;
        }
        if (this.pieChart) {
            this.pieChart.destroy();
            this.pieChart = null;
        }
        if (this.barChart) {
            this.barChart.destroy();
            this.barChart = null;
        }
    }

    async refreshDashboard() {
        try {
            this.state.loading = true;
            this.state.error = null;

            // Destroy existing charts
            this._destroyCharts();

            // Simulate data refresh delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Re-initialize charts
            await this._initializeCharts();

            this.notification.add("Dashboard refreshed successfully", {
                type: "success",
            });
        } catch (error) {
            this.state.error = "Failed to refresh dashboard";
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
            // Simple print functionality
            window.print();

            this.notification.add("Print dialog opened", {
                type: "info",
            });
        } catch (error) {
            this.notification.add("Failed to print dashboard", {
                type: "danger",
            });
            console.error("Error printing dashboard:", error);
        }
    }
}

// Register the client action
registry.category("actions").add("day_plan_work_report_ai.guaranteed_chart_dashboard", GuaranteedChartDashboard);

export { GuaranteedChartDashboard };