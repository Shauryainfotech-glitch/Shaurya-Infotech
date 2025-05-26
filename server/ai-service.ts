import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export class AIService {
  // Intelligent chatbot for tender assistance
  async generateChatResponse(message: string): Promise<string> {
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4o", // the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        messages: [
          {
            role: "system",
            content: "You are TenderAI Pro, an expert AI assistant for tender management. You help users with tender analysis, document processing, compliance checking, risk assessment, and strategic recommendations. Provide clear, actionable advice for tender-related queries."
          },
          {
            role: "user",
            content: message
          }
        ],
        max_tokens: 500,
        temperature: 0.7,
      });

      return response.choices[0].message.content || "I'm sorry, I couldn't process your request right now.";
    } catch (error) {
      console.error('Error generating chat response:', error);
      throw new Error('Failed to generate AI response');
    }
  }

  // Document analysis with AI
  async analyzeDocument(documentText: string): Promise<any> {
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4o", // the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        messages: [
          {
            role: "system",
            content: "You are an expert document analyst. Extract key information from tender documents and provide structured analysis."
          },
          {
            role: "user",
            content: `Analyze this document and extract key information. Provide response in JSON format:
            {
              "entities": [{"type": "ORGANIZATION|AMOUNT|DATE|REQUIREMENT", "text": "entity text"}],
              "keyPhrases": ["important phrases"],
              "sentiment": {"score": 0.0-1.0, "label": "positive|negative|neutral"},
              "criticalClauses": ["important clauses"],
              "complianceRequirements": ["compliance items"],
              "summary": "brief summary"
            }
            
            Document: ${documentText}`
          }
        ],
        response_format: { type: "json_object" },
        max_tokens: 1000,
      });

      return JSON.parse(response.choices[0].message.content || '{}');
    } catch (error) {
      console.error('Error analyzing document:', error);
      throw new Error('Failed to analyze document');
    }
  }

  // Strategic tender analysis
  async analyzeTender(tenderData: any): Promise<any> {
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4o", // the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        messages: [
          {
            role: "system",
            content: "You are a strategic tender analyst. Provide comprehensive analysis of tender opportunities including recommendations, insights, and risk assessment."
          },
          {
            role: "user",
            content: `Analyze this tender opportunity and provide strategic recommendations in JSON format:
            {
              "recommendation": "HIGHLY_FAVORABLE|FAVORABLE|NEUTRAL|UNFAVORABLE",
              "score": 0-100,
              "insights": [{"category": "category", "score": 0-10, "details": "details"}],
              "predictiveAnalytics": {
                "successProbability": 0-100,
                "optimalStrategy": "strategy description",
                "resourceAllocation": "resource needs",
                "cashFlowImpact": "impact description"
              },
              "riskAssessment": {
                "technical": {"level": "LOW|MEDIUM|HIGH", "details": "details"},
                "financial": {"level": "LOW|MEDIUM|HIGH", "details": "details"},
                "timeline": {"level": "LOW|MEDIUM|HIGH", "details": "details"},
                "compliance": {"level": "LOW|MEDIUM|HIGH", "details": "details"}
              },
              "actionRecommendations": ["recommendation 1", "recommendation 2"],
              "summary": "comprehensive summary"
            }
            
            Tender Data: ${JSON.stringify(tenderData)}`
          }
        ],
        response_format: { type: "json_object" },
        max_tokens: 1500,
      });

      return JSON.parse(response.choices[0].message.content || '{}');
    } catch (error) {
      console.error('Error analyzing tender:', error);
      throw new Error('Failed to analyze tender');
    }
  }

  // Risk score calculation
  async calculateRiskScore(tenderData: any): Promise<number> {
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4o", // the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        messages: [
          {
            role: "system",
            content: "You are a risk assessment expert. Calculate a risk score (0-100) for tender opportunities based on various factors."
          },
          {
            role: "user",
            content: `Calculate a risk score (0-100, where 0 is lowest risk) for this tender. Consider factors like complexity, timeline, financial requirements, competition, and compliance. Respond with JSON: {"riskScore": number, "explanation": "brief explanation"}
            
            Tender Data: ${JSON.stringify(tenderData)}`
          }
        ],
        response_format: { type: "json_object" },
        max_tokens: 300,
      });

      const result = JSON.parse(response.choices[0].message.content || '{"riskScore": 50}');
      return Math.min(100, Math.max(0, result.riskScore));
    } catch (error) {
      console.error('Error calculating risk score:', error);
      throw new Error('Failed to calculate risk score');
    }
  }

  // Success probability prediction
  async predictSuccessProbability(tenderData: any, firmData: any): Promise<number> {
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4o", // the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        messages: [
          {
            role: "system",
            content: "You are a success prediction expert. Analyze tender opportunities and firm capabilities to predict success probability."
          },
          {
            role: "user",
            content: `Predict the success probability (0-100%) for this firm bidding on this tender. Consider firm capabilities, experience, financial strength, and tender requirements. Respond with JSON: {"successProbability": number, "keyFactors": ["factor 1", "factor 2"]}
            
            Tender: ${JSON.stringify(tenderData)}
            Firm: ${JSON.stringify(firmData)}`
          }
        ],
        response_format: { type: "json_object" },
        max_tokens: 400,
      });

      const result = JSON.parse(response.choices[0].message.content || '{"successProbability": 75}');
      return Math.min(100, Math.max(0, result.successProbability));
    } catch (error) {
      console.error('Error predicting success probability:', error);
      throw new Error('Failed to predict success probability');
    }
  }
}

export const aiService = new AIService();