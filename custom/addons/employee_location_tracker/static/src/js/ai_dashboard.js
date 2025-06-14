/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AIDashboard extends Component {
    static template = "employee_location_tracker.AIDashboard";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            dashboardData: {},
            loading: true
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            
            // Calculate date range (last 30 days)
            const dateFrom = new Date();
            dateFrom.setDate(dateFrom.getDate() - 30);
            const dateTo = new Date();

            // Get location data
            const locations = await this.orm.searchRead(
                "hr.employee.location",
                [
                    ["timestamp", ">=", dateFrom.toISOString().split('T')[0]],
                    ["timestamp", "<=", dateTo.toISOString().split('T')[0]]
                ],
                [
                    "employee_id", "timestamp", "location_type", "anomaly_detected",
                    "ai_confidence_score", "accuracy", "distance_from_last"
                ],
                { limit: 1000 }
            );

            // Calculate summary statistics
            const summary = this.calculateSummaryStats(locations);
            this.state.dashboardData = summary;
            
            this.state.loading = false;
            this.renderDashboard();
            
        } catch (error) {
            this.state.loading = false;
            this.notification.add("Failed to load dashboard data", { type: "danger" });
            console.error("Dashboard loading error:", error);
        }
    }

    calculateSummaryStats(locations) {
        const uniqueEmployees = new Set(locations.map(l => l.employee_id[0])).size;
        const totalDistance = locations.reduce((sum, l) => sum + (l.distance_from_last || 0), 0);
        const anomalies = locations.filter(l => l.anomaly_detected).length;
        const highConfidence = locations.filter(l => l.ai_confidence_score > 0.8).length;
        const avgAccuracy = locations.length > 0 
            ? locations.reduce((sum, l) => sum + (l.accuracy || 0), 0) / locations.length 
            : 0;

        // Location types distribution
        const locationTypes = {};
        locations.forEach(l => {
            locationTypes[l.location_type] = (locationTypes[l.location_type] || 0) + 1;
        });

        return {
            totalLocations: locations.length,
            uniqueEmployees,
            totalDistance: totalDistance.toFixed(2),
            anomalies,
            highConfidence,
            avgAccuracy: avgAccuracy.toFixed(1),
            locationTypes
        };
    }

    renderDashboard() {
        // Update summary cards
        this.updateSummaryCards();
        this.loadRecentActivities();
    }

    updateSummaryCards() {
        const data = this.state.dashboardData;
        
        // The template will handle the display using t-esc
        // This method can be used for any additional UI updates
    }

    async loadRecentActivities() {
        try {
            // Get recent locations (last 24 hours)
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);

            const recentLocations = await this.orm.searchRead(
                "hr.employee.location",
                [["timestamp", ">=", yesterday.toISOString()]],
                ["employee_id", "timestamp", "location_type", "anomaly_detected"],
                { limit: 10, order: "timestamp desc" }
            );

            this.state.dashboardData.recentActivities = recentLocations;
            
        } catch (error) {
            console.error("Failed to load recent activities:", error);
        }
    }

    async onRefreshDashboard() {
        this.notification.add("Refreshing dashboard data...", { type: "info" });
        await this.loadDashboardData();
        this.notification.add("Dashboard refreshed successfully", { type: "success" });
    }

    onFilterChange(event) {
        // Handle filter changes
        const days = parseInt(event.target.value);
        // Reload data with new date range
        this.loadDashboardData();
    }

    formatNumber(num, decimals = 0) {
        return parseFloat(num).toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffMs = now - time;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 60) return `${diffMins} minutes ago`;
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours} hours ago`;
        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays} days ago`;
    }
}

registry.category("actions").add("employee_location_tracker.ai_dashboard", AIDashboard);