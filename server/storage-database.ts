import { db } from "./db";
import { eq } from "drizzle-orm";
import { 
  users, type User, type InsertUser,
  tenders, type Tender, type InsertTender,
  firms, type Firm, type InsertFirm,
  firmDocuments, type FirmDocument, type InsertFirmDocument,
  documents, type Document, type InsertDocument,
  pipelineStages, type PipelineStage, type InsertPipelineStage,
  tasks, type Task, type InsertTask,
  calendarEvents, type CalendarEvent, type InsertCalendarEvent,
  emailNotifications, type EmailNotification, type InsertEmailNotification,
  automationRules, type AutomationRule, type InsertAutomationRule
} from "@shared/schema";
import type { IStorage } from "./storage";

export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db
      .insert(users)
      .values(insertUser)
      .returning();
    return user;
  }

  async getTender(id: number): Promise<Tender | undefined> {
    const [tender] = await db.select().from(tenders).where(eq(tenders.id, id));
    return tender;
  }

  async getAllTenders(): Promise<Tender[]> {
    return await db.select().from(tenders);
  }

  async createTender(tender: InsertTender): Promise<Tender> {
    const [newTender] = await db
      .insert(tenders)
      .values(tender)
      .returning();
    return newTender;
  }

  async updateTender(id: number, tender: InsertTender): Promise<Tender | undefined> {
    const [updatedTender] = await db
      .update(tenders)
      .set(tender)
      .where(eq(tenders.id, id))
      .returning();
    return updatedTender;
  }

  async deleteTender(id: number): Promise<boolean> {
    const result = await db.delete(tenders).where(eq(tenders.id, id));
    return result.rowCount > 0;
  }

  async getFirm(id: number): Promise<Firm | undefined> {
    const [firm] = await db.select().from(firms).where(eq(firms.id, id));
    return firm;
  }

  async getAllFirms(): Promise<Firm[]> {
    return await db.select().from(firms);
  }

  async createFirm(firm: InsertFirm): Promise<Firm> {
    const [newFirm] = await db
      .insert(firms)
      .values(firm)
      .returning();
    return newFirm;
  }

  async updateFirm(id: number, firm: InsertFirm): Promise<Firm | undefined> {
    const [updatedFirm] = await db
      .update(firms)
      .set(firm)
      .where(eq(firms.id, id))
      .returning();
    return updatedFirm;
  }

  async deleteFirm(id: number): Promise<boolean> {
    const result = await db.delete(firms).where(eq(firms.id, id));
    return result.rowCount > 0;
  }

  async getDocument(id: number): Promise<Document | undefined> {
    const [document] = await db.select().from(documents).where(eq(documents.id, id));
    return document;
  }

  async getAllDocuments(): Promise<Document[]> {
    return await db.select().from(documents);
  }

  async createDocument(document: InsertDocument): Promise<Document> {
    const [newDocument] = await db
      .insert(documents)
      .values(document)
      .returning();
    return newDocument;
  }

  async updateDocument(id: number, document: Partial<InsertDocument>): Promise<Document | undefined> {
    const [updatedDocument] = await db
      .update(documents)
      .set(document)
      .where(eq(documents.id, id))
      .returning();
    return updatedDocument;
  }

  async deleteDocument(id: number): Promise<boolean> {
    const result = await db.delete(documents).where(eq(documents.id, id));
    return result.rowCount > 0;
  }

  async getPipelineStage(id: number): Promise<PipelineStage | undefined> {
    const [stage] = await db.select().from(pipelineStages).where(eq(pipelineStages.id, id));
    return stage;
  }

  async getAllPipelineStages(): Promise<PipelineStage[]> {
    return await db.select().from(pipelineStages);
  }

  async createPipelineStage(stage: InsertPipelineStage): Promise<PipelineStage> {
    const [newStage] = await db
      .insert(pipelineStages)
      .values(stage)
      .returning();
    return newStage;
  }

  async updatePipelineStage(id: number, stage: InsertPipelineStage): Promise<PipelineStage | undefined> {
    const [updatedStage] = await db
      .update(pipelineStages)
      .set(stage)
      .where(eq(pipelineStages.id, id))
      .returning();
    return updatedStage;
  }

  async deletePipelineStage(id: number): Promise<boolean> {
    const result = await db.delete(pipelineStages).where(eq(pipelineStages.id, id));
    return result.rowCount > 0;
  }

  async getTask(id: number): Promise<Task | undefined> {
    const [task] = await db.select().from(tasks).where(eq(tasks.id, id));
    return task;
  }

  async getAllTasks(): Promise<Task[]> {
    return await db.select().from(tasks);
  }

  async getTasksByTenderId(tenderId: number): Promise<Task[]> {
    return await db.select().from(tasks).where(eq(tasks.tenderId, tenderId));
  }

  async getTasksByUserId(userId: number): Promise<Task[]> {
    return await db.select().from(tasks).where(eq(tasks.assignedUserId, userId));
  }

  async createTask(task: InsertTask): Promise<Task> {
    const [newTask] = await db
      .insert(tasks)
      .values(task)
      .returning();
    return newTask;
  }

  async updateTask(id: number, task: Partial<InsertTask>): Promise<Task | undefined> {
    const [updatedTask] = await db
      .update(tasks)
      .set(task)
      .where(eq(tasks.id, id))
      .returning();
    return updatedTask;
  }

  async completeTask(id: number): Promise<Task | undefined> {
    const [completedTask] = await db
      .update(tasks)
      .set({ 
        status: "Completed",
        completedAt: new Date()
      })
      .where(eq(tasks.id, id))
      .returning();
    return completedTask;
  }

  async deleteTask(id: number): Promise<boolean> {
    const result = await db.delete(tasks).where(eq(tasks.id, id));
    return result.rowCount > 0;
  }

  async getCalendarEvent(id: number): Promise<CalendarEvent | undefined> {
    const [event] = await db.select().from(calendarEvents).where(eq(calendarEvents.id, id));
    return event;
  }

  async getAllCalendarEvents(): Promise<CalendarEvent[]> {
    return await db.select().from(calendarEvents);
  }

  async getCalendarEventsByUserId(userId: number): Promise<CalendarEvent[]> {
    return await db.select().from(calendarEvents).where(eq(calendarEvents.userId, userId));
  }

  async getCalendarEventsByTenderId(tenderId: number): Promise<CalendarEvent[]> {
    return await db.select().from(calendarEvents).where(eq(calendarEvents.tenderId, tenderId));
  }

  async createCalendarEvent(event: InsertCalendarEvent): Promise<CalendarEvent> {
    const [newEvent] = await db
      .insert(calendarEvents)
      .values(event)
      .returning();
    return newEvent;
  }

  async updateCalendarEvent(id: number, event: Partial<InsertCalendarEvent>): Promise<CalendarEvent | undefined> {
    const [updatedEvent] = await db
      .update(calendarEvents)
      .set(event)
      .where(eq(calendarEvents.id, id))
      .returning();
    return updatedEvent;
  }

  async deleteCalendarEvent(id: number): Promise<boolean> {
    const result = await db.delete(calendarEvents).where(eq(calendarEvents.id, id));
    return result.rowCount > 0;
  }

  async getEmailNotification(id: number): Promise<EmailNotification | undefined> {
    const [notification] = await db.select().from(emailNotifications).where(eq(emailNotifications.id, id));
    return notification;
  }

  async getAllEmailNotifications(): Promise<EmailNotification[]> {
    return await db.select().from(emailNotifications);
  }

  async createEmailNotification(notification: InsertEmailNotification): Promise<EmailNotification> {
    const [newNotification] = await db
      .insert(emailNotifications)
      .values(notification)
      .returning();
    return newNotification;
  }

  async updateEmailNotificationStatus(id: number, status: string): Promise<EmailNotification | undefined> {
    const [updatedNotification] = await db
      .update(emailNotifications)
      .set({ 
        status: status,
        sentAt: status === "Sent" ? new Date() : null
      })
      .where(eq(emailNotifications.id, id))
      .returning();
    return updatedNotification;
  }

  async deleteEmailNotification(id: number): Promise<boolean> {
    const result = await db.delete(emailNotifications).where(eq(emailNotifications.id, id));
    return result.rowCount > 0;
  }

  async getAutomationRule(id: number): Promise<AutomationRule | undefined> {
    const [rule] = await db.select().from(automationRules).where(eq(automationRules.id, id));
    return rule;
  }

  async getAllAutomationRules(): Promise<AutomationRule[]> {
    return await db.select().from(automationRules);
  }

  async createAutomationRule(rule: InsertAutomationRule): Promise<AutomationRule> {
    const [newRule] = await db
      .insert(automationRules)
      .values(rule)
      .returning();
    return newRule;
  }

  async updateAutomationRule(id: number, rule: Partial<InsertAutomationRule>): Promise<AutomationRule | undefined> {
    const [updatedRule] = await db
      .update(automationRules)
      .set(rule)
      .where(eq(automationRules.id, id))
      .returning();
    return updatedRule;
  }

  async toggleAutomationRule(id: number, enabled: boolean): Promise<AutomationRule | undefined> {
    const [updatedRule] = await db
      .update(automationRules)
      .set({ enabled })
      .where(eq(automationRules.id, id))
      .returning();
    return updatedRule;
  }

  async deleteAutomationRule(id: number): Promise<boolean> {
    const result = await db.delete(automationRules).where(eq(automationRules.id, id));
    return result.rowCount > 0;
  }

  async getFirmDocument(id: number): Promise<FirmDocument | undefined> {
    const [document] = await db.select().from(firmDocuments).where(eq(firmDocuments.id, id));
    return document;
  }

  async getFirmDocuments(firmId?: number): Promise<FirmDocument[]> {
    if (firmId) {
      return await db.select().from(firmDocuments).where(eq(firmDocuments.firmId, firmId));
    }
    return await db.select().from(firmDocuments);
  }

  async createFirmDocument(document: InsertFirmDocument): Promise<FirmDocument> {
    const [newDocument] = await db
      .insert(firmDocuments)
      .values(document)
      .returning();
    return newDocument;
  }

  async updateFirmDocument(id: number, document: Partial<InsertFirmDocument>): Promise<FirmDocument | undefined> {
    const [updatedDocument] = await db
      .update(firmDocuments)
      .set(document)
      .where(eq(firmDocuments.id, id))
      .returning();
    return updatedDocument;
  }

  async deleteFirmDocument(id: number): Promise<boolean> {
    const result = await db.delete(firmDocuments).where(eq(firmDocuments.id, id));
    return result.rowCount > 0;
  }

  async getFirmDocumentsByCategory(firmId: number, category: string): Promise<FirmDocument[]> {
    return await db
      .select()
      .from(firmDocuments)
      .where(eq(firmDocuments.firmId, firmId))
      .where(eq(firmDocuments.category, category));
  }

  async getExpiringDocuments(days: number): Promise<FirmDocument[]> {
    const currentDate = new Date();
    const futureDate = new Date();
    futureDate.setDate(currentDate.getDate() + days);

    return await db
      .select()
      .from(firmDocuments)
      .where(eq(firmDocuments.expiryDate !== null))
      .where(eq(firmDocuments.expiryDate <= futureDate))
      .where(eq(firmDocuments.expiryDate >= currentDate));
  }
}
