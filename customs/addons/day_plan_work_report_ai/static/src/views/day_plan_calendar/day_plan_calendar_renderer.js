/** @odoo-module **/

import { CalendarRenderer } from "@web/views/calendar/calendar_renderer";

/**
 * Extended Calendar Renderer for Day Plan
 * 
 * Customizes the calendar appearance for day plans
 */
export class DayPlanCalendarRenderer extends CalendarRenderer {
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
