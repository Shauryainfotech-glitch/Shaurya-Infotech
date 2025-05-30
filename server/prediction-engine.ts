import { aiService } from "./ai-service";

export interface PredictionMetrics {
  successProbability: number;
  marketTrends: {
    sector: string;
    growth: number;
    volatility: number;
    outlook: 'Positive' | 'Neutral' | 'Negative';
  };
  competitionAnalysis: {
    level: 'Low' | 'Medium' | 'High';
    keyCompetitors: number;
    marketShare: number;
    winRate: number;
  };
  financialProjection: {
    estimatedRevenue: number;
    profitMargin: number;
    breakEvenTime: number;
    roi: number;
  };
  riskFactors: {
    technical: number;
    financial: number;
    delivery: number;
    compliance: number;
  };
  recommendations: string[];
  confidenceScore: number;
}

export interface MarketIntelligence {
  sectorTrends: {
    emergingOpportunities: string[];
    decliningSegments: string[];
    averageContractValue: number;
    winRateBySize: Record<string, number>;
  };
  competitorInsights: {
    topPerformers: Array<{
      name: string;
      winRate: number;
      averageContractSize: number;
      specialization: string;
    }>;
    marketGaps: string[];
    pricingTrends: {
      average: number;
      premium: number;
      budget: number;
    };
  };
  tenderPatterns: {
    seasonalTrends: Record<string, number>;
    popularSectors: string[];
    averageTimelines: Record<string, number>;
  };
}

export class PredictionEngine {
  
  async generateTenderPrediction(tenderData: any, firmData?: any): Promise<PredictionMetrics> {
    const successProbability = await this.calculateSuccessProbability(tenderData, firmData);
    const marketTrends = await this.analyzeMarketTrends(tenderData);
    const competitionAnalysis = await this.analyzeCompetition(tenderData);
    const financialProjection = await this.projectFinancials(tenderData);
    const riskFactors = await this.assessPredictionRisks(tenderData);
    const recommendations = await this.generatePredictionRecommendations(tenderData, successProbability);
    
    return {
      successProbability,
      marketTrends,
      competitionAnalysis,
      financialProjection,
      riskFactors,
      recommendations,
      confidenceScore: this.calculatePredictionConfidence(tenderData, firmData)
    };
  }

  async generateMarketIntelligence(sector?: string): Promise<MarketIntelligence> {
    return {
      sectorTrends: await this.analyzeSectorTrends(sector),
      competitorInsights: await this.analyzeCompetitorLandscape(sector),
      tenderPatterns: await this.analyzeTenderPatterns(sector)
    };
  }

  private async calculateSuccessProbability(tenderData: any, firmData?: any): Promise<number> {
    let probability = 50; // Base probability
    
    // Tender complexity analysis
    const complexity = this.assessTenderComplexity(tenderData);
    if (complexity === 'Low') probability += 15;
    else if (complexity === 'High') probability -= 20;
    
    // Competition level impact
    if (tenderData.competition === 'Low') probability += 20;
    else if (tenderData.competition === 'High') probability -= 15;
    
    // Firm capability matching
    if (firmData) {
      const capabilityMatch = this.assessCapabilityMatch(tenderData, firmData);
      probability += capabilityMatch;
    }
    
    // Timeline pressure
    const timelinePressure = this.assessTimelinePressure(tenderData);
    probability -= timelinePressure;
    
    // Value range analysis
    const valueImpact = this.assessValueImpact(tenderData);
    probability += valueImpact;
    
    // Sector experience boost
    if (firmData?.specialization && this.matchesSector(tenderData.sector, firmData.specialization)) {
      probability += 10;
    }
    
    // Past performance factor
    if (firmData?.rating >= 4.5) probability += 15;
    else if (firmData?.rating >= 4.0) probability += 10;
    else if (firmData?.rating < 3.0) probability -= 15;
    
    return Math.max(5, Math.min(95, probability));
  }

  private async analyzeMarketTrends(tenderData: any) {
    const sector = tenderData.sector || 'General';
    
    // Simulate market analysis based on sector
    const sectorGrowth = this.getSectorGrowthRate(sector);
    const volatility = this.getSectorVolatility(sector);
    
    return {
      sector,
      growth: sectorGrowth,
      volatility,
      outlook: sectorGrowth > 5 ? 'Positive' : sectorGrowth < -2 ? 'Negative' : 'Neutral' as const
    };
  }

  private async analyzeCompetition(tenderData: any) {
    const competitionLevel = tenderData.competition || 'Medium';
    
    // Estimate based on tender characteristics
    const estimatedCompetitors = this.estimateCompetitorCount(tenderData);
    const marketShare = this.estimateMarketShare(tenderData);
    const historicalWinRate = this.getHistoricalWinRate(tenderData.sector);
    
    return {
      level: competitionLevel as 'Low' | 'Medium' | 'High',
      keyCompetitors: estimatedCompetitors,
      marketShare,
      winRate: historicalWinRate
    };
  }

  private async projectFinancials(tenderData: any) {
    const contractValue = this.parseContractValue(tenderData.value);
    
    // Financial projections based on industry standards
    const estimatedMargin = this.estimateProfitMargin(tenderData);
    const breakEvenMonths = this.estimateBreakEvenTime(tenderData);
    const roi = this.calculateROI(contractValue, estimatedMargin);
    
    return {
      estimatedRevenue: contractValue,
      profitMargin: estimatedMargin,
      breakEvenTime: breakEvenMonths,
      roi
    };
  }

  private async assessPredictionRisks(tenderData: any) {
    return {
      technical: this.assessTechnicalRisk(tenderData),
      financial: this.assessFinancialRisk(tenderData),
      delivery: this.assessDeliveryRisk(tenderData),
      compliance: this.assessComplianceRisk(tenderData)
    };
  }

  private async generatePredictionRecommendations(tenderData: any, successProbability: number): Promise<string[]> {
    const recommendations: string[] = [];
    
    if (successProbability > 70) {
      recommendations.push("High success probability - prioritize this opportunity");
      recommendations.push("Allocate premium resources for proposal development");
    } else if (successProbability < 30) {
      recommendations.push("Low success probability - consider strategic value only");
      recommendations.push("Evaluate opportunity cost against other prospects");
    } else {
      recommendations.push("Moderate success probability - prepare competitive proposal");
      recommendations.push("Focus on unique value propositions and differentiators");
    }
    
    // Technical recommendations
    if (this.assessTenderComplexity(tenderData) === 'High') {
      recommendations.push("Complex technical requirements - consider technical partnerships");
    }
    
    // Timeline recommendations
    if (this.assessTimelinePressure(tenderData) > 15) {
      recommendations.push("Tight timeline - ensure resource availability and fast-track processes");
    }
    
    // Financial recommendations
    const contractValue = this.parseContractValue(tenderData.value);
    if (contractValue > 10000000) {
      recommendations.push("High-value contract - implement enhanced risk management");
    }
    
    return recommendations.slice(0, 5); // Limit to top 5 recommendations
  }

  private async analyzeSectorTrends(sector?: string) {
    // Sector-specific trend analysis
    const emergingOpportunities = this.getEmergingOpportunities(sector);
    const decliningSegments = this.getDecliningSegments(sector);
    
    return {
      emergingOpportunities,
      decliningSegments,
      averageContractValue: this.getAverageContractValue(sector),
      winRateBySize: {
        'Small (<1M)': 45,
        'Medium (1-10M)': 35,
        'Large (10M+)': 25
      }
    };
  }

  private async analyzeCompetitorLandscape(sector?: string) {
    return {
      topPerformers: [
        { name: "TechCorp Solutions", winRate: 68, averageContractSize: 5200000, specialization: "IT Infrastructure" },
        { name: "InnovateNow Ltd", winRate: 72, averageContractSize: 3800000, specialization: "Digital Transformation" },
        { name: "BuildRight Engineering", winRate: 58, averageContractSize: 8500000, specialization: "Construction" }
      ],
      marketGaps: [
        "AI-powered healthcare solutions",
        "Sustainable infrastructure development",
        "Cybersecurity for government sectors"
      ],
      pricingTrends: {
        average: 4500000,
        premium: 8200000,
        budget: 1800000
      }
    };
  }

  private async analyzeTenderPatterns(sector?: string) {
    return {
      seasonalTrends: {
        'Q1': 15,
        'Q2': 25,
        'Q3': 35,
        'Q4': 25
      },
      popularSectors: ['IT & Technology', 'Healthcare', 'Infrastructure', 'Education'],
      averageTimelines: {
        'Preparation': 21,
        'Submission': 45,
        'Evaluation': 60,
        'Award': 90
      }
    };
  }

  // Helper methods for calculations
  private assessTenderComplexity(tenderData: any): 'Low' | 'Medium' | 'High' {
    const description = (tenderData.description || '').toLowerCase();
    const complexityIndicators = ['advanced', 'complex', 'sophisticated', 'cutting-edge', 'innovative'];
    
    const hasComplexKeywords = complexityIndicators.some(keyword => description.includes(keyword));
    const contractValue = this.parseContractValue(tenderData.value);
    
    if (hasComplexKeywords || contractValue > 15000000) return 'High';
    if (contractValue > 5000000) return 'Medium';
    return 'Low';
  }

  private assessCapabilityMatch(tenderData: any, firmData: any): number {
    let match = 0;
    
    // Specialization alignment
    if (this.matchesSector(tenderData.sector, firmData.specialization)) match += 15;
    
    // Experience level
    if (firmData.completedProjects > 50) match += 10;
    else if (firmData.completedProjects > 20) match += 5;
    
    // Rating factor
    if (firmData.rating >= 4.5) match += 10;
    else if (firmData.rating >= 4.0) match += 5;
    
    return match;
  }

  private assessTimelinePressure(tenderData: any): number {
    const deadline = new Date(tenderData.deadline);
    const now = new Date();
    const daysRemaining = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysRemaining < 7) return 25;
    if (daysRemaining < 15) return 15;
    if (daysRemaining < 30) return 10;
    return 0;
  }

  private assessValueImpact(tenderData: any): number {
    const value = this.parseContractValue(tenderData.value);
    
    if (value < 500000) return -5; // Small contracts might have lower margins
    if (value > 20000000) return -10; // Very large contracts are more competitive
    if (value >= 1000000 && value <= 10000000) return 5; // Sweet spot
    return 0;
  }

  private parseContractValue(valueStr: string): number {
    if (!valueStr) return 1000000; // Default
    return parseFloat(valueStr.replace(/[₹,]/g, '')) || 1000000;
  }

  private matchesSector(tenderSector: string, firmSpecialization: string): boolean {
    if (!tenderSector || !firmSpecialization) return false;
    
    const sectorKeywords = tenderSector.toLowerCase().split(/[\s,&]+/);
    const specKeywords = firmSpecialization.toLowerCase().split(/[\s,&]+/);
    
    return sectorKeywords.some(sector => 
      specKeywords.some(spec => 
        sector.includes(spec) || spec.includes(sector)
      )
    );
  }

  private getSectorGrowthRate(sector: string): number {
    const growthRates: Record<string, number> = {
      'IT & Technology': 8.5,
      'Healthcare': 6.2,
      'Infrastructure': 4.8,
      'Education': 3.2,
      'Defense': 5.5,
      'Energy': 7.1,
      'Manufacturing': 2.8
    };
    
    return growthRates[sector] || 4.0;
  }

  private getSectorVolatility(sector: string): number {
    const volatilityScores: Record<string, number> = {
      'IT & Technology': 25,
      'Healthcare': 15,
      'Infrastructure': 10,
      'Education': 8,
      'Defense': 12,
      'Energy': 30,
      'Manufacturing': 18
    };
    
    return volatilityScores[sector] || 15;
  }

  private estimateCompetitorCount(tenderData: any): number {
    const value = this.parseContractValue(tenderData.value);
    
    if (value > 20000000) return 8; // High-value attracts many
    if (value > 5000000) return 5;
    if (value > 1000000) return 3;
    return 2;
  }

  private estimateMarketShare(tenderData: any): number {
    const complexity = this.assessTenderComplexity(tenderData);
    
    if (complexity === 'High') return 15; // Specialized market
    if (complexity === 'Medium') return 25;
    return 35; // More fragmented market
  }

  private getHistoricalWinRate(sector: string): number {
    const winRates: Record<string, number> = {
      'IT & Technology': 32,
      'Healthcare': 28,
      'Infrastructure': 25,
      'Education': 35,
      'Defense': 22,
      'Energy': 30
    };
    
    return winRates[sector] || 30;
  }

  private estimateProfitMargin(tenderData: any): number {
    const sector = tenderData.sector || 'General';
    const complexity = this.assessTenderComplexity(tenderData);
    
    let baseMargin = 15; // Base 15%
    
    // Sector adjustments
    if (sector.includes('IT')) baseMargin += 5;
    if (sector.includes('Healthcare')) baseMargin += 3;
    if (sector.includes('Infrastructure')) baseMargin -= 2;
    
    // Complexity adjustments
    if (complexity === 'High') baseMargin += 8;
    else if (complexity === 'Low') baseMargin -= 3;
    
    return Math.max(5, Math.min(35, baseMargin));
  }

  private estimateBreakEvenTime(tenderData: any): number {
    const value = this.parseContractValue(tenderData.value);
    const complexity = this.assessTenderComplexity(tenderData);
    
    let months = 6; // Base 6 months
    
    if (value > 10000000) months += 3;
    if (complexity === 'High') months += 2;
    
    return months;
  }

  private calculateROI(revenue: number, margin: number): number {
    return Math.round((revenue * margin / 100) / (revenue * 0.8) * 100); // ROI percentage
  }

  private assessTechnicalRisk(tenderData: any): number {
    const complexity = this.assessTenderComplexity(tenderData);
    if (complexity === 'High') return 65;
    if (complexity === 'Medium') return 35;
    return 15;
  }

  private assessFinancialRisk(tenderData: any): number {
    const value = this.parseContractValue(tenderData.value);
    if (value > 20000000) return 55;
    if (value > 5000000) return 35;
    return 20;
  }

  private assessDeliveryRisk(tenderData: any): number {
    const pressure = this.assessTimelinePressure(tenderData);
    return Math.min(60, pressure * 2 + 15);
  }

  private assessComplianceRisk(tenderData: any): number {
    const sector = tenderData.sector || '';
    if (sector.includes('Healthcare') || sector.includes('Defense')) return 45;
    if (sector.includes('Education') || sector.includes('Government')) return 30;
    return 15;
  }

  private calculatePredictionConfidence(tenderData: any, firmData?: any): number {
    let confidence = 80;
    
    // Data completeness
    const requiredFields = ['title', 'description', 'value', 'deadline', 'organization'];
    const missingFields = requiredFields.filter(field => !tenderData[field]);
    confidence -= missingFields.length * 8;
    
    // Firm data availability
    if (!firmData) confidence -= 15;
    
    // Description quality
    if (tenderData.description && tenderData.description.length < 100) confidence -= 10;
    
    return Math.max(25, confidence);
  }

  private getEmergingOpportunities(sector?: string): string[] {
    const opportunities = [
      "AI and Machine Learning Integration",
      "Sustainable Technology Solutions",
      "Digital Transformation Services",
      "Cybersecurity Enhancement Projects",
      "IoT and Smart Infrastructure",
      "Renewable Energy Systems"
    ];
    
    return opportunities.slice(0, 4);
  }

  private getDecliningSegments(sector?: string): string[] {
    return [
      "Legacy System Maintenance",
      "Traditional Paper-based Processes",
      "Non-digital Communication Systems"
    ];
  }

  private getAverageContractValue(sector?: string): number {
    const averages: Record<string, number> = {
      'IT & Technology': 5800000,
      'Healthcare': 4200000,
      'Infrastructure': 12500000,
      'Education': 2800000
    };
    
    return averages[sector || 'General'] || 4500000;
  }
}

export const predictionEngine = new PredictionEngine();