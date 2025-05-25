import { pgTable, text, serial, integer, boolean, timestamp, real } from "drizzle-orm/pg-core";
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
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
  name: true,
  email: true,
  role: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

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
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertTenderSchema = createInsertSchema(tenders).omit({
  id: true,
  createdAt: true,
});

export type InsertTender = z.infer<typeof insertTenderSchema>;
export type Tender = typeof tenders.$inferSelect;

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
