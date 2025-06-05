/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, useRef, onMounted } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

class ProductivityDashboard extends Component {
    setup() {
        this.state = useState({
            data: {
                total_plans: 0,
                plans_today: 0,
                completed_plans: 0,
                pending_tasks: 0,
                productivity_score: 0,
                efficiency_rating: 0,
                wellbeing_assessment: 0,
                plans_change: 0,
                tasks_change: 0,
                completion_rate: 0,
                avg_productivity: 0,
                tasks_due_today: 0,
                overdue_tasks: 0,
                attention_items: 0,
            },
            chartData: {
                productivity: { labels: [], datasets: [] },
                tasks: { labels: [], datasets: [] },
                completion: { labels: [], datasets: [] },
            },
            filters: {
                dateRange: "week",
                employee: false,
                department: false,
            },
            loading: true,
        });
        
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.user = useService("user");
        
        this.chartRefs = {
            productivity: useRef("productivity-chart"),
            tasks: useRef("tasks-chart"),
            completion: useRef("completion-chart"),
            wellbeing: useRef("wellbeing-chart"),
        };
        
        this.charts = {};
        
        onWillStart(async () => {
            await this._loadChartJS();
            await this._fetchDashboardData();
        });
        
        onMounted(() => {
            this._renderCharts();
        });
    }
    
    async _loadChartJS() {
        return loadJS("/web/static/lib/Chart/Chart.js");
    }
    
    async _fetchDashboardData() {
        this.state.loading = true;
        try {
            // Get dashboard data from server
            const result = await this.rpc("/day_plan_work_report_ai/dashboard_data", {
                date_range: this.state.filters.dateRange,
                employee_id: this.state.filters.employee,
                department_id: this.state.filters.department,
            });
            
            // Update state with received data
            this.state.data = result.kpis;
            this.state.chartData = result.charts;
            
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }
    
    _renderCharts() {
        // Destroy existing charts first
        Object.values(this.charts).forEach(chart => chart && chart.destroy());
        
        // Productivity Chart (Line chart)
        if (this.chartRefs.productivity.el) {
            const ctx = this.chartRefs.productivity.el.getContext("2d");
            this.charts.productivity = new Chart(ctx, {
                type: "line",
                data: this.state.chartData.productivity,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "bottom",
                        },
                        title: {
                            display: true,
                            text: "Productivity Trends"
                        },
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + "%";
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Tasks Chart (Bar chart)
        if (this.chartRefs.tasks.el) {
            const ctx = this.chartRefs.tasks.el.getContext("2d");
            this.charts.tasks = new Chart(ctx, {
                type: "bar",
                data: this.state.chartData.tasks,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "bottom",
                        },
                        title: {
                            display: true,
                            text: "Task Statistics"
                        },
                    },
                }
            });
        }
        
        // Completion Chart (Doughnut chart)
        if (this.chartRefs.completion.el) {
            const ctx = this.chartRefs.completion.el.getContext("2d");
            this.charts.completion = new Chart(ctx, {
                type: "doughnut",
                data: this.state.chartData.completion,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "bottom",
                        },
                        title: {
                            display: true,
                            text: "Task Completion"
                        },
                    },
                }
            });
        }
        
        // Wellbeing Chart (Radar chart)
        if (this.chartRefs.wellbeing.el) {
            const ctx = this.chartRefs.wellbeing.el.getContext("2d");
            this.charts.wellbeing = new Chart(ctx, {
                type: "radar",
                data: this.state.chartData.wellbeing || {
                    labels: ["Focus", "Energy", "Stress", "Satisfaction", "Work-Life Balance"],
                    datasets: [{
                        label: "Current Week",
                        data: [80, 70, 60, 75, 65],
                        fill: true,
                        backgroundColor: "rgba(75, 192, 192, 0.2)",
                        borderColor: "rgb(75, 192, 192)",
                        pointBackgroundColor: "rgb(75, 192, 192)",
                        pointBorderColor: "#fff",
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "bottom",
                        },
                        title: {
                            display: true,
                            text: "Wellbeing Metrics"
                        },
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                        }
                    }
                }
            });
        }
    }
    
    async onFilterChange(filter, value) {
        this.state.filters[filter] = value;
        await this._fetchDashboardData();
        this._renderCharts();
    }
    
    exportData(format) {
        const exportUrl = `/day_plan_work_report_ai/export_dashboard_data?format=${format}&filters=${JSON.stringify(this.state.filters)}`;
        window.open(exportUrl, '_blank');
    }
}

ProductivityDashboard.template = "day_plan_work_report_ai.ProductivityDashboard";
ProductivityDashboard.components = { Layout };

export { ProductivityDashboard };
