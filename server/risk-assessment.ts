import { aiService } from "./ai-service";

export interface RiskFactors {
  financial: number;
  technical: number;
  operational: number;
  compliance: number;
  market: number;
  timeline: number;
}

export interface RiskAssessmentResult {
  overallScore: number;
  riskLevel: 'Low' | 'Medium' | 'High' | 'Critical';
  factors: RiskFactors;
  recommendations: string[];
  mitigationStrategies: string[];
  confidenceScore: number;
}

export class RiskAssessmentEngine {
  
  async assessTenderRisk(tenderData: any): Promise<RiskAssessmentResult> {
    const factors = await this.calculateRiskFactors(tenderData);
    const overallScore = this.calculateOverallScore(factors);
    const riskLevel = this.determineRiskLevel(overallScore);
    
    const recommendations = await this.generateRecommendations(factors, tenderData);
    const mitigationStrategies = await this.generateMitigationStrategies(factors, tenderData);
    
    return {
      overallScore,
      riskLevel,
      factors,
      recommendations,
      mitigationStrategies,
      confidenceScore: this.calculateConfidenceScore(tenderData)
    };
  }

  async assessFirmRisk(firmData: any): Promise<RiskAssessmentResult> {
    const factors = await this.calculateFirmRiskFactors(firmData);
    const overallScore = this.calculateOverallScore(factors);
    const riskLevel = this.determineRiskLevel(overallScore);
    
    const recommendations = await this.generateFirmRecommendations(factors, firmData);
    const mitigationStrategies = await this.generateFirmMitigationStrategies(factors, firmData);
    
    return {
      overallScore,
      riskLevel,
      factors,
      recommendations,
      mitigationStrategies,
      confidenceScore: this.calculateFirmConfidenceScore(firmData)
    };
  }

  private async calculateRiskFactors(tenderData: any): Promise<RiskFactors> {
    // Financial Risk Assessment
    const financialRisk = this.assessFinancialRisk(tenderData);
    
    // Technical Risk Assessment
    const technicalRisk = this.assessTechnicalRisk(tenderData);
    
    // Operational Risk Assessment
    const operationalRisk = this.assessOperationalRisk(tenderData);
    
    // Compliance Risk Assessment
    const complianceRisk = this.assessComplianceRisk(tenderData);
    
    // Market Risk Assessment
    const marketRisk = this.assessMarketRisk(tenderData);
    
    // Timeline Risk Assessment
    const timelineRisk = this.assessTimelineRisk(tenderData);

    return {
      financial: financialRisk,
      technical: technicalRisk,
      operational: operationalRisk,
      compliance: complianceRisk,
      market: marketRisk,
      timeline: timelineRisk
    };
  }

  private async calculateFirmRiskFactors(firmData: any): Promise<RiskFactors> {
    return {
      financial: this.assessFirmFinancialRisk(firmData),
      technical: this.assessFirmTechnicalRisk(firmData),
      operational: this.assessFirmOperationalRisk(firmData),
      compliance: this.assessFirmComplianceRisk(firmData),
      market: this.assessFirmMarketRisk(firmData),
      timeline: this.assessFirmDeliveryRisk(firmData)
    };
  }

  private assessFinancialRisk(tenderData: any): number {
    let risk = 0;
    
    // Value-based risk
    const value = parseFloat(tenderData.value?.replace(/[₹,]/g, '') || '0');
    if (value > 10000000) risk += 20; // High value tenders
    else if (value > 5000000) risk += 10;
    else if (value < 1000000) risk += 5; // Very low value might indicate issues
    
    // Payment terms risk
    if (tenderData.paymentTerms > 90) risk += 15;
    else if (tenderData.paymentTerms > 60) risk += 10;
    
    // EMD requirements
    if (tenderData.emdRequired && !tenderData.emdAmount) risk += 10;
    
    return Math.min(risk, 100);
  }

  private assessTechnicalRisk(tenderData: any): number {
    let risk = 0;
    
    // Technical complexity
    const complexityKeywords = ['advanced', 'cutting-edge', 'prototype', 'custom', 'complex'];
    const description = (tenderData.description || '').toLowerCase();
    
    complexityKeywords.forEach(keyword => {
      if (description.includes(keyword)) risk += 10;
    });
    
    // Technical specifications clarity
    if (!tenderData.technicalSpecs || tenderData.technicalSpecs.length < 100) {
      risk += 20; // Vague specifications
    }
    
    // Innovation requirement
    if (description.includes('innovation') || description.includes('research')) {
      risk += 15;
    }
    
    return Math.min(risk, 100);
  }

  private assessOperationalRisk(tenderData: any): number {
    let risk = 0;
    
    // Geographic risk
    const location = (tenderData.location || '').toLowerCase();
    const highRiskLocations = ['remote', 'rural', 'conflict', 'border'];
    
    highRiskLocations.forEach(loc => {
      if (location.includes(loc)) risk += 15;
    });
    
    // Implementation complexity
    if (tenderData.multipleLocations) risk += 10;
    if (tenderData.requiresCoordination) risk += 10;
    
    // Resource requirements
    if (tenderData.manpowerRequirement > 50) risk += 15;
    else if (tenderData.manpowerRequirement > 20) risk += 10;
    
    return Math.min(risk, 100);
  }

  private assessComplianceRisk(tenderData: any): number {
    let risk = 0;
    
    // Regulatory compliance
    if (tenderData.sector === 'Healthcare' || tenderData.sector === 'Defense') {
      risk += 20; // High regulatory requirements
    }
    
    // Documentation requirements
    if (tenderData.requiredCertifications?.length > 5) risk += 15;
    
    // Compliance history
    if (tenderData.pastNonCompliance) risk += 25;
    
    // Environmental clearances
    if (tenderData.requiresEnvironmentalClearance) risk += 15;
    
    return Math.min(risk, 100);
  }

  private assessMarketRisk(tenderData: any): number {
    let risk = 0;
    
    // Competition level
    if (tenderData.competition === 'High') risk += 20;
    else if (tenderData.competition === 'Medium') risk += 10;
    
    // Market conditions
    if (tenderData.marketVolatility === 'High') risk += 15;
    
    // Currency risk
    if (tenderData.foreignCurrency) risk += 10;
    
    // Supplier dependency
    if (tenderData.singleSourceSupplier) risk += 15;
    
    return Math.min(risk, 100);
  }

  private assessTimelineRisk(tenderData: any): number {
    let risk = 0;
    
    // Deadline pressure
    const deadline = new Date(tenderData.deadline);
    const now = new Date();
    const daysToDeadline = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysToDeadline < 7) risk += 30; // Very tight deadline
    else if (daysToDeadline < 15) risk += 20;
    else if (daysToDeadline < 30) risk += 10;
    
    // Implementation timeline
    if (tenderData.implementationDays < 30) risk += 15; // Very fast implementation
    
    // Seasonal factors
    const month = deadline.getMonth();
    if (month === 2 || month === 11) risk += 5; // March/December rush
    
    return Math.min(risk, 100);
  }

  private assessFirmFinancialRisk(firmData: any): number {
    let risk = 0;
    
    // Financial health
    if (firmData.financialHealth === 'Poor') risk += 30;
    else if (firmData.financialHealth === 'Average') risk += 15;
    
    // Payment history
    if (firmData.paymentDelays > 2) risk += 20;
    
    // Credit rating
    if (firmData.creditRating < 600) risk += 25;
    else if (firmData.creditRating < 700) risk += 15;
    
    return Math.min(risk, 100);
  }

  private assessFirmTechnicalRisk(firmData: any): number {
    let risk = 0;
    
    // Technical capability
    if (firmData.technicalCapability === 'Limited') risk += 25;
    else if (firmData.technicalCapability === 'Moderate') risk += 10;
    
    // Past project complexity
    if (firmData.averageProjectComplexity === 'Low') risk += 15;
    
    // Innovation track record
    if (!firmData.innovationRecord) risk += 20;
    
    return Math.min(risk, 100);
  }

  private assessFirmOperationalRisk(firmData: any): number {
    let risk = 0;
    
    // Operational capacity
    if (firmData.currentCapacityUtilization > 90) risk += 20; // Overutilized
    else if (firmData.currentCapacityUtilization < 30) risk += 15; // Underutilized
    
    // Management quality
    if (firmData.managementQuality === 'Poor') risk += 25;
    else if (firmData.managementQuality === 'Average') risk += 10;
    
    // Employee turnover
    if (firmData.employeeTurnover > 20) risk += 15;
    
    return Math.min(risk, 100);
  }

  private assessFirmComplianceRisk(firmData: any): number {
    let risk = 0;
    
    // Compliance status
    if (firmData.complianceStatus === 'Non-Compliant') risk += 30;
    else if (firmData.complianceStatus === 'Pending') risk += 15;
    
    // Legal issues
    if (firmData.pendingLegalIssues > 0) risk += 20;
    
    // Certification status
    if (firmData.expiredCertifications > 0) risk += 15;
    
    return Math.min(risk, 100);
  }

  private assessFirmMarketRisk(firmData: any): number {
    let risk = 0;
    
    // Market position
    if (firmData.marketPosition === 'Weak') risk += 20;
    else if (firmData.marketPosition === 'Average') risk += 10;
    
    // Client concentration
    if (firmData.topClientDependency > 50) risk += 15; // High dependency on top client
    
    // Market reputation
    if (firmData.marketReputation === 'Poor') risk += 25;
    else if (firmData.marketReputation === 'Average') risk += 10;
    
    return Math.min(risk, 100);
  }

  private assessFirmDeliveryRisk(firmData: any): number {
    let risk = 0;
    
    // Delivery track record
    if (firmData.onTimeDeliveryRate < 70) risk += 25;
    else if (firmData.onTimeDeliveryRate < 85) risk += 15;
    
    // Quality issues
    if (firmData.qualityIssueRate > 10) risk += 20;
    
    // Project delays
    if (firmData.averageProjectDelay > 15) risk += 15; // Days
    
    return Math.min(risk, 100);
  }

  private calculateOverallScore(factors: RiskFactors): number {
    // Weighted average based on importance
    const weights = {
      financial: 0.25,
      technical: 0.20,
      operational: 0.20,
      compliance: 0.15,
      market: 0.10,
      timeline: 0.10
    };
    
    return Math.round(
      factors.financial * weights.financial +
      factors.technical * weights.technical +
      factors.operational * weights.operational +
      factors.compliance * weights.compliance +
      factors.market * weights.market +
      factors.timeline * weights.timeline
    );
  }

  private determineRiskLevel(score: number): 'Low' | 'Medium' | 'High' | 'Critical' {
    if (score >= 75) return 'Critical';
    if (score >= 50) return 'High';
    if (score >= 25) return 'Medium';
    return 'Low';
  }

  private async generateRecommendations(factors: RiskFactors, tenderData: any): Promise<string[]> {
    const recommendations: string[] = [];
    
    if (factors.financial > 50) {
      recommendations.push("Consider financial guarantees and milestone-based payments");
      recommendations.push("Evaluate payment terms and cash flow impact");
    }
    
    if (factors.technical > 50) {
      recommendations.push("Conduct detailed technical feasibility study");
      recommendations.push("Consider partnering with technical experts");
    }
    
    if (factors.compliance > 50) {
      recommendations.push("Review all regulatory requirements thoroughly");
      recommendations.push("Engage compliance specialists early");
    }
    
    if (factors.timeline > 50) {
      recommendations.push("Develop detailed project timeline with buffers");
      recommendations.push("Consider phased implementation approach");
    }
    
    // Use AI for additional context-specific recommendations
    if (recommendations.length < 3) {
      try {
        const aiRecommendations = await aiService.generateRiskRecommendations(tenderData, factors);
        recommendations.push(...aiRecommendations);
      } catch (error) {
        console.error('AI recommendation generation failed:', error);
      }
    }
    
    return recommendations.slice(0, 5); // Limit to 5 recommendations
  }

  private async generateMitigationStrategies(factors: RiskFactors, tenderData: any): Promise<string[]> {
    const strategies: string[] = [];
    
    if (factors.operational > 40) {
      strategies.push("Establish clear communication protocols and project management systems");
      strategies.push("Implement regular progress monitoring and reporting mechanisms");
    }
    
    if (factors.market > 40) {
      strategies.push("Develop competitive differentiation strategy");
      strategies.push("Monitor market conditions and have contingency plans");
    }
    
    if (factors.financial > 40) {
      strategies.push("Secure adequate working capital and credit facilities");
      strategies.push("Consider insurance coverage for project risks");
    }
    
    return strategies;
  }

  private async generateFirmRecommendations(factors: RiskFactors, firmData: any): Promise<string[]> {
    const recommendations: string[] = [];
    
    if (factors.financial > 50) {
      recommendations.push("Request additional financial guarantees or bank guarantees");
      recommendations.push("Consider shorter payment cycles or advance payments");
    }
    
    if (factors.technical > 50) {
      recommendations.push("Require demonstration of technical capabilities");
      recommendations.push("Consider technical support partnerships");
    }
    
    if (factors.operational > 50) {
      recommendations.push("Implement enhanced project monitoring and reporting");
      recommendations.push("Consider performance-based contracts");
    }
    
    return recommendations;
  }

  private async generateFirmMitigationStrategies(factors: RiskFactors, firmData: any): Promise<string[]> {
    const strategies: string[] = [];
    
    if (factors.compliance > 40) {
      strategies.push("Require regular compliance audits and certifications");
      strategies.push("Establish compliance monitoring checkpoints");
    }
    
    if (factors.operational > 40) {
      strategies.push("Implement vendor performance management system");
      strategies.push("Develop backup vendor relationships");
    }
    
    return strategies;
  }

  private calculateConfidenceScore(data: any): number {
    let confidence = 100;
    
    // Reduce confidence based on missing data
    const requiredFields = ['value', 'deadline', 'description', 'organization'];
    const missingFields = requiredFields.filter(field => !data[field]);
    confidence -= missingFields.length * 10;
    
    // Adjust based on data quality
    if (data.description && data.description.length < 50) confidence -= 15;
    if (!data.technicalSpecs) confidence -= 10;
    
    return Math.max(confidence, 30); // Minimum 30% confidence
  }

  private calculateFirmConfidenceScore(data: any): number {
    let confidence = 100;
    
    const requiredFields = ['name', 'specialization', 'completedProjects'];
    const missingFields = requiredFields.filter(field => !data[field]);
    confidence -= missingFields.length * 15;
    
    if (!data.financialHealth) confidence -= 20;
    if (!data.certifications) confidence -= 10;
    
    return Math.max(confidence, 25);
  }
}

export const riskAssessmentEngine = new RiskAssessmentEngine();