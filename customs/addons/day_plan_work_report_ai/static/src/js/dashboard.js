/** @odoo-module **/

import { registry } from '@web/core/registry';
import { Component, useState, onMounted, useRef } from "@odoo/owl";

class ProductivityDashboard extends Component {
    setup() {
        this.state = useState({
            loading: true,
            stats: {
                total_plans: 0,
                plans_today: 0,
                completed_plans: 0,
                pending_tasks: 0,
                completion_rate: 0,
                productivity_score: 0,
                efficiency_rating: 0,
                wellbeing_assessment: 0,
                plans_change: 0,
                tasks_change: 0,
                tasks_due_today: 0,
                overdue_tasks: 0,
                attention_items: 0,
            },
            charts: {}
        });
        
        this.chartRefs = {
            productivity: useRef("productivity-chart"),
            tasks: useRef("tasks-chart"),
            completion: useRef("completion-chart")
        };
        
        this.rpc = this.env.services.rpc;
        
        onMounted(() => {
            this._loadData();
        });
    }
    
    async _loadData() {
        this.state.loading = true;
        try {
            const data = await this.rpc('/day_plan_work_report_ai/dashboard_data');
            this.state.stats = data.kpis;
            this.state.loading = false;
            this._renderCharts(data.charts);
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.loading = false;
        }
    }
    
    _renderCharts(chartData) {
        if (!window.Chart) {
            // Load Chart.js dynamically
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            script.onload = () => {
                this._initCharts(chartData);
            };
            document.head.appendChild(script);
        } else {
            this._initCharts(chartData);
        }
    }
    
    _initCharts(chartData) {
        // Productivity Chart
        if (this.chartRefs.productivity.el) {
            new window.Chart(this.chartRefs.productivity.el.getContext('2d'), {
                type: 'line',
                data: chartData.productivity || {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Productivity',
                        data: [65, 78, 66, 74, 63, 40, 55],
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        }
        
        // Tasks Chart
        if (this.chartRefs.tasks.el) {
            new window.Chart(this.chartRefs.tasks.el.getContext('2d'), {
                type: 'bar',
                data: chartData.tasks || {
                    labels: ['Planning', 'Development', 'Design', 'Meetings', 'Admin'],
                    datasets: [{
                        label: 'Tasks Completed',
                        data: [12, 19, 8, 15, 10],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 206, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(153, 102, 255, 0.2)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Completion Chart
        if (this.chartRefs.completion.el) {
            new window.Chart(this.chartRefs.completion.el.getContext('2d'), {
                type: 'doughnut',
                data: chartData.completion || {
                    labels: ['Completed', 'In Progress', 'Not Started'],
                    datasets: [{
                        data: [70, 15, 15],
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(255, 206, 86, 0.2)',
                            'rgba(255, 99, 132, 0.2)'
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(255, 99, 132, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }
}

ProductivityDashboard.template = 'day_plan_work_report_ai.ProductivityDashboard';

registry.category("actions").add("day_plan_work_report_ai.productivity_dashboard", {
    Component: ProductivityDashboard,
    target: 'main_component',
    actionInfo: {
        type: 'ir.actions.client',
        tag: 'day_plan_work_report_ai.productivity_dashboard',
    }
});
