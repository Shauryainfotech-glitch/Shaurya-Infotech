import { db } from "./db";
import { 
  users, firms, tenders, documents, pipelineStages, tasks, 
  calendarEvents, emailNotifications, automationRules,
  type User, type Firm, type Tender, type Document, type PipelineStage,
  type Task, type CalendarEvent, type EmailNotification, type AutomationRule,
  type InsertUser, type InsertFirm, type InsertTender, type InsertDocument,
  type InsertPipelineStage, type InsertTask, type InsertCalendarEvent,
  type InsertEmailNotification, type InsertAutomationRule
} from "@shared/schema";
import { eq, desc } from "drizzle-orm";
import type { IStorage } from "./storage";

export class DatabaseStorage implements IStorage {
  // User methods
  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user || undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user || undefined;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db.insert(users).values(insertUser).returning();
    return user;
  }

  async updateUser(id: number, updates: Partial<InsertUser>): Promise<User | undefined> {
    const [user] = await db.update(users).set(updates).where(eq(users.id, id)).returning();
    return user || undefined;
  }

  async deleteUser(id: number): Promise<boolean> {
    const result = await db.delete(users).where(eq(users.id, id));
    return result.rowCount > 0;
  }

  // Firm methods
  async getFirms(): Promise<Firm[]> {
    return await db.select().from(firms).orderBy(desc(firms.id));
  }

  async getFirm(id: number): Promise<Firm | undefined> {
    const [firm] = await db.select().from(firms).where(eq(firms.id, id));
    return firm || undefined;
  }

  async createFirm(insertFirm: InsertFirm): Promise<Firm> {
    const [firm] = await db.insert(firms).values(insertFirm).returning();
    return firm;
  }

  async updateFirm(id: number, updates: Partial<InsertFirm>): Promise<Firm | undefined> {
    const [firm] = await db.update(firms).set(updates).where(eq(firms.id, id)).returning();
    return firm || undefined;
  }

  async deleteFirm(id: number): Promise<boolean> {
    const result = await db.delete(firms).where(eq(firms.id, id));
    return result.rowCount > 0;
  }

  // Tender methods
  async getTenders(): Promise<Tender[]> {
    return await db.select().from(tenders).orderBy(desc(tenders.id));
  }

  async getTender(id: number): Promise<Tender | undefined> {
    const [tender] = await db.select().from(tenders).where(eq(tenders.id, id));
    return tender || undefined;
  }

  async createTender(insertTender: InsertTender): Promise<Tender> {
    const [tender] = await db.insert(tenders).values(insertTender).returning();
    return tender;
  }

  async updateTender(id: number, updates: Partial<InsertTender>): Promise<Tender | undefined> {
    const [tender] = await db.update(tenders).set(updates).where(eq(tenders.id, id)).returning();
    return tender || undefined;
  }

  async deleteTender(id: number): Promise<boolean> {
    const result = await db.delete(tenders).where(eq(tenders.id, id));
    return result.rowCount > 0;
  }

  // Document methods
  async getDocuments(): Promise<Document[]> {
    return await db.select().from(documents).orderBy(desc(documents.id));
  }

  async getDocument(id: number): Promise<Document | undefined> {
    const [document] = await db.select().from(documents).where(eq(documents.id, id));
    return document || undefined;
  }

  async createDocument(insertDocument: InsertDocument): Promise<Document> {
    const [document] = await db.insert(documents).values(insertDocument).returning();
    return document;
  }

  async updateDocument(id: number, updates: Partial<InsertDocument>): Promise<Document | undefined> {
    const [document] = await db.update(documents).set(updates).where(eq(documents.id, id)).returning();
    return document || undefined;
  }

  async deleteDocument(id: number): Promise<boolean> {
    const result = await db.delete(documents).where(eq(documents.id, id));
    return result.rowCount > 0;
  }

  // Pipeline Stage methods
  async getPipelineStages(): Promise<PipelineStage[]> {
    return await db.select().from(pipelineStages).orderBy(desc(pipelineStages.id));
  }

  async getPipelineStage(id: number): Promise<PipelineStage | undefined> {
    const [stage] = await db.select().from(pipelineStages).where(eq(pipelineStages.id, id));
    return stage || undefined;
  }

  async createPipelineStage(insertStage: InsertPipelineStage): Promise<PipelineStage> {
    const [stage] = await db.insert(pipelineStages).values(insertStage).returning();
    return stage;
  }

  async updatePipelineStage(id: number, updates: Partial<InsertPipelineStage>): Promise<PipelineStage | undefined> {
    const [stage] = await db.update(pipelineStages).set(updates).where(eq(pipelineStages.id, id)).returning();
    return stage || undefined;
  }

  async deletePipelineStage(id: number): Promise<boolean> {
    const result = await db.delete(pipelineStages).where(eq(pipelineStages.id, id));
    return result.rowCount > 0;
  }

  // Task methods
  async getTasks(): Promise<Task[]> {
    return await db.select().from(tasks).orderBy(desc(tasks.id));
  }

  async getTask(id: number): Promise<Task | undefined> {
    const [task] = await db.select().from(tasks).where(eq(tasks.id, id));
    return task || undefined;
  }

  async createTask(insertTask: InsertTask): Promise<Task> {
    const [task] = await db.insert(tasks).values(insertTask).returning();
    return task;
  }

  async updateTask(id: number, updates: Partial<InsertTask>): Promise<Task | undefined> {
    const [task] = await db.update(tasks).set(updates).where(eq(tasks.id, id)).returning();
    return task || undefined;
  }

  async deleteTask(id: number): Promise<boolean> {
    const result = await db.delete(tasks).where(eq(tasks.id, id));
    return result.rowCount > 0;
  }

  // Calendar Event methods
  async getCalendarEvents(): Promise<CalendarEvent[]> {
    return await db.select().from(calendarEvents).orderBy(desc(calendarEvents.id));
  }

  async getCalendarEvent(id: number): Promise<CalendarEvent | undefined> {
    const [event] = await db.select().from(calendarEvents).where(eq(calendarEvents.id, id));
    return event || undefined;
  }

  async createCalendarEvent(insertEvent: InsertCalendarEvent): Promise<CalendarEvent> {
    const [event] = await db.insert(calendarEvents).values(insertEvent).returning();
    return event;
  }

  async updateCalendarEvent(id: number, updates: Partial<InsertCalendarEvent>): Promise<CalendarEvent | undefined> {
    const [event] = await db.update(calendarEvents).set(updates).where(eq(calendarEvents.id, id)).returning();
    return event || undefined;
  }

  async deleteCalendarEvent(id: number): Promise<boolean> {
    const result = await db.delete(calendarEvents).where(eq(calendarEvents.id, id));
    return result.rowCount > 0;
  }

  // Email Notification methods
  async getEmailNotifications(): Promise<EmailNotification[]> {
    return await db.select().from(emailNotifications).orderBy(desc(emailNotifications.id));
  }

  async getEmailNotification(id: number): Promise<EmailNotification | undefined> {
    const [notification] = await db.select().from(emailNotifications).where(eq(emailNotifications.id, id));
    return notification || undefined;
  }

  async createEmailNotification(insertNotification: InsertEmailNotification): Promise<EmailNotification> {
    const [notification] = await db.insert(emailNotifications).values(insertNotification).returning();
    return notification;
  }

  async updateEmailNotification(id: number, updates: Partial<InsertEmailNotification>): Promise<EmailNotification | undefined> {
    const [notification] = await db.update(emailNotifications).set(updates).where(eq(emailNotifications.id, id)).returning();
    return notification || undefined;
  }

  async deleteEmailNotification(id: number): Promise<boolean> {
    const result = await db.delete(emailNotifications).where(eq(emailNotifications.id, id));
    return result.rowCount > 0;
  }

  // Automation Rule methods
  async getAutomationRules(): Promise<AutomationRule[]> {
    return await db.select().from(automationRules).orderBy(desc(automationRules.id));
  }

  async getAutomationRule(id: number): Promise<AutomationRule | undefined> {
    const [rule] = await db.select().from(automationRules).where(eq(automationRules.id, id));
    return rule || undefined;
  }

  async createAutomationRule(insertRule: InsertAutomationRule): Promise<AutomationRule> {
    const [rule] = await db.insert(automationRules).values(insertRule).returning();
    return rule;
  }

  async updateAutomationRule(id: number, updates: Partial<InsertAutomationRule>): Promise<AutomationRule | undefined> {
    const [rule] = await db.update(automationRules).set(updates).where(eq(automationRules.id, id)).returning();
    return rule || undefined;
  }

  async deleteAutomationRule(id: number): Promise<boolean> {
    const result = await db.delete(automationRules).where(eq(automationRules.id, id));
    return result.rowCount > 0;
  }
}