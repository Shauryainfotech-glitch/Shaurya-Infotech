/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

class AIDashboard extends Component {
    static template = "omnihr_ai_platform.AIDashboard";
    
    setup() {
        this.metrics = {
            totalEmployees: 0,
            aiAnalysisCompleted: 0,
            averageSentiment: 0,
            flightRiskEmployees: 0
        };
        this.loadMetrics();
    }
    
    async loadMetrics() {
        // Load dashboard metrics
        try {
            const result = await this.env.services.rpc("/omnihr/ai/dashboard/metrics");
            this.metrics = result;
            this.render();
        } catch (error) {
            console.error("Failed to load AI dashboard metrics:", error);
        }
    }
}

registry.category("actions").add("hr_ai_dashboard", AIDashboard); 