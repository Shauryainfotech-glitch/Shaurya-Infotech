odoo.define('purchase_ai.widgets', function (require) {
    'use strict';

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var fieldRegistry = require('web.field_registry');
    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');
    var QWeb = core.qweb;
    var _t = core._t;

    /**
     * AI Confidence Score Widget
     * Displays confidence score with color coding and progress bar
     */
    var AIConfidenceWidget = AbstractField.extend({
        className: 'ai_confidence_widget',
        supportedFieldTypes: ['float'],

        _render: function () {
            var value = this.value || 0;
            var percentage = Math.round(value * 100);
            var confidenceClass = this._getConfidenceClass(value);
            
            this.$el.html(QWeb.render('AIConfidenceWidget', {
                value: value,
                percentage: percentage,
                confidenceClass: confidenceClass
            }));
        },

        _getConfidenceClass: function (value) {
            if (value >= 0.8) return 'ai_confidence_high';
            if (value >= 0.6) return 'ai_confidence_medium';
            return 'ai_confidence_low';
        }
    });

    /**
     * Risk Level Widget
     * Displays risk level with appropriate styling and animations
     */
    var RiskLevelWidget = AbstractField.extend({
        className: 'risk_level_widget',
        supportedFieldTypes: ['selection', 'char'],

        _render: function () {
            var value = this.value || 'unknown';
            var riskClass = 'risk_level ' + value;
            var riskText = this._getRiskText(value);
            
            this.$el.html(QWeb.render('RiskLevelWidget', {
                value: value,
                riskClass: riskClass,
                riskText: riskText
            }));
        },

        _getRiskText: function (value) {
            var riskTexts = {
                'low': _t('Low Risk'),
                'medium': _t('Medium Risk'),
                'high': _t('High Risk'),
                'critical': _t('Critical Risk')
            };
            return riskTexts[value] || _t('Unknown');
        }
    });

    /**
     * AI Processing Status Widget
     * Shows real-time processing status with spinner and progress
     */
    var AIProcessingStatusWidget = AbstractField.extend({
        className: 'ai_processing_status_widget',
        supportedFieldTypes: ['selection', 'char'],

        init: function () {
            this._super.apply(this, arguments);
            this.pollingInterval = null;
        },

        _render: function () {
            var status = this.value || 'pending';
            var statusClass = 'queue_status ' + status;
            var statusText = this._getStatusText(status);
            var showSpinner = status === 'processing';
            
            this.$el.html(QWeb.render('AIProcessingStatusWidget', {
                status: status,
                statusClass: statusClass,
                statusText: statusText,
                showSpinner: showSpinner
            }));

            // Start polling if processing
            if (status === 'processing') {
                this._startPolling();
            } else {
                this._stopPolling();
            }
        },

        _getStatusText: function (status) {
            var statusTexts = {
                'pending': _t('Pending'),
                'processing': _t('Processing'),
                'completed': _t('Completed'),
                'failed': _t('Failed')
            };
            return statusTexts[status] || _t('Unknown');
        },

        _startPolling: function () {
            var self = this;
            if (this.pollingInterval) return;
            
            this.pollingInterval = setInterval(function () {
                self._refreshStatus();
            }, 3000); // Poll every 3 seconds
        },

        _stopPolling: function () {
            if (this.pollingInterval) {
                clearInterval(this.pollingInterval);
                this.pollingInterval = null;
            }
        },

        _refreshStatus: function () {
            var self = this;
            if (!this.record || !this.record.data.id) return;

            rpc.query({
                model: this.record.model,
                method: 'read',
                args: [[this.record.data.id], [this.name]]
            }).then(function (result) {
                if (result.length > 0) {
                    var newValue = result[0][self.name];
                    if (newValue !== self.value) {
                        self.value = newValue;
                        self._render();
                        self.trigger_up('field_changed', {
                            dataPointID: self.record.id,
                            changes: {}
                        });
                    }
                }
            });
        },

        destroy: function () {
            this._stopPolling();
            this._super.apply(this, arguments);
        }
    });

    /**
     * Vendor Suggestion Score Widget
     * Interactive widget showing detailed scoring breakdown
     */
    var VendorSuggestionScoreWidget = AbstractField.extend({
        className: 'vendor_suggestion_score_widget',
        supportedFieldTypes: ['float'],
        events: {
            'click .score_details_toggle': '_toggleDetails'
        },

        _render: function () {
            var score = this.value || 0;
            var percentage = Math.round(score * 100);
            var scoreClass = this._getScoreClass(score);
            
            // Get related scoring fields from record
            var scores = this._getDetailedScores();
            
            this.$el.html(QWeb.render('VendorSuggestionScoreWidget', {
                score: score,
                percentage: percentage,
                scoreClass: scoreClass,
                scores: scores
            }));
        },

        _getScoreClass: function (score) {
            if (score >= 0.8) return 'excellent';
            if (score >= 0.6) return 'good';
            if (score >= 0.4) return 'average';
            return 'poor';
        },

        _getDetailedScores: function () {
            var record = this.record.data;
            return {
                price_competitiveness: record.price_competitiveness || 0,
                quality_history: record.quality_history || 0,
                delivery_reliability: record.delivery_reliability || 0,
                relationship_score: record.relationship_score || 0,
                compliance_rating: record.compliance_rating || 0,
                capacity_match: record.capacity_match || 0,
                geographic_proximity: record.geographic_proximity || 0,
                payment_terms_score: record.payment_terms_score || 0
            };
        },

        _toggleDetails: function (event) {
            event.preventDefault();
            this.$('.score_details').slideToggle();
            var $toggle = this.$('.score_details_toggle');
            $toggle.text($toggle.text() === '▼' ? '▲' : '▼');
        }
    });

    /**
     * AI Analysis Result Widget
     * Displays AI analysis with expandable sections
     */
    var AIAnalysisResultWidget = AbstractField.extend({
        className: 'ai_analysis_result_widget',
        supportedFieldTypes: ['text', 'html'],
        events: {
            'click .analysis_section_toggle': '_toggleSection'
        },

        _render: function () {
            var content = this.value || '';
            var sections = this._parseAnalysisContent(content);
            
            this.$el.html(QWeb.render('AIAnalysisResultWidget', {
                sections: sections
            }));
        },

        _parseAnalysisContent: function (content) {
            // Parse structured AI analysis content
            try {
                var parsed = JSON.parse(content);
                return parsed.sections || [{ title: 'Analysis', content: content }];
            } catch (e) {
                return [{ title: 'Analysis', content: content }];
            }
        },

        _toggleSection: function (event) {
            event.preventDefault();
            var $section = $(event.currentTarget).closest('.analysis_section');
            $section.find('.analysis_content').slideToggle();
            var $toggle = $section.find('.analysis_section_toggle');
            $toggle.text($toggle.text() === '▼' ? '▲' : '▼');
        }
    });

    /**
     * AI Cost Monitor Widget
     * Real-time cost monitoring with budget alerts
     */
    var AICostMonitorWidget = AbstractField.extend({
        className: 'ai_cost_monitor_widget',
        supportedFieldTypes: ['float'],

        init: function () {
            this._super.apply(this, arguments);
            this.costThresholds = {
                warning: 0.8,
                danger: 0.95
            };
        },

        _render: function () {
            var cost = this.value || 0;
            var budget = this.record.data.daily_ai_budget || 100;
            var percentage = budget > 0 ? (cost / budget) : 0;
            var alertLevel = this._getAlertLevel(percentage);
            
            this.$el.html(QWeb.render('AICostMonitorWidget', {
                cost: cost.toFixed(2),
                budget: budget.toFixed(2),
                percentage: Math.round(percentage * 100),
                alertLevel: alertLevel
            }));
        },

        _getAlertLevel: function (percentage) {
            if (percentage >= this.costThresholds.danger) return 'danger';
            if (percentage >= this.costThresholds.warning) return 'warning';
            return 'normal';
        }
    });

    /**
     * Document Upload and Analysis Widget
     */
    var DocumentAnalysisWidget = AbstractField.extend({
        className: 'document_analysis_widget',
        supportedFieldTypes: ['binary'],
        events: {
            'change input[type="file"]': '_onFileChange',
            'click .analyze_document_btn': '_analyzeDocument'
        },

        _render: function () {
            this.$el.html(QWeb.render('DocumentAnalysisWidget', {
                hasDocument: !!this.value
            }));
        },

        _onFileChange: function (event) {
            var file = event.target.files[0];
            if (file) {
                this._uploadFile(file);
            }
        },

        _uploadFile: function (file) {
            var self = this;
            var formData = new FormData();
            formData.append('file', file);
            formData.append('model', this.record.model);
            formData.append('id', this.record.data.id);
            formData.append('field', this.name);

            // Show upload progress
            this.$('.upload_progress').show();

            $.ajax({
                url: '/web/binary/upload_attachment',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (result) {
                    self.$('.upload_progress').hide();
                    self.$('.analyze_document_btn').show();
                    self.trigger_up('field_changed', {
                        dataPointID: self.record.id,
                        changes: {}
                    });
                },
                error: function () {
                    self.$('.upload_progress').hide();
                    Dialog.alert(self, _t('File upload failed. Please try again.'));
                }
            });
        },

        _analyzeDocument: function () {
            var self = this;
            if (!this.record.data.id) return;

            rpc.query({
                model: 'document.analysis',
                method: 'analyze_document',
                args: [this.record.data.id]
            }).then(function (result) {
                if (result.success) {
                    Dialog.alert(self, _t('Document analysis started. You will be notified when complete.'));
                } else {
                    Dialog.alert(self, result.message || _t('Analysis failed to start.'));
                }
            });
        }
    });

    // Register widgets
    fieldRegistry.add('ai_confidence', AIConfidenceWidget);
    fieldRegistry.add('risk_level', RiskLevelWidget);
    fieldRegistry.add('ai_processing_status', AIProcessingStatusWidget);
    fieldRegistry.add('vendor_suggestion_score', VendorSuggestionScoreWidget);
    fieldRegistry.add('ai_analysis_result', AIAnalysisResultWidget);
    fieldRegistry.add('ai_cost_monitor', AICostMonitorWidget);
    fieldRegistry.add('document_analysis', DocumentAnalysisWidget);

    return {
        AIConfidenceWidget: AIConfidenceWidget,
        RiskLevelWidget: RiskLevelWidget,
        AIProcessingStatusWidget: AIProcessingStatusWidget,
        VendorSuggestionScoreWidget: VendorSuggestionScoreWidget,
        AIAnalysisResultWidget: AIAnalysisResultWidget,
        AICostMonitorWidget: AICostMonitorWidget,
        DocumentAnalysisWidget: DocumentAnalysisWidget
    };
});

// QWeb Templates
odoo.define('purchase_ai.templates', function (require) {
    'use strict';

    var core = require('web.core');
    var QWeb = core.qweb;

    QWeb.add_template(`
        <templates>
            <t t-name="AIConfidenceWidget">
                <div class="ai_confidence_display">
                    <span t-att-class="confidenceClass" t-esc="percentage"/>%
                    <div class="ai_progress_bar">
                        <div class="ai_progress_fill" t-att-style="'width: ' + percentage + '%'"/>
                    </div>
                </div>
            </t>

            <t t-name="RiskLevelWidget">
                <span t-att-class="riskClass" t-esc="riskText"/>
            </t>

            <t t-name="AIProcessingStatusWidget">
                <div class="ai_processing_status">
                    <t t-if="showSpinner">
                        <div class="ai_processing_spinner"/>
                    </t>
                    <span t-att-class="statusClass" t-esc="statusText"/>
                </div>
            </t>

            <t t-name="VendorSuggestionScoreWidget">
                <div class="vendor_score_display">
                    <div class="score_header">
                        <span class="score_value" t-esc="percentage"/>%
                        <div class="score_bar">
                            <div t-att-class="'score_fill ' + scoreClass" t-att-style="'width: ' + percentage + '%'"/>
                        </div>
                        <a href="#" class="score_details_toggle">▼</a>
                    </div>
                    <div class="score_details" style="display: none;">
                        <t t-foreach="scores" t-as="score_key">
                            <div class="score_indicator">
                                <span t-esc="score_key.replace('_', ' ').title()"/>:
                                <span class="score_value" t-esc="Math.round(score_value * 100)"/>%
                                <div class="score_bar">
                                    <div class="score_fill" t-att-style="'width: ' + Math.round(score_value * 100) + '%'"/>
                                </div>
                            </div>
                        </t>
                    </div>
                </div>
            </t>

            <t t-name="AIAnalysisResultWidget">
                <div class="ai_analysis_container">
                    <t t-foreach="sections" t-as="section">
                        <div class="analysis_section">
                            <div class="analysis_header">
                                <span t-esc="section.title"/>
                                <a href="#" class="analysis_section_toggle">▼</a>
                            </div>
                            <div class="analysis_content" t-raw="section.content"/>
                        </div>
                    </t>
                </div>
            </t>

            <t t-name="AICostMonitorWidget">
                <div t-att-class="'cost_monitor ' + alertLevel">
                    <span class="cost_icon">💰</span>
                    <div class="cost_text">
                        <div>Cost: $<span t-esc="cost"/> / $<span t-esc="budget"/></div>
                        <div>Usage: <span t-esc="percentage"/>%</div>
                    </div>
                </div>
            </t>

            <t t-name="DocumentAnalysisWidget">
                <div class="document_analysis_container">
                    <input type="file" accept=".pdf,.doc,.docx,.txt,.jpg,.png" style="display: none;"/>
                    <button type="button" class="btn btn-primary" onclick="this.previousElementSibling.click()">
                        Upload Document
                    </button>
                    <div class="upload_progress" style="display: none;">
                        <div class="ai_processing_spinner"/>
                        Uploading...
                    </div>
                    <button t-if="hasDocument" type="button" class="btn btn-success analyze_document_btn" style="display: none;">
                        Analyze Document
                    </button>
                </div>
            </t>
        </templates>
    `);
});

// Main Purchase AI Module
odoo.define('purchase_ai.main', function (require) {
    'use strict';

    var core = require('web.core');
    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');
    var _t = core._t;

    /**
     * Global AI Purchase utilities and functions
     */
    var PurchaseAI = {
        
        /**
         * Generate vendor suggestions for a product
         */
        generateVendorSuggestions: function (productId, requirements) {
            return rpc.query({
                model: 'purchase.vendor.suggestion',
                method: 'generate_suggestions',
                args: [productId],
                kwargs: {
                    requirements: requirements || {}
                }
            });
        },

        /**
         * Trigger risk assessment for a vendor
         */
        assessVendorRisk: function (vendorId, assessmentType) {
            return rpc.query({
                model: 'risk.assessment',
                method: 'create_assessment',
                args: [{
                    vendor_id: vendorId,
                    assessment_type: assessmentType || 'manual'
                }]
            });
        },

        /**
         * Start vendor enrichment process
         */
        enrichVendor: function (vendorId) {
            return rpc.query({
                model: 'vendor.enrichment',
                method: 'start_enrichment',
                args: [vendorId]
            });
        },

        /**
         * Submit feedback for vendor suggestion
         */
        submitFeedback: function (suggestionId, rating, feedback) {
            return rpc.query({
                model: 'vendor.suggestion.feedback',
                method: 'create',
                args: [{
                    suggestion_id: suggestionId,
                    rating: rating,
                    feedback_text: feedback,
                    feedback_type: 'user'
                }]
            });
        },

        /**
         * Get AI service status
         */
        getAIServiceStatus: function () {
            return rpc.query({
                model: 'purchase.ai.service',
                method: 'get_service_status',
                args: []
            });
        },

        /**
         * Test AI service connection
         */
        testAIService: function (serviceId) {
            return rpc.query({
                model: 'purchase.ai.service',
                method: 'test_connection',
                args: [serviceId]
            });
        }
    };

    // Export for global use
    window.PurchaseAI = PurchaseAI;

    return PurchaseAI;
});

// Auto-refresh functionality for real-time updates
odoo.define('purchase_ai.auto_refresh', function (require) {
    'use strict';

    var core = require('web.core');
    var AbstractController = require('web.AbstractController');

    // Extend list controller to add auto-refresh for AI processing queues
    AbstractController.include({
        init: function () {
            this._super.apply(this, arguments);
            this.autoRefreshInterval = null;
            
            // Enable auto-refresh for specific models
            var autoRefreshModels = [
                'ai.processing.queue',
                'vendor.creation.request',
                'vendor.enrichment',
                'risk.assessment'
            ];
            
            if (autoRefreshModels.includes(this.modelName)) {
                this._startAutoRefresh();
            }
        },

        _startAutoRefresh: function () {
            var self = this;
            if (this.autoRefreshInterval) return;
            
            this.autoRefreshInterval = setInterval(function () {
                if (self.renderer && self.renderer.state) {
                    self.reload();
                }
            }, 10000); // Refresh every 10 seconds
        },

        _stopAutoRefresh: function () {
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
                this.autoRefreshInterval = null;
            }
        },

        destroy: function () {
            this._stopAutoRefresh();
            this._super.apply(this, arguments);
        }
    });
}); 