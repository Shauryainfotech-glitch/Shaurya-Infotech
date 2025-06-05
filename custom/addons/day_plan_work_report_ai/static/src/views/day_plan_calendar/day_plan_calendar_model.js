/** @odoo-module **/

import { CalendarModel } from "@web/views/calendar/calendar_model";

/**
 * Extended Calendar Model for Day Plan
 * 
 * Customizes the calendar model behavior for day plans
 */
export class DayPlanCalendarModel extends CalendarModel {
    /**
     * @override
     */
    async load(params) {
        const result = await super.load(params);
        
        // Add any day.plan specific logic here if needed
        if (this.resModel === 'day.plan') {
            // For example, you could add additional information or processing
        }
        
        return result;
    }
    
    /**
     * @override
     */
    recordToCalendarEvent(record) {
        const result = super.recordToCalendarEvent(record);
        
        // Add day.plan specific data to the event if needed
        if (this.resModel === 'day.plan') {
            // For example, add task count as a property
            result.extendedProps.task_count = record.task_ids ? record.task_ids.length : 0;
        }
        
        return result;
    }
}
