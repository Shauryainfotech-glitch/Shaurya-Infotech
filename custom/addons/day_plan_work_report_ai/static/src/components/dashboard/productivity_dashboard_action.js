/** @odoo-module **/
import { registry } from "@web/core/registry";
import { ProductivityDashboard } from "./productivity_dashboard";

// Register the productivity dashboard as a client action
registry.category("actions").add("day_plan_work_report_ai.productivity_dashboard", {
    Component: ProductivityDashboard,
});
