/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

class RecruitmentAI extends Component {
    static template = "omnihr_ai_platform.RecruitmentAI";
    
    setup() {
        this.assessments = [];
        this.loadAssessments();
    }
    
    async loadAssessments() {
        try {
            const result = await this.env.services.orm.searchRead(
                "hr.recruitment.ai",
                [],
                ["applicant_id", "overall_score", "recommendation", "analysis_status"]
            );
            this.assessments = result;
            this.render();
        } catch (error) {
            console.error("Failed to load recruitment assessments:", error);
        }
    }
    
    async runAssessment(applicantId) {
        try {
            await this.env.services.rpc("/omnihr/ai/recruitment/assess", {
                applicant_id: applicantId
            });
            this.loadAssessments();
        } catch (error) {
            console.error("Failed to run assessment:", error);
        }
    }
    
    getScoreClass(score) {
        if (score >= 80) return 'ai-score-high';
        if (score >= 60) return 'ai-score-medium';
        return 'ai-score-low';
    }
}

registry.category("actions").add("hr_recruitment_ai", RecruitmentAI); 