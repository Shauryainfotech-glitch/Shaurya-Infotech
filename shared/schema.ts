import { pgTable, text, serial, integer, boolean, timestamp, real, date } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// User model
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  name: text("name").notNull(),
  email: text("email").notNull(),
  role: text("role").notNull().default("user"),
  notificationPreferences: text("notification_preferences").notNull().default("email"),
  profilePicture: text("profile_picture"),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
  name: true,
  email: true,
  role: true,
  notificationPreferences: true,
  profilePicture: true,
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

// Tender model
export const tenders = pgTable("tenders", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  organization: text("organization").notNull(),
  description: text("description").notNull(),
  value: text("value").notNull(),
  deadline: text("deadline").notNull(),
  status: text("status").notNull().default("Active"),
  aiScore: integer("ai_score").notNull().default(0),
  eligibility: text("eligibility").notNull().default("Under Review"),
  gemId: text("gem_id"),
  riskScore: integer("risk_score").notNull().default(50),
  successProbability: integer("success_probability").notNull().default(50),
  competition: text("competition").notNull().default("Medium"),
  predictedMargin: real("predicted_margin").notNull().default(10.0),
  nlpSummary: text("nlp_summary"),
  blockchainVerified: boolean("blockchain_verified").notNull().default(false),
  gptAnalysis: text("gpt_analysis"),
  pipelineStageId: integer("pipeline_stage_id"),
  assignedUserId: integer("assigned_user_id"),
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
