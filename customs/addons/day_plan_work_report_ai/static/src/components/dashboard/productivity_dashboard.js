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
        try {
            // Check if Chart is already defined globally
            if (typeof Chart !== 'undefined') {
                console.log('Chart.js is already loaded');
                return Promise.resolve();
            }
            
            console.log('Loading Chart.js library...');
            return loadJS("/web/static/lib/Chart/Chart.js");
        } catch (error) {
            console.error('Error loading Chart.js:', error);
            return Promise.reject(error);
        }
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
        try {
            console.log('Rendering dashboard charts...');
            
            // Check if Chart.js is loaded
            if (typeof Chart === 'undefined') {
                console.error('Chart.js library not loaded');
                return;
            }
            
            // Destroy existing charts first
            Object.values(this.charts).forEach(chart => {
                if (chart) {
                    try {
                        chart.destroy();
                    } catch (e) {
                        console.warn('Error destroying chart:', e);
                    }
                }
            });
            
            // Log available chart data
            console.log('Chart data available:', {
                productivity: this.state.chartData.productivity ? 'yes' : 'no',
                tasks: this.state.chartData.tasks ? 'yes' : 'no',
                completion: this.state.chartData.completion ? 'yes' : 'no',
                wellbeing: this.state.chartData.wellbeing ? 'yes' : 'no'
            });
            
            // Provide default data if needed
            const defaultChartData = {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Default Data',
                    data: [65, 70, 75, 80, 75, 68, 72],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            };
            
            // Productivity Chart (Line chart)
            if (this.chartRefs.productivity.el) {
                try {
                    const ctx = this.chartRefs.productivity.el.getContext("2d");
                    if (!ctx) {
                        console.error('Failed to get 2D context for productivity chart');
                    } else {
                        const chartData = this.state.chartData.productivity || defaultChartData;
                        console.log('Creating productivity chart with data:', chartData);
                        
                        this.charts.productivity = new Chart(ctx, {
                            type: "line",
                            data: chartData,
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
                        console.log('Productivity chart created successfully');
                    }
                } catch (error) {
                    console.error('Error rendering productivity chart:', error);
                }
            }
        } catch (err) {
            console.error('Critical error in _renderCharts:', err);
        }
        
        // Tasks Chart (Bar chart)
        if (this.chartRefs.tasks.el) {
            try {
                const ctx = this.chartRefs.tasks.el.getContext("2d");
                if (!ctx) {
                    console.error('Failed to get 2D context for tasks chart');
                } else {
                    const chartData = this.state.chartData.tasks || {
                        labels: ['Done', 'In Progress', 'Draft'],
                        datasets: [{
                            data: [10, 5, 3],
                            backgroundColor: ['#1cc88a', '#f6c23e', '#858796'],
                        }]
                    };
                    
                    console.log('Creating tasks chart with data:', chartData);
                    this.charts.tasks = new Chart(ctx, {
                        type: "bar",
                        data: chartData,
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
                    console.log('Tasks chart created successfully');
                }
            } catch (error) {
                console.error('Error rendering tasks chart:', error);
            }
        }
        
        // Completion Chart (Doughnut chart)
        if (this.chartRefs.completion.el) {
            try {
                const ctx = this.chartRefs.completion.el.getContext("2d");
                if (!ctx) {
                    console.error('Failed to get 2D context for completion chart');
                } else {
                    const chartData = this.state.chartData.completion || {
                        labels: ['Completed', 'Pending'],
                        datasets: [{
                            data: [18, 6],
                            backgroundColor: ['#4e73df', '#858796'],
                        }]
                    };
                    
                    console.log('Creating completion chart with data:', chartData);
                    this.charts.completion = new Chart(ctx, {
                        type: "doughnut",
                        data: chartData,
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
                    console.log('Completion chart created successfully');
                }
            } catch (error) {
                console.error('Error rendering completion chart:', error);
            }
        }
        
        // Wellbeing Chart (Radar chart)
        if (this.chartRefs.wellbeing.el) {
            try {
                const ctx = this.chartRefs.wellbeing.el.getContext("2d");
                if (!ctx) {
                    console.error('Failed to get 2D context for wellbeing chart');
                } else {
                    const defaultWellbeingData = {
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
                    };
                    
                    const chartData = this.state.chartData.wellbeing || defaultWellbeingData;
                    console.log('Creating wellbeing chart with data:', chartData);
                    
                    this.charts.wellbeing = new Chart(ctx, {
                        type: "radar",
                        data: chartData,
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
                    console.log('Wellbeing chart created successfully');
                }
            } catch (error) {
                console.error('Error rendering wellbeing chart:', error);
            }
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
