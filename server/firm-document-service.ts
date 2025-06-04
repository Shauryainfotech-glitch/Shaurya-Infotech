import { storage } from './storage';
import { InsertFirmDocument, FirmDocument } from '@shared/schema';

export class FirmDocumentService {
  
  // Create predefined document structure for a firm based on Wildrex Solutions template
  async initializeFirmDocuments(firmId: number): Promise<FirmDocument[]> {
    const documentTemplates = [
      // Basic Documents
      { category: 'Basic Documents', documentName: 'Adhar Card', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'Gst Certificate', documentNumber: '27ASGPD9447E2ZO', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'Pan Card', documentNumber: 'ASGPD9447E', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'Shop Act', documentNumber: 'L 04717E+11', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'Udyam', documentNumber: 'UDYAM-MH-01-0023903', status: 'Available', validity: 'NA', renewal: 'Every Year Update', responsible: 'Pranali' },
      { category: 'Basic Documents', documentName: 'Company Details', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'PF certification', status: 'No', validity: '', renewal: '' },
      { category: 'Basic Documents', documentName: 'Rent/ Lease/Ownership Deed', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'Employee List', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'Machinery List', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'ECS mandate', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'ITR /Balance sheet/P&L 3 Year', status: 'Available', validity: 'NA', renewal: 'NA' },
      { category: 'Basic Documents', documentName: 'CA Turnover certificate', status: 'Available', validity: 'NA', renewal: 'Every Year Update', responsible: 'Pranali', support: 'Help from Acc Dep' },
      { category: 'Basic Documents', documentName: 'Character certificate', status: 'No', validity: '', renewal: '' },
      { category: 'Basic Documents', documentName: 'PTRC & PETC with chalan', status: 'Available', validity: 'NA', renewal: 'Every Year Update' },

      // Advance Documents
      { category: 'Advance Document', documentName: 'ITR clearance', status: 'Available', validity: 'NA', renewal: 'Every Year Update', responsible: 'Pranali', support: 'Help from Acc Dep' },
      { category: 'Advance Document', documentName: 'GST Return', status: 'Available', validity: 'NA', renewal: 'Monthly', responsible: 'Pranali', support: 'Help from Acc Dep' },
      { category: 'Advance Document', documentName: 'Bank Solvency Certificate', status: 'As per need', validity: 'NA', renewal: 'NA', responsible: 'Pranali', charges: '5000', duration: '4-5' },
      { category: 'Advance Document', documentName: 'ISO 9001:2015 Quality', documentNumber: 'IKSRQW250332905', status: 'Available', validity: '5-3-2028', renewal: 'Require', responsible: 'Pranali', charges: '7000', duration: '4-5', challenges: 'Payment not done' },
      { category: 'Advance Document', documentName: 'ISO 14001:2015', documentNumber: '23EEN23', status: 'Available', validity: '7-8-2026', renewal: 'Require', responsible: 'Pranali', charges: '7000', duration: '4-5', challenges: 'Payment not done' },
      { category: 'Advance Document', documentName: 'ISO 45001:2018 Safety', documentNumber: '23EON25', status: 'Available', validity: '7-8-2026', renewal: 'Require', responsible: 'Pranali', charges: '7000', duration: '4-5', challenges: 'Payment not done' },
      { category: 'Advance Document', documentName: 'ISO 18519-2015(FRP)', documentNumber: 'BOS23W523N', status: 'Available', validity: '12-6-2026', renewal: 'Require', responsible: 'Pranali' },
      { category: 'Advance Document', documentName: 'ISO 18519-2:2022 (FRP)', documentNumber: 'BOS23W523N', status: 'Available', validity: '12-6-2026', renewal: 'Require', responsible: 'Pranali' },
      { category: 'Advance Document', documentName: 'ISO 10406-1:2015 (FRP)', documentNumber: 'BOS23W34N', status: 'Available', validity: '12-6-2026', renewal: 'Require', responsible: 'Pranali' },
      { category: 'Advance Document', documentName: 'NSC Certificate', documentNumber: 'NSC/CP/NAS/2022/93216', status: 'Available', validity: '14-2-2025', renewal: 'Require', responsible: 'Pranali' },

      // Test Reports
      { category: 'Test Report', documentName: 'Test Report Barricade', status: 'Checking', responsible: 'Pranali' },
      { category: 'Test Report', documentName: 'Test report Fire ball', status: 'Checking', responsible: 'Pranali' },
      { category: 'Test Report', documentName: 'Test report Helmet', status: 'Checking', responsible: 'Pranali' },
      { category: 'Test Report', documentName: 'Trade mark class 8', status: 'Waiting for', responsible: 'Pranali' },
      { category: 'Test Report', documentName: 'EN 16630:2015 /GYM', documentNumber: 'BOS23W574N', status: 'Available', validity: '9-8-2026' },

      // MFG Set Up
      { category: 'MFG Set Up', documentName: 'Air Conditioned Helmet', status: '', responsible: '' },
      { category: 'MFG Set Up', documentName: 'Floating Barricade', status: '', responsible: '' },
      { category: 'MFG Set Up', documentName: 'underwater victim search', status: '', responsible: '' },
      { category: 'MFG Set Up', documentName: 'Fire Ball', status: '', responsible: '' },

      // Gem OEM Panel
      { category: 'Gem OEM Panel', documentName: 'FRP Statue', status: '', responsible: '' },
      { category: 'Gem OEM Panel', documentName: 'Fire Ball', status: '', responsible: '' },

      // Subsidy
      { category: 'Subsidy', documentName: 'PMEGP', status: 'DPR', responsible: 'Pranali', duration: '2-3', challenges: 'Machineries have', support: 'Viresh Sir' },
      { category: 'Subsidy', documentName: 'CMEGP', status: 'DPR', responsible: 'Pranali', duration: '2-3', challenges: 'Machineries have', support: 'Viresh Sir' }
    ];

    const createdDocuments: FirmDocument[] = [];
    
    for (const template of documentTemplates) {
      const document = await storage.createFirmDocument({
        firmId,
        category: template.category,
        documentName: template.documentName,
        documentNumber: template.documentNumber || null,
        status: template.status,
        validity: template.validity || null,
        renewal: template.renewal || 'NA',
        responsible: template.responsible || null,
        charges: template.charges || null,
        duration: template.duration || null,
        challenges: template.challenges || null,
        support: template.support || null,
        priority: 'Medium',
        complianceRequired: template.category === 'Advance Document',
        reminderDays: 30
      });
      
      createdDocuments.push(document);
    }
    
    return createdDocuments;
  }

  async getFirmDocumentsByCategory(firmId: number): Promise<Record<string, FirmDocument[]>> {
    const documents = await storage.getFirmDocuments(firmId);
    
    const categorized: Record<string, FirmDocument[]> = {};
    
    documents.forEach(doc => {
      if (!categorized[doc.category]) {
        categorized[doc.category] = [];
      }
      categorized[doc.category].push(doc);
    });
    
    return categorized;
  }

  async updateDocumentStatus(documentId: number, status: string, notes?: string): Promise<FirmDocument | undefined> {
    return await storage.updateFirmDocument(documentId, { 
      status, 
      notes: notes || undefined,
      lastUpdated: new Date()
    });
  }

  async getExpiringDocuments(firmId?: number, days: number = 30): Promise<FirmDocument[]> {
    const allExpiring = await storage.getExpiringDocuments(days);
    
    if (firmId) {
      return allExpiring.filter(doc => doc.firmId === firmId);
    }
    
    return allExpiring;
  }

  async getDocumentComplianceReport(firmId: number): Promise<{
    totalDocuments: number;
    availableDocuments: number;
    missingDocuments: number;
    expiringDocuments: number;
    complianceScore: number;
  }> {
    const documents = await storage.getFirmDocuments(firmId);
    const expiring = await this.getExpiringDocuments(firmId);
    
    const totalDocuments = documents.length;
    const availableDocuments = documents.filter(doc => doc.status === 'Available').length;
    const missingDocuments = documents.filter(doc => doc.status === 'No' || doc.status === 'Not Available').length;
    const expiringDocuments = expiring.length;
    
    const complianceScore = totalDocuments > 0 ? Math.round((availableDocuments / totalDocuments) * 100) : 0;
    
    return {
      totalDocuments,
      availableDocuments,
      missingDocuments,
      expiringDocuments,
      complianceScore
    };
  }
}

export const firmDocumentService = new FirmDocumentService();