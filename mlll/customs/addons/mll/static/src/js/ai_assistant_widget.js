/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AiAssistantWidget extends Component {
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
            this.action.doAction(action);
        } catch (error) {
            this.notification.add(
                "Error opening AI Assistant",
                { type: "danger" }
            );
        }
    }
}

AiAssistantWidget.template = "ai_llm_integration.AiAssistantWidget";

// Register the widget
registry.category("view_widgets").add("ai_assistant", AiAssistantWidget);

// AI Chat Widget for universal access
export class AiChatWidget extends Component {
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
        
        // Add user message to chat
        this.state.messages.push({
            role: "user",
            content: userMessage,
            timestamp: new Date()
        });
        
        try {
            // Open AI content generator
            const action = await this.orm.call(
                "ai.content.generator",
                "create",
                [{
                    prompt_type: "custom",
                    custom_prompt: userMessage
                }]
            );
            
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "ai.content.generator",
                res_id: action,
                view_mode: "form",
                target: "new"
            });
            
        } catch (error) {
            this.notification.add(
                "Error sending message to AI",
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

// Register the chat widget
registry.category("view_widgets").add("ai_chat", AiChatWidget);
