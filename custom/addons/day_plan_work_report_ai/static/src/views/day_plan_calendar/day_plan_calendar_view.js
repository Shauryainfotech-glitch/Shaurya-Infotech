/** @odoo-module **/

import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { DayPlanCalendarController } from "./day_plan_calendar_controller";
import { DayPlanCalendarRenderer } from "./day_plan_calendar_renderer";
import { DayPlanCalendarModel } from "./day_plan_calendar_model";

// Define and register the day plan calendar view
export const dayPlanCalendarView = {
    ...calendarView,
    Controller: DayPlanCalendarController,
    Renderer: DayPlanCalendarRenderer,
    Model: DayPlanCalendarModel,
};

// Register our custom view in the registry
registry.category("views").add("day_plan_calendar", dayPlanCalendarView);
