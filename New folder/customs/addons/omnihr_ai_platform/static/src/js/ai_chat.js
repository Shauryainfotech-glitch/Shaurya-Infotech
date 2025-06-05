/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

class AIChat extends Component {
    static template = "omnihr_ai_platform.AIChat";
    
    setup() {
        this.state = useState({
            messages: [],
            currentMessage: "",
            isLoading: false,
            sessionId: null
        });
    }
    
    async sendMessage() {
        if (!this.state.currentMessage.trim()) return;
        
        const userMessage = this.state.currentMessage;
        this.state.messages.push({
            type: 'user',
            content: userMessage,
            timestamp: new Date()
        });
        
        this.state.currentMessage = "";
        this.state.isLoading = true;
        
        try {
            const result = await this.env.services.rpc("/omnihr/ai/chat", {
                message: userMessage,
                session_id: this.state.sessionId
            });
            
            if (result.success) {
                this.state.sessionId = result.session_id;
                this.state.messages.push({
                    type: 'assistant',
                    content: result.response,
                    timestamp: new Date()
                });
            } else {
                this.state.messages.push({
                    type: 'error',
                    content: result.error || 'An error occurred',
                    timestamp: new Date()
                });
            }
        } catch (error) {
            console.error("Chat error:", error);
            this.state.messages.push({
                type: 'error',
                content: 'Failed to send message',
                timestamp: new Date()
            });
        } finally {
            this.state.isLoading = false;
        }
    }
    
    onKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }
}

registry.category("actions").add("hr_ai_chat", AIChat); 