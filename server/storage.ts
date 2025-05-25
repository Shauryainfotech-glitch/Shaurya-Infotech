import { 
  users, type User, type InsertUser,
  tenders, type Tender, type InsertTender,
  firms, type Firm, type InsertFirm,
  documents, type Document, type InsertDocument
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
}

// In-memory storage implementation
export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private tenders: Map<number, Tender>;
  private firms: Map<number, Firm>;
  private documents: Map<number, Document>;
  
  private nextUserId: number;
  private nextTenderId: number;
  private nextFirmId: number;
  private nextDocumentId: number;

  constructor() {
    this.users = new Map();
    this.tenders = new Map();
    this.firms = new Map();
    this.documents = new Map();
    
    this.nextUserId = 1;
    this.nextTenderId = 1;
    this.nextFirmId = 1;
    this.nextDocumentId = 1;
    
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
    return Array.from(this.tenders.values());
  }
  
  async createTender(tender: InsertTender): Promise<Tender> {
    const id = this.nextTenderId++;
    const now = new Date();
    const newTender: Tender = { 
      ...tender, 
      id, 
      createdAt: now
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
    return Array.from(this.firms.values());
  }
  
  async createFirm(firm: InsertFirm): Promise<Firm> {
    const id = this.nextFirmId++;
    const now = new Date();
    const newFirm: Firm = { 
      ...firm, 
      id, 
      createdAt: now
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
  
  // Initialize with sample data
  private initializeData() {
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
        gptAnalysis: "GPT-4 recommends pursuing this tender. High alignment with firm capabilities, favorable market conditions."
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
        gptAnalysis: "Moderate recommendation. Higher competition but strong profit potential."
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
        gptAnalysis: "Highly recommended. Excellent fit, low risk, high success probability."
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
    
    // Add users
    this.createUser({
      username: "admin",
      password: "admin123",
      name: "Admin User",
      email: "admin@tenderai.com",
      role: "admin"
    });
    
    // Add tenders
    sampleTenders.forEach(tender => {
      this.createTender(tender);
    });
    
    // Add firms
    sampleFirms.forEach(firm => {
      this.createFirm(firm);
    });
  }
}

export const storage = new MemStorage();
