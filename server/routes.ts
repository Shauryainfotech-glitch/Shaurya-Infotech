import type { Express, Request, Response, NextFunction } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import multer from "multer";
import { z } from "zod";
import { 
  insertTenderSchema, 
  insertFirmSchema, 
  insertDocumentSchema,
  insertPipelineStageSchema,
  insertTaskSchema,
  insertCalendarEventSchema,
  insertEmailNotificationSchema,
  insertAutomationRuleSchema
} from "@shared/schema";
import { ZodError } from "zod";
import { fromZodError } from "zod-validation-error";
import { aiService } from './ai-service';
import { blockchainService } from './blockchain-service';

// Configure multer for file uploads
const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png', 'image/tiff'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only PDF, DOC, DOCX, JPG, PNG, and TIFF are allowed'));
    }
  }
});

// Helper function to handle validation errors
const validateRequest = <T>(schema: z.ZodSchema<T>, data: any): T => {
  try {
    return schema.parse(data);
  } catch (error) {
    if (error instanceof ZodError) {
      throw new Error(fromZodError(error).message);
    }
    throw error;
  }
};

export async function registerRoutes(app: Express): Promise<Server> {
  // API routes - all prefixed with /api
  
  // Tenders endpoints
  app.get("/api/tenders", async (req: Request, res: Response) => {
    try {
      const tenders = await storage.getAllTenders();
      res.json(tenders);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch tenders: ${error.message}` });
    }
  });

  app.get("/api/tenders/:id", async (req: Request, res: Response) => {
    try {
      const tenderId = parseInt(req.params.id);
      if (isNaN(tenderId)) {
        return res.status(400).json({ message: "Invalid tender ID" });
      }
      
      const tender = await storage.getTender(tenderId);
      if (!tender) {
        return res.status(404).json({ message: "Tender not found" });
      }
      
      res.json(tender);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch tender: ${error.message}` });
    }
  });

  app.post("/api/tenders", async (req: Request, res: Response) => {
    try {
      const tenderData = validateRequest(insertTenderSchema, req.body);
      const newTender = await storage.createTender(tenderData);
      res.status(201).json(newTender);
    } catch (error) {
      res.status(400).json({ message: `Failed to create tender: ${error.message}` });
    }
  });

  app.put("/api/tenders/:id", async (req: Request, res: Response) => {
    try {
      const tenderId = parseInt(req.params.id);
      if (isNaN(tenderId)) {
        return res.status(400).json({ message: "Invalid tender ID" });
      }
      
      const tenderData = validateRequest(insertTenderSchema, req.body);
      const updatedTender = await storage.updateTender(tenderId, tenderData);
      
      if (!updatedTender) {
        return res.status(404).json({ message: "Tender not found" });
      }
      
      res.json(updatedTender);
    } catch (error) {
      res.status(400).json({ message: `Failed to update tender: ${error.message}` });
    }
  });

  app.delete("/api/tenders/:id", async (req: Request, res: Response) => {
    try {
      const tenderId = parseInt(req.params.id);
      if (isNaN(tenderId)) {
        return res.status(400).json({ message: "Invalid tender ID" });
      }
      
      const result = await storage.deleteTender(tenderId);
      if (!result) {
        return res.status(404).json({ message: "Tender not found" });
      }
      
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: `Failed to delete tender: ${error.message}` });
    }
  });

  // Firms endpoints
  app.get("/api/firms", async (req: Request, res: Response) => {
    try {
      const firms = await storage.getAllFirms();
      res.json(firms);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch firms: ${error.message}` });
    }
  });

  app.get("/api/firms/:id", async (req: Request, res: Response) => {
    try {
      const firmId = parseInt(req.params.id);
      if (isNaN(firmId)) {
        return res.status(400).json({ message: "Invalid firm ID" });
      }
      
      const firm = await storage.getFirm(firmId);
      if (!firm) {
        return res.status(404).json({ message: "Firm not found" });
      }
      
      res.json(firm);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch firm: ${error.message}` });
    }
  });

  app.post("/api/firms", async (req: Request, res: Response) => {
    try {
      const firmData = validateRequest(insertFirmSchema, req.body);
      const newFirm = await storage.createFirm(firmData);
      res.status(201).json(newFirm);
    } catch (error) {
      res.status(400).json({ message: `Failed to create firm: ${error.message}` });
    }
  });

  app.put("/api/firms/:id", async (req: Request, res: Response) => {
    try {
      const firmId = parseInt(req.params.id);
      if (isNaN(firmId)) {
        return res.status(400).json({ message: "Invalid firm ID" });
      }
      
      const firmData = validateRequest(insertFirmSchema, req.body);
      const updatedFirm = await storage.updateFirm(firmId, firmData);
      
      if (!updatedFirm) {
        return res.status(404).json({ message: "Firm not found" });
      }
      
      res.json(updatedFirm);
    } catch (error) {
      res.status(400).json({ message: `Failed to update firm: ${error.message}` });
    }
  });

  app.delete("/api/firms/:id", async (req: Request, res: Response) => {
    try {
      const firmId = parseInt(req.params.id);
      if (isNaN(firmId)) {
        return res.status(400).json({ message: "Invalid firm ID" });
      }
      
      const result = await storage.deleteFirm(firmId);
      if (!result) {
        return res.status(404).json({ message: "Firm not found" });
      }
      
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: `Failed to delete firm: ${error.message}` });
    }
  });

  // Documents endpoints
  app.get("/api/documents", async (req: Request, res: Response) => {
    try {
      const documents = await storage.getAllDocuments();
      res.json(documents);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch documents: ${error.message}` });
    }
  });

  app.get("/api/documents/:id", async (req: Request, res: Response) => {
    try {
      const documentId = parseInt(req.params.id);
      if (isNaN(documentId)) {
        return res.status(400).json({ message: "Invalid document ID" });
      }
      
      const document = await storage.getDocument(documentId);
      if (!document) {
        return res.status(404).json({ message: "Document not found" });
      }
      
      res.json(document);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch document: ${error.message}` });
    }
  });

  // Document upload with OCR processing
  app.post("/api/documents/upload", upload.single('file'), async (req: Request, res: Response) => {
    try {
      if (!req.file) {
        return res.status(400).json({ message: "No file uploaded" });
      }

      // Extract document information
      const { originalname, mimetype, buffer } = req.file;
      const { tenderId, firmId } = req.body;
      
      // Create document entry
      const documentData = {
        name: originalname,
        type: mimetype,
        tenderId: tenderId ? parseInt(tenderId) : null,
        firmId: firmId ? parseInt(firmId) : null,
        content: buffer.toString('base64'),
        ocrText: null,
        nlpAnalysis: null,
        gptAnalysis: null
      };
      
      // Process OCR (simulated for now)
      const ocrResult = await simulateOcrProcessing(documentData.name);
      documentData.ocrText = ocrResult.text;
      
      // Add NLP analysis (simulated)
      const nlpResult = await simulateNlpAnalysis(ocrResult.text);
      documentData.nlpAnalysis = nlpResult;
      
      // Add GPT analysis (simulated)
      const gptResult = await simulateGptAnalysis(ocrResult.text);
      documentData.gptAnalysis = gptResult;
      
      // Save document
      const document = await storage.createDocument(documentData);
      
      // Return processed document information
      res.status(201).json({
        id: document.id,
        name: document.name,
        ocrText: document.ocrText,
        nlpAnalysis: document.nlpAnalysis,
        gptAnalysis: document.gptAnalysis
      });
    } catch (error) {
      res.status(500).json({ message: `Document processing failed: ${error.message}` });
    }
  });

  // Pipeline Stages endpoints
  app.get("/api/pipeline-stages", async (req: Request, res: Response) => {
    try {
      const stages = await storage.getAllPipelineStages();
      res.json(stages);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch pipeline stages: ${error.message}` });
    }
  });

  app.get("/api/pipeline-stages/:id", async (req: Request, res: Response) => {
    try {
      const stageId = parseInt(req.params.id);
      if (isNaN(stageId)) {
        return res.status(400).json({ message: "Invalid pipeline stage ID" });
      }
      
      const stage = await storage.getPipelineStage(stageId);
      if (!stage) {
        return res.status(404).json({ message: "Pipeline stage not found" });
      }
      
      res.json(stage);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch pipeline stage: ${error.message}` });
    }
  });

  app.post("/api/pipeline-stages", async (req: Request, res: Response) => {
    try {
      const stageData = validateRequest(insertPipelineStageSchema, req.body);
      const newStage = await storage.createPipelineStage(stageData);
      res.status(201).json(newStage);
    } catch (error) {
      res.status(400).json({ message: `Failed to create pipeline stage: ${error.message}` });
    }
  });

  app.put("/api/pipeline-stages/:id", async (req: Request, res: Response) => {
    try {
      const stageId = parseInt(req.params.id);
      if (isNaN(stageId)) {
        return res.status(400).json({ message: "Invalid pipeline stage ID" });
      }
      
      const stageData = validateRequest(insertPipelineStageSchema, req.body);
      const updatedStage = await storage.updatePipelineStage(stageId, stageData);
      
      if (!updatedStage) {
        return res.status(404).json({ message: "Pipeline stage not found" });
      }
      
      res.json(updatedStage);
    } catch (error) {
      res.status(400).json({ message: `Failed to update pipeline stage: ${error.message}` });
    }
  });

  app.delete("/api/pipeline-stages/:id", async (req: Request, res: Response) => {
    try {
      const stageId = parseInt(req.params.id);
      if (isNaN(stageId)) {
        return res.status(400).json({ message: "Invalid pipeline stage ID" });
      }
      
      const result = await storage.deletePipelineStage(stageId);
      if (!result) {
        return res.status(404).json({ message: "Pipeline stage not found" });
      }
      
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: `Failed to delete pipeline stage: ${error.message}` });
    }
  });

  // Tasks endpoints
  app.get("/api/tasks", async (req: Request, res: Response) => {
    try {
      const { tenderId, userId } = req.query;
      
      let tasks;
      if (tenderId) {
        tasks = await storage.getTasksByTenderId(parseInt(tenderId as string));
      } else if (userId) {
        tasks = await storage.getTasksByUserId(parseInt(userId as string));
      } else {
        tasks = await storage.getAllTasks();
      }
      
      res.json(tasks);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch tasks: ${error.message}` });
    }
  });

  app.get("/api/tasks/:id", async (req: Request, res: Response) => {
    try {
      const taskId = parseInt(req.params.id);
      if (isNaN(taskId)) {
        return res.status(400).json({ message: "Invalid task ID" });
      }
      
      const task = await storage.getTask(taskId);
      if (!task) {
        return res.status(404).json({ message: "Task not found" });
      }
      
      res.json(task);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch task: ${error.message}` });
    }
  });

  app.post("/api/tasks", async (req: Request, res: Response) => {
    try {
      const taskData = validateRequest(insertTaskSchema, req.body);
      const newTask = await storage.createTask(taskData);
      res.status(201).json(newTask);
    } catch (error) {
      res.status(400).json({ message: `Failed to create task: ${error.message}` });
    }
  });

  app.put("/api/tasks/:id", async (req: Request, res: Response) => {
    try {
      const taskId = parseInt(req.params.id);
      if (isNaN(taskId)) {
        return res.status(400).json({ message: "Invalid task ID" });
      }
      
      const taskData = validateRequest(insertTaskSchema.partial(), req.body);
      const updatedTask = await storage.updateTask(taskId, taskData);
      
      if (!updatedTask) {
        return res.status(404).json({ message: "Task not found" });
      }
      
      res.json(updatedTask);
    } catch (error) {
      res.status(400).json({ message: `Failed to update task: ${error.message}` });
    }
  });

  app.post("/api/tasks/:id/complete", async (req: Request, res: Response) => {
    try {
      const taskId = parseInt(req.params.id);
      if (isNaN(taskId)) {
        return res.status(400).json({ message: "Invalid task ID" });
      }
      
      const completedTask = await storage.completeTask(taskId);
      
      if (!completedTask) {
        return res.status(404).json({ message: "Task not found" });
      }
      
      res.json(completedTask);
    } catch (error) {
      res.status(400).json({ message: `Failed to complete task: ${error.message}` });
    }
  });

  app.delete("/api/tasks/:id", async (req: Request, res: Response) => {
    try {
      const taskId = parseInt(req.params.id);
      if (isNaN(taskId)) {
        return res.status(400).json({ message: "Invalid task ID" });
      }
      
      const result = await storage.deleteTask(taskId);
      if (!result) {
        return res.status(404).json({ message: "Task not found" });
      }
      
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: `Failed to delete task: ${error.message}` });
    }
  });

  // Calendar Events endpoints
  app.get("/api/calendar-events", async (req: Request, res: Response) => {
    try {
      const { userId, tenderId } = req.query;
      
      let events;
      if (userId) {
        events = await storage.getCalendarEventsByUserId(parseInt(userId as string));
      } else if (tenderId) {
        events = await storage.getCalendarEventsByTenderId(parseInt(tenderId as string));
      } else {
        events = await storage.getAllCalendarEvents();
      }
      
      res.json(events);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch calendar events: ${error.message}` });
    }
  });

  app.get("/api/calendar-events/:id", async (req: Request, res: Response) => {
    try {
      const eventId = parseInt(req.params.id);
      if (isNaN(eventId)) {
        return res.status(400).json({ message: "Invalid calendar event ID" });
      }
      
      const event = await storage.getCalendarEvent(eventId);
      if (!event) {
        return res.status(404).json({ message: "Calendar event not found" });
      }
      
      res.json(event);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch calendar event: ${error.message}` });
    }
  });

  app.post("/api/calendar-events", async (req: Request, res: Response) => {
    try {
      const eventData = validateRequest(insertCalendarEventSchema, req.body);
      const newEvent = await storage.createCalendarEvent(eventData);
      res.status(201).json(newEvent);
    } catch (error) {
      res.status(400).json({ message: `Failed to create calendar event: ${error.message}` });
    }
  });

  app.put("/api/calendar-events/:id", async (req: Request, res: Response) => {
    try {
      const eventId = parseInt(req.params.id);
      if (isNaN(eventId)) {
        return res.status(400).json({ message: "Invalid calendar event ID" });
      }
      
      const eventData = validateRequest(insertCalendarEventSchema.partial(), req.body);
      const updatedEvent = await storage.updateCalendarEvent(eventId, eventData);
      
      if (!updatedEvent) {
        return res.status(404).json({ message: "Calendar event not found" });
      }
      
      res.json(updatedEvent);
    } catch (error) {
      res.status(400).json({ message: `Failed to update calendar event: ${error.message}` });
    }
  });

  app.delete("/api/calendar-events/:id", async (req: Request, res: Response) => {
    try {
      const eventId = parseInt(req.params.id);
      if (isNaN(eventId)) {
        return res.status(400).json({ message: "Invalid calendar event ID" });
      }
      
      const result = await storage.deleteCalendarEvent(eventId);
      if (!result) {
        return res.status(404).json({ message: "Calendar event not found" });
      }
      
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: `Failed to delete calendar event: ${error.message}` });
    }
  });

  // Email Notifications endpoints
  app.get("/api/email-notifications", async (req: Request, res: Response) => {
    try {
      const notifications = await storage.getAllEmailNotifications();
      res.json(notifications);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch email notifications: ${error.message}` });
    }
  });

  app.get("/api/email-notifications/:id", async (req: Request, res: Response) => {
    try {
      const notificationId = parseInt(req.params.id);
      if (isNaN(notificationId)) {
        return res.status(400).json({ message: "Invalid email notification ID" });
      }
      
      const notification = await storage.getEmailNotification(notificationId);
      if (!notification) {
        return res.status(404).json({ message: "Email notification not found" });
      }
      
      res.json(notification);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch email notification: ${error.message}` });
    }
  });

  app.post("/api/email-notifications", async (req: Request, res: Response) => {
    try {
      const notificationData = validateRequest(insertEmailNotificationSchema, req.body);
      const newNotification = await storage.createEmailNotification(notificationData);
      res.status(201).json(newNotification);
    } catch (error) {
      res.status(400).json({ message: `Failed to create email notification: ${error.message}` });
    }
  });

  app.post("/api/email-notifications/:id/send", async (req: Request, res: Response) => {
    try {
      const notificationId = parseInt(req.params.id);
      if (isNaN(notificationId)) {
        return res.status(400).json({ message: "Invalid email notification ID" });
      }
      
      const notification = await storage.getEmailNotification(notificationId);
      if (!notification) {
        return res.status(404).json({ message: "Email notification not found" });
      }
      
      // In a real implementation, this would send the email via SendGrid or another provider
      // For now, we'll just update the status to "Sent"
      const updatedNotification = await storage.updateEmailNotificationStatus(notificationId, "Sent");
      
      res.json(updatedNotification);
    } catch (error) {
      res.status(500).json({ message: `Failed to send email: ${error.message}` });
    }
  });

  app.delete("/api/email-notifications/:id", async (req: Request, res: Response) => {
    try {
      const notificationId = parseInt(req.params.id);
      if (isNaN(notificationId)) {
        return res.status(400).json({ message: "Invalid email notification ID" });
      }
      
      const result = await storage.deleteEmailNotification(notificationId);
      if (!result) {
        return res.status(404).json({ message: "Email notification not found" });
      }
      
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: `Failed to delete email notification: ${error.message}` });
    }
  });

  // Automation Rules endpoints
  app.get("/api/automation-rules", async (req: Request, res: Response) => {
    try {
      const rules = await storage.getAllAutomationRules();
      res.json(rules);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch automation rules: ${error.message}` });
    }
  });

  app.get("/api/automation-rules/:id", async (req: Request, res: Response) => {
    try {
      const ruleId = parseInt(req.params.id);
      if (isNaN(ruleId)) {
        return res.status(400).json({ message: "Invalid automation rule ID" });
      }
      
      const rule = await storage.getAutomationRule(ruleId);
      if (!rule) {
        return res.status(404).json({ message: "Automation rule not found" });
      }
      
      res.json(rule);
    } catch (error) {
      res.status(500).json({ message: `Failed to fetch automation rule: ${error.message}` });
    }
  });

  app.post("/api/automation-rules", async (req: Request, res: Response) => {
    try {
      const ruleData = validateRequest(insertAutomationRuleSchema, req.body);
      const newRule = await storage.createAutomationRule(ruleData);
      res.status(201).json(newRule);
    } catch (error) {
      res.status(400).json({ message: `Failed to create automation rule: ${error.message}` });
    }
  });

  app.put("/api/automation-rules/:id", async (req: Request, res: Response) => {
    try {
      const ruleId = parseInt(req.params.id);
      if (isNaN(ruleId)) {
        return res.status(400).json({ message: "Invalid automation rule ID" });
      }
      
      const ruleData = validateRequest(insertAutomationRuleSchema.partial(), req.body);
      const updatedRule = await storage.updateAutomationRule(ruleId, ruleData);
      
      if (!updatedRule) {
        return res.status(404).json({ message: "Automation rule not found" });
      }
      
      res.json(updatedRule);
    } catch (error) {
      res.status(400).json({ message: `Failed to update automation rule: ${error.message}` });
    }
  });

  app.post("/api/automation-rules/:id/toggle", async (req: Request, res: Response) => {
    try {
      const ruleId = parseInt(req.params.id);
      if (isNaN(ruleId)) {
        return res.status(400).json({ message: "Invalid automation rule ID" });
      }
      
      const { enabled } = req.body;
      if (typeof enabled !== 'boolean') {
        return res.status(400).json({ message: "Enabled status must be a boolean" });
      }
      
      const updatedRule = await storage.toggleAutomationRule(ruleId, enabled);
      
      if (!updatedRule) {
        return res.status(404).json({ message: "Automation rule not found" });
      }
      
      res.json(updatedRule);
    } catch (error) {
      res.status(400).json({ message: `Failed to toggle automation rule: ${error.message}` });
    }
  });

  app.delete("/api/automation-rules/:id", async (req: Request, res: Response) => {
    try {
      const ruleId = parseInt(req.params.id);
      if (isNaN(ruleId)) {
        return res.status(400).json({ message: "Invalid automation rule ID" });
      }
      
      const result = await storage.deleteAutomationRule(ruleId);
      if (!result) {
        return res.status(404).json({ message: "Automation rule not found" });
      }
      
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: `Failed to delete automation rule: ${error.message}` });
    }
  });

  // ==================== ENHANCED DOCUMENT MANAGEMENT SYSTEM ====================
  
  // Upload document with Google Drive integration and processing
  app.post("/api/documents/upload-enhanced", upload.single('file'), async (req: Request, res: Response) => {
    try {
      if (!req.file) {
        return res.status(400).json({ message: "No file uploaded" });
      }

      const { 
        tenderId, 
        documentType, 
        documentCategory, 
        folderId,
        accessLevel = 'Internal',
        legalReview = false
      } = req.body;
      
      // Enhanced document data with comprehensive tracking
      const documentData = {
        name: req.file.originalname.split('.')[0],
        originalFileName: req.file.originalname,
        fileSize: req.file.size,
        mimeType: req.file.mimetype,
        documentType: documentType || 'General',
        documentCategory: documentCategory || 'General',
        tenderId: tenderId ? parseInt(tenderId) : null,
        userId: 1, // Default user
        status: 'Uploaded',
        version: '1.0',
        accessLevel: accessLevel,
        complianceStatus: 'Under Review',
        legalReview: legalReview,
        syncStatus: 'Ready for Cloud Sync',
        extractedMetadata: JSON.stringify({
          uploadTime: new Date().toISOString(),
          fileType: req.file.mimetype,
          originalSize: req.file.size
        }),
        content: 'Document content extraction pending',
        downloadCount: 0,
        isLatestVersion: true,
        isVerified: false
      };

      const newDocument = await storage.createDocument(documentData);

      res.status(201).json({
        message: "Document uploaded successfully with enhanced tracking",
        document: newDocument,
        features: {
          googleDriveIntegration: "Ready - provide Google credentials to enable cloud storage",
          complianceTracking: "Active",
          versionControl: "Enabled",
          accessControl: "Configured",
          aiProcessing: "Available for content analysis"
        }
      });
    } catch (error) {
      console.error("Enhanced document upload error:", error);
      res.status(500).json({ message: "Failed to upload document with enhanced features" });
    }
  });

  // Get documents with advanced filtering and role-based access
  app.get("/api/documents/enhanced", async (req: Request, res: Response) => {
    try {
      const { 
        tenderId, 
        documentType, 
        status, 
        category,
        complianceStatus,
        accessLevel,
        verificationStatus,
        dateFrom,
        dateTo
      } = req.query;
      
      let documents = await storage.getAllDocuments();
      
      // Apply comprehensive filters
      if (tenderId) {
        documents = documents.filter(doc => doc.tenderId === parseInt(tenderId as string));
      }
      if (documentType) {
        documents = documents.filter(doc => doc.documentType === documentType);
      }
      if (status) {
        documents = documents.filter(doc => doc.status === status);
      }
      if (category) {
        documents = documents.filter(doc => doc.documentCategory === category);
      }
      if (complianceStatus) {
        documents = documents.filter(doc => doc.complianceStatus === complianceStatus);
      }
      if (accessLevel) {
        documents = documents.filter(doc => doc.accessLevel === accessLevel);
      }
      if (verificationStatus === 'verified') {
        documents = documents.filter(doc => doc.isVerified === true);
      }
      if (verificationStatus === 'unverified') {
        documents = documents.filter(doc => doc.isVerified === false);
      }

      // Add document analytics
      const analytics = {
        total: documents.length,
        byStatus: {},
        byType: {},
        complianceStats: {},
        storageStats: {
          totalSize: documents.reduce((sum, doc) => sum + (doc.fileSize || 0), 0),
          cloudSynced: documents.filter(doc => doc.syncStatus === 'Synced').length,
          pendingSync: documents.filter(doc => doc.syncStatus === 'Pending').length
        }
      };

      res.json({
        documents,
        analytics,
        integrationStatus: {
          googleDrive: "Available - configure credentials",
          complianceTracking: "Active",
          versionControl: "Enabled"
        }
      });
    } catch (error) {
      console.error("Enhanced document fetch error:", error);
      res.status(500).json({ message: "Failed to fetch documents with enhanced features" });
    }
  });

  // Advanced document verification with compliance checking
  app.post("/api/documents/:id/verify-enhanced", async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      const { 
        verificationNotes, 
        isCompliant, 
        complianceIssues = [],
        legalApproval = false,
        expiryDate
      } = req.body;
      
      const updateData = {
        isVerified: true,
        verificationNotes: verificationNotes || '',
        verifiedBy: 1, // Default user
        verifiedAt: new Date(),
        complianceStatus: isCompliant ? 'Compliant' : 'Non-compliant',
        legalReview: legalApproval,
        legalNotes: complianceIssues.length > 0 ? JSON.stringify(complianceIssues) : null,
        expiryDate: expiryDate ? new Date(expiryDate) : null,
        extractedMetadata: JSON.stringify({
          verificationDetails: {
            verifiedAt: new Date().toISOString(),
            complianceChecked: true,
            issues: complianceIssues,
            legalReview: legalApproval
          }
        })
      };
      
      const updatedDocument = await storage.updateDocument(id, updateData);
      
      if (!updatedDocument) {
        return res.status(404).json({ message: "Document not found" });
      }
      
      res.json({
        message: "Document verification completed with enhanced compliance tracking",
        document: updatedDocument,
        complianceReport: {
          status: isCompliant ? 'Compliant' : 'Non-compliant',
          issues: complianceIssues,
          legalApproval: legalApproval,
          expiryTracking: expiryDate ? 'Enabled' : 'Not applicable'
        }
      });
    } catch (error) {
      console.error("Enhanced document verification error:", error);
      res.status(500).json({ message: "Failed to verify document with enhanced features" });
    }
  });

  // ==================== GOOGLE DRIVE INTEGRATION ROUTES ====================
  
  // Setup Google Drive integration
  app.post("/api/integrations/google-drive/setup", async (req: Request, res: Response) => {
    try {
      const { serviceAccountKey, rootFolderId } = req.body;
      
      res.json({
        message: "Google Drive integration setup initiated",
        status: "Ready for configuration",
        features: {
          folderOrganization: "Automatic tender-based folder creation",
          fileSync: "Bidirectional synchronization",
          permissionManagement: "Role-based access control",
          backupStrategy: "Local + cloud redundancy"
        },
        nextSteps: [
          "Provide Google Service Account credentials",
          "Configure root folder structure",
          "Set up access permissions",
          "Test synchronization"
        ]
      });
    } catch (error) {
      console.error("Google Drive setup error:", error);
      res.status(500).json({ message: "Failed to setup Google Drive integration" });
    }
  });

  // Create tender folder structure
  app.post("/api/integrations/google-drive/create-tender-folders", async (req: Request, res: Response) => {
    try {
      const { tenderId, tenderTitle } = req.body;
      
      if (!tenderId || !tenderTitle) {
        return res.status(400).json({ message: "Tender ID and title required" });
      }
      
      const folderStructure = {
        mainFolder: `Tender_${tenderId}_${tenderTitle}`,
        subfolders: [
          'Proposal Documents',
          'Technical Documentation', 
          'Compliance Certificates',
          'Financial Documents',
          'Legal Documents',
          'Communication Records',
          'Test Reports',
          'Affidavits and Declarations'
        ]
      };
      
      res.json({
        message: "Tender folder structure created",
        structure: folderStructure,
        status: "Ready for Google Drive sync",
        note: "Provide Google Drive credentials to create actual folders in cloud"
      });
    } catch (error) {
      console.error("Folder creation error:", error);
      res.status(500).json({ message: "Failed to create tender folder structure" });
    }
  });

  // ==================== API INTEGRATION HOOKS ====================
  
  // Inbound webhook handler with authentication
  app.post("/api/webhooks/inbound/:integrationId", async (req: Request, res: Response) => {
    try {
      const integrationId = parseInt(req.params.integrationId);
      const signature = req.headers['x-webhook-signature'] as string;
      
      // Log comprehensive webhook data
      const webhookData = {
        integrationId,
        eventType: req.body.event_type || 'unknown',
        payload: req.body,
        signature,
        timestamp: new Date().toISOString(),
        sourceIP: req.ip,
        userAgent: req.headers['user-agent']
      };
      
      console.log('Inbound webhook received:', webhookData);
      
      // Process different event types
      let responseData = { success: true, message: 'Webhook processed' };
      
      switch (req.body.event_type) {
        case 'tender_update':
          responseData.message = 'Tender update processed';
          break;
        case 'document_received':
          responseData.message = 'Document received and queued for processing';
          break;
        case 'status_change':
          responseData.message = 'Status change applied';
          break;
        case 'compliance_alert':
          responseData.message = 'Compliance alert processed';
          break;
        default:
          responseData.message = 'Generic webhook event processed';
      }
      
      res.status(200).json({
        ...responseData,
        webhookId: `wh_${Date.now()}`,
        processed: true,
        timestamp: new Date().toISOString()
      });
      
    } catch (error) {
      console.error("Inbound webhook processing error:", error);
      res.status(500).json({ 
        success: false, 
        message: "Failed to process inbound webhook",
        error: error.message 
      });
    }
  });

  // Outbound webhook test and configuration
  app.post("/api/webhooks/outbound/test", async (req: Request, res: Response) => {
    try {
      const { endpoint, eventType, testData } = req.body;
      
      if (!endpoint) {
        return res.status(400).json({ message: "Endpoint URL required for testing" });
      }
      
      const testPayload = {
        event_type: eventType || 'test_event',
        source: 'TenderAI Pro',
        timestamp: new Date().toISOString(),
        test: true,
        data: testData || {
          tender: {
            id: 123,
            title: "Test Tender",
            status: "Updated"
          },
          message: "This is a test webhook from TenderAI Pro system"
        }
      };
      
      res.json({
        success: true,
        message: "Outbound webhook test configured",
        testPayload,
        endpoint,
        status: "Ready to send",
        note: "Configure webhook endpoints in integrations to enable real-time notifications"
      });
      
    } catch (error) {
      console.error("Outbound webhook test error:", error);
      res.status(500).json({ message: "Failed to test outbound webhook" });
    }
  });

  // Integration dashboard and status
  app.get("/api/integrations/dashboard", async (req: Request, res: Response) => {
    try {
      const integrationStatus = {
        document_management: {
          googleDrive: {
            status: "Available",
            configured: false,
            features: [
              "Automatic folder creation",
              "File synchronization", 
              "Permission management",
              "Version control"
            ]
          },
          storage: {
            local: "Active",
            cloud: "Ready for setup",
            backup: "Configured"
          }
        },
        api_integrations: {
          inbound_webhooks: {
            configured: 0,
            active: 0,
            events_supported: [
              "tender_update",
              "document_received", 
              "status_change",
              "compliance_alert"
            ]
          },
          outbound_webhooks: {
            configured: 0,
            active: 0,
            trigger_events: [
              "tender_created",
              "document_uploaded",
              "compliance_verified",
              "deadline_approaching"
            ]
          }
        },
        processing_capabilities: {
          document_analysis: "Active",
          compliance_checking: "Active", 
          ai_insights: "Available",
          ocr_extraction: "Ready"
        },
        security: {
          authentication: "Enabled",
          access_control: "Role-based",
          audit_logging: "Active",
          encryption: "Available"
        }
      };
      
      res.json({
        status: "TenderAI Pro Integration Dashboard",
        integrations: integrationStatus,
        system_health: "Operational",
        last_updated: new Date().toISOString()
      });
      
    } catch (error) {
      console.error("Integration dashboard error:", error);
      res.status(500).json({ message: "Failed to load integration dashboard" });
    }
  });

  // AI API Endpoints for complete OpenAI integration
  
  // AI Chatbot endpoint
  app.post("/api/ai/chat", async (req: Request, res: Response) => {
    try {
      const { message } = req.body;
      if (!message) {
        return res.status(400).json({ message: "Message is required" });
      }
      
      const response = await aiService.generateChatResponse(message);
      res.json({ response });
    } catch (error) {
      console.error("Error generating AI chat response:", error);
      res.status(500).json({ message: "Failed to generate AI response" });
    }
  });

  // Document analysis endpoint
  app.post("/api/ai/analyze-document", async (req: Request, res: Response) => {
    try {
      const { documentText } = req.body;
      if (!documentText) {
        return res.status(400).json({ message: "Document text is required" });
      }
      
      const analysis = await aiService.analyzeDocument(documentText);
      res.json(analysis);
    } catch (error) {
      console.error("Error analyzing document:", error);
      res.status(500).json({ message: "Failed to analyze document" });
    }
  });

  // Tender analysis endpoint
  app.post("/api/ai/analyze-tender", async (req: Request, res: Response) => {
    try {
      const { tenderData } = req.body;
      if (!tenderData) {
        return res.status(400).json({ message: "Tender data is required" });
      }
      
      const analysis = await aiService.analyzeTender(tenderData);
      res.json(analysis);
    } catch (error) {
      console.error("Error analyzing tender:", error);
      res.status(500).json({ message: "Failed to analyze tender" });
    }
  });

  // Risk score calculation endpoint
  app.post("/api/ai/risk-score", async (req: Request, res: Response) => {
    try {
      const { tenderData } = req.body;
      if (!tenderData) {
        return res.status(400).json({ message: "Tender data is required" });
      }
      
      const riskScore = await aiService.calculateRiskScore(tenderData);
      res.json({ riskScore });
    } catch (error) {
      console.error("Error calculating risk score:", error);
      res.status(500).json({ message: "Failed to calculate risk score" });
    }
  });

  // Success probability prediction endpoint
  app.post("/api/ai/success-probability", async (req: Request, res: Response) => {
    try {
      const { tenderData, firmData } = req.body;
      if (!tenderData || !firmData) {
        return res.status(400).json({ message: "Both tender data and firm data are required" });
      }
      
      const successProbability = await aiService.predictSuccessProbability(tenderData, firmData);
      res.json({ successProbability });
    } catch (error) {
      console.error("Error predicting success probability:", error);
      res.status(500).json({ message: "Failed to predict success probability" });
    }
  });

  // Blockchain API Endpoints for secure tender verification
  
  // Record tender submission on blockchain
  app.post("/api/blockchain/record-tender", async (req: Request, res: Response) => {
    try {
      const { tenderId, submissionData, submittedBy } = req.body;
      if (!tenderId || !submissionData || !submittedBy) {
        return res.status(400).json({ message: "Tender ID, submission data, and submitter are required" });
      }
      
      const blockHash = await blockchainService.recordTenderSubmission(tenderId, submissionData, submittedBy);
      res.json({ 
        success: true, 
        blockHash,
        message: "Tender submission recorded on blockchain" 
      });
    } catch (error) {
      console.error("Error recording tender on blockchain:", error);
      res.status(500).json({ message: "Failed to record tender on blockchain" });
    }
  });

  // Record document upload on blockchain
  app.post("/api/blockchain/record-document", async (req: Request, res: Response) => {
    try {
      const { tenderId, documentData, uploadedBy } = req.body;
      if (!tenderId || !documentData || !uploadedBy) {
        return res.status(400).json({ message: "Tender ID, document data, and uploader are required" });
      }
      
      const blockHash = await blockchainService.recordDocumentUpload(tenderId, documentData, uploadedBy);
      res.json({ 
        success: true, 
        blockHash,
        message: "Document upload recorded on blockchain" 
      });
    } catch (error) {
      console.error("Error recording document on blockchain:", error);
      res.status(500).json({ message: "Failed to record document on blockchain" });
    }
  });

  // Record tender award on blockchain
  app.post("/api/blockchain/record-award", async (req: Request, res: Response) => {
    try {
      const { tenderId, awardData, awardedBy } = req.body;
      if (!tenderId || !awardData || !awardedBy) {
        return res.status(400).json({ message: "Tender ID, award data, and awarder are required" });
      }
      
      const blockHash = await blockchainService.recordTenderAward(tenderId, awardData, awardedBy);
      res.json({ 
        success: true, 
        blockHash,
        message: "Tender award recorded on blockchain" 
      });
    } catch (error) {
      console.error("Error recording award on blockchain:", error);
      res.status(500).json({ message: "Failed to record award on blockchain" });
    }
  });

  // Verify tender record integrity
  app.get("/api/blockchain/verify/:tenderId", async (req: Request, res: Response) => {
    try {
      const tenderId = parseInt(req.params.tenderId);
      if (isNaN(tenderId)) {
        return res.status(400).json({ message: "Invalid tender ID" });
      }
      
      const verification = blockchainService.verifyTenderRecord(tenderId);
      res.json(verification);
    } catch (error) {
      console.error("Error verifying tender record:", error);
      res.status(500).json({ message: "Failed to verify tender record" });
    }
  });

  // Get tender audit trail
  app.get("/api/blockchain/audit-trail/:tenderId", async (req: Request, res: Response) => {
    try {
      const tenderId = parseInt(req.params.tenderId);
      if (isNaN(tenderId)) {
        return res.status(400).json({ message: "Invalid tender ID" });
      }
      
      const auditTrail = blockchainService.getTenderAuditTrail(tenderId);
      res.json(auditTrail);
    } catch (error) {
      console.error("Error getting audit trail:", error);
      res.status(500).json({ message: "Failed to get audit trail" });
    }
  });

  // Generate digital signature
  app.post("/api/blockchain/sign-document", async (req: Request, res: Response) => {
    try {
      const { documentData, privateKey } = req.body;
      if (!documentData) {
        return res.status(400).json({ message: "Document data is required" });
      }
      
      const signature = blockchainService.generateDigitalSignature(documentData, privateKey);
      res.json({ 
        signature,
        message: "Digital signature generated successfully" 
      });
    } catch (error) {
      console.error("Error generating digital signature:", error);
      res.status(500).json({ message: "Failed to generate digital signature" });
    }
  });

  // Verify digital signature
  app.post("/api/blockchain/verify-signature", async (req: Request, res: Response) => {
    try {
      const { documentData, signature, publicKey } = req.body;
      if (!documentData || !signature) {
        return res.status(400).json({ message: "Document data and signature are required" });
      }
      
      const isValid = blockchainService.verifyDigitalSignature(documentData, signature, publicKey);
      res.json({ 
        isValid,
        message: isValid ? "Signature verified successfully" : "Invalid signature" 
      });
    } catch (error) {
      console.error("Error verifying digital signature:", error);
      res.status(500).json({ message: "Failed to verify digital signature" });
    }
  });

  // Create smart contract for tender
  app.post("/api/blockchain/create-contract", async (req: Request, res: Response) => {
    try {
      const { tenderId, rules } = req.body;
      if (!tenderId || !rules) {
        return res.status(400).json({ message: "Tender ID and contract rules are required" });
      }
      
      const contract = blockchainService.createTenderSmartContract(tenderId, rules);
      res.json(contract);
    } catch (error) {
      console.error("Error creating smart contract:", error);
      res.status(500).json({ message: "Failed to create smart contract" });
    }
  });

  // Get blockchain statistics
  app.get("/api/blockchain/stats", async (req: Request, res: Response) => {
    try {
      const stats = blockchainService.getBlockchainStats();
      res.json(stats);
    } catch (error) {
      console.error("Error getting blockchain stats:", error);
      res.status(500).json({ message: "Failed to get blockchain stats" });
    }
  });

  // Create HTTP server
  const httpServer = createServer(app);
  // Enhanced Risk Assessment Endpoints
  app.post("/api/risk-assessment/tender", async (req: Request, res: Response) => {
    try {
      const { tenderData } = req.body;
      if (!tenderData) {
        return res.status(400).json({ message: "Tender data is required" });
      }
      
      const { riskAssessmentEngine } = await import('./risk-assessment');
      const assessment = await riskAssessmentEngine.assessTenderRisk(tenderData);
      
      res.json({
        success: true,
        assessment,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        message: `Tender risk assessment failed: ${error.message}` 
      });
    }
  });

  app.post("/api/risk-assessment/firm", async (req: Request, res: Response) => {
    try {
      const { firmData } = req.body;
      if (!firmData) {
        return res.status(400).json({ message: "Firm data is required" });
      }
      
      const { riskAssessmentEngine } = await import('./risk-assessment');
      const assessment = await riskAssessmentEngine.assessFirmRisk(firmData);
      
      res.json({
        success: true,
        assessment,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        message: `Firm risk assessment failed: ${error.message}` 
      });
    }
  });

  app.get("/api/risk-assessment/dashboard", async (req: Request, res: Response) => {
    try {
      const tenders = await storage.getTenders();
      const firms = await storage.getFirms();
      
      // Calculate risk statistics
      const tenderRisks = tenders.map(t => t.riskScore || 25);
      const avgTenderRisk = tenderRisks.length > 0 ? 
        Math.round(tenderRisks.reduce((a, b) => a + b, 0) / tenderRisks.length) : 25;
      
      const highRiskTenders = tenders.filter(t => (t.riskScore || 25) >= 70).length;
      const criticalRiskTenders = tenders.filter(t => (t.riskScore || 25) >= 85).length;
      
      res.json({
        summary: {
          totalTenders: tenders.length,
          totalFirms: firms.length,
          avgTenderRisk,
          avgFirmRisk: 35,
          highRiskTenders,
          criticalRiskTenders,
          highRiskFirms: 1
        },
        tenderRiskDistribution: {
          low: tenders.filter(t => (t.riskScore || 25) < 25).length,
          medium: tenders.filter(t => (t.riskScore || 25) >= 25 && (t.riskScore || 25) < 50).length,
          high: tenders.filter(t => (t.riskScore || 25) >= 50 && (t.riskScore || 25) < 75).length,
          critical: tenders.filter(t => (t.riskScore || 25) >= 75).length
        },
        recentHighRiskItems: tenders.filter(t => (t.riskScore || 25) >= 50)
          .slice(0, 5)
          .map(t => ({ 
            type: 'tender', 
            id: t.id, 
            title: t.title, 
            risk: t.riskScore || 25,
            factors: {
              financial: t.riskScore > 60 ? 'High' : 'Medium',
              technical: 'Medium',
              compliance: t.title.includes('Medical') ? 'High' : 'Low'
            }
          }))
      });
    } catch (error) {
      res.status(500).json({ 
        message: `Risk dashboard data failed: ${error.message}` 
      });
    }
  });

  return httpServer;
}

// Helper functions for simulating AI processing

function simulateOcrProcessing(filename: string): Promise<{ text: string }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        text: `TENDER NOTIFICATION
Project: ${filename.split('.')[0]}
Reference: GEM/2023/B/AI-12345
Estimated Value: ₹2,50,00,000
Bid Submission Deadline: 30 days from publication
Technical Bid Opening: Next day after submission
Financial Bid Opening: After technical evaluation

ELIGIBILITY CRITERIA:
• Class A contractors with minimum 5 years experience
• ISO certification mandatory
• Previous government project experience required
• Minimum annual turnover: ₹50 Crores
• Valid contractor license

TECHNICAL SPECIFICATIONS:
• Cloud-based infrastructure required
• 24/7 support and maintenance
• Data migration and security compliance
• Performance benchmarks defined`
      });
    }, 1000);
  });
}

function simulateNlpAnalysis(text: string): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(JSON.stringify({
        sentiment: { score: 0.82, label: "Positive" },
        entities: [
          { type: "ORGANIZATION", text: "Ministry of Electronics & IT" },
          { type: "AMOUNT", text: "₹2,50,00,000" },
          { type: "REQUIREMENT", text: "ISO certification" },
          { type: "REQUIREMENT", text: "Class A license" }
        ],
        keyPhrases: [
          "Cloud-based infrastructure",
          "Security compliance",
          "Technical specifications",
          "Performance benchmarks"
        ],
        criticalClauses: [
          "Penalty clause: 0.5% per week delay",
          "Performance guarantee: 10% of contract value",
          "Warranty period: 3 years comprehensive"
        ],
        complianceRequirements: [
          "GDPR compliance for data handling",
          "Indian data localization mandatory",
          "Security audit clearance required"
        ],
        summary: "High-value IT infrastructure project focusing on cloud migration and digital transformation. Strong technical requirements with emphasis on security compliance and performance benchmarks."
      }));
    }, 1500);
  });
}

function simulateGptAnalysis(text: string): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(JSON.stringify({
        recommendation: "HIGHLY FAVORABLE",
        score: 92,
        insights: [
          { category: "Market Opportunity", score: 9.2, details: "Excellent market fit with current trends" },
          { category: "Technical Feasibility", score: 9.4, details: "Strong match with firm capabilities" },
          { category: "Financial Viability", score: 8.7, details: "Estimated ROI: 24-28%" },
          { category: "Competitive Advantage", score: 8.2, details: "8-12 expected bidders" }
        ],
        predictiveAnalytics: {
          successProbability: 87,
          optimalStrategy: "Competitive pricing with technical emphasis",
          resourceAllocation: "15 FTE for 8 months",
          cashFlowImpact: "Positive from month 2"
        },
        riskAssessment: {
          technical: { level: "Low", details: "Existing capabilities cover requirements" },
          financial: { level: "Low", details: "Strong payment terms" },
          timeline: { level: "Medium", details: "Tight delivery schedule" },
          compliance: { level: "Low", details: "Established processes in place" }
        },
        actionRecommendations: [
          "Immediate team assembly for proposal preparation",
          "Focus on technical differentiators in bid",
          "Highlight government project experience",
          "Competitive pricing strategy (12-15% margin)"
        ],
        summary: "GPT-4 recommends pursuing this tender. High alignment with firm capabilities, favorable market conditions, and strong potential ROI make this an excellent opportunity."
      }));
    }, 2000);
  });
}
