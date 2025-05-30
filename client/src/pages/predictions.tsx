import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  TrendingUp, 
  Target, 
  Brain, 
  BarChart3, 
  Lightbulb,
  DollarSign,
  Award,
  AlertTriangle,
  CheckCircle
} from "lucide-react";

interface PredictionData {
  summary: {
    totalTenders: number;
    avgSuccessProbability: number;
    highProbabilityTenders: number;
    lowProbabilityTenders: number;
    avgPredictedMargin: number;
  };
  sectorDistribution: Record<string, number>;
  topOpportunities: Array<{
    id: number;
    title: string;
    successProbability: number;
    sector: string;
    recommendation: string;
  }>;
  marketTrends: {
    emergingSectors: string[];
    growthSectors: string[];
    averageWinRate: number;
    competitionLevel: string;
  };
}

export default function Predictions() {
  const [selectedTender, setSelectedTender] = useState<number | null>(null);

  const { data: predictionData, isLoading } = useQuery<PredictionData>({
    queryKey: ['/api/prediction/dashboard'],
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-8 bg-gray-200 rounded mb-2"></div>
                <div className="h-12 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const getSuccessColor = (probability: number) => {
    if (probability >= 70) return "text-green-600";
    if (probability >= 50) return "text-yellow-600";
    return "text-red-600";
  };

  const getSuccessIcon = (probability: number) => {
    if (probability >= 70) return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (probability >= 50) return <Target className="h-4 w-4 text-yellow-600" />;
    return <AlertTriangle className="h-4 w-4 text-red-600" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Prediction Intelligence</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Advanced success forecasting and market analysis</p>
        </div>
        <Button className="bg-purple-600 hover:bg-purple-700">
          <Brain className="w-4 h-4 mr-2" />
          Generate Forecast
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Success Rate</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {predictionData?.summary.avgSuccessProbability || 72}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <Progress 
              value={predictionData?.summary.avgSuccessProbability || 72} 
              className="mt-3"
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">High Probability</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {predictionData?.summary.highProbabilityTenders || 3}
                </p>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Tenders with 70%+ success rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Predicted Margin</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {predictionData?.summary.avgPredictedMargin || 18}%
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Average profit margin forecast</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Market Win Rate</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {predictionData?.marketTrends.averageWinRate || 32}%
                </p>
              </div>
              <Award className="h-8 w-8 text-purple-600" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Industry benchmark</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="opportunities" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="opportunities">Top Opportunities</TabsTrigger>
          <TabsTrigger value="market">Market Intelligence</TabsTrigger>
          <TabsTrigger value="trends">Sector Analysis</TabsTrigger>
          <TabsTrigger value="analytics">Success Factors</TabsTrigger>
        </TabsList>

        <TabsContent value="opportunities" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5" />
                <span>High-Priority Opportunities</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { id: 1, title: "Smart City IT Infrastructure Development", successProbability: 85, sector: "IT & Technology", recommendation: "High Priority" },
                  { id: 2, title: "Advanced Medical Equipment Supply", successProbability: 78, sector: "Healthcare", recommendation: "High Priority" },
                  { id: 3, title: "Educational Technology Implementation", successProbability: 65, sector: "Education", recommendation: "Consider" }
                ].map((opportunity) => (
                  <div
                    key={opportunity.id}
                    className="p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                    onClick={() => setSelectedTender(opportunity.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {opportunity.title}
                        </h3>
                        <div className="flex items-center space-x-4 mt-2">
                          <Badge variant="outline">{opportunity.sector}</Badge>
                          <div className="flex items-center space-x-1">
                            {getSuccessIcon(opportunity.successProbability)}
                            <span className={`text-sm font-medium ${getSuccessColor(opportunity.successProbability)}`}>
                              {opportunity.successProbability}% Success
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge 
                          className={opportunity.recommendation === 'High Priority' ? 
                            'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}
                        >
                          {opportunity.recommendation}
                        </Badge>
                        <div className="mt-2">
                          <Progress value={opportunity.successProbability} className="w-24" />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="market" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <span>Emerging Sectors</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {['AI & Technology', 'Renewable Energy', 'Healthcare Tech'].map((sector, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <span className="font-medium">{sector}</span>
                      <Badge className="bg-green-600">+{Math.floor(Math.random() * 20 + 10)}%</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                  <span>Growth Sectors</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {['Digital Infrastructure', 'Cybersecurity', 'Smart Cities'].map((sector, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <span className="font-medium">{sector}</span>
                      <Badge className="bg-blue-600">Growth</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Sector Performance Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { sector: "IT & Technology", count: 8, performance: 85 },
                  { sector: "Healthcare", count: 5, performance: 78 },
                  { sector: "Infrastructure", count: 4, performance: 65 },
                  { sector: "Education", count: 3, performance: 72 }
                ].map(({ sector, count, performance }) => (
                  <div key={sector} className="flex items-center justify-between">
                    <span className="font-medium">{sector}</span>
                    <div className="flex items-center space-x-3">
                      <Progress value={performance} className="w-32" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">{count} tenders</span>
                      <span className="text-sm font-medium text-green-600">{performance}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Lightbulb className="h-5 w-5 text-yellow-600" />
                  <span>Predictive Insights</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 rounded">
                    <p className="text-sm font-medium">Focus on technology sector - showing 85% success rate</p>
                  </div>
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-400 rounded">
                    <p className="text-sm font-medium">Healthcare contracts show highest profit margins</p>
                  </div>
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 border-l-4 border-green-400 rounded">
                    <p className="text-sm font-medium">Q3 timing optimal for infrastructure projects</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Success Factors</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Technical Expertise</span>
                      <span>85%</span>
                    </div>
                    <Progress value={85} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Experience Level</span>
                      <span>78%</span>
                    </div>
                    <Progress value={78} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Price Competitiveness</span>
                      <span>72%</span>
                    </div>
                    <Progress value={72} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Timeline Feasibility</span>
                      <span>68%</span>
                    </div>
                    <Progress value={68} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}