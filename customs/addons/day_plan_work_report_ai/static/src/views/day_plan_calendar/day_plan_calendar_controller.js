/** @odoo-module **/

import { CalendarController } from "@web/views/calendar/calendar_controller";

/**
 * Extended Calendar Controller for Day Plan
 * 
 * Extends the standard calendar controller with day plan specific actions
 */
export class DayPlanCalendarController extends CalendarController {
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
