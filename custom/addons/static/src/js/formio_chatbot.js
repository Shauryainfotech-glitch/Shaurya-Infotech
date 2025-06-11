odoo.define('formio.chatbot', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;

    var FormioChatbot = AbstractAction.extend({
        template: 'formio_chatbot_template',
        events: {
            'click .send_message': '_onSendMessage',
            'keypress .chatbot_input input': '_onInputKeypress',
            'click .minimize_chat': '_onMinimizeChat',
            'click .close_chat': '_onCloseChat',
            'click .chatbot_toggle': '_onToggleChat'
        },

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.form_id = action.params.form_id;
            this.isTyping = false;
            this.minimized = false;
        },

        start: function() {
            var self = this;
            return this._super().then(function() {
                self._loadChatHistory();
                self._initializeUI();
            });
        },

        _initializeUI: function() {
            this.$el.addClass('chatbot_container');
            this.$('.chatbot_messages').perfectScrollbar();
            
            // Add welcome message
            this._appendMessage('bot', 'Hello! I\'m your form assistant. How can I help you today?');
        },

        _loadChatHistory: function() {
            var self = this;
            return this._rpc({
                model: 'formio.builder',
                method: 'read',
                args: [[this.form_id], ['chat_message_ids']],
            }).then(function(result) {
                if (result && result[0]) {
                    var messageIds = result[0].chat_message_ids;
                    if (messageIds && messageIds.length > 0) {
                        return self._rpc({
                            model: 'formio.chat.message',
                            method: 'read',
                            args: [messageIds, ['message', 'sender', 'create_date']],
                        }).then(function(messages) {
                            messages.forEach(function(msg) {
                                self._appendMessage(msg.sender, msg.message, msg.create_date);
                            });
                        });
                    }
                }
            });
        },

        _onSendMessage: function () {
            var self = this;
            var input = this.$('.chatbot_input input');
            var message = input.val().trim();
            
            if (message) {
                input.prop('disabled', true);
                this._appendMessage('user', message);
                this._showTypingIndicator();

                this._rpc({
                    model: 'formio.builder',
                    method: 'process_chat_message',
                    args: [[this.form_id], message],
                }).then(function (response) {
                    self._hideTypingIndicator();
                    self._appendMessage('bot', response.message);
                    input.prop('disabled', false);
                    input.val('').focus();
                }).catch(function(error) {
                    self._hideTypingIndicator();
                    self._appendMessage('bot', 'Sorry, I encountered an error. Please try again.');
                    input.prop('disabled', false);
                });
            }
        },

        _onInputKeypress: function (event) {
            if (event.which === 13) {
                this._onSendMessage();
            }
        },

        _appendMessage: function (sender, message, timestamp) {
            var time = timestamp ? moment(timestamp).format('HH:mm') : moment().format('HH:mm');
            var messageHtml = QWeb.render('formio_chatbot_message', {
                sender: sender,
                message: message,
                time: time
            });
            
            var $messages = this.$('.chatbot_messages');
            $messages.append(messageHtml);
            
            // Smooth scroll to bottom
            $messages.stop().animate({
                scrollTop: $messages[0].scrollHeight
            }, 500);
        },

        _showTypingIndicator: function() {
            if (!this.isTyping) {
                this.isTyping = true;
                var typingHtml = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
                this.$('.chatbot_messages').append(typingHtml);
                this._scrollToBottom();
            }
        },

        _hideTypingIndicator: function() {
            this.isTyping = false;
            this.$('.typing-indicator').remove();
        },

        _scrollToBottom: function() {
            var $messages = this.$('.chatbot_messages');
            $messages.stop().animate({
                scrollTop: $messages[0].scrollHeight
            }, 200);
        },

        _onMinimizeChat: function() {
            this.minimized = !this.minimized;
            this.$el.toggleClass('minimized', this.minimized);
        },

        _onCloseChat: function() {
            this.destroy();
        },

        _onToggleChat: function() {
            this._onMinimizeChat();
        },

        destroy: function () {
            if (this.$el) {
                this.$el.remove();
            }
            this._super.apply(this, arguments);
        }
    });

    core.action_registry.add('formio_chatbot', FormioChatbot);

    return FormioChatbot;
}); 