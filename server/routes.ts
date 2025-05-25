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

  // Create HTTP server
  const httpServer = createServer(app);
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
