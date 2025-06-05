/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';
import { Layout } from '@web/search/layout';
import { Component, useState, onMounted, useRef } from "@odoo/owl";

/**
 * Productivity Dashboard Main Component
 * 
 * This component implements a dynamic dashboard for the day plan module
 * showing productivity metrics, task completion statistics, and charts
 * using Chart.js for visualization.
 */
class ProductivityDashboardMain extends Component {
    setup() {
        this.rpc = useService("rpc");
        
        // Initialize state with empty data
        this.state = useState({
            loading: true,
            error: null,
            kpis: {
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
        
        // Chart canvas references
        this.chartRefs = {
            productivity: useRef("productivity-chart"),
            tasks: useRef("tasks-chart"),
            completion: useRef("completion-chart")
        };
        
        // Load data when component is mounted
        onMounted(() => this.loadDashboardData());
    }
    
    /**
     * Load dashboard data from the server
     */
    async loadDashboardData() {
        this.state.loading = true;
        try {
            const result = await this.rpc("/day_plan_work_report_ai/dashboard_data");
            this.state.kpis = result.kpis || this.state.kpis;
            this.state.loading = false;
            
            // Load Chart.js and initialize charts
            this.loadChartJS(result.charts);
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
            this.state.error = "Failed to load dashboard data. Please try again later.";
            this.state.loading = false;
        }
    }
    
    /**
     * Load Chart.js library and initialize charts
     */
    loadChartJS(chartData) {
        // If Chart.js is already loaded, initialize charts directly
        if (window.Chart) {
            this.initializeCharts(chartData);
            return;
        }
        
        // Otherwise load Chart.js dynamically
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js';
        script.integrity = 'sha256-ErZ09KkZnzjpqcane4SCyyHsKAXMvID9/xwbl/Aq1pc=';
        script.crossOrigin = 'anonymous';
        script.onload = () => this.initializeCharts(chartData);
        document.head.appendChild(script);
    }
    
    /**
     * Initialize all charts with data
     */
    initializeCharts(chartData) {
        // If no chart data is provided, use demo data
        chartData = chartData || {
            productivity: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Productivity',
                    data: [65, 78, 66, 74, 63, 40, 55],
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            tasks: {
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
            completion: {
                labels: ['Completed', 'In Progress', 'Not Started'],
                datasets: [{
                    data: [70, 15, 15],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(255, 99, 132, 0.5)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            }
        };
        
        // Create Productivity Trend Chart (Line)
        if (this.chartRefs.productivity.el) {
            new window.Chart(this.chartRefs.productivity.el, {
                type: 'line',
                data: chartData.productivity,
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        // Create Task Statistics Chart (Bar)
        if (this.chartRefs.tasks.el) {
            new window.Chart(this.chartRefs.tasks.el, {
                type: 'bar',
                data: chartData.tasks,
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
        
        // Create Task Completion Chart (Doughnut)
        if (this.chartRefs.completion.el) {
            new window.Chart(this.chartRefs.completion.el, {
                type: 'doughnut',
                data: chartData.completion,
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }
}

// Define component template
ProductivityDashboardMain.template = 'day_plan_work_report_ai.ProductivityDashboard';
ProductivityDashboardMain.components = { Layout };

// Register the client action
registry.category("actions").add("day_plan_work_report_ai.productivity_dashboard", {
    Component: ProductivityDashboardMain,
});
