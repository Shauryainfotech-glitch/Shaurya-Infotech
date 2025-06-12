/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class DashboardComponent extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            data: {},
            loading: true
        });

        onMounted(() => {
            this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            const data = await this.orm.call(
                "day.plan.dashboard",
                "get_dashboard_data",
                [],
                {
                    date_range: "week",
                    employee_id: false,
                    department_id: false
                }
            );
            this.state.data = data;
            this.state.loading = false;
            this.renderCharts();
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.loading = false;
        }
    }

    renderCharts() {
        // Basic chart rendering logic
        if (typeof Chart !== 'undefined') {
            const ctx = document.getElementById('productivityChart');
            if (ctx) {
                new Chart(ctx, {
                    type: 'line',
                    data: JSON.parse(this.state.data.chart_data || '{}'),
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
        }
    }
}

DashboardComponent.template = "day_plan_work_report_ai.Dashboard";

registry.category("actions").add("day_plan_dashboard", DashboardComponent);