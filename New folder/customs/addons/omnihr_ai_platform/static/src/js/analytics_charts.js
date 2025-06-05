/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";

class AnalyticsCharts extends Component {
    static template = "omnihr_ai_platform.AnalyticsCharts";
    
    setup() {
        onMounted(() => {
            this.initCharts();
        });
    }
    
    async initCharts() {
        // Initialize Chart.js charts for analytics
        try {
            await this.loadChartData();
            this.renderSentimentChart();
            this.renderPerformanceChart();
            this.renderFlightRiskChart();
        } catch (error) {
            console.error("Failed to initialize charts:", error);
        }
    }
    
    async loadChartData() {
        const result = await this.env.services.rpc("/omnihr/ai/analytics/charts");
        this.chartData = result;
    }
    
    renderSentimentChart() {
        const ctx = document.getElementById('sentimentChart');
        if (!ctx) return;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.chartData.sentiment.labels,
                datasets: [{
                    label: 'Average Sentiment',
                    data: this.chartData.sentiment.data,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    renderPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.chartData.performance.labels,
                datasets: [{
                    label: 'Performance Score',
                    data: this.chartData.performance.data,
                    backgroundColor: '#28a745'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    renderFlightRiskChart() {
        const ctx = document.getElementById('flightRiskChart');
        if (!ctx) return;
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                datasets: [{
                    data: this.chartData.flightRisk.data,
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true
            }
        });
    }
}

registry.category("actions").add("hr_analytics_charts", AnalyticsCharts); 