/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class CostAnalysisWidget extends Component {
    setup() {
        super.setup();
        this.canvasRef = useRef("canvas");
    }

    mounted() {
        this._renderChart();
    }

    willUpdateProps(nextProps) {
        if (this.props.value !== nextProps.value) {
            this._renderChart();
        }
    }

    _renderChart() {
        const canvas = this.canvasRef.el;
        const ctx = canvas.getContext("2d");
        
        // Clear previous chart
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const record = this.props.record.data;
        
        // Prepare data for the chart
        const data = {
            labels: ["Raw Materials", "Labor", "Overhead", "Machine", "Quality"],
            datasets: [
                {
                    label: "Planned Cost",
                    data: [
                        record.raw_material_cost || 0,
                        record.labor_cost_actual || 0,
                        record.overhead_cost || 0,
                        record.machine_cost || 0,
                        record.quality_cost || 0
                    ],
                    backgroundColor: [
                        "#0d6efd",
                        "#198754",
                        "#fd7e14",
                        "#6f42c1",
                        "#20c997"
                    ]
                }
            ]
        };

        // Chart configuration
        const config = {
            type: "doughnut",
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom"
                    },
                    title: {
                        display: true,
                        text: "Cost Breakdown Analysis"
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || "";
                                const value = context.parsed || 0;
                                const currency = record.currency_id[1] || "";
                                return `${label}: ${currency} ${value.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        };

        // Create new chart
        new Chart(ctx, config);
    }
}

CostAnalysisWidget.template = "mrp_estimation.CostAnalysisWidget";
CostAnalysisWidget.props = {
    ...standardFieldProps
};

// Register the widget
registry.category("fields").add("cost_analysis_chart", CostAnalysisWidget);
