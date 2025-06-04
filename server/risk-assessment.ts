import { storage } from './storage';
import { Tender, Firm, FirmDocument } from '@shared/schema';

export interface RiskFactor {
  category: string;
  factor: string;
  score: number; // 0-100 (0 = low risk, 100 = high risk)
  weight: number; // 0-1 (importance of this factor)
  description: string;
  impact: 'Low' | 'Medium' | 'High' | 'Critical';
  mitigation?: string;
}

export interface RiskAssessment {
  tenderId: number;
  firmId?: number;
  overallRiskScore: number; // 0-100
  riskLevel: 'Low' | 'Medium' | 'High' | 'Critical';
  riskFactors: RiskFactor[];
  recommendations: string[];
  mitigationStrategies: string[];
  assessmentDate: Date;
  confidence: number; // 0-100
}

export class RiskAssessmentEngine {
  
  // Comprehensive risk assessment for tender participation
  async assessTenderRisk(tenderId: number, firmId?: number): Promise<RiskAssessment> {
    const tender = await storage.getTender(tenderId);
    if (!tender) {
      throw new Error(`Tender ${tenderId} not found`);
    }

    const firm = firmId ? await storage.getFirm(firmId) : null;
    const firmDocuments = firmId ? await storage.getFirmDocuments(firmId) : [];

    const riskFactors: RiskFactor[] = [];

    // 1. Financial Risk Assessment
    riskFactors.push(...this.assessFinancialRisk(tender, firm));

    // 2. Technical Risk Assessment
    riskFactors.push(...this.assessTechnicalRisk(tender, firm));

    // 3. Compliance Risk Assessment
    riskFactors.push(...this.assessComplianceRisk(tender, firm, firmDocuments));

    // 4. Timeline Risk Assessment
    riskFactors.push(...this.assessTimelineRisk(tender));

    // 5. Market Competition Risk
    riskFactors.push(...this.assessCompetitionRisk(tender));

    // 6. Legal and Regulatory Risk
    riskFactors.push(...this.assessLegalRisk(tender));

    // 7. Operational Risk Assessment
    riskFactors.push(...this.assessOperationalRisk(tender, firm));

    // Calculate overall risk score
    const overallRiskScore = this.calculateOverallRiskScore(riskFactors);
    const riskLevel = this.determineRiskLevel(overallRiskScore);

    // Generate recommendations and mitigation strategies
    const recommendations = this.generateRecommendations(riskFactors, riskLevel);
    const mitigationStrategies = this.generateMitigationStrategies(riskFactors);

    return {
      tenderId,
      firmId,
      overallRiskScore,
      riskLevel,
      riskFactors,
      recommendations,
      mitigationStrategies,
      assessmentDate: new Date(),
      confidence: this.calculateConfidence(riskFactors, firm !== null, firmDocuments.length > 0)
    };
  }

  private assessFinancialRisk(tender: Tender, firm: Firm | null): RiskFactor[] {
    const factors: RiskFactor[] = [];

    // Tender value risk
    const tenderValue = this.extractNumericValue(tender.value);
    if (tenderValue > 10000000) { // > 1 Crore
      factors.push({
        category: 'Financial',
        factor: 'High Value Contract',
        score: 75,
        weight: 0.9,
        description: `Tender value of ${tender.value} presents high financial exposure`,
        impact: 'High',
        mitigation: 'Ensure adequate cash flow and consider performance guarantees'
      });
    } else if (tenderValue > 5000000) { // > 50 Lakhs
      factors.push({
        category: 'Financial',
        factor: 'Medium Value Contract',
        score: 45,
        weight: 0.7,
        description: `Tender value of ${tender.value} requires careful financial planning`,
        impact: 'Medium',
        mitigation: 'Monitor cash flow and maintain adequate working capital'
      });
    }

    // Firm financial health risk
    if (firm) {
      if (firm.financialHealth === 'Poor') {
        factors.push({
          category: 'Financial',
          factor: 'Poor Financial Health',
          score: 85,
          weight: 0.8,
          description: 'Firm has poor financial health rating',
          impact: 'High',
          mitigation: 'Improve financial position before bidding or seek financial backing'
        });
      } else if (firm.financialHealth === 'Fair') {
        factors.push({
          category: 'Financial',
          factor: 'Fair Financial Health',
          score: 55,
          weight: 0.6,
          description: 'Firm has fair financial health with room for improvement',
          impact: 'Medium',
          mitigation: 'Monitor financial metrics and maintain conservative cash flow'
        });
      }
    }

    // Payment terms risk
    if (tender.description?.toLowerCase().includes('delayed payment') || 
        tender.description?.toLowerCase().includes('quarterly payment')) {
      factors.push({
        category: 'Financial',
        factor: 'Payment Terms Risk',
        score: 60,
        weight: 0.7,
        description: 'Tender indicates potential payment delays or irregular payment terms',
        impact: 'Medium',
        mitigation: 'Factor payment delays into cash flow projections'
      });
    }

    return factors;
  }

  private assessTechnicalRisk(tender: Tender, firm: Firm | null): RiskFactor[] {
    const factors: RiskFactor[] = [];

    // Technology complexity assessment
    const techKeywords = ['AI', 'machine learning', 'blockchain', 'cloud', 'IoT', 'cybersecurity'];
    const complexTech = techKeywords.filter(keyword => 
      tender.description?.toLowerCase().includes(keyword.toLowerCase()) ||
      tender.title.toLowerCase().includes(keyword.toLowerCase())
    );

    if (complexTech.length >= 3) {
      factors.push({
        category: 'Technical',
        factor: 'High Technology Complexity',
        score: 70,
        weight: 0.8,
        description: `Project involves complex technologies: ${complexTech.join(', ')}`,
        impact: 'High',
        mitigation: 'Ensure technical team has required expertise or consider partnerships'
      });
    } else if (complexTech.length > 0) {
      factors.push({
        category: 'Technical',
        factor: 'Moderate Technology Complexity',
        score: 45,
        weight: 0.6,
        description: `Project involves: ${complexTech.join(', ')}`,
        impact: 'Medium',
        mitigation: 'Verify team capabilities and provide additional training if needed'
      });
    }

    // Firm specialization alignment
    if (firm && firm.specialization) {
      const specializationMatch = this.assessSpecializationMatch(tender, firm.specialization);
      if (specializationMatch < 0.3) {
        factors.push({
          category: 'Technical',
          factor: 'Specialization Mismatch',
          score: 80,
          weight: 0.9,
          description: `Tender requirements don't align well with firm specialization: ${firm.specialization}`,
          impact: 'High',
          mitigation: 'Consider partnerships or subcontracting for specialized requirements'
        });
      } else if (specializationMatch < 0.6) {
        factors.push({
          category: 'Technical',
          factor: 'Partial Specialization Match',
          score: 50,
          weight: 0.7,
          description: `Tender partially aligns with firm specialization: ${firm.specialization}`,
          impact: 'Medium',
          mitigation: 'Strengthen capabilities in required areas or seek technical partnerships'
        });
      }
    }

    return factors;
  }

  private assessComplianceRisk(tender: Tender, firm: Firm | null, firmDocuments: any[]): RiskFactor[] {
    const factors: RiskFactor[] = [];

    // Document compliance risk
    const requiredDocs = this.identifyRequiredDocuments(tender);
    const availableDocs = firmDocuments.filter(doc => doc.status === 'Available');
    const missingDocs = requiredDocs.filter(req => 
      !availableDocs.some(doc => doc.documentName.toLowerCase().includes(req.toLowerCase()))
    );

    if (missingDocs.length > 0) {
      factors.push({
        category: 'Compliance',
        factor: 'Missing Required Documents',
        score: 85,
        weight: 0.9,
        description: `Missing critical documents: ${missingDocs.join(', ')}`,
        impact: 'Critical',
        mitigation: 'Urgently obtain missing documents or risk disqualification'
      });
    }

    // Expiring documents risk
    const expiringDocs = firmDocuments.filter(doc => {
      if (!doc.expiryDate) return false;
      const expiryDate = new Date(doc.expiryDate);
      const deadline = new Date(tender.deadline);
      return expiryDate <= deadline;
    });

    if (expiringDocs.length > 0) {
      factors.push({
        category: 'Compliance',
        factor: 'Expiring Documents',
        score: 70,
        weight: 0.8,
        description: `Documents expiring before tender deadline: ${expiringDocs.map(d => d.documentName).join(', ')}`,
        impact: 'High',
        mitigation: 'Renew expiring documents immediately'
      });
    }

    // Certification requirements
    if (tender.description?.toLowerCase().includes('iso') && firm) {
      const hasISO = firm.certifications?.some(cert => cert.toLowerCase().includes('iso'));
      if (!hasISO) {
        factors.push({
          category: 'Compliance',
          factor: 'Missing ISO Certification',
          score: 75,
          weight: 0.8,
          description: 'Tender requires ISO certification which firm lacks',
          impact: 'High',
          mitigation: 'Obtain required ISO certification or partner with certified firm'
        });
      }
    }

    return factors;
  }

  private assessTimelineRisk(tender: Tender): RiskFactor[] {
    const factors: RiskFactor[] = [];

    const deadline = new Date(tender.deadline);
    const now = new Date();
    const daysUntilDeadline = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (daysUntilDeadline < 7) {
      factors.push({
        category: 'Timeline',
        factor: 'Very Short Preparation Time',
        score: 90,
        weight: 0.9,
        description: `Only ${daysUntilDeadline} days until submission deadline`,
        impact: 'Critical',
        mitigation: 'Mobilize all resources for urgent preparation or consider skipping'
      });
    } else if (daysUntilDeadline < 15) {
      factors.push({
        category: 'Timeline',
        factor: 'Short Preparation Time',
        score: 65,
        weight: 0.7,
        description: `${daysUntilDeadline} days until submission deadline`,
        impact: 'High',
        mitigation: 'Prioritize critical components and allocate dedicated resources'
      });
    } else if (daysUntilDeadline < 30) {
      factors.push({
        category: 'Timeline',
        factor: 'Limited Preparation Time',
        score: 40,
        weight: 0.5,
        description: `${daysUntilDeadline} days until submission deadline`,
        impact: 'Medium',
        mitigation: 'Plan preparation timeline carefully with buffer time'
      });
    }

    // Project duration risk
    if (tender.description?.toLowerCase().includes('urgent') || 
        tender.description?.toLowerCase().includes('immediate')) {
      factors.push({
        category: 'Timeline',
        factor: 'Urgent Project Requirements',
        score: 70,
        weight: 0.8,
        description: 'Project indicates urgent or immediate delivery requirements',
        impact: 'High',
        mitigation: 'Ensure team availability and consider resource augmentation'
      });
    }

    return factors;
  }

  private assessCompetitionRisk(tender: Tender): RiskFactor[] {
    const factors: RiskFactor[] = [];

    // Competition level based on tender characteristics
    const competitionLevel = tender.competition || 'Medium';
    
    switch (competitionLevel.toLowerCase()) {
      case 'high':
        factors.push({
          category: 'Competition',
          factor: 'High Competition Level',
          score: 75,
          weight: 0.7,
          description: 'High competition expected for this tender',
          impact: 'High',
          mitigation: 'Focus on unique value propositions and competitive pricing'
        });
        break;
      case 'medium':
        factors.push({
          category: 'Competition',
          factor: 'Medium Competition Level',
          score: 50,
          weight: 0.6,
          description: 'Moderate competition expected',
          impact: 'Medium',
          mitigation: 'Prepare strong technical and commercial proposal'
        });
        break;
    }

    // Market position risk
    if (tender.value && this.extractNumericValue(tender.value) > 50000000) { // > 5 Crores
      factors.push({
        category: 'Competition',
        factor: 'Large Contract Attracts Major Players',
        score: 65,
        weight: 0.7,
        description: 'High-value contract likely to attract established competitors',
        impact: 'High',
        mitigation: 'Emphasize unique capabilities and consider consortium approach'
      });
    }

    return factors;
  }

  private assessLegalRisk(tender: Tender): RiskFactor[] {
    const factors: RiskFactor[] = [];

    // Penalty clause risk
    if (tender.description?.toLowerCase().includes('penalty') || 
        tender.description?.toLowerCase().includes('liquidated damages')) {
      factors.push({
        category: 'Legal',
        factor: 'Penalty Clauses Present',
        score: 60,
        weight: 0.7,
        description: 'Tender contains penalty clauses for delays or non-performance',
        impact: 'Medium',
        mitigation: 'Review penalty terms carefully and factor into pricing'
      });
    }

    // Government tender complexity
    if (tender.organization?.toLowerCase().includes('government') || 
        tender.organization?.toLowerCase().includes('ministry')) {
      factors.push({
        category: 'Legal',
        factor: 'Government Tender Complexity',
        score: 45,
        weight: 0.6,
        description: 'Government tenders involve complex compliance and audit requirements',
        impact: 'Medium',
        mitigation: 'Ensure strict compliance with government procurement guidelines'
      });
    }

    // Warranty and maintenance obligations
    if (tender.description?.toLowerCase().includes('warranty') || 
        tender.description?.toLowerCase().includes('maintenance')) {
      factors.push({
        category: 'Legal',
        factor: 'Extended Warranty Obligations',
        score: 50,
        weight: 0.6,
        description: 'Tender requires warranty and maintenance commitments',
        impact: 'Medium',
        mitigation: 'Factor long-term support costs into pricing strategy'
      });
    }

    return factors;
  }

  private assessOperationalRisk(tender: Tender, firm: Firm | null): RiskFactor[] {
    const factors: RiskFactor[] = [];

    // Resource availability risk
    if (firm && firm.activeProjects > 10) {
      factors.push({
        category: 'Operational',
        factor: 'High Current Workload',
        score: 70,
        weight: 0.8,
        description: `Firm has ${firm.activeProjects} active projects, may strain resources`,
        impact: 'High',
        mitigation: 'Assess resource availability and consider team expansion'
      });
    } else if (firm && firm.activeProjects > 5) {
      factors.push({
        category: 'Operational',
        factor: 'Moderate Current Workload',
        score: 45,
        weight: 0.6,
        description: `Firm has ${firm.activeProjects} active projects`,
        impact: 'Medium',
        mitigation: 'Plan resource allocation carefully to avoid conflicts'
      });
    }

    // Geographic risk
    if (tender.location && tender.location !== 'National') {
      factors.push({
        category: 'Operational',
        factor: 'Geographic Location Risk',
        score: 35,
        weight: 0.5,
        description: `Project location: ${tender.location} may require additional logistics`,
        impact: 'Medium',
        mitigation: 'Factor travel and accommodation costs into proposal'
      });
    }

    return factors;
  }

  private calculateOverallRiskScore(riskFactors: RiskFactor[]): number {
    if (riskFactors.length === 0) return 0;

    const weightedSum = riskFactors.reduce((sum, factor) => 
      sum + (factor.score * factor.weight), 0
    );
    const totalWeight = riskFactors.reduce((sum, factor) => sum + factor.weight, 0);

    return Math.round(weightedSum / totalWeight);
  }

  private determineRiskLevel(score: number): 'Low' | 'Medium' | 'High' | 'Critical' {
    if (score >= 80) return 'Critical';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    return 'Low';
  }

  private generateRecommendations(riskFactors: RiskFactor[], riskLevel: string): string[] {
    const recommendations: string[] = [];

    if (riskLevel === 'Critical') {
      recommendations.push('CRITICAL: Carefully reconsider participation in this tender');
      recommendations.push('Conduct detailed risk mitigation planning before proceeding');
    } else if (riskLevel === 'High') {
      recommendations.push('HIGH RISK: Proceed with caution and comprehensive mitigation strategies');
      recommendations.push('Consider partnership opportunities to share risks');
    } else if (riskLevel === 'Medium') {
      recommendations.push('MODERATE RISK: Manageable with proper planning and monitoring');
      recommendations.push('Implement standard risk management practices');
    } else {
      recommendations.push('LOW RISK: Favorable conditions for tender participation');
      recommendations.push('Proceed with confidence using standard processes');
    }

    // Category-specific recommendations
    const categories = [...new Set(riskFactors.map(f => f.category))];
    categories.forEach(category => {
      const categoryFactors = riskFactors.filter(f => f.category === category);
      const avgScore = categoryFactors.reduce((sum, f) => sum + f.score, 0) / categoryFactors.length;
      
      if (avgScore > 70) {
        recommendations.push(`${category}: Requires immediate attention and mitigation measures`);
      } else if (avgScore > 50) {
        recommendations.push(`${category}: Monitor closely and implement preventive measures`);
      }
    });

    return recommendations;
  }

  private generateMitigationStrategies(riskFactors: RiskFactor[]): string[] {
    const strategies = riskFactors
      .filter(factor => factor.mitigation)
      .map(factor => factor.mitigation!)
      .filter((value, index, self) => self.indexOf(value) === index); // Remove duplicates

    // Add general mitigation strategies
    strategies.push('Maintain detailed project monitoring and regular risk reviews');
    strategies.push('Establish clear communication channels with all stakeholders');
    strategies.push('Implement contingency plans for identified high-risk areas');

    return strategies;
  }

  private calculateConfidence(riskFactors: RiskFactor[], hasFirmData: boolean, hasDocumentData: boolean): number {
    let confidence = 60; // Base confidence

    if (hasFirmData) confidence += 20;
    if (hasDocumentData) confidence += 15;
    if (riskFactors.length > 5) confidence += 5; // More factors = better analysis

    return Math.min(confidence, 100);
  }

  private extractNumericValue(value: string): number {
    // Extract numeric value from currency strings like "₹2,50,00,000"
    const cleaned = value.replace(/[^\d.]/g, '');
    return parseFloat(cleaned) || 0;
  }

  private assessSpecializationMatch(tender: Tender, specialization: string): number {
    const tenderText = (tender.title + ' ' + tender.description).toLowerCase();
    const specWords = specialization.toLowerCase().split(/[\s&,-]+/);
    
    const matches = specWords.filter(word => 
      word.length > 3 && tenderText.includes(word)
    ).length;
    
    return matches / specWords.length;
  }

  private identifyRequiredDocuments(tender: Tender): string[] {
    const docs: string[] = [];
    const text = (tender.title + ' ' + tender.description).toLowerCase();

    if (text.includes('iso')) docs.push('ISO Certification');
    if (text.includes('gst')) docs.push('GST Registration');
    if (text.includes('pan')) docs.push('PAN Card');
    if (text.includes('udyam') || text.includes('msme')) docs.push('Udyam Registration');
    if (text.includes('experience') || text.includes('work order')) docs.push('Experience Certificates');
    if (text.includes('financial') || text.includes('turnover')) docs.push('Financial Statements');
    if (text.includes('bank') || text.includes('solvency')) docs.push('Bank Solvency Certificate');

    return docs;
  }
}

export const riskAssessmentEngine = new RiskAssessmentEngine();