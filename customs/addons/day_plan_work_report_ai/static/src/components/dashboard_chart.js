/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";

export class DashboardChart extends Component {
    static template = "day_plan_work_report_ai.DashboardChart";  // Single reference
    static props = {
        data: { type: [String, Object], optional: true },
        type: { type: String, optional: true },
        style: { type: String, optional: true },
    };

    setup() {
        this.chartRef = useRef("chart");
        this.chart = null;

        onMounted(() => {
            // Add delay to ensure DOM is ready
            setTimeout(() => this._renderChart(), 100);
        });

        onWillUnmount(() => this._destroyChart());
    }

    _renderChart() {
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
                    chartData = this._getDefaultData();
                }
            } else {
                chartData = this.props.data || this._getDefaultData();
            }

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

    _getDefaultData() {
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

    _destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}