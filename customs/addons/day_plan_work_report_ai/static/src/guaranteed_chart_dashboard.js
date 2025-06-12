/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

class GuaranteedChartDashboard extends Component {
    setup() {
        this.state = useState({
            loading: true,
            chartData: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Productivity',
                    data: [65, 70, 75, 80, 75, 68, 72],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            }
        });
        
        this.chartRef = useRef("chartCanvas");
        this.chart = null;
        
        onMounted(async () => {
            try {
                console.log("Chart dashboard mounted");
                await this._loadChartJS();
                this._renderChart();
                this.state.loading = false;
            } catch (error) {
                console.error("Failed to initialize dashboard:", error);
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
    
    _renderChart() {
        console.log("Rendering chart...");
        
        if (!this.chartRef.el) {
            console.error("Chart canvas element not found");
            return;
        }
        
        const ctx = this.chartRef.el.getContext('2d');
        if (!ctx) {
            console.error("Failed to get 2D context for chart");
            return;
        }
        
        console.log("Creating chart with context:", ctx);
        this.chart = new Chart(ctx, {
            type: 'line',
            data: this.state.chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Guaranteed Working Chart'
                    },
                }
            }
        });
        
        console.log("Chart created successfully");
    }
}

GuaranteedChartDashboard.template = 'day_plan_work_report_ai.GuaranteedChartDashboard';
GuaranteedChartDashboard.components = { Layout };

// Register the client action
registry.category("actions").add("day_plan_work_report_ai.guaranteed_chart_dashboard", {
    Component: GuaranteedChartDashboard,
});

export { GuaranteedChartDashboard };
