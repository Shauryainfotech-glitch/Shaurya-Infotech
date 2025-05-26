import { pgTable, text, serial, integer, boolean, timestamp, real, date } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// User model with expanded role management
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  name: text("name").notNull(),
  email: text("email").notNull(),
  positionTitle: text("position_title").notNull().default("Tender Executive"), // Role name (e.g., Tender Manager, Executive, Proposal Writer, Legal Officer, etc.)
  department: text("department").notNull().default("Tender Department"),
  reportingManagerId: integer("reporting_manager_id"),
  jobResponsibilities: text("job_responsibilities"),
  notificationPreferences: text("notification_preferences").notNull().default("email"),
  profilePicture: text("profile_picture"),
});

export const insertUserSchema = createInsertSchema(users).omit({
  id: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

// Pipeline stages model
export const pipelineStages = pgTable("pipeline_stages", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description"),
  displayOrder: integer("display_order").notNull(),
  color: text("color").notNull().default("#6366F1"),
});

export const insertPipelineStageSchema = createInsertSchema(pipelineStages).omit({
  id: true,
});

export type InsertPipelineStage = z.infer<typeof insertPipelineStageSchema>;
export type PipelineStage = typeof pipelineStages.$inferSelect;

// Tender model with comprehensive Odoo field mapping
export const tenders = pgTable("tenders", {
  id: serial("id").primaryKey(),
  tenderId: text("tender_id"), // Auto-generated Tender Identifier
  title: text("title").notNull(), // Tender Name
  departmentName: text("department_name").notNull(), // Government department issuing tender
  organization: text("organization").notNull(),
  description: text("description").notNull(),
  tenderType: text("tender_type").notNull().default("Open"), // Open/Limited/GeM/Offline etc.
  value: text("value").notNull(), // Bid Value
  deadline: timestamp("deadline").notNull(), // Final submission date & time
  status: text("status").notNull().default("Draft"), // Draft/Submitted/Awarded/Rejected
  
  // Role assignments based on CSV roles
  assignedUserId: integer("assigned_user_id"), // Tender Executive assigned
  technicalCoordinatorId: integer("technical_coordinator_id"), // Technical Coordinator
  proposalWriterId: integer("proposal_writer_id"), // Proposal Writer
  complianceOfficerId: integer("compliance_officer_id"), // Legal/Compliance Officer
  
  // Submission details
  submissionMethod: text("submission_method").notNull().default("Online"), // Online/Offline/GeM/Email
  tenderSourcePortal: text("tender_source_portal").notNull().default("Manual"), // GeM / CPPP / eProc / TenderTiger / Manual
  tenderClassification: text("tender_classification").notNull().default("Goods"), // Works / Goods / Services / Consultancy
  
  // EMD and compliance
  emdRequired: boolean("emd_required").notNull().default(false),
  emdAmount: real("emd_amount"),
  emdSubmissionMode: text("emd_submission_mode"), // BG / Online Payment / MSME Exemption
  affidavitRequired: boolean("affidavit_required").notNull().default(false),
  
  // Pre-bid details
  preBidMeetingDate: timestamp("pre_bid_meeting_date"),
  preBidAttended: boolean("pre_bid_attended").notNull().default(false),
  corrigendumIssued: boolean("corrigendum_issued").notNull().default(false),
  
  // Post-bid requirements
  postBidRequirement: text("post_bid_requirement"), // Presentation / Technical Demo / Price Negotiation
  bidClarificationNotes: text("bid_clarification_notes"),
  consortiumPartner: text("consortium_partner"),
  
  // Results and awards
  resultDate: date("result_date"), // Expected or actual bid opening date
  workOrderReceived: boolean("work_order_received").notNull().default(false),
  workOrderDate: date("work_order_date"),
  agreementSigned: boolean("agreement_signed").notNull().default(false),
  executionTeamAssignedId: integer("execution_team_assigned_id"),
  
  // Financial details
  tenderBudgetEstimate: real("tender_budget_estimate"),
  finalQuotedPrice: real("final_quoted_price"),
  quotationMargin: real("quotation_margin"), // Profit margin %
  invoiceRaised: boolean("invoice_raised").notNull().default(false),
  paymentReceived: boolean("payment_received").notNull().default(false),
  recoveryLegalStatus: text("recovery_legal_status").notNull().default("Normal"), // Normal / Legal / Arbitration
  
  // AI and analysis fields
  aiScore: integer("ai_score").notNull().default(0),
  eligibility: text("eligibility").notNull().default("Under Review"),
  riskScore: integer("risk_score").notNull().default(50),
  successProbability: integer("success_probability").notNull().default(50),
  competition: text("competition").notNull().default("Medium"),
  predictedMargin: real("predicted_margin").notNull().default(10.0),
  nlpSummary: text("nlp_summary"),
  blockchainVerified: boolean("blockchain_verified").notNull().default(false),
  gptAnalysis: text("gpt_analysis"),
  
  // Pipeline management
  pipelineStageId: integer("pipeline_stage_id"),
  submissionDate: timestamp("submission_date"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertTenderSchema = createInsertSchema(tenders).omit({
  id: true,
  createdAt: true,
});

export type InsertTender = z.infer<typeof insertTenderSchema>;
export type Tender = typeof tenders.$inferSelect;

// Tasks model
export const tasks = pgTable("tasks", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description"),
  status: text("status").notNull().default("Pending"),
  priority: text("priority").notNull().default("Medium"),
  dueDate: timestamp("due_date"),
  assignedUserId: integer("assigned_user_id"),
  tenderId: integer("tender_id"),
  completedAt: timestamp("completed_at"),
  reminderSent: boolean("reminder_sent").notNull().default(false),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertTaskSchema = createInsertSchema(tasks).omit({
  id: true,
  createdAt: true,
  completedAt: true,
});

export type InsertTask = z.infer<typeof insertTaskSchema>;
export type Task = typeof tasks.$inferSelect;

// Firm model
export const firms = pgTable("firms", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  rating: real("rating").notNull().default(0),
  completedProjects: integer("completed_projects").notNull().default(0),
  specialization: text("specialization").notNull(),
  eligibilityScore: integer("eligibility_score").notNull().default(50),
  activeProjects: integer("active_projects").notNull().default(0),
  riskProfile: text("risk_profile").notNull().default("Medium"),
  aiRecommendation: text("ai_recommendation"),
  certifications: text("certifications").array(),
  financialHealth: text("financial_health").notNull().default("Good"),
  marketPosition: text("market_position"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertFirmSchema = createInsertSchema(firms).omit({
  id: true,
  createdAt: true,
});

export type InsertFirm = z.infer<typeof insertFirmSchema>;
export type Firm = typeof firms.$inferSelect;

// Document model
export const documents = pgTable("documents", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  type: text("type").notNull(),
  tenderId: integer("tender_id"),
  firmId: integer("firm_id"),
  content: text("content"),
  ocrText: text("ocr_text"),
  nlpAnalysis: text("nlp_analysis"),
  gptAnalysis: text("gpt_analysis"),
  uploadedAt: timestamp("uploaded_at").notNull().defaultNow(),
});

export const insertDocumentSchema = createInsertSchema(documents).omit({
  id: true,
  uploadedAt: true,
});

export type InsertDocument = z.infer<typeof insertDocumentSchema>;
export type Document = typeof documents.$inferSelect;

// Calendar events model
export const calendarEvents = pgTable("calendar_events", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description"),
  startDate: timestamp("start_date").notNull(),
  endDate: timestamp("end_date").notNull(),
  allDay: boolean("all_day").notNull().default(false),
  location: text("location"),
  userId: integer("user_id"),
  tenderId: integer("tender_id"),
  taskId: integer("task_id"),
  color: text("color").notNull().default("#4F46E5"),
  reminderSent: boolean("reminder_sent").notNull().default(false),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertCalendarEventSchema = createInsertSchema(calendarEvents).omit({
  id: true,
  createdAt: true,
});

export type InsertCalendarEvent = z.infer<typeof insertCalendarEventSchema>;
export type CalendarEvent = typeof calendarEvents.$inferSelect;

// Email notifications model
export const emailNotifications = pgTable("email_notifications", {
  id: serial("id").primaryKey(),
  recipientEmail: text("recipient_email").notNull(),
  subject: text("subject").notNull(),
  body: text("body").notNull(),
  sentAt: timestamp("sent_at"),
  status: text("status").notNull().default("Pending"),
  userId: integer("user_id"),
  tenderId: integer("tender_id"),
  taskId: integer("task_id"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertEmailNotificationSchema = createInsertSchema(emailNotifications).omit({
  id: true,
  sentAt: true,
  createdAt: true,
});

export type InsertEmailNotification = z.infer<typeof insertEmailNotificationSchema>;
export type EmailNotification = typeof emailNotifications.$inferSelect;

// Automation rules model
export const automationRules = pgTable("automation_rules", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description"),
  triggerType: text("trigger_type").notNull(), // e.g., "task_due", "tender_deadline", "stage_change"
  triggerValue: text("trigger_value"), // specific value for the trigger
  actionType: text("action_type").notNull(), // e.g., "create_task", "send_email", "update_stage"
  actionParams: text("action_params").notNull(), // JSON string with parameters for the action
  enabled: boolean("enabled").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertAutomationRuleSchema = createInsertSchema(automationRules).omit({
  id: true,
  createdAt: true,
});

export type InsertAutomationRule = z.infer<typeof insertAutomationRuleSchema>;
export type AutomationRule = typeof automationRules.$inferSelect;

// Performance Rewards model based on CSV parameters
export const performanceRewards = pgTable("performance_rewards", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull(),
  tenderId: integer("tender_id"),
  parameter: text("parameter").notNull(), // e.g., "Tender Submission On-Time", "Tender Win Ratio"
  description: text("description").notNull(),
  applicableRoles: text("applicable_roles").array(), // Roles this applies to
  rewardType: text("reward_type").notNull(), // Cash Bonus / Points / Certificate etc.
  pointsEarned: integer("points_earned").notNull().default(0),
  cashBonus: real("cash_bonus").notNull().default(0),
  achievedDate: timestamp("achieved_date").notNull().defaultNow(),
  quarterYear: text("quarter_year"), // For quarterly tracking
  status: text("status").notNull().default("Earned"), // Earned / Pending / Processed
  notes: text("notes"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertPerformanceRewardSchema = createInsertSchema(performanceRewards).omit({
  id: true,
  createdAt: true,
});

export type InsertPerformanceReward = z.infer<typeof insertPerformanceRewardSchema>;
export type PerformanceReward = typeof performanceRewards.$inferSelect;
