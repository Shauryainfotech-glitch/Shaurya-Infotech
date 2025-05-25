import { Tender } from "@shared/schema";
import { useState } from "react";
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle, 
  CardDescription 
} from "@/components/ui/card";
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Brain, 
  LineChart, 
  AlertTriangle, 
  Target, 
  Shield, 
  CheckCircle, 
  Clock, 
  Zap, 
  DollarSign, 
  TrendingUp, 
  Users, 
  ChevronRight,
  ArrowUpRight
} from "lucide-react";
import { Separator } from "@/components/ui/separator";

interface AIAnalysisProps {
  tender: Tender;
}

export function AIAnalysis({ tender }: AIAnalysisProps) {
  const [activeTab, setActiveTab] = useState("overview");

  // Parse GPT analysis from JSON string if possible
  let gptAnalysisData = null;
  try {
    gptAnalysisData = JSON.parse(tender.gptAnalysis || '{}');
  } catch {
    // If parsing fails, we'll use the raw string version
  }

  // Parse NLP analysis from JSON string if possible
  let nlpAnalysisData = null;
  try {
    nlpAnalysisData = JSON.parse(tender.nlpSummary || '{}');
  } catch {
    // If parsing fails, we'll use the raw string version
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-700 dark:to-purple-700 p-6 rounded-xl text-white">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Brain className="h-6 w-6" />
              <h2 className="text-2xl font-bold">AI Analysis: {tender.title}</h2>
            </div>
            <p className="text-blue-100 dark:text-blue-200 max-w-3xl">{tender.nlpSummary || "Advanced AI analysis powered by GPT-4, NLP processing, and predictive analytics to evaluate tender opportunities and provide strategic insights."}</p>
            <div className="flex items-center mt-4 space-x-3">
              <div className="bg-white/20 px-3 py-1 rounded-full text-sm flex items-center space-x-1">
                <Brain className="h-3 w-3" />
                <span>GPT-4 Enhanced</span>
              </div>
              <div className="bg-white/20 px-3 py-1 rounded-full text-sm flex items-center space-x-1">
                <Target className="h-3 w-3" />
                <span>{tender.successProbability}% Success Rate</span>
              </div>
              <div className="bg-white/20 px-3 py-1 rounded-full text-sm flex items-center space-x-1">
                <Shield className="h-3 w-3" />
                <span>Risk Score: {tender.riskScore}/100</span>
              </div>
            </div>
          </div>
          <div className="bg-white/10 p-4 rounded-lg">
            <div className="text-3xl font-bold">{tender.aiScore}%</div>
            <div className="text-sm text-blue-100">AI Confidence Score</div>
          </div>
        </div>
      </div>

      <Tabs defaultValue={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">AI Overview</TabsTrigger>
          <TabsTrigger value="insights">Strategic Insights</TabsTrigger>
          <TabsTrigger value="risk">Risk Assessment</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-gradient-to-r from-green-50 to-green-100 dark:from-green-950/50 dark:to-green-900/30 border-none">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Success Probability</p>
                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">{tender.successProbability}%</p>
                  </div>
                  <Target className="h-8 w-8 text-green-500 dark:text-green-400 opacity-70" />
                </div>
                <Progress value={tender.successProbability} className="h-1.5 mt-2 bg-green-200 dark:bg-green-900" />
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-orange-50 to-orange-100 dark:from-orange-950/50 dark:to-orange-900/30 border-none">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Risk Score</p>
                    <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">{tender.riskScore}/100</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-orange-500 dark:text-orange-400 opacity-70" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-purple-50 to-purple-100 dark:from-purple-950/50 dark:to-purple-900/30 border-none">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Competition</p>
                    <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{tender.competition}</p>
                  </div>
                  <Users className="h-8 w-8 text-purple-500 dark:text-purple-400 opacity-70" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/30 border-none">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Profit Margin</p>
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{tender.predictedMargin}%</p>
                  </div>
                  <LineChart className="h-8 w-8 text-blue-500 dark:text-blue-400 opacity-70" />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>GPT-4 Analysis</CardTitle>
                <CardDescription>Strategic assessment powered by GPT-4</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 dark:bg-blue-950/50 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Brain className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      <h3 className="font-semibold text-blue-700 dark:text-blue-300">Strategic Recommendation</h3>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300">
                      {gptAnalysisData?.recommendation || tender.gptAnalysis || "Highly favorable opportunity that aligns with organizational capabilities and strategic goals."}
                    </p>
                  </div>

                  <div className="p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold mb-2">Key Insights</h3>
                    <ul className="space-y-2">
                      {gptAnalysisData?.insights ? (
                        gptAnalysisData.insights.map((insight: any, index: number) => (
                          <li key={index} className="flex items-start">
                            <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 mr-2 flex-shrink-0" />
                            <span>{insight.category}: {insight.details}</span>
                          </li>
                        ))
                      ) : (
                        <>
                          <li className="flex items-start">
                            <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 mr-2 flex-shrink-0" />
                            <span>Market Opportunity: Strong alignment with current market trends</span>
                          </li>
                          <li className="flex items-start">
                            <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 mr-2 flex-shrink-0" />
                            <span>Technical Feasibility: Good match with current capabilities</span>
                          </li>
                          <li className="flex items-start">
                            <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 mr-2 flex-shrink-0" />
                            <span>Financial Viability: Favorable ROI projections</span>
                          </li>
                        </>
                      )}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>NLP Intelligence</CardTitle>
                <CardDescription>Extracted insights from tender documents</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {nlpAnalysisData ? (
                    <>
                      <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <div className="flex items-center">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                          <span className="text-sm">Sentiment</span>
                        </div>
                        <Badge variant="outline" className={`${nlpAnalysisData.sentiment?.label === "Positive" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"}`}>
                          {nlpAnalysisData.sentiment?.label || "Positive"} ({nlpAnalysisData.sentiment?.score || "0.82"})
                        </Badge>
                      </div>

                      <div>
                        <h3 className="font-semibold mb-2">Key Entities</h3>
                        <div className="flex flex-wrap gap-2">
                          {nlpAnalysisData.entities ? (
                            nlpAnalysisData.entities.map((entity: any, index: number) => (
                              <Badge key={index} variant="secondary" className="bg-gray-100 dark:bg-gray-800">
                                {entity.text} <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">({entity.type})</span>
                              </Badge>
                            ))
                          ) : (
                            <>
                              <Badge variant="secondary" className="bg-gray-100 dark:bg-gray-800">
                                Ministry of Electronics & IT <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">(ORG)</span>
                              </Badge>
                              <Badge variant="secondary" className="bg-gray-100 dark:bg-gray-800">
                                ₹2,50,00,000 <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">(AMT)</span>
                              </Badge>
                            </>
                          )}
                        </div>
                      </div>

                      <div>
                        <h3 className="font-semibold mb-2">Critical Clauses</h3>
                        <ul className="space-y-1 text-sm">
                          {nlpAnalysisData.criticalClauses ? (
                            nlpAnalysisData.criticalClauses.map((clause: string, index: number) => (
                              <li key={index} className="flex items-start">
                                <AlertTriangle className="h-3 w-3 text-orange-500 dark:text-orange-400 mt-0.5 mr-2 flex-shrink-0" />
                                <span>{clause}</span>
                              </li>
                            ))
                          ) : (
                            <>
                              <li className="flex items-start">
                                <AlertTriangle className="h-3 w-3 text-orange-500 dark:text-orange-400 mt-0.5 mr-2 flex-shrink-0" />
                                <span>Penalty clause: 0.5% per week delay</span>
                              </li>
                              <li className="flex items-start">
                                <AlertTriangle className="h-3 w-3 text-orange-500 dark:text-orange-400 mt-0.5 mr-2 flex-shrink-0" />
                                <span>Performance guarantee: 10% of contract value</span>
                              </li>
                            </>
                          )}
                        </ul>
                      </div>
                    </>
                  ) : (
                    <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <p className="text-gray-700 dark:text-gray-300">
                        {tender.nlpSummary || "High-value IT infrastructure project focusing on cloud migration and digital transformation. Strong technical requirements match our capabilities."}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Market Intelligence</CardTitle>
              <CardDescription>AI-powered market analysis and competitive positioning</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/40 dark:to-green-900/20 rounded-lg">
                  <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">+23%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{tender.organization.includes("IT") ? "IT" : tender.organization.includes("Health") ? "Healthcare" : "Infrastructure"} Tender Growth</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/40 dark:to-blue-900/20 rounded-lg">
                  <Target className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{Math.floor(Math.random() * 400) + 400}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Similar Opportunities</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/40 dark:to-purple-900/20 rounded-lg">
                  <Users className="w-8 h-8 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{tender.competition === "Low" ? "5-8" : tender.competition === "Medium" ? "8-12" : "12-20"}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Expected Bidders</p>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="font-semibold mb-3">Competitive Analysis</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Your Position</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-green-500 dark:bg-green-400 h-2 rounded-full" 
                          style={{width: `${tender.successProbability}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">#{Math.floor(tender.successProbability / 10)}</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Technical Advantage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-blue-500 dark:bg-blue-400 h-2 rounded-full" 
                          style={{width: `${tender.aiScore}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{tender.aiScore}%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Pricing Competitiveness</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-purple-500 dark:bg-purple-400 h-2 rounded-full" 
                          style={{width: `${100 - (tender.predictedMargin * 2)}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{100 - (tender.predictedMargin * 2)}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-3">Market Trends</h3>
                <div className="p-4 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-lg">
                  <p className="text-gray-700 dark:text-gray-300">
                    The {tender.organization.includes("IT") ? "IT services" : tender.organization.includes("Health") ? "healthcare equipment" : "infrastructure"} sector shows a {Math.floor(Math.random() * 10) + 15}% growth trend in government tenders. Budget allocations are increasing, with emphasis on {tender.title.toLowerCase().includes("it") ? "digital transformation" : tender.title.toLowerCase().includes("medical") ? "medical technology innovation" : "sustainable development"}. Bid competitiveness is {tender.competition.toLowerCase()}, with average bid-to-win ratios at {tender.competition === "Low" ? "1:3" : tender.competition === "Medium" ? "1:5" : "1:8"}.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Financial Analysis</CardTitle>
              <CardDescription>Projected costs, revenue, and profitability assessment</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex items-center space-x-2 mb-1">
                    <DollarSign className="h-4 w-4 text-green-600 dark:text-green-400" />
                    <h4 className="font-medium">Tender Value</h4>
                  </div>
                  <p className="text-2xl font-bold">{tender.value}</p>
                </div>
                <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex items-center space-x-2 mb-1">
                    <Zap className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                    <h4 className="font-medium">Est. Costs</h4>
                  </div>
                  <p className="text-2xl font-bold">₹{parseFloat(tender.value.replace(/[^\d.]/g, '')) * (1 - (tender.predictedMargin / 100)).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')}</p>
                </div>
                <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex items-center space-x-2 mb-1">
                    <TrendingUp className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    <h4 className="font-medium">Profit Margin</h4>
                  </div>
                  <p className="text-2xl font-bold">{tender.predictedMargin}%</p>
                </div>
                <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex items-center space-x-2 mb-1">
                    <ArrowUpRight className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                    <h4 className="font-medium">ROI</h4>
                  </div>
                  <p className="text-2xl font-bold">{Math.floor(tender.predictedMargin * 1.5)}%</p>
                </div>
              </div>

              <div className="p-4 bg-gradient-to-r from-gray-50 to-green-50 dark:from-gray-800 dark:to-green-900/20 rounded-lg mb-6">
                <div className="flex items-center space-x-2 mb-2">
                  <Brain className="w-5 h-5 text-green-600 dark:text-green-400" />
                  <h3 className="font-semibold text-green-700 dark:text-green-300">AI Financial Recommendation</h3>
                </div>
                <p className="text-gray-700 dark:text-gray-300">
                  Based on financial analysis, this tender offers a {tender.predictedMargin > 20 ? "highly attractive" : tender.predictedMargin > 15 ? "good" : "moderate"} profit potential with an estimated margin of {tender.predictedMargin}%. Cost structure analysis indicates {tender.predictedMargin > 20 ? "favorable" : "reasonable"} pricing conditions. Recommended bid strategy: {tender.competition === "Low" ? "Premium pricing with emphasis on quality" : tender.competition === "Medium" ? "Balanced approach with competitive pricing" : "Aggressive pricing with operational efficiency focus"}.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-3">Resource Requirements</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-1">
                      <Users className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                      <span className="font-medium">Personnel</span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {parseFloat(tender.value.replace(/[^\d.]/g, '')) > 3000000 ? "15-20 FTE" : parseFloat(tender.value.replace(/[^\d.]/g, '')) > 1000000 ? "8-12 FTE" : "4-6 FTE"} for project duration
                    </p>
                  </div>
                  <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-1">
                      <Clock className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                      <span className="font-medium">Timeline</span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {parseFloat(tender.value.replace(/[^\d.]/g, '')) > 3000000 ? "8-10 months" : parseFloat(tender.value.replace(/[^\d.]/g, '')) > 1000000 ? "4-6 months" : "2-3 months"} estimated duration
                    </p>
                  </div>
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-1">
                      <DollarSign className="h-4 w-4 text-green-600 dark:text-green-400" />
                      <span className="font-medium">Cash Flow</span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      Positive from month {parseFloat(tender.value.replace(/[^\d.]/g, '')) > 3000000 ? "3" : "2"} with standard payment terms
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risk" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Comprehensive Risk Assessment</CardTitle>
              <CardDescription>AI-powered risk analysis and mitigation strategies</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">Overall Risk Score: {tender.riskScore}/100</h3>
                  <Badge 
                    className={
                      tender.riskScore < 30 ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" : 
                      tender.riskScore < 60 ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300" :
                      "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
                    }
                  >
                    {tender.riskScore < 30 ? "Low Risk" : tender.riskScore < 60 ? "Medium Risk" : "High Risk"}
                  </Badge>
                </div>
                
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 mb-6">
                  <div 
                    className={
                      tender.riskScore < 30 ? "bg-green-500 dark:bg-green-400" : 
                      tender.riskScore < 60 ? "bg-yellow-500 dark:bg-yellow-400" :
                      "bg-red-500 dark:bg-red-400"
                    }
                    style={{ width: `${tender.riskScore}%` }}
                    className="h-4 rounded-full"
                  ></div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold mb-3">Risk Breakdown</h3>
                  <div className="space-y-4">
                    <div className="p-3 bg-gradient-to-r from-red-50 to-red-100 dark:from-red-950/50 dark:to-red-900/30 rounded-lg border-l-4 border-red-500 dark:border-red-400">
                      <h4 className="font-medium mb-1">High Risk Factors</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-start">
                          <AlertTriangle className="h-4 w-4 text-red-600 dark:text-red-400 mt-0.5 mr-2 flex-shrink-0" />
                          <div>
                            <p className="font-medium">Timeline Constraints</p>
                            <p className="text-gray-700 dark:text-gray-300">Tight deadline with complex requirements</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="p-3 bg-gradient-to-r from-yellow-50 to-yellow-100 dark:from-yellow-950/50 dark:to-yellow-900/30 rounded-lg border-l-4 border-yellow-500 dark:border-yellow-400">
                      <h4 className="font-medium mb-1">Medium Risk Factors</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-start">
                          <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
                          <div>
                            <p className="font-medium">Competition Level</p>
                            <p className="text-gray-700 dark:text-gray-300">{tender.competition} competition with established players</p>
                          </div>
                        </div>
                        <div className="flex items-start">
                          <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
                          <div>
                            <p className="font-medium">Technical Complexity</p>
                            <p className="text-gray-700 dark:text-gray-300">Integration challenges with existing systems</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Risk Assessment Matrix</h3>
                  <div className="p-3 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-950/50 dark:to-green-900/30 rounded-lg border-l-4 border-green-500 dark:border-green-400 mb-4">
                    <h4 className="font-medium mb-1">Low Risk Factors</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-start">
                        <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                        <div>
                          <p className="font-medium">Financial Terms</p>
                          <p className="text-gray-700 dark:text-gray-300">Standard payment schedule with secure client</p>
                        </div>
                      </div>
                      <div className="flex items-start">
                        <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                        <div>
                          <p className="font-medium">Legal/Compliance</p>
                          <p className="text-gray-700 dark:text-gray-300">Clear eligibility criteria and standard terms</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-blue-50 dark:bg-blue-950/50 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      <h3 className="font-semibold text-blue-700 dark:text-blue-300">AI Risk Verdict</h3>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300">
                      This tender presents a {tender.riskScore < 30 ? "manageable" : tender.riskScore < 60 ? "moderate" : "significant"} risk profile with a score of {tender.riskScore}/100. The primary concerns are {tender.riskScore < 30 ? "minor and easily mitigated" : tender.riskScore < 60 ? "addressable with proper planning" : "substantial and require careful management"}. Overall assessment indicates that risks are {tender.riskScore < 30 ? "outweighed by potential rewards" : tender.riskScore < 60 ? "balanced against potential rewards" : "potentially challenging but manageable"}.
                    </p>
                  </div>
                </div>
              </div>

              <Separator className="my-6" />

              <div>
                <h3 className="font-semibold mb-4">Mitigation Strategies</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Clock className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                      <h4 className="font-medium">Timeline Risk</h4>
                    </div>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Early resource mobilization and planning</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Phased implementation approach</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Buffer periods for critical milestones</span>
                      </li>
                    </ul>
                  </div>

                  <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Users className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                      <h4 className="font-medium">Competition Risk</h4>
                    </div>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Emphasize unique technical capabilities</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Competitive pricing strategy</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Highlight past successful projects</span>
                      </li>
                    </ul>
                  </div>

                  <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Zap className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                      <h4 className="font-medium">Technical Risk</h4>
                    </div>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Early technical proof-of-concept</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Dedicated integration specialists</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Comprehensive testing strategy</span>
                      </li>
                    </ul>
                  </div>

                  <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <DollarSign className="h-4 w-4 text-green-600 dark:text-green-400" />
                      <h4 className="font-medium">Financial Risk</h4>
                    </div>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Clear payment milestone structure</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Contingency budget allocation (15%)</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-3 w-3 text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                        <span>Regular financial health monitoring</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Strategic Recommendations</CardTitle>
              <CardDescription>GPT-4 powered strategic insights and action plan</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-5 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/50 dark:to-purple-950/50 rounded-xl mb-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 rounded-full ai-gradient flex items-center justify-center">
                    <Brain className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">GPT-4 Executive Summary</h3>
                    <p className="text-gray-600 dark:text-gray-400">Strategic assessment and actionable insights</p>
                  </div>
                </div>
                <div className="text-gray-700 dark:text-gray-300 space-y-4">
                  <p>
                    Based on comprehensive analysis of the <strong>{tender.title}</strong> tender, this opportunity is rated as 
                    <strong className={
                      tender.aiScore > 90 ? " text-green-600 dark:text-green-400" : 
                      tender.aiScore > 80 ? " text-blue-600 dark:text-blue-400" : 
                      " text-yellow-600 dark:text-yellow-400"
                    }> {tender.aiScore > 90 ? "highly favorable" : tender.aiScore > 80 ? "favorable" : "moderately favorable"}</strong> with an AI confidence score of <strong>{tender.aiScore}%</strong>.
                  </p>
                  <p>
                    The tender aligns well with organizational capabilities and strategic objectives, offering a projected margin of <strong>{tender.predictedMargin}%</strong> with a success probability of <strong>{tender.successProbability}%</strong>.
                  </p>
                  <p>
                    Risk assessment indicates a <strong className={
                      tender.riskScore < 30 ? "text-green-600 dark:text-green-400" : 
                      tender.riskScore < 60 ? "text-yellow-600 dark:text-yellow-400" : 
                      "text-red-600 dark:text-red-400"
                    }>{tender.riskScore < 30 ? "low" : tender.riskScore < 60 ? "moderate" : "significant"} risk profile</strong> that can be effectively managed with proper planning and execution.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold mb-3">Key Strengths & Opportunities</h3>
                  <ul className="space-y-2">
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <p className="font-medium">Technical Alignment</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Strong match with existing capabilities and expertise</p>
                      </div>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <p className="font-medium">Market Positioning</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Opportunity to strengthen presence in {tender.organization.includes("IT") ? "IT services" : tender.organization.includes("Health") ? "healthcare" : "infrastructure"} sector</p>
                      </div>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <p className="font-medium">Profitability Potential</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Attractive margin with potential for follow-on work</p>
                      </div>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <p className="font-medium">Competitive Environment</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{tender.competition.toLowerCase()} competition providing favorable conditions</p>
                      </div>
                    </li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Challenges & Considerations</h3>
                  <ul className="space-y-2">
                    <li className="flex items-start">
                      <AlertTriangle className="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <p className="font-medium">Timeline Pressure</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Tight deadline requiring efficient resource allocation</p>
                      </div>
                    </li>
                    <li className="flex items-start">
                      <AlertTriangle className="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <p className="font-medium">Technical Complexity</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Integration challenges with existing systems</p>
                      </div>
                    </li>
                    <li className="flex items-start">
                      <AlertTriangle className="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <p className="font-medium">Compliance Requirements</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Stringent regulatory and security standards</p>
                      </div>
                    </li>
                    <li className="flex items-start">
                      <AlertTriangle className="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <p className="font-medium">Resource Allocation</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Need for specialized skills and expertise</p>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="font-semibold mb-3">Strategic Action Plan</h3>
                <div className="space-y-4">
                  <div className="p-3 border-l-4 border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-950/30 rounded-r-lg">
                    <h4 className="font-medium text-blue-700 dark:text-blue-300 mb-2">Bid Strategy</h4>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-start">
                        <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0 mr-1 flex-shrink-0" />
                        <span>Emphasize technical expertise and past project success in similar sectors</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0 mr-1 flex-shrink-0" />
                        <span>Highlight unique value propositions and differentiators</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0 mr-1 flex-shrink-0" />
                        <span>Competitive pricing with {tender.predictedMargin}-{tender.predictedMargin + 2}% margin target</span>
                      </li>
                    </ul>
                  </div>

                  <div className="p-3 border-l-4 border-purple-500 dark:border-purple-400 bg-purple-50 dark:bg-purple-950/30 rounded-r-lg">
                    <h4 className="font-medium text-purple-700 dark:text-purple-300 mb-2">Resource Planning</h4>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-start">
                        <ChevronRight className="h-4 w-4 text-purple-600 dark:text-purple-400 mt-0 mr-1 flex-shrink-0" />
                        <span>Form dedicated bid team with technical and domain experts</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-4 w-4 text-purple-600 dark:text-purple-400 mt-0 mr-1 flex-shrink-0" />
                        <span>Engage with potential technology partners and suppliers early</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-4 w-4 text-purple-600 dark:text-purple-400 mt-0 mr-1 flex-shrink-0" />
                        <span>Develop comprehensive resource allocation plan for implementation</span>
                      </li>
                    </ul>
                  </div>

                  <div className="p-3 border-l-4 border-green-500 dark:border-green-400 bg-green-50 dark:bg-green-950/30 rounded-r-lg">
                    <h4 className="font-medium text-green-700 dark:text-green-300 mb-2">Implementation Roadmap</h4>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-start">
                        <ChevronRight className="h-4 w-4 text-green-600 dark:text-green-400 mt-0 mr-1 flex-shrink-0" />
                        <span>Phased delivery approach with clear milestones and deliverables</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-4 w-4 text-green-600 dark:text-green-400 mt-0 mr-1 flex-shrink-0" />
                        <span>Proactive risk management with contingency planning</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="h-4 w-4 text-green-600 dark:text-green-400 mt-0 mr-1 flex-shrink-0" />
                        <span>Regular communication cadence with stakeholders</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-lg">
                <h3 className="font-semibold mb-2">Final Recommendation</h3>
                <p className="text-gray-700 dark:text-gray-300">
                  <strong className="text-blue-700 dark:text-blue-300">
                    {tender.aiScore > 90 ? "Strongly Pursue" : tender.aiScore > 80 ? "Pursue" : "Consider with Caution"}
                  </strong> - 
                  This tender represents a {tender.aiScore > 90 ? "highly attractive" : tender.aiScore > 80 ? "promising" : "potential"} opportunity aligned with organizational capabilities. 
                  With a success probability of {tender.successProbability}% and margin potential of {tender.predictedMargin}%, 
                  the {tender.riskScore < 30 ? "low" : tender.riskScore < 60 ? "moderate" : "elevated"} risk profile 
                  is {tender.riskScore < 30 ? "easily manageable" : tender.riskScore < 60 ? "manageable with proper planning" : "challenging but potentially worthwhile"}. 
                  Immediate action is recommended to prepare a competitive and compelling bid.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
