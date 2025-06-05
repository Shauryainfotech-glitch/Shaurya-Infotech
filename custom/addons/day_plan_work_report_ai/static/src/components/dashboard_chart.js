/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";

/**
 * Dashboard Chart Component
 * 
 * A reusable chart component that uses Chart.js to render different types of charts
 * for the day.plan dashboard.
 */
export class DashboardChart extends Component {
    setup() {
        this.chartRef = useRef("chart");
        this.chart = null;
        
        onMounted(() => this._renderChart());
        onWillUnmount(() => this._destroyChart());
    }
    
    /**
     * Renders the chart using Chart.js
     * @private
     */
    _renderChart() {
        if (this.chart) {
            this._destroyChart();
        }
        
        const ctx = this.chartRef.el.getContext('2d');
        const chartData = this.props.data || {};
        const chartType = this.props.type || 'bar';
        const chartOptions = this.props.options || this._getDefaultOptions(chartType);
        
        this.chart = new Chart(ctx, {
            type: chartType,
            data: chartData,
            options: chartOptions
        });
    }
    
    /**
     * Get default chart options based on chart type
     * @private
     * @param {string} chartType - The type of chart ('bar', 'line', 'pie', 'radar')
     * @returns {Object} Chart options
     */
    _getDefaultOptions(chartType) {
        const options = {
            responsive: true,
            maintainAspectRatio: false,
        };
        
        // Additional options based on chart type
        if (chartType === 'line') {
            options.scales = {
                y: {
                    beginAtZero: true
                }
            };
        } else if (chartType === 'radar') {
            options.scale = {
                ticks: {
                    beginAtZero: true,
                    max: 100
                }
            };
        }
        
        return options;
    }
    
    /**
     * Clean up chart instance when component is unmounted
     * @private
     */
    _destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

DashboardChart.template = 'day_plan_work_report_ai.DashboardChart';
DashboardChart.props = {
    data: { type: Object, optional: true },
    type: { type: String, optional: true },
    options: { type: Object, optional: true },
    style: { type: String, optional: true }
};
