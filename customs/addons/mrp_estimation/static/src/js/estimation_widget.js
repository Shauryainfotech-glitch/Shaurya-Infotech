/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useRef, onMounted, onWillUpdateProps } from "@odoo/owl";
import { xml } from "@odoo/owl";

export class CostAnalysisWidget extends Component {
    static template = xml`
        <div class="o_cost_analysis_chart">
            <canvas t-ref="canvas" width="400" height="300"></canvas>
        </div>
    `;

    static props = {
        ...standardFieldProps,
    };

    setup() {
        super.setup();
        this.canvasRef = useRef("canvas");

        onMounted(() => {
            this._renderChart();
        });

        onWillUpdateProps((nextProps) => {
            if (this.props.record !== nextProps.record) {
                this._renderChart();
            }
        });
    }

    _renderChart() {
        if (!this.canvasRef.el) return;

        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext("2d");

        // Clear previous chart
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const record = this.props.record.data;

        // Prepare data for the chart
        const materialCost = record.raw_material_cost || 0;
        const laborCost = record.labor_cost_actual || 0;
        const overheadCost = record.overhead_cost || 0;
        const machineCost = record.machine_cost || 0;
        const qualityCost = record.quality_cost || 0;

        const total = materialCost + laborCost + overheadCost + machineCost + qualityCost;

        if (total === 0) {
            // Display "No data" message
            ctx.fillStyle = "#6c757d";
            ctx.font = "16px Arial";
            ctx.textAlign = "center";
            ctx.fillText("No cost data available", canvas.width / 2, canvas.height / 2);
            return;
        }

        const data = [
            { label: "Raw Materials", value: materialCost, color: "#0d6efd" },
            { label: "Labor", value: laborCost, color: "#198754" },
            { label: "Overhead", value: overheadCost, color: "#fd7e14" },
            { label: "Machine", value: machineCost, color: "#6f42c1" },
            { label: "Quality", value: qualityCost, color: "#20c997" }
        ].filter(item => item.value > 0);

        // Draw pie chart
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 20;

        let currentAngle = -Math.PI / 2;

        data.forEach((item) => {
            const sliceAngle = (item.value / total) * 2 * Math.PI;

            // Draw slice
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fillStyle = item.color;
            ctx.fill();

            // Draw label
            const labelAngle = currentAngle + sliceAngle / 2;
            const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
            const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);

            ctx.fillStyle = "#fff";
            ctx.font = "12px Arial";
            ctx.textAlign = "center";
            ctx.fillText(
                `${((item.value / total) * 100).toFixed(1)}%`,
                labelX,
                labelY
            );

            currentAngle += sliceAngle;
        });

        // Draw legend
        const legendX = 10;
        let legendY = 10;

        ctx.font = "12px Arial";
        ctx.textAlign = "left";

        data.forEach((item) => {
            // Legend color box
            ctx.fillStyle = item.color;
            ctx.fillRect(legendX, legendY, 15, 15);

            // Legend text
            ctx.fillStyle = "#333";
            const currency = record.currency_id && record.currency_id[1] ? record.currency_id[1] : "";
            ctx.fillText(
                `${item.label}: ${currency} ${item.value.toFixed(2)}`,
                legendX + 20,
                legendY + 12
            );

            legendY += 20;
        });
    }
}

// Register the widget
registry.category("fields").add("cost_analysis_chart", CostAnalysisWidget);