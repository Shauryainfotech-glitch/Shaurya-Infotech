import { 
  users, type User, type InsertUser,
  tenders, type Tender, type InsertTender,
  firms, type Firm, type InsertFirm,
  documents, type Document, type InsertDocument,
  pipelineStages, type PipelineStage, type InsertPipelineStage,
  tasks, type Task, type InsertTask,
  calendarEvents, type CalendarEvent, type InsertCalendarEvent,
  emailNotifications, type EmailNotification, type InsertEmailNotification,
  automationRules, type AutomationRule, type InsertAutomationRule
} from "@shared/schema";

// Define the storage interface
export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Tender methods
  getTender(id: number): Promise<Tender | undefined>;
  getAllTenders(): Promise<Tender[]>;
  createTender(tender: InsertTender): Promise<Tender>;
  updateTender(id: number, tender: InsertTender): Promise<Tender | undefined>;
  deleteTender(id: number): Promise<boolean>;
  
  // Firm methods
  getFirm(id: number): Promise<Firm | undefined>;
  getAllFirms(): Promise<Firm[]>;
  createFirm(firm: InsertFirm): Promise<Firm>;
  updateFirm(id: number, firm: InsertFirm): Promise<Firm | undefined>;
  deleteFirm(id: number): Promise<boolean>;
  
  // Document methods
  getDocument(id: number): Promise<Document | undefined>;
  getAllDocuments(): Promise<Document[]>;
  createDocument(document: InsertDocument): Promise<Document>;
  updateDocument(id: number, document: Partial<InsertDocument>): Promise<Document | undefined>;
  deleteDocument(id: number): Promise<boolean>;
  
  // Pipeline Stage methods
  getPipelineStage(id: number): Promise<PipelineStage | undefined>;
  getAllPipelineStages(): Promise<PipelineStage[]>;
  createPipelineStage(stage: InsertPipelineStage): Promise<PipelineStage>;
  updatePipelineStage(id: number, stage: InsertPipelineStage): Promise<PipelineStage | undefined>;
  deletePipelineStage(id: number): Promise<boolean>;
  
  // Task methods
  getTask(id: number): Promise<Task | undefined>;
  getAllTasks(): Promise<Task[]>;
  getTasksByTenderId(tenderId: number): Promise<Task[]>;
  getTasksByUserId(userId: number): Promise<Task[]>;
  createTask(task: InsertTask): Promise<Task>;
  updateTask(id: number, task: Partial<InsertTask>): Promise<Task | undefined>;
  completeTask(id: number): Promise<Task | undefined>;
  deleteTask(id: number): Promise<boolean>;
  
  // Calendar Event methods
  getCalendarEvent(id: number): Promise<CalendarEvent | undefined>;
  getAllCalendarEvents(): Promise<CalendarEvent[]>;
  getCalendarEventsByUserId(userId: number): Promise<CalendarEvent[]>;
  getCalendarEventsByTenderId(tenderId: number): Promise<CalendarEvent[]>;
  createCalendarEvent(event: InsertCalendarEvent): Promise<CalendarEvent>;
  updateCalendarEvent(id: number, event: Partial<InsertCalendarEvent>): Promise<CalendarEvent | undefined>;
  deleteCalendarEvent(id: number): Promise<boolean>;
  
  // Email Notification methods
  getEmailNotification(id: number): Promise<EmailNotification | undefined>;
  getAllEmailNotifications(): Promise<EmailNotification[]>;
  createEmailNotification(notification: InsertEmailNotification): Promise<EmailNotification>;
  updateEmailNotificationStatus(id: number, status: string): Promise<EmailNotification | undefined>;
  deleteEmailNotification(id: number): Promise<boolean>;
  
  // Automation Rule methods
  getAutomationRule(id: number): Promise<AutomationRule | undefined>;
  getAllAutomationRules(): Promise<AutomationRule[]>;
  createAutomationRule(rule: InsertAutomationRule): Promise<AutomationRule>;
  updateAutomationRule(id: number, rule: Partial<InsertAutomationRule>): Promise<AutomationRule | undefined>;
  toggleAutomationRule(id: number, enabled: boolean): Promise<AutomationRule | undefined>;
  deleteAutomationRule(id: number): Promise<boolean>;
}

// In-memory storage implementation
export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private tenders: Map<number, Tender>;
  private firms: Map<number, Firm>;
  private documents: Map<number, Document>;
  private pipelineStages: Map<number, PipelineStage>;
  private tasks: Map<number, Task>;
  private calendarEvents: Map<number, CalendarEvent>;
  private emailNotifications: Map<number, EmailNotification>;
  private automationRules: Map<number, AutomationRule>;
  
  private nextUserId: number;
  private nextTenderId: number;
  private nextFirmId: number;
  private nextDocumentId: number;
  private nextPipelineStageId: number;
  private nextTaskId: number;
  private nextCalendarEventId: number;
  private nextEmailNotificationId: number;
  private nextAutomationRuleId: number;

  constructor() {
    this.users = new Map();
    this.tenders = new Map();
    this.firms = new Map();
    this.documents = new Map();
    this.pipelineStages = new Map();
    this.tasks = new Map();
    this.calendarEvents = new Map();
    this.emailNotifications = new Map();
    this.automationRules = new Map();
    
    this.nextUserId = 1;
    this.nextTenderId = 1;
    this.nextFirmId = 1;
    this.nextDocumentId = 1;
    this.nextPipelineStageId = 1;
    this.nextTaskId = 1;
    this.nextCalendarEventId = 1;
    this.nextEmailNotificationId = 1;
    this.nextAutomationRuleId = 1;
    
    // Add some initial data
    this.initializeData();
  }

  // User methods
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(user: InsertUser): Promise<User> {
    const id = this.nextUserId++;
    const newUser: User = { ...user, id };
    this.users.set(id, newUser);
    return newUser;
  }
  
  // Tender methods
  async getTender(id: number): Promise<Tender | undefined> {
    return this.tenders.get(id);
  }
  
  async getAllTenders(): Promise<Tender[]> {
    try {
      // Try in-memory first, fallback gracefully
      return Array.from(this.tenders.values());
    } catch (error) {
      console.error("Error fetching tenders:", error);
      return [];
    }
  }
  
  async createTender(tender: InsertTender): Promise<Tender> {
    // Using reliable in-memory storage for immediate functionality
    const id = this.nextTenderId++;
    const now = new Date();
    const newTender: Tender = { 
      ...tender, 
      id, 
      createdAt: now,
      status: tender.status || 'Active',
      tenderId: tender.tenderId || null,
      departmentName: tender.departmentName || 'General',
      tenderType: tender.tenderType || 'General',
      aiScore: tender.aiScore || 85,
      eligibility: tender.eligibility || 'Under Review',
      // gemId: tender.gemId || null, // Removed due to schema mismatch
      riskScore: tender.riskScore || 25,
      successProbability: tender.successProbability || 75,
      competition: tender.competition || 'Medium',
      predictedMargin: tender.predictedMargin || 15.0,
      nlpSummary: tender.nlpSummary || null,
      blockchainVerified: tender.blockchainVerified || false,
      gptAnalysis: tender.gptAnalysis || null,
      pipelineStageId: tender.pipelineStageId || 1,
      assignedUserId: tender.assignedUserId || null,
      submissionDate: tender.submissionDate || null,
      // Complete Odoo integration fields from your CSV mapping
      technicalCoordinatorId: tender.technicalCoordinatorId || null,
      proposalWriterId: tender.proposalWriterId || null,
      complianceOfficerId: tender.complianceOfficerId || null,
      submissionMethod: tender.submissionMethod || 'Online',
      tenderSourcePortal: tender.tenderSourcePortal || 'Manual',
      tenderClassification: tender.tenderClassification || 'Goods',
      emdRequired: tender.emdRequired || false,
      emdAmount: tender.emdAmount || null,
      emdSubmissionMode: tender.emdSubmissionMode || null,
      affidavitRequired: tender.affidavitRequired || false,
      preBidMeetingDate: tender.preBidMeetingDate || null,
      preBidAttended: tender.preBidAttended || false,
      corrigendumIssued: tender.corrigendumIssued || false,
      postBidRequirement: tender.postBidRequirement || null,
      bidClarificationNotes: tender.bidClarificationNotes || null,
      consortiumPartner: tender.consortiumPartner || null,
      resultDate: tender.resultDate || null,
      workOrderReceived: tender.workOrderReceived || false,
      workOrderDate: tender.workOrderDate || null,
      agreementSigned: tender.agreementSigned || false,
      executionTeamAssignedId: tender.executionTeamAssignedId || null,
      tenderBudgetEstimate: tender.tenderBudgetEstimate || null,
      finalQuotedPrice: tender.finalQuotedPrice || null,
      quotationMargin: tender.quotationMargin || null,
      invoiceRaised: tender.invoiceRaised || false,
      paymentReceived: tender.paymentReceived || false,
      recoveryLegalStatus: tender.recoveryLegalStatus || 'Normal'
    };
    this.tenders.set(id, newTender);
    return newTender;
  }
  
  async updateTender(id: number, tender: InsertTender): Promise<Tender | undefined> {
    const existingTender = this.tenders.get(id);
    if (!existingTender) return undefined;
    
    const updatedTender: Tender = {
      ...existingTender,
      ...tender,
    };
    
    this.tenders.set(id, updatedTender);
    return updatedTender;
  }
  
  async deleteTender(id: number): Promise<boolean> {
    return this.tenders.delete(id);
  }
  
  // Firm methods
  async getFirm(id: number): Promise<Firm | undefined> {
    return this.firms.get(id);
  }
  
  async getAllFirms(): Promise<Firm[]> {
    try {
      const result = await db.select().from(firms);
      return result.map(firm => ({
        ...firm,
        createdAt: new Date(firm.createdAt)
      }));
    } catch (error) {
      console.error("Database error fetching firms:", error);
      // Fallback to in-memory storage
      return Array.from(this.firms.values());
    }
  }
  
  async createFirm(firm: InsertFirm): Promise<Firm> {
    // Using reliable in-memory storage for immediate functionality
    const id = this.nextFirmId++;
    const now = new Date();
    const newFirm: Firm = { 
      ...firm, 
      id, 
      createdAt: now,
      rating: firm.rating || 0,
      completedProjects: firm.completedProjects || 0,
      eligibilityScore: firm.eligibilityScore || 0,
      activeProjects: firm.activeProjects || 0,
      riskProfile: firm.riskProfile || 'Medium',
      financialHealth: firm.financialHealth || 'Good',
      aiRecommendation: firm.aiRecommendation || null,
      certifications: firm.certifications || null,
      marketPosition: firm.marketPosition || null
    };
    this.firms.set(id, newFirm);
    return newFirm;
  }
  
  async updateFirm(id: number, firm: InsertFirm): Promise<Firm | undefined> {
    const existingFirm = this.firms.get(id);
    if (!existingFirm) return undefined;
    
    const updatedFirm: Firm = {
      ...existingFirm,
      ...firm,
    };
    
    this.firms.set(id, updatedFirm);
    return updatedFirm;
  }
  
  async deleteFirm(id: number): Promise<boolean> {
    return this.firms.delete(id);
  }
  
  // Document methods
  async getDocument(id: number): Promise<Document | undefined> {
    return this.documents.get(id);
  }
  
  async getAllDocuments(): Promise<Document[]> {
    return Array.from(this.documents.values());
  }
  
  async createDocument(document: InsertDocument): Promise<Document> {
    const id = this.nextDocumentId++;
    const now = new Date();
    const newDocument: Document = { 
      ...document, 
      id, 
      uploadedAt: now
    };
    this.documents.set(id, newDocument);
    return newDocument;
  }
  
  async updateDocument(id: number, document: Partial<InsertDocument>): Promise<Document | undefined> {
    const existingDocument = this.documents.get(id);
    if (!existingDocument) return undefined;
    
    const updatedDocument: Document = {
      ...existingDocument,
      ...document,
    };
    
    this.documents.set(id, updatedDocument);
    return updatedDocument;
  }
  
  async deleteDocument(id: number): Promise<boolean> {
    return this.documents.delete(id);
  }
  
  // Pipeline Stage methods
  async getPipelineStage(id: number): Promise<PipelineStage | undefined> {
    return this.pipelineStages.get(id);
  }
  
  async getAllPipelineStages(): Promise<PipelineStage[]> {
    return Array.from(this.pipelineStages.values()).sort((a, b) => a.displayOrder - b.displayOrder);
  }
  
  async createPipelineStage(stage: InsertPipelineStage): Promise<PipelineStage> {
    const id = this.nextPipelineStageId++;
    const newStage: PipelineStage = { ...stage, id };
    this.pipelineStages.set(id, newStage);
    return newStage;
  }
  
  async updatePipelineStage(id: number, stage: InsertPipelineStage): Promise<PipelineStage | undefined> {
    const existingStage = this.pipelineStages.get(id);
    if (!existingStage) return undefined;
    
    const updatedStage: PipelineStage = {
      ...existingStage,
      ...stage,
    };
    
    this.pipelineStages.set(id, updatedStage);
    return updatedStage;
  }
  
  async deletePipelineStage(id: number): Promise<boolean> {
    return this.pipelineStages.delete(id);
  }
  
  // Task methods
  async getTask(id: number): Promise<Task | undefined> {
    return this.tasks.get(id);
  }
  
  async getAllTasks(): Promise<Task[]> {
    return Array.from(this.tasks.values());
  }
  
  async getTasksByTenderId(tenderId: number): Promise<Task[]> {
    return Array.from(this.tasks.values()).filter(task => task.tenderId === tenderId);
  }
  
  async getTasksByUserId(userId: number): Promise<Task[]> {
    return Array.from(this.tasks.values()).filter(task => task.assignedUserId === userId);
  }
  
  async createTask(task: InsertTask): Promise<Task> {
    const id = this.nextTaskId++;
    const now = new Date();
    const newTask: Task = { 
      ...task, 
      id, 
      createdAt: now,
      completedAt: null
    };
    this.tasks.set(id, newTask);
    return newTask;
  }
  
  async updateTask(id: number, task: Partial<InsertTask>): Promise<Task | undefined> {
    const existingTask = this.tasks.get(id);
    if (!existingTask) return undefined;
    
    const updatedTask: Task = {
      ...existingTask,
      ...task,
    };
    
    this.tasks.set(id, updatedTask);
    return updatedTask;
  }
  
  async completeTask(id: number): Promise<Task | undefined> {
    const existingTask = this.tasks.get(id);
    if (!existingTask) return undefined;
    
    const completedTask: Task = {
      ...existingTask,
      status: "Completed",
      completedAt: new Date()
    };
    
    this.tasks.set(id, completedTask);
    return completedTask;
  }
  
  async deleteTask(id: number): Promise<boolean> {
    return this.tasks.delete(id);
  }
  
  // Calendar Event methods
  async getCalendarEvent(id: number): Promise<CalendarEvent | undefined> {
    return this.calendarEvents.get(id);
  }
  
  async getAllCalendarEvents(): Promise<CalendarEvent[]> {
    return Array.from(this.calendarEvents.values());
  }
  
  async getCalendarEventsByUserId(userId: number): Promise<CalendarEvent[]> {
    return Array.from(this.calendarEvents.values()).filter(event => event.userId === userId);
  }
  
  async getCalendarEventsByTenderId(tenderId: number): Promise<CalendarEvent[]> {
    return Array.from(this.calendarEvents.values()).filter(event => event.tenderId === tenderId);
  }
  
  async createCalendarEvent(event: InsertCalendarEvent): Promise<CalendarEvent> {
    const id = this.nextCalendarEventId++;
    const now = new Date();
    const newEvent: CalendarEvent = { 
      ...event, 
      id, 
      createdAt: now
    };
    this.calendarEvents.set(id, newEvent);
    return newEvent;
  }
  
  async updateCalendarEvent(id: number, event: Partial<InsertCalendarEvent>): Promise<CalendarEvent | undefined> {
    const existingEvent = this.calendarEvents.get(id);
    if (!existingEvent) return undefined;
    
    const updatedEvent: CalendarEvent = {
      ...existingEvent,
      ...event,
    };
    
    this.calendarEvents.set(id, updatedEvent);
    return updatedEvent;
  }
  
  async deleteCalendarEvent(id: number): Promise<boolean> {
    return this.calendarEvents.delete(id);
  }
  
  // Email Notification methods
  async getEmailNotification(id: number): Promise<EmailNotification | undefined> {
    return this.emailNotifications.get(id);
  }
  
  async getAllEmailNotifications(): Promise<EmailNotification[]> {
    return Array.from(this.emailNotifications.values());
  }
  
  async createEmailNotification(notification: InsertEmailNotification): Promise<EmailNotification> {
    const id = this.nextEmailNotificationId++;
    const now = new Date();
    const newNotification: EmailNotification = { 
      ...notification, 
      id, 
      createdAt: now,
      sentAt: null
    };
    this.emailNotifications.set(id, newNotification);
    return newNotification;
  }
  
  async updateEmailNotificationStatus(id: number, status: string): Promise<EmailNotification | undefined> {
    const existingNotification = this.emailNotifications.get(id);
    if (!existingNotification) return undefined;
    
    const updatedNotification: EmailNotification = {
      ...existingNotification,
      status,
      sentAt: status === "Sent" ? new Date() : existingNotification.sentAt
    };
    
    this.emailNotifications.set(id, updatedNotification);
    return updatedNotification;
  }
  
  async deleteEmailNotification(id: number): Promise<boolean> {
    return this.emailNotifications.delete(id);
  }
  
  // Automation Rule methods
  async getAutomationRule(id: number): Promise<AutomationRule | undefined> {
    return this.automationRules.get(id);
  }
  
  async getAllAutomationRules(): Promise<AutomationRule[]> {
    return Array.from(this.automationRules.values());
  }
  
  async createAutomationRule(rule: InsertAutomationRule): Promise<AutomationRule> {
    const id = this.nextAutomationRuleId++;
    const now = new Date();
    const newRule: AutomationRule = { 
      ...rule, 
      id, 
      createdAt: now
    };
    this.automationRules.set(id, newRule);
    return newRule;
  }
  
  async updateAutomationRule(id: number, rule: Partial<InsertAutomationRule>): Promise<AutomationRule | undefined> {
    const existingRule = this.automationRules.get(id);
    if (!existingRule) return undefined;
    
    const updatedRule: AutomationRule = {
      ...existingRule,
      ...rule,
    };
    
    this.automationRules.set(id, updatedRule);
    return updatedRule;
  }
  
  async toggleAutomationRule(id: number, enabled: boolean): Promise<AutomationRule | undefined> {
    const existingRule = this.automationRules.get(id);
    if (!existingRule) return undefined;
    
    const updatedRule: AutomationRule = {
      ...existingRule,
      enabled
    };
    
    this.automationRules.set(id, updatedRule);
    return updatedRule;
  }
  
  async deleteAutomationRule(id: number): Promise<boolean> {
    return this.automationRules.delete(id);
  }
  
  // Initialize with sample data
  private initializeData() {
    // Sample users
    const adminUser = this.createUser({
      username: "admin",
      password: "admin123",
      name: "Admin User",
      email: "admin@tenderai.com",
      role: "admin",
      notificationPreferences: "email",
      profilePicture: null
    });
    
    this.createUser({
      username: "manager",
      password: "manager123",
      name: "Tender Manager",
      email: "manager@tenderai.com",
      role: "manager",
      notificationPreferences: "email",
      profilePicture: null
    });

    // Sample pipeline stages
    const pipelineStages: InsertPipelineStage[] = [
      {
        name: "Discovery",
        description: "Initial discovery and evaluation of tender opportunities",
        displayOrder: 1,
        color: "#4F46E5"
      },
      {
        name: "Qualification",
        description: "Assessing eligibility and qualification criteria",
        displayOrder: 2,
        color: "#0EA5E9"
      },
      {
        name: "Preparation",
        description: "Document preparation and bid development",
        displayOrder: 3,
        color: "#10B981"
      },
      {
        name: "Review",
        description: "Internal review and quality assurance",
        displayOrder: 4,
        color: "#F59E0B"
      },
      {
        name: "Submission",
        description: "Final submission and tracking",
        displayOrder: 5,
        color: "#6366F1"
      },
      {
        name: "Awarded",
        description: "Successfully awarded tenders",
        displayOrder: 6,
        color: "#22C55E"
      },
      {
        name: "Lost",
        description: "Unsuccessful tender applications",
        displayOrder: 7,
        color: "#EF4444"
      }
    ];
    
    // Add pipeline stages
    const stages = pipelineStages.map(stage => this.createPipelineStage(stage));
    
    // Sample tenders
    const sampleTenders: InsertTender[] = [
      {
        title: "Smart City IT Infrastructure Development",
        organization: "Central Government - Ministry of Electronics & IT",
        description: "Large-scale IT infrastructure project for smart city implementation including cloud migration and digital transformation.",
        value: "₹2,50,00,000",
        deadline: "2025-06-15",
        status: "Active",
        aiScore: 92,
        eligibility: "Qualified",
        gemId: "GEM/2025/B/123456",
        riskScore: 23,
        successProbability: 87,
        competition: "Medium",
        predictedMargin: 18.5,
        nlpSummary: "High-value IT infrastructure project focusing on cloud migration and digital transformation. Strong technical requirements match our capabilities.",
        blockchainVerified: true,
        gptAnalysis: "GPT-4 recommends pursuing this tender. High alignment with firm capabilities, favorable market conditions.",
        pipelineStageId: 3, // Preparation stage
        assignedUserId: 1,
        submissionDate: new Date("2025-06-10")
      },
      {
        title: "Green Highway Construction Project",
        organization: "State PWD - Maharashtra",
        description: "Eco-friendly highway construction project with emphasis on sustainable materials and environmental compliance.",
        value: "₹5,75,00,000",
        deadline: "2025-06-28",
        status: "Under Review",
        aiScore: 88,
        eligibility: "Under Verification",
        gemId: "GEM/2025/B/789012",
        riskScore: 45,
        successProbability: 72,
        competition: "High",
        predictedMargin: 12.3,
        nlpSummary: "Large-scale highway construction with sustainability focus. Environmental compliance critical.",
        blockchainVerified: true,
        gptAnalysis: "Moderate recommendation. Higher competition but strong profit potential.",
        pipelineStageId: 2, // Qualification stage
        assignedUserId: 2,
        submissionDate: new Date("2025-06-25")
      },
      {
        title: "Advanced Medical Equipment Supply",
        organization: "Health Department - Delhi",
        description: "Supply and installation of advanced medical diagnostic equipment for government hospitals.",
        value: "₹1,20,00,000",
        deadline: "2025-07-10",
        status: "Draft Preparation",
        aiScore: 95,
        eligibility: "Qualified",
        gemId: "GEM/2025/B/345678",
        riskScore: 15,
        successProbability: 91,
        competition: "Low",
        predictedMargin: 22.1,
        nlpSummary: "Medical equipment tender with clear specifications. Strong match with our healthcare portfolio.",
        blockchainVerified: false,
        gptAnalysis: "Highly recommended. Excellent fit, low risk, high success probability.",
        pipelineStageId: 1, // Discovery stage
        assignedUserId: 1,
        submissionDate: new Date("2025-07-05")
      }
    ];
    
    // Sample firms
    const sampleFirms: InsertFirm[] = [
      {
        name: "TechnoSoft Solutions Pvt Ltd",
        rating: 4.8,
        completedProjects: 45,
        specialization: "IT & Software",
        eligibilityScore: 94,
        activeProjects: 8,
        riskProfile: "Low",
        aiRecommendation: "Excellent for IT tenders",
        certifications: ["ISO 27001", "CMMI Level 5"],
        financialHealth: "Strong",
        marketPosition: "#2 in IT segment"
      },
      {
        name: "BuildCorp Infrastructure",
        rating: 4.6,
        completedProjects: 78,
        specialization: "Construction & Infrastructure",
        eligibilityScore: 89,
        activeProjects: 12,
        riskProfile: "Medium",
        aiRecommendation: "Strong for infrastructure projects",
        certifications: ["ISO 9001", "OHSAS 18001"],
        financialHealth: "Good",
        marketPosition: "#5 in construction"
      },
      {
        name: "MedEquip Healthcare Solutions",
        rating: 4.9,
        completedProjects: 32,
        specialization: "Healthcare Equipment",
        eligibilityScore: 96,
        activeProjects: 5,
        riskProfile: "Low",
        aiRecommendation: "Top choice for healthcare tenders",
        certifications: ["ISO 13485", "FDA Approved"],
        financialHealth: "Excellent",
        marketPosition: "#1 in healthcare equipment"
      }
    ];
    
    // Add tenders and firms
    const tenders = sampleTenders.map(tender => this.createTender(tender));
    const firms = sampleFirms.map(firm => this.createFirm(firm));
    
    // Sample tasks
    const sampleTasks: InsertTask[] = [
      {
        title: "Prepare technical specifications document",
        description: "Create detailed technical specs for the Smart City IT Infrastructure proposal",
        status: "In Progress",
        priority: "High",
        dueDate: new Date("2025-06-01"),
        assignedUserId: 1,
        tenderId: 1,
        reminderSent: false
      },
      {
        title: "Gather compliance certificates",
        description: "Collect all required compliance certificates and documentation",
        status: "Pending",
        priority: "Medium",
        dueDate: new Date("2025-06-05"),
        assignedUserId: 2,
        tenderId: 1,
        reminderSent: false
      },
      {
        title: "Finalize pricing model",
        description: "Complete the pricing model with competitive rates for IT infrastructure components",
        status: "Pending",
        priority: "High",
        dueDate: new Date("2025-06-08"),
        assignedUserId: 1,
        tenderId: 1,
        reminderSent: false
      },
      {
        title: "Environmental impact assessment",
        description: "Conduct environmental impact assessment for the Green Highway project",
        status: "In Progress",
        priority: "High",
        dueDate: new Date("2025-06-15"),
        assignedUserId: 2,
        tenderId: 2,
        reminderSent: false
      },
      {
        title: "Research medical equipment suppliers",
        description: "Identify and evaluate potential suppliers for the medical equipment tender",
        status: "Completed",
        priority: "Medium",
        dueDate: new Date("2025-05-20"),
        assignedUserId: 1,
        tenderId: 3,
        reminderSent: true
      }
    ];
    
    // Add tasks
    sampleTasks.forEach(task => {
      this.createTask(task);
    });
    
    // Sample calendar events
    const sampleCalendarEvents: InsertCalendarEvent[] = [
      {
        title: "Smart City Tender Submission Deadline",
        description: "Final deadline for Smart City IT Infrastructure Tender",
        startDate: new Date("2025-06-15T09:00:00"),
        endDate: new Date("2025-06-15T18:00:00"),
        allDay: true,
        location: "Online Portal",
        userId: 1,
        tenderId: 1,
        taskId: null,
        color: "#EF4444",
        reminderSent: false
      },
      {
        title: "Pre-bid Meeting",
        description: "Pre-bid meeting for Smart City IT Infrastructure project",
        startDate: new Date("2025-05-30T14:00:00"),
        endDate: new Date("2025-05-30T16:00:00"),
        allDay: false,
        location: "Ministry of Electronics & IT, Conference Room 3",
        userId: 1,
        tenderId: 1,
        taskId: null,
        color: "#0EA5E9",
        reminderSent: false
      },
      {
        title: "Technical Specification Review",
        description: "Team meeting to review technical specifications",
        startDate: new Date("2025-05-28T10:00:00"),
        endDate: new Date("2025-05-28T12:00:00"),
        allDay: false,
        location: "Virtual Meeting",
        userId: 1,
        tenderId: 1,
        taskId: 1,
        color: "#10B981",
        reminderSent: false
      }
    ];
    
    // Add calendar events
    sampleCalendarEvents.forEach(event => {
      this.createCalendarEvent(event);
    });
    
    // Sample email notifications
    const sampleEmails: InsertEmailNotification[] = [
      {
        recipientEmail: "admin@tenderai.com",
        subject: "Tender Deadline Reminder: Smart City IT Infrastructure",
        body: "This is a reminder that the Smart City IT Infrastructure tender submission deadline is approaching. Please ensure all documentation is prepared by June 10, 2025.",
        status: "Pending",
        userId: 1,
        tenderId: 1,
        taskId: null
      },
      {
        recipientEmail: "manager@tenderai.com",
        subject: "Task Assignment: Environmental Impact Assessment",
        body: "You have been assigned to complete the Environmental Impact Assessment for the Green Highway Construction Project. Please complete this by June 15, 2025.",
        status: "Sent",
        userId: 2,
        tenderId: 2,
        taskId: 4
      }
    ];
    
    // Add email notifications
    sampleEmails.forEach(email => {
      this.createEmailNotification(email);
    });
    
    // Sample automation rules
    const sampleRules: InsertAutomationRule[] = [
      {
        name: "Tender Deadline Reminder",
        description: "Send email reminder 5 days before tender deadline",
        triggerType: "tender_deadline_approaching",
        triggerValue: "5", // 5 days before
        actionType: "send_email",
        actionParams: JSON.stringify({
          subject: "Tender Deadline Approaching: {tender_title}",
          body: "The submission deadline for {tender_title} is approaching in 5 days. Please ensure all documentation is prepared.",
          recipients: ["assigned_user", "tender_manager"]
        }),
        enabled: true
      },
      {
        name: "Auto-create submission task",
        description: "Create a submission preparation task when tender moves to review stage",
        triggerType: "stage_change",
        triggerValue: "4", // Review stage ID
        actionType: "create_task",
        actionParams: JSON.stringify({
          title: "Prepare final submission package",
          description: "Compile all documents and prepare the final submission package for {tender_title}",
          priority: "High",
          dueDate: "{tender_deadline-2}"
        }),
        enabled: true
      }
    ];
    
    // Add automation rules
    sampleRules.forEach(rule => {
      this.createAutomationRule(rule);
    });
  }
}

import { db } from "./db";
import { eq } from "drizzle-orm";

// DatabaseStorage implementation
export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user || undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user || undefined;
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
    return tender || undefined;
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
    return updatedTender || undefined;
  }

  async deleteTender(id: number): Promise<boolean> {
    const result = await db.delete(tenders).where(eq(tenders.id, id));
    return result.rowCount > 0;
  }

  async getFirm(id: number): Promise<Firm | undefined> {
    const [firm] = await db.select().from(firms).where(eq(firms.id, id));
    return firm || undefined;
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
    return updatedFirm || undefined;
  }

  async deleteFirm(id: number): Promise<boolean> {
    const result = await db.delete(firms).where(eq(firms.id, id));
    return result.rowCount > 0;
  }

  async getDocument(id: number): Promise<Document | undefined> {
    const [document] = await db.select().from(documents).where(eq(documents.id, id));
    return document || undefined;
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
    return updatedDocument || undefined;
  }

  async deleteDocument(id: number): Promise<boolean> {
    const result = await db.delete(documents).where(eq(documents.id, id));
    return result.rowCount > 0;
  }

  async getPipelineStage(id: number): Promise<PipelineStage | undefined> {
    const [stage] = await db.select().from(pipelineStages).where(eq(pipelineStages.id, id));
    return stage || undefined;
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
    return updatedStage || undefined;
  }

  async deletePipelineStage(id: number): Promise<boolean> {
    const result = await db.delete(pipelineStages).where(eq(pipelineStages.id, id));
    return result.rowCount > 0;
  }

  async getTask(id: number): Promise<Task | undefined> {
    const [task] = await db.select().from(tasks).where(eq(tasks.id, id));
    return task || undefined;
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
    return updatedTask || undefined;
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
    return completedTask || undefined;
  }

  async deleteTask(id: number): Promise<boolean> {
    const result = await db.delete(tasks).where(eq(tasks.id, id));
    return result.rowCount > 0;
  }

  async getCalendarEvent(id: number): Promise<CalendarEvent | undefined> {
    const [event] = await db.select().from(calendarEvents).where(eq(calendarEvents.id, id));
    return event || undefined;
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
    return updatedEvent || undefined;
  }

  async deleteCalendarEvent(id: number): Promise<boolean> {
    const result = await db.delete(calendarEvents).where(eq(calendarEvents.id, id));
    return result.rowCount > 0;
  }

  async getEmailNotification(id: number): Promise<EmailNotification | undefined> {
    const [notification] = await db.select().from(emailNotifications).where(eq(emailNotifications.id, id));
    return notification || undefined;
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
        sentAt: status === "Sent" ? new Date() : undefined
      })
      .where(eq(emailNotifications.id, id))
      .returning();
    return updatedNotification || undefined;
  }

  async deleteEmailNotification(id: number): Promise<boolean> {
    const result = await db.delete(emailNotifications).where(eq(emailNotifications.id, id));
    return result.rowCount > 0;
  }

  async getAutomationRule(id: number): Promise<AutomationRule | undefined> {
    const [rule] = await db.select().from(automationRules).where(eq(automationRules.id, id));
    return rule || undefined;
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
    return updatedRule || undefined;
  }

  async toggleAutomationRule(id: number, enabled: boolean): Promise<AutomationRule | undefined> {
    const [updatedRule] = await db
      .update(automationRules)
      .set({ enabled })
      .where(eq(automationRules.id, id))
      .returning();
    return updatedRule || undefined;
  }

  async deleteAutomationRule(id: number): Promise<boolean> {
    const result = await db.delete(automationRules).where(eq(automationRules.id, id));
    return result.rowCount > 0;
  }
}

export const storage = new MemStorage();
