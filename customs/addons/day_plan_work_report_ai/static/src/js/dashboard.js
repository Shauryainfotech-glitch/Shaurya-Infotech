// /** @odoo-module **/
//
// import { registry } from '@web/core/registry';
// import { Component, useState, onMounted, useRef } from "@odoo/owl";
//
// class ProductivityDashboard extends Component {
//     setup() {
//         this.state = useState({
//             loading: true,
//             stats: {
//                 total_plans: 0,
//                 plans_today: 0,
//                 completed_plans: 0,
//                 pending_tasks: 0,
//                 completion_rate: 0,
//                 productivity_score: 0,
//                 efficiency_rating: 0,
//                 wellbeing_assessment: 0,
//                 plans_change: 0,
//                 tasks_change: 0,
//                 tasks_due_today: 0,
//                 overdue_tasks: 0,
//                 attention_items: 0,
//             },
//             charts: {}
//         });
//
//         this.chartRefs = {
//             productivity: useRef("productivity-chart"),
//             tasks: useRef("tasks-chart"),
//             completion: useRef("completion-chart")
//         };
//
//         this.rpc = this.env.services.rpc;
//
//         onMounted(() => {
//             this._loadData();
//         });
//     }
//
//     async _loadData() {
//         this.state.loading = true;
//         try {
//             const data = await this.rpc('/day_plan_work_report_ai/dashboard_data');
//             this.state.stats = data.kpis;
//             this.state.loading = false;
//             this._renderCharts(data.charts);
//         } catch (error) {
//             console.error("Error loading dashboard data:", error);
//             this.state.loading = false;
//         }
//     }
//
//     _renderCharts(chartData) {
//         if (!window.Chart) {
//             // Load Chart.js dynamically
//             const script = document.createElement('script');
//             script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
//             script.onload = () => {
//                 this._initCharts(chartData);
//             };
//             document.head.appendChild(script);
//         } else {
//             this._initCharts(chartData);
//         }
//     }
//
//     _initCharts(chartData) {
//         // Productivity Chart
//         if (this.chartRefs.productivity.el) {
//             new window.Chart(this.chartRefs.productivity.el.getContext('2d'), {
//                 type: 'line',
//                 data: chartData.productivity || {
//                     labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
//                     datasets: [{
//                         label: 'Productivity',
//                         data: [65, 78, 66, 74, 63, 40, 55],
//                         fill: false,
//                         borderColor: 'rgb(75, 192, 192)',
//                         tension: 0.1
//                     }]
//                 },
//                 options: {
//                     responsive: true,
//                     maintainAspectRatio: false,
//                 }
//             });
//         }
//
//         // Tasks Chart
//         if (this.chartRefs.tasks.el) {
//             new window.Chart(this.chartRefs.tasks.el.getContext('2d'), {
//                 type: 'bar',
//                 data: chartData.tasks || {
//                     labels: ['Planning', 'Development', 'Design', 'Meetings', 'Admin'],
//                     datasets: [{
//                         label: 'Tasks Completed',
//                         data: [12, 19, 8, 15, 10],
//                         backgroundColor: [
//                             'rgba(255, 99, 132, 0.2)',
//                             'rgba(54, 162, 235, 0.2)',
//                             'rgba(255, 206, 86, 0.2)',
//                             'rgba(75, 192, 192, 0.2)',
//                             'rgba(153, 102, 255, 0.2)'
//                         ],
//                         borderColor: [
//                             'rgba(255, 99, 132, 1)',
//                             'rgba(54, 162, 235, 1)',
//                             'rgba(255, 206, 86, 1)',
//                             'rgba(75, 192, 192, 1)',
//                             'rgba(153, 102, 255, 1)'
//                         ],
//                         borderWidth: 1
//                     }]
//                 },
//                 options: {
//                     responsive: true,
//                     maintainAspectRatio: false,
//                     scales: {
//                         y: {
//                             beginAtZero: true
//                         }
//                     }
//                 }
//             });
//         }
//
//         // Completion Chart
//         if (this.chartRefs.completion.el) {
//             new window.Chart(this.chartRefs.completion.el.getContext('2d'), {
//                 type: 'doughnut',
//                 data: chartData.completion || {
//                     labels: ['Completed', 'In Progress', 'Not Started'],
//                     datasets: [{
//                         data: [70, 15, 15],
//                         backgroundColor: [
//                             'rgba(75, 192, 192, 0.2)',
//                             'rgba(255, 206, 86, 0.2)',
//                             'rgba(255, 99, 132, 0.2)'
//                         ],
//                         borderColor: [
//                             'rgba(75, 192, 192, 1)',
//                             'rgba(255, 206, 86, 1)',
//                             'rgba(255, 99, 132, 1)'
//                         ],
//                         borderWidth: 1
//                     }]
//                 },
//                 options: {
//                     responsive: true,
//                     maintainAspectRatio: false
//                 }
//             });
//         }
//     }
// }
//
// ProductivityDashboard.template = 'day_plan_work_report_ai.ProductivityDashboard';
//
// registry.category("actions").add("day_plan_work_report_ai.productivity_dashboard", {
//     Component: ProductivityDashboard,
//     target: 'main_component',
//     actionInfo: {
//         type: 'ir.actions.client',
//         tag: 'day_plan_work_report_ai.productivity_dashboard',
//     }
// });
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { Component, useState, useRef, onMounted, onWillStart, onWillUnmount } from "@odoo/owl";

/**
 * Chart.js Dashboard Graph Component
 * Renders various chart types based on provided data
 */
export class DashboardGraph extends Component {
    static template = "day_plan_work_report_ai.DashboardGraph";
    static props = {
        data: { type: [Object, String], optional: true },
        graphType: { type: String, optional: true },
        style: { type: String, optional: true },
        title: { type: String, optional: true },
    };

    setup() {
        this.chartRef = useRef("chart");
        this.chart = null;
        this.chartLoaded = false;

        onWillStart(async () => {
            await this.loadChartJS();
        });

        onMounted(() => {
            this.renderChart();
        });

        onWillUnmount(() => {
            this.destroyChart();
        });
    }

    async loadChartJS() {
        if (window.Chart) {
            this.chartLoaded = true;
            return;
        }

        try {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js");
            this.chartLoaded = true;
            console.log("Chart.js loaded successfully");
        } catch (error) {
            console.error("Error loading Chart.js:", error);
            this.chartLoaded = false;
        }
    }

    renderChart() {
        if (!this.chartLoaded || !window.Chart) {
            console.warn("Chart.js not loaded, cannot render chart");
            return;
        }

        if (!this.chartRef.el) {
            console.warn("Chart canvas element not found");
            return;
        }

        this.destroyChart(); // Clean up existing chart

        const ctx = this.chartRef.el.getContext("2d");
        let chartData = this.getChartData();
        let chartOptions = this.getChartOptions();

        if (!chartData || !chartData.labels || !chartData.datasets) {
            console.warn("Invalid chart data provided");
            return;
        }

        try {
            this.chart = new window.Chart(ctx, {
                type: this.props.graphType || 'bar',
                data: chartData,
                options: chartOptions
            });

            console.log(`${this.props.graphType || 'bar'} chart rendered successfully`);
        } catch (error) {
            console.error("Error rendering chart:", error);
        }
    }

    getChartData() {
        if (!this.props.data) {
            return this.getDefaultChartData();
        }

        try {
            if (typeof this.props.data === 'string') {
                return JSON.parse(this.props.data);
            } else if (typeof this.props.data === 'object') {
                return this.props.data;
            }
        } catch (error) {
            console.error("Error parsing chart data:", error);
            return this.getDefaultChartData();
        }

        return this.getDefaultChartData();
    }

    getDefaultChartData() {
        return {
            labels: ['No Data'],
            datasets: [{
                label: 'No Data Available',
                data: [0],
                backgroundColor: ['#e9ecef'],
                borderColor: ['#dee2e6'],
                borderWidth: 1
            }]
        };
    }

    getChartOptions() {
        const graphType = this.props.graphType || 'bar';

        const baseOptions = {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                title: {
                    display: !!this.props.title,
                    text: this.props.title || ''
                }
            }
        };

        switch (graphType) {
            case 'pie':
            case 'doughnut':
                return {
                    ...baseOptions,
                    plugins: {
                        ...baseOptions.plugins,
                        legend: { position: 'right' }
                    }
                };
            case 'bar':
            case 'line':
                return {
                    ...baseOptions,
                    plugins: {
                        ...baseOptions.plugins,
                        legend: { position: 'top' }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                };
            case 'radar':
                return {
                    ...baseOptions,
                    plugins: {
                        ...baseOptions.plugins,
                        legend: { position: 'top' }
                    },
                    scales: {
                        r: {
                            min: 0,
                            max: 100,
                            ticks: { stepSize: 20 }
                        }
                    }
                };
            default:
                return baseOptions;
        }
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
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

        onMounted(() => {
            this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            this.state.error = null;

            // Check if the model exists first
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
                this.updateStateWithData(dashboardData[0]);
                console.log("Dashboard data loaded successfully");
            } else {
                // Load default/sample data if no dashboard record exists
                this.loadDefaultData();
                console.log("No dashboard data found, using defaults");
            }
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.error = "Error loading dashboard data";
            this.loadDefaultData();

            this.notification.add(_t("Failed to load dashboard data"), {
                type: "warning",
            });
        } finally {
            this.state.loading = false;
        }
    }

    updateStateWithData(data) {
        this.state.totalPlans = data.total_plans || 0;
        this.state.plansChange = data.plans_change || 0;
        this.state.completionRate = data.completion_rate || 0;
        this.state.productivityScore = data.productivity_score || 0;
        this.state.attentionItems = data.attention_items || 0;

        this.state.chartData = this.parseChartData(data.chart_data);
        this.state.pieChartData = this.parseChartData(data.pie_chart_data);
        this.state.lineChartData = this.parseChartData(data.line_chart_data);
        this.state.radarChartData = this.parseChartData(data.radar_chart_data);
    }

    parseChartData(data) {
        if (!data) return null;
        try {
            return typeof data === 'string' ? JSON.parse(data) : data;
        } catch (error) {
            console.error("Error parsing chart data:", error);
            return null;
        }
    }

    loadDefaultData() {
        this.state.totalPlans = 12;
        this.state.plansChange = 5;
        this.state.completionRate = 78;
        this.state.productivityScore = 85;
        this.state.attentionItems = 3;

        // Sample chart data
        this.state.chartData = {
            labels: ['Completed', 'In Progress', 'Pending'],
            datasets: [{
                label: 'Tasks Status',
                data: [12, 5, 3],
                backgroundColor: ['#28a745', '#ffc107', '#dc3545']
            }]
        };

        this.state.pieChartData = {
            labels: ['High Priority', 'Medium Priority', 'Low Priority'],
            datasets: [{
                data: [8, 7, 5],
                backgroundColor: ['#dc3545', '#ffc107', '#28a745']
            }]
        };
    }

    async refreshDashboard() {
        try {
            this.notification.add(_t("Refreshing dashboard..."), {
                type: "info",
            });

            // Try to call refresh method if it exists
            try {
                await this.orm.call(
                    "day.plan.dashboard",
                    "action_refresh_dashboard",
                    []
                );
            } catch (methodError) {
                console.log("Refresh method not available, reloading data directly");
            }

            await this.loadDashboardData();

            this.notification.add(_t("Dashboard refreshed successfully"), {
                type: "success",
            });
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

            if (result) {
                this.actionService.doAction(result);
            } else {
                // Fallback: open print dialog
                window.print();
            }
        } catch (error) {
            this.notification.add(_t("Print functionality not available"), {
                type: "warning",
            });
            console.error("Error printing dashboard:", error);

            // Fallback: open browser print dialog
            window.print();
        }
    }

    get isDataAvailable() {
        return !this.state.loading && !this.state.error;
    }

    get hasChartData() {
        return this.state.chartData || this.state.pieChartData ||
               this.state.lineChartData || this.state.radarChartData;
    }
}

// Register the dashboard action
registry.category("actions").add("day_plan_work_report_ai.dashboard_action", ProductivityDashboard);