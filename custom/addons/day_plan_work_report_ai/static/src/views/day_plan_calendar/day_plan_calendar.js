/** @odoo-module **/

import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { CalendarRenderer } from "@web/views/calendar/calendar_renderer";
import { CalendarModel } from "@web/views/calendar/calendar_model";

/**
 * Extended Calendar Controller for Day Plan
 * 
 * Extends the standard calendar controller with day plan specific actions
 */
class DayPlanCalendarController extends CalendarController {
    /**
     * Opens quick create form for day plan
     * @override
     */
    onOpenCreate(record) {
        if (this.props.resModel === 'day.plan') {
            // Custom handling for day.plan records
            const context = Object.assign({}, this.props.context);
            if (record) {
                // Add date from the clicked calendar slot
                context.default_date = record.start.toFormat('yyyy-MM-dd');
            }
            this.actionService.doAction({
                type: 'ir.actions.act_window',
                res_model: 'day.plan',
                views: [[false, 'form']],
                target: 'current',
                context: context,
            });
        } else {
            // Use standard behavior for other models
            super.onOpenCreate(record);
        }
    }
    
    /**
     * Open day plan form when clicking on an existing record
     * @override
     */
    onClick(info) {
        if (this.props.resModel === 'day.plan' && info.event) {
            const context = Object.assign({}, this.props.context);
            this.actionService.doAction({
                type: 'ir.actions.act_window',
                res_model: 'day.plan',
                res_id: info.event.extendedProps.record.id,
                views: [[false, 'form']],
                target: 'current',
                context: context,
            });
        } else {
            super.onClick(info);
        }
    }
}

/**
 * Extended Calendar Renderer for Day Plan
 * 
 * Customizes the calendar appearance for day plans
 */
class DayPlanCalendarRenderer extends CalendarRenderer {
    /**
     * @override
     */
    eventRender(info) {
        super.eventRender(info);
        
        // Customize the event element for day plans
        if (this.props.model.resModel === 'day.plan') {
            const record = info.event.extendedProps.record;
            
            // Add completion status indicator based on state
            if (record.state === 'done') {
                info.el.classList.add('o_calendar_event_completed');
            } else if (record.state === 'in_progress') {
                info.el.classList.add('o_calendar_event_in_progress');
            }
            
            // Add any task counts or other indicators if needed
            if (record.task_count > 0) {
                const taskIndicator = document.createElement('div');
                taskIndicator.className = 'o_calendar_task_count';
                taskIndicator.textContent = record.task_count + ' tasks';
                info.el.appendChild(taskIndicator);
            }
        }
    }
}

// Define and register the day plan calendar view
export const dayPlanCalendarView = {
    ...calendarView,
    Controller: DayPlanCalendarController,
    Renderer: DayPlanCalendarRenderer,
    Model: CalendarModel, // Using standard model
};

registry.category("views").add("day_plan_calendar", dayPlanCalendarView);
