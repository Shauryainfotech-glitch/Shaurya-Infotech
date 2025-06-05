/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useState } from "@odoo/owl";  // Added missing useState import
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class AiAssistantWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
    }
    
    async onClickAiAssist() {
        const { model, resId } = this.props.record;
        
        try {
            const action = await this.orm.call(
                model,
                "action_open_ai_assistant",
                [resId]
            );
            await this.action.doAction(action);  // Added await for better error handling
        } catch (error) {
            console.error("AI Assistant Error:", error);  // Added error logging
            this.notification.add(
                error.message || "Error opening AI Assistant",
                { type: "danger" }
            );
        }
    }
}

AiAssistantWidget.template = "ai_llm_integration.AiAssistantWidget";

// Register the widget with error handling
try {
    registry.category("view_widgets").add("ai_assistant", AiAssistantWidget);
} catch (error) {
    console.error("Failed to register AI Assistant widget:", error);
}

class AiChatWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            isOpen: false,
            messages: [],
            inputText: "",
            isLoading: false
        });
    }
    
    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
    }
    
    async sendMessage() {
        if (!this.state.inputText.trim() || this.state.isLoading) {
            return;
        }
        
        const userMessage = this.state.inputText.trim();
        this.state.inputText = "";
        this.state.isLoading = true;
        
        try {
            // Add user message to chat
            this.state.messages.push({
                role: "user",
                content: userMessage,
                timestamp: new Date()
            });
            
            // Open AI content generator
            const action = await this.orm.call(
                "ai.content.generator",
                "create",
                [{
                    prompt_type: "custom",
                    custom_prompt: userMessage
                }]
            );
            
            await this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "ai.content.generator",
                res_id: action,
                view_mode: "form",
                target: "new"
            });
            
        } catch (error) {
            console.error("AI Chat Error:", error);  // Added error logging
            this.notification.add(
                error.message || "Error sending message to AI",
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }
    
    onKeyPress(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }
}

AiChatWidget.template = "ai_llm_integration.AiChatWidget";

// Register the chat widget with error handling
try {
    registry.category("view_widgets").add("ai_chat", AiChatWidget);
} catch (error) {
    console.error("Failed to register AI Chat widget:", error);
}

// Export the widgets for potential external use
export { AiAssistantWidget, AiChatWidget };
