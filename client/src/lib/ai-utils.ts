// AI-powered tender management utilities with real OpenAI integration

import { apiRequest } from './queryClient';

/**
 * Generates an AI response using real OpenAI GPT-4
 */
export async function generateAIResponse(message: string): Promise<string> {
  try {
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message })
    });
    
    if (!response.ok) {
      throw new Error('Failed to get AI response');
    }
    
    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('Error generating AI response:', error);
    return "I apologize, but I'm having trouble processing your request right now. Please try again.";
  }
}

/**
 * Analyzes tender documents using real OpenAI
 */
export async function analyzeTenderDocument(documentText: string): Promise<{
  entities: Array<{type: string, text: string}>;
  keyPhrases: string[];
  sentiment: {score: number, label: string};
  criticalClauses: string[];
  complianceRequirements: string[];
  summary: string;
}> {
  try {
    const response = await fetch('/api/ai/analyze-document', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ documentText })
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze document');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error analyzing document:', error);
    return {
      entities: [],
      keyPhrases: [],
      sentiment: { score: 0, label: 'neutral' },
      criticalClauses: [],
      complianceRequirements: [],
      summary: 'Analysis unavailable'
    };
  }
}

/**
 * Performs strategic analysis using real OpenAI GPT-4
 */
export async function performGPTAnalysis(tenderData: any): Promise<{
  recommendation: string;
  score: number;
  insights: Array<{category: string, score: number, details: string}>;
  predictiveAnalytics: {
    successProbability: number;
    optimalStrategy: string;
    resourceAllocation: string;
    cashFlowImpact: string;
  };
  riskAssessment: {
    [key: string]: {level: string, details: string}
  };
  actionRecommendations: string[];
  summary: string;
}> {
  try {
    const response = await fetch('/api/ai/analyze-tender', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ tenderData })
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze tender');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error performing GPT analysis:', error);
    return {
      recommendation: "Analysis unavailable",
      score: 0,
      insights: [],
      predictiveAnalytics: {
        successProbability: 0,
        optimalStrategy: "Unknown",
        resourceAllocation: "Unknown",
        cashFlowImpact: "Unknown"
      },
      riskAssessment: {},
      actionRecommendations: [],
      summary: "Analysis unavailable"
    };
  }
}

/**
 * Calculates risk score using AI analysis
 */
export async function calculateRiskScore(tenderData: any): Promise<number> {
  try {
    const response = await fetch('/api/ai/risk-score', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ tenderData })
    });
    
    if (!response.ok) {
      throw new Error('Failed to calculate risk score');
    }
    
    const data = await response.json();
    return data.riskScore;
  } catch (error) {
    console.error('Error calculating risk score:', error);
    return 50; // Default moderate risk
  }
}

/**
 * Predicts success probability using AI
 */
export async function predictSuccessProbability(tenderData: any, firmData: any): Promise<number> {
  try {
    const response = await fetch('/api/ai/success-probability', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ tenderData, firmData })
    });
    
    if (!response.ok) {
      throw new Error('Failed to predict success probability');
    }
    
    const data = await response.json();
    return data.successProbability;
  } catch (error) {
    console.error('Error predicting success probability:', error);
    return 75; // Default moderate probability
  }
}