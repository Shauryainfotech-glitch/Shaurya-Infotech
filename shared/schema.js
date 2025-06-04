"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.insertDocumentFolderSchema = exports.documentFolders = exports.insertWebhookEventSchema = exports.webhookEvents = exports.insertApiIntegrationSchema = exports.apiIntegrations = exports.insertPerformanceRewardSchema = exports.performanceRewards = exports.insertAutomationRuleSchema = exports.automationRules = exports.insertEmailNotificationSchema = exports.emailNotifications = exports.insertCalendarEventSchema = exports.calendarEvents = exports.insertDocumentSchema = exports.documents = exports.insertFirmDocumentSchema = exports.firmDocuments = exports.insertFirmSchema = exports.firms = exports.insertTaskSchema = exports.tasks = exports.insertTenderSchema = exports.tenders = exports.insertPipelineStageSchema = exports.pipelineStages = exports.insertUserSchema = exports.users = void 0;
const pg_core_1 = require("drizzle-orm/pg-core");
const drizzle_zod_1 = require("drizzle-zod");
// User model with expanded role management
exports.users = (0, pg_core_1.pgTable)("users", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    username: (0, pg_core_1.text)("username").notNull().unique(),
    password: (0, pg_core_1.text)("password").notNull(),
    name: (0, pg_core_1.text)("name").notNull(),
    email: (0, pg_core_1.text)("email").notNull(),
    positionTitle: (0, pg_core_1.text)("position_title").notNull().default("Tender Executive"), // Role name (e.g., Tender Manager, Executive, Proposal Writer, Legal Officer, etc.)
    department: (0, pg_core_1.text)("department").notNull().default("Tender Department"),
    reportingManagerId: (0, pg_core_1.integer)("reporting_manager_id"),
    jobResponsibilities: (0, pg_core_1.text)("job_responsibilities"),
    notificationPreferences: (0, pg_core_1.text)("notification_preferences").notNull().default("email"),
    profilePicture: (0, pg_core_1.text)("profile_picture"),
});
exports.insertUserSchema = (0, drizzle_zod_1.createInsertSchema)(exports.users).omit({
    id: true,
});
// Pipeline stages model
exports.pipelineStages = (0, pg_core_1.pgTable)("pipeline_stages", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    name: (0, pg_core_1.text)("name").notNull(),
    description: (0, pg_core_1.text)("description"),
    displayOrder: (0, pg_core_1.integer)("display_order").notNull(),
    color: (0, pg_core_1.text)("color").notNull().default("#6366F1"),
});
exports.insertPipelineStageSchema = (0, drizzle_zod_1.createInsertSchema)(exports.pipelineStages).omit({
    id: true,
});
// Tender model with comprehensive Odoo field mapping
exports.tenders = (0, pg_core_1.pgTable)("tenders", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    tenderId: (0, pg_core_1.text)("tender_id"), // Auto-generated Tender Identifier
    title: (0, pg_core_1.text)("title").notNull(), // Tender Name
    departmentName: (0, pg_core_1.text)("department_name").notNull(), // Government department issuing tender
    organization: (0, pg_core_1.text)("organization").notNull(),
    description: (0, pg_core_1.text)("description").notNull(),
    tenderType: (0, pg_core_1.text)("tender_type").notNull().default("Open"), // Open/Limited/GeM/Offline etc.
    value: (0, pg_core_1.text)("value").notNull(), // Bid Value
    deadline: (0, pg_core_1.timestamp)("deadline").notNull(), // Final submission date & time
    status: (0, pg_core_1.text)("status").notNull().default("Draft"), // Draft/Submitted/Awarded/Rejected
    // Role assignments based on CSV roles
    assignedUserId: (0, pg_core_1.integer)("assigned_user_id"), // Tender Executive assigned
    technicalCoordinatorId: (0, pg_core_1.integer)("technical_coordinator_id"), // Technical Coordinator
    proposalWriterId: (0, pg_core_1.integer)("proposal_writer_id"), // Proposal Writer
    complianceOfficerId: (0, pg_core_1.integer)("compliance_officer_id"), // Legal/Compliance Officer
    // Submission details
    submissionMethod: (0, pg_core_1.text)("submission_method").notNull().default("Online"), // Online/Offline/GeM/Email
    tenderSourcePortal: (0, pg_core_1.text)("tender_source_portal").notNull().default("Manual"), // GeM / CPPP / eProc / TenderTiger / Manual
    tenderClassification: (0, pg_core_1.text)("tender_classification").notNull().default("Goods"), // Works / Goods / Services / Consultancy
    // EMD and compliance
    emdRequired: (0, pg_core_1.boolean)("emd_required").notNull().default(false),
    emdAmount: (0, pg_core_1.real)("emd_amount"),
    emdSubmissionMode: (0, pg_core_1.text)("emd_submission_mode"), // BG / Online Payment / MSME Exemption
    affidavitRequired: (0, pg_core_1.boolean)("affidavit_required").notNull().default(false),
    // Pre-bid details
    preBidMeetingDate: (0, pg_core_1.timestamp)("pre_bid_meeting_date"),
    preBidAttended: (0, pg_core_1.boolean)("pre_bid_attended").notNull().default(false),
    corrigendumIssued: (0, pg_core_1.boolean)("corrigendum_issued").notNull().default(false),
    // Post-bid requirements
    postBidRequirement: (0, pg_core_1.text)("post_bid_requirement"), // Presentation / Technical Demo / Price Negotiation
    bidClarificationNotes: (0, pg_core_1.text)("bid_clarification_notes"),
    consortiumPartner: (0, pg_core_1.text)("consortium_partner"),
    // Results and awards
    resultDate: (0, pg_core_1.date)("result_date"), // Expected or actual bid opening date
    workOrderReceived: (0, pg_core_1.boolean)("work_order_received").notNull().default(false),
    workOrderDate: (0, pg_core_1.date)("work_order_date"),
    agreementSigned: (0, pg_core_1.boolean)("agreement_signed").notNull().default(false),
    executionTeamAssignedId: (0, pg_core_1.integer)("execution_team_assigned_id"),
    // Financial details
    tenderBudgetEstimate: (0, pg_core_1.real)("tender_budget_estimate"),
    finalQuotedPrice: (0, pg_core_1.real)("final_quoted_price"),
    quotationMargin: (0, pg_core_1.real)("quotation_margin"), // Profit margin %
    invoiceRaised: (0, pg_core_1.boolean)("invoice_raised").notNull().default(false),
    paymentReceived: (0, pg_core_1.boolean)("payment_received").notNull().default(false),
    recoveryLegalStatus: (0, pg_core_1.text)("recovery_legal_status").notNull().default("Normal"), // Normal / Legal / Arbitration
    // AI and analysis fields
    aiScore: (0, pg_core_1.integer)("ai_score").notNull().default(0),
    eligibility: (0, pg_core_1.text)("eligibility").notNull().default("Under Review"),
    riskScore: (0, pg_core_1.integer)("risk_score").notNull().default(50),
    successProbability: (0, pg_core_1.integer)("success_probability").notNull().default(50),
    competition: (0, pg_core_1.text)("competition").notNull().default("Medium"),
    predictedMargin: (0, pg_core_1.real)("predicted_margin").notNull().default(10.0),
    nlpSummary: (0, pg_core_1.text)("nlp_summary"),
    blockchainVerified: (0, pg_core_1.boolean)("blockchain_verified").notNull().default(false),
    gptAnalysis: (0, pg_core_1.text)("gpt_analysis"),
    // Pipeline management
    pipelineStageId: (0, pg_core_1.integer)("pipeline_stage_id"),
    submissionDate: (0, pg_core_1.timestamp)("submission_date"),
    createdAt: (0, pg_core_1.timestamp)("created_at").notNull().defaultNow(),
});
exports.insertTenderSchema = (0, drizzle_zod_1.createInsertSchema)(exports.tenders).omit({
    id: true,
    createdAt: true,
});
// Tasks model
exports.tasks = (0, pg_core_1.pgTable)("tasks", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    title: (0, pg_core_1.text)("title").notNull(),
    description: (0, pg_core_1.text)("description"),
    status: (0, pg_core_1.text)("status").notNull().default("Pending"),
    priority: (0, pg_core_1.text)("priority").notNull().default("Medium"),
    dueDate: (0, pg_core_1.timestamp)("due_date"),
    assignedUserId: (0, pg_core_1.integer)("assigned_user_id"),
    tenderId: (0, pg_core_1.integer)("tender_id"),
    completedAt: (0, pg_core_1.timestamp)("completed_at"),
    reminderSent: (0, pg_core_1.boolean)("reminder_sent").notNull().default(false),
    createdAt: (0, pg_core_1.timestamp)("created_at").notNull().defaultNow(),
});
exports.insertTaskSchema = (0, drizzle_zod_1.createInsertSchema)(exports.tasks).omit({
    id: true,
    createdAt: true,
    completedAt: true,
});
// Firm model
exports.firms = (0, pg_core_1.pgTable)("firms", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    name: (0, pg_core_1.text)("name").notNull(),
    rating: (0, pg_core_1.real)("rating").notNull().default(0),
    completedProjects: (0, pg_core_1.integer)("completed_projects").notNull().default(0),
    specialization: (0, pg_core_1.text)("specialization").notNull(),
    eligibilityScore: (0, pg_core_1.integer)("eligibility_score").notNull().default(50),
    activeProjects: (0, pg_core_1.integer)("active_projects").notNull().default(0),
    riskProfile: (0, pg_core_1.text)("risk_profile").notNull().default("Medium"),
    aiRecommendation: (0, pg_core_1.text)("ai_recommendation"),
    certifications: (0, pg_core_1.text)("certifications").array(),
    financialHealth: (0, pg_core_1.text)("financial_health").notNull().default("Good"),
    marketPosition: (0, pg_core_1.text)("market_position"),
    createdAt: (0, pg_core_1.timestamp)("created_at").notNull().defaultNow(),
});
exports.insertFirmSchema = (0, drizzle_zod_1.createInsertSchema)(exports.firms).omit({
    id: true,
    createdAt: true,
});
// Firm Document Management System
exports.firmDocuments = (0, pg_core_1.pgTable)("firm_documents", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    firmId: (0, pg_core_1.integer)("firm_id").notNull(),
    // Document Categories
    category: (0, pg_core_1.text)("category").notNull(), // Basic Documents, Advance Document, Authorization Document, etc.
    documentName: (0, pg_core_1.text)("document_name").notNull(),
    documentNumber: (0, pg_core_1.text)("document_number"),
    // Status and Validity
    status: (0, pg_core_1.text)("status").notNull().default("Not Available"), // Available, Not Available, Checking, Waiting for, etc.
    validity: (0, pg_core_1.text)("validity"), // NA, date string, or validity period
    renewal: (0, pg_core_1.text)("renewal").notNull().default("NA"), // NA, Every Year Update, Monthly, etc.
    // Responsibility and Management
    responsible: (0, pg_core_1.text)("responsible"), // Pranali, Viresh Sir, etc.
    charges: (0, pg_core_1.text)("charges"), // Fee amounts
    duration: (0, pg_core_1.text)("duration"), // Processing duration
    challenges: (0, pg_core_1.text)("challenges"), // Implementation challenges
    support: (0, pg_core_1.text)("support"), // Required support
    timeline: (0, pg_core_1.text)("timeline"), // Expected timeline
    // Document specific fields
    certificateNumber: (0, pg_core_1.text)("certificate_number"), // For certificates
    issuingAuthority: (0, pg_core_1.text)("issuing_authority"),
    expiryDate: (0, pg_core_1.date)("expiry_date"),
    renewalDate: (0, pg_core_1.date)("renewal_date"),
    // File management
    filePath: (0, pg_core_1.text)("file_path"),
    fileSize: (0, pg_core_1.integer)("file_size"),
    uploadedAt: (0, pg_core_1.timestamp)("uploaded_at"),
    // Tracking
    lastUpdated: (0, pg_core_1.timestamp)("last_updated").defaultNow(),
    createdAt: (0, pg_core_1.timestamp)("created_at").defaultNow(),
    // Additional metadata
    priority: (0, pg_core_1.text)("priority").notNull().default("Medium"), // High, Medium, Low
    complianceRequired: (0, pg_core_1.boolean)("compliance_required").notNull().default(false),
    reminderDays: (0, pg_core_1.integer)("reminder_days").default(30), // Days before expiry to remind
    notes: (0, pg_core_1.text)("notes")
});
exports.insertFirmDocumentSchema = (0, drizzle_zod_1.createInsertSchema)(exports.firmDocuments).omit({
    id: true,
    createdAt: true,
    lastUpdated: true
});
// Enhanced Document Management model with Google Drive integration
exports.documents = (0, pg_core_1.pgTable)("documents", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    name: (0, pg_core_1.text)("name").notNull(),
    originalFileName: (0, pg_core_1.text)("original_file_name").notNull(),
    fileSize: (0, pg_core_1.integer)("file_size"), // File size in bytes
    mimeType: (0, pg_core_1.text)("mime_type").notNull(),
    // Document categorization based on Odoo CSV mapping
    documentType: (0, pg_core_1.text)("document_type").notNull(), // Proposal Document, Affidavit/Declaration, Test Reports, etc.
    documentCategory: (0, pg_core_1.text)("document_category").notNull().default("General"), // Technical, Compliance, Financial, Legal
    // Linking to tenders and entities
    tenderId: (0, pg_core_1.integer)("tender_id"),
    firmId: (0, pg_core_1.integer)("firm_id"),
    userId: (0, pg_core_1.integer)("user_id"), // Who uploaded the document
    // Google Drive integration
    googleDriveFileId: (0, pg_core_1.text)("google_drive_file_id"), // Google Drive file ID
    googleDriveUrl: (0, pg_core_1.text)("google_drive_url"), // Direct Google Drive URL
    googleDriveFolderId: (0, pg_core_1.text)("google_drive_folder_id"), // Parent folder ID
    drivePermissions: (0, pg_core_1.text)("drive_permissions").array(), // List of permissions
    // Local storage backup
    localFilePath: (0, pg_core_1.text)("local_file_path"), // Local backup path
    cloudStorageUrl: (0, pg_core_1.text)("cloud_storage_url"), // Alternative cloud storage
    // Document processing and analysis
    content: (0, pg_core_1.text)("content"), // Extracted text content
    ocrText: (0, pg_core_1.text)("ocr_text"), // OCR extracted text
    nlpAnalysis: (0, pg_core_1.text)("nlp_analysis"), // NLP processing results
    gptAnalysis: (0, pg_core_1.text)("gpt_analysis"), // AI analysis
    extractedMetadata: (0, pg_core_1.text)("extracted_metadata"), // JSON metadata
    // Document status and validation
    status: (0, pg_core_1.text)("status").notNull().default("Uploaded"), // Uploaded, Processing, Verified, Rejected
    isVerified: (0, pg_core_1.boolean)("is_verified").notNull().default(false),
    verificationNotes: (0, pg_core_1.text)("verification_notes"),
    verifiedBy: (0, pg_core_1.integer)("verified_by"), // User ID who verified
    verifiedAt: (0, pg_core_1.timestamp)("verified_at"),
    // Compliance and legal tracking
    complianceStatus: (0, pg_core_1.text)("compliance_status").notNull().default("Pending"), // Compliant, Non-compliant, Under Review
    legalReview: (0, pg_core_1.boolean)("legal_review").notNull().default(false),
    legalNotes: (0, pg_core_1.text)("legal_notes"),
    expiryDate: (0, pg_core_1.date)("expiry_date"), // For certificates and time-bound documents
    // Version control
    version: (0, pg_core_1.text)("version").notNull().default("1.0"),
    previousVersionId: (0, pg_core_1.integer)("previous_version_id"), // Link to previous version
    isLatestVersion: (0, pg_core_1.boolean)("is_latest_version").notNull().default(true),
    // Access and security
    accessLevel: (0, pg_core_1.text)("access_level").notNull().default("Internal"), // Public, Internal, Confidential, Restricted
    downloadCount: (0, pg_core_1.integer)("download_count").notNull().default(0),
    lastAccessedAt: (0, pg_core_1.timestamp)("last_accessed_at"),
    // Integration tracking
    syncStatus: (0, pg_core_1.text)("sync_status").notNull().default("Synced"), // Synced, Pending, Failed
    lastSyncAt: (0, pg_core_1.timestamp)("last_sync_at"),
    syncErrors: (0, pg_core_1.text)("sync_errors"),
    // Timestamps
    uploadedAt: (0, pg_core_1.timestamp)("uploaded_at").notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)("updated_at").notNull().defaultNow(),
});
exports.insertDocumentSchema = (0, drizzle_zod_1.createInsertSchema)(exports.documents).omit({
    id: true,
    uploadedAt: true,
});
// Calendar events model
exports.calendarEvents = (0, pg_core_1.pgTable)("calendar_events", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    title: (0, pg_core_1.text)("title").notNull(),
    description: (0, pg_core_1.text)("description"),
    startDate: (0, pg_core_1.timestamp)("start_date").notNull(),
    endDate: (0, pg_core_1.timestamp)("end_date").notNull(),
    allDay: (0, pg_core_1.boolean)("all_day").notNull().default(false),
    location: (0, pg_core_1.text)("location"),
    userId: (0, pg_core_1.integer)("user_id"),
    tenderId: (0, pg_core_1.integer)("tender_id"),
    taskId: (0, pg_core_1.integer)("task_id"),
    color: (0, pg_core_1.text)("color").notNull().default("#4F46E5"),
    reminderSent: (0, pg_core_1.boolean)("reminder_sent").notNull().default(false),
    createdAt: (0, pg_core_1.timestamp)("created_at").notNull().defaultNow(),
});
exports.insertCalendarEventSchema = (0, drizzle_zod_1.createInsertSchema)(exports.calendarEvents).omit({
    id: true,
    createdAt: true,
});
// Email notifications model
exports.emailNotifications = (0, pg_core_1.pgTable)("email_notifications", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    recipientEmail: (0, pg_core_1.text)("recipient_email").notNull(),
    subject: (0, pg_core_1.text)("subject").notNull(),
    body: (0, pg_core_1.text)("body").notNull(),
    sentAt: (0, pg_core_1.timestamp)("sent_at"),
    status: (0, pg_core_1.text)("status").notNull().default("Pending"),
    userId: (0, pg_core_1.integer)("user_id"),
    tenderId: (0, pg_core_1.integer)("tender_id"),
    taskId: (0, pg_core_1.integer)("task_id"),
    createdAt: (0, pg_core_1.timestamp)("created_at").notNull().defaultNow(),
});
exports.insertEmailNotificationSchema = (0, drizzle_zod_1.createInsertSchema)(exports.emailNotifications).omit({
    id: true,
    sentAt: true,
    createdAt: true,
});
// Automation rules model
exports.automationRules = (0, pg_core_1.pgTable)("automation_rules", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    name: (0, pg_core_1.text)("name").notNull(),
    description: (0, pg_core_1.text)("description"),
    triggerType: (0, pg_core_1.text)("trigger_type").notNull(), // e.g., "task_due", "tender_deadline", "stage_change"
    triggerValue: (0, pg_core_1.text)("trigger_value"), // specific value for the trigger
    actionType: (0, pg_core_1.text)("action_type").notNull(), // e.g., "create_task", "send_email", "update_stage"
    actionParams: (0, pg_core_1.text)("action_params").notNull(), // JSON string with parameters for the action
    enabled: (0, pg_core_1.boolean)("enabled").notNull().default(true),
    createdAt: (0, pg_core_1.timestamp)("created_at").notNull().defaultNow(),
});
exports.insertAutomationRuleSchema = (0, drizzle_zod_1.createInsertSchema)(exports.automationRules).omit({
    id: true,
    createdAt: true,
});
// Performance Rewards model based on CSV parameters
exports.performanceRewards = (0, pg_core_1.pgTable)("performance_rewards", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    userId: (0, pg_core_1.integer)("user_id").notNull(),
    tenderId: (0, pg_core_1.integer)("tender_id"),
    parameter: (0, pg_core_1.text)("parameter").notNull(), // e.g., "Tender Submission On-Time", "Tender Win Ratio"
    description: (0, pg_core_1.text)("description").notNull(),
    applicableRoles: (0, pg_core_1.text)("applicable_roles").array(), // Roles this applies to
    rewardType: (0, pg_core_1.text)("reward_type").notNull(), // Cash Bonus / Points / Certificate etc.
    pointsEarned: (0, pg_core_1.integer)("points_earned").notNull().default(0),
    cashBonus: (0, pg_core_1.real)("cash_bonus").notNull().default(0),
    achievedDate: (0, pg_core_1.timestamp)("achieved_date").notNull().defaultNow(),
    quarterYear: (0, pg_core_1.text)("quarter_year"), // For quarterly tracking
    status: (0, pg_core_1.text)("status").notNull().default("Earned"), // Earned / Pending / Processed
    notes: (0, pg_core_1.text)("notes"),
    createdAt: (0, pg_core_1.timestamp)("created_at").notNull().defaultNow(),
});
exports.insertPerformanceRewardSchema = (0, drizzle_zod_1.createInsertSchema)(exports.performanceRewards).omit({
    id: true,
    createdAt: true,
});
// API Integration Hooks for inbound and outbound integrations
exports.apiIntegrations = (0, pg_core_1.pgTable)("api_integrations", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    name: (0, pg_core_1.text)("name").notNull(), // Integration name (Google Drive, Webhook, External API)
    type: (0, pg_core_1.text)("type").notNull(), // inbound, outbound, bidirectional
    endpoint: (0, pg_core_1.text)("endpoint").notNull(), // API endpoint URL
    method: (0, pg_core_1.text)("method").notNull().default("POST"), // HTTP method
    // Authentication and security
    authType: (0, pg_core_1.text)("auth_type").notNull().default("bearer"), // bearer, oauth, apikey, basic
    apiKey: (0, pg_core_1.text)("api_key"), // Encrypted API key
    accessToken: (0, pg_core_1.text)("access_token"), // OAuth access token
    refreshToken: (0, pg_core_1.text)("refresh_token"), // OAuth refresh token
    tokenExpiresAt: (0, pg_core_1.timestamp)("token_expires_at"),
    // Integration configuration
    config: (0, pg_core_1.text)("config"), // JSON configuration
    headers: (0, pg_core_1.text)("headers"), // JSON headers
    isActive: (0, pg_core_1.boolean)("is_active").notNull().default(true),
    // Monitoring and tracking
    lastExecuted: (0, pg_core_1.timestamp)("last_executed"),
    executionCount: (0, pg_core_1.integer)("execution_count").notNull().default(0),
    successCount: (0, pg_core_1.integer)("success_count").notNull().default(0),
    errorCount: (0, pg_core_1.integer)("error_count").notNull().default(0),
    lastError: (0, pg_core_1.text)("last_error"),
    // Rate limiting
    rateLimit: (0, pg_core_1.integer)("rate_limit").notNull().default(100), // Requests per hour
    rateLimitWindow: (0, pg_core_1.integer)("rate_limit_window").notNull().default(3600), // Window in seconds
    createdAt: (0, pg_core_1.timestamp)("created_at").notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)("updated_at").notNull().defaultNow(),
});
exports.insertApiIntegrationSchema = (0, drizzle_zod_1.createInsertSchema)(exports.apiIntegrations).omit({
    id: true,
    createdAt: true,
    updatedAt: true,
});
// Webhook Events for real-time integrations
exports.webhookEvents = (0, pg_core_1.pgTable)("webhook_events", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    integrationId: (0, pg_core_1.integer)("integration_id").notNull(),
    eventType: (0, pg_core_1.text)("event_type").notNull(), // tender_created, document_uploaded, status_changed
    entityType: (0, pg_core_1.text)("entity_type").notNull(), // tender, document, task, etc.
    entityId: (0, pg_core_1.integer)("entity_id").notNull(),
    // Payload and processing
    payload: (0, pg_core_1.text)("payload").notNull(), // JSON payload
    response: (0, pg_core_1.text)("response"), // Response from webhook
    status: (0, pg_core_1.text)("status").notNull().default("pending"), // pending, success, failed, retrying
    // Retry mechanism
    retryCount: (0, pg_core_1.integer)("retry_count").notNull().default(0),
    maxRetries: (0, pg_core_1.integer)("max_retries").notNull().default(3),
    nextRetryAt: (0, pg_core_1.timestamp)("next_retry_at"),
    // Timestamps
    triggeredAt: (0, pg_core_1.timestamp)("triggered_at").notNull().defaultNow(),
    processedAt: (0, pg_core_1.timestamp)("processed_at"),
    completedAt: (0, pg_core_1.timestamp)("completed_at"),
});
exports.insertWebhookEventSchema = (0, drizzle_zod_1.createInsertSchema)(exports.webhookEvents).omit({
    id: true,
    triggeredAt: true,
});
// Document Folders for organizing Google Drive structure
exports.documentFolders = (0, pg_core_1.pgTable)("document_folders", {
    id: (0, pg_core_1.serial)("id").primaryKey(),
    name: (0, pg_core_1.text)("name").notNull(),
    description: (0, pg_core_1.text)("description"),
    parentFolderId: (0, pg_core_1.integer)("parent_folder_id"),
    // Google Drive integration
    googleDriveFolderId: (0, pg_core_1.text)("google_drive_folder_id"),
    googleDriveUrl: (0, pg_core_1.text)("google_drive_url"),
    // Organization
    tenderId: (0, pg_core_1.integer)("tender_id"), // Link to specific tender
    folderType: (0, pg_core_1.text)("folder_type").notNull().default("general"), // tender, compliance, technical, financial
    accessLevel: (0, pg_core_1.text)("access_level").notNull().default("internal"), // public, internal, restricted
    // Permissions
    allowedRoles: (0, pg_core_1.text)("allowed_roles").array(), // Roles that can access this folder
    ownerId: (0, pg_core_1.integer)("owner_id").notNull(),
    // Status
    isActive: (0, pg_core_1.boolean)("is_active").notNull().default(true),
    syncStatus: (0, pg_core_1.text)("sync_status").notNull().default("synced"),
    createdAt: (0, pg_core_1.timestamp)("created_at").notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)("updated_at").notNull().defaultNow(),
});
exports.insertDocumentFolderSchema = (0, drizzle_zod_1.createInsertSchema)(exports.documentFolders).omit({
    id: true,
    createdAt: true,
    updatedAt: true,
});
