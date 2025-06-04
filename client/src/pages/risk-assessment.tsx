import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { 
  Shield, 
  AlertTriangle, 
  TrendingUp, 
  Target, 
  Clock, 
  FileCheck,
  DollarSign,
  Users,
  BarChart3,
  AlertCircle,
  CheckCircle,
  XCircle,
  Activity
} from 'lucide-react';

interface RiskFactor {
  category: string;
  factor: string;
  score: number;
  weight: number;
  description: string;
  impact: 'Low' | 'Medium' | 'High' | 'Critical';
  mitigation?: string;
}

interface RiskAssessment {
  tenderId: number;
  firmId?: number;
  overallRiskScore: number;
  riskLevel: 'Low' | 'Medium' | 'High' | 'Critical';
  riskFactors: RiskFactor[];
  recommendations: string[];
  mitigationStrategies: string[];
  assessmentDate: string;
  confidence: number;
}

export default function RiskAssessmentPage() {
  const [selectedTender, setSelectedTender] = useState<number | null>(null);
  const [selectedFirm, setSelectedFirm] = useState<number | null>(null);
  const [assessment, setAssessment] = useState<RiskAssessment | null>(null);
  const [isAssessing, setIsAssessing] = useState(false);

  // Fetch available tenders and firms
  const { data: tenders = [] } = useQuery({
    queryKey: ['/api/tenders'],
  });

  const { data: firms = [] } = useQuery({
    queryKey: ['/api/firms'],
  });

  const { data: dashboardData } = useQuery({
    queryKey: ['/api/risk-assessment/dashboard'],
  });

  const performRiskAssessment = async () => {
    if (!selectedTender) return;
    
    setIsAssessing(true);
    try {
      const response = await fetch('/api/risk-assessment/tender', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenderId: selectedTender,
          firmId: selectedFirm
        })
      });
      
      const result = await response.json();
      if (result.success) {
        setAssessment(result.assessment);
      }
    } catch (error) {
      console.error('Risk assessment failed:', error);
    } finally {
      setIsAssessing(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'Low': return 'text-green-600 bg-green-50 border-green-200';
      case 'Medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'High': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'Critical': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getImpactIcon = (impact: string) => {
    switch (impact) {
      case 'Low': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'Medium': return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'High': return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'Critical': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Financial': return <DollarSign className="h-5 w-5" />;
      case 'Technical': return <Activity className="h-5 w-5" />;
      case 'Compliance': return <FileCheck className="h-5 w-5" />;
      case 'Timeline': return <Clock className="h-5 w-5" />;
      case 'Competition': return <Users className="h-5 w-5" />;
      case 'Legal': return <Shield className="h-5 w-5" />;
      case 'Operational': return <BarChart3 className="h-5 w-5" />;
      default: return <Target className="h-5 w-5" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Risk Assessment</h1>
          <p className="text-muted-foreground">
            Comprehensive risk analysis for tender participation decisions
          </p>
        </div>
        <Badge variant="outline" className="px-3 py-1">
          <Shield className="h-4 w-4 mr-2" />
          AI-Powered Analysis
        </Badge>
      </div>

      {/* Dashboard Summary */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Tenders</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.summary?.totalTenders || 0}</div>
              <p className="text-xs text-muted-foreground">Active tender opportunities</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Average Risk</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.summary?.avgTenderRisk || 0}%</div>
              <p className="text-xs text-muted-foreground">Across all tenders</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">High Risk</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{dashboardData.summary?.highRiskTenders || 0}</div>
              <p className="text-xs text-muted-foreground">Require attention</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Critical Risk</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{dashboardData.summary?.criticalRiskTenders || 0}</div>
              <p className="text-xs text-muted-foreground">Immediate action needed</p>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="assessment" className="space-y-6">
        <TabsList>
          <TabsTrigger value="assessment">Risk Assessment</TabsTrigger>
          <TabsTrigger value="analysis">Analysis Results</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="assessment" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configure Assessment</CardTitle>
              <CardDescription>
                Select tender and firm to generate comprehensive risk analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Select Tender</label>
                  <Select onValueChange={(value) => setSelectedTender(Number(value))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a tender" />
                    </SelectTrigger>
                    <SelectContent>
                      {tenders.map((tender: any) => (
                        <SelectItem key={tender.id} value={tender.id.toString()}>
                          {tender.title} - {tender.value}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Select Firm (Optional)</label>
                  <Select onValueChange={(value) => setSelectedFirm(Number(value))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a firm" />
                    </SelectTrigger>
                    <SelectContent>
                      {firms.map((firm: any) => (
                        <SelectItem key={firm.id} value={firm.id.toString()}>
                          {firm.name} - {firm.specialization}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button 
                onClick={performRiskAssessment}
                disabled={!selectedTender || isAssessing}
                className="w-full"
              >
                {isAssessing ? 'Analyzing...' : 'Generate Risk Assessment'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-6">
          {assessment ? (
            <>
              {/* Overall Risk Score */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Overall Risk Assessment
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-3xl font-bold">{assessment.overallRiskScore}%</div>
                      <Badge className={getRiskLevelColor(assessment.riskLevel)}>
                        {assessment.riskLevel} Risk
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">Confidence Score</div>
                      <div className="text-2xl font-semibold">{assessment.confidence}%</div>
                    </div>
                  </div>
                  <Progress value={assessment.overallRiskScore} className="h-3" />
                  <div className="text-sm text-muted-foreground">
                    Assessment Date: {new Date(assessment.assessmentDate).toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>

              {/* Risk Factors by Category */}
              <Card>
                <CardHeader>
                  <CardTitle>Risk Factors Analysis</CardTitle>
                  <CardDescription>
                    Detailed breakdown of risk factors by category
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {assessment.riskFactors.reduce((acc, factor) => {
                      if (!acc[factor.category]) {
                        acc[factor.category] = [];
                      }
                      acc[factor.category].push(factor);
                      return acc;
                    }, {} as Record<string, RiskFactor[]>)}
                    
                    {Object.entries(
                      assessment.riskFactors.reduce((acc, factor) => {
                        if (!acc[factor.category]) {
                          acc[factor.category] = [];
                        }
                        acc[factor.category].push(factor);
                        return acc;
                      }, {} as Record<string, RiskFactor[]>)
                    ).map(([category, factors]) => (
                      <div key={category} className="space-y-3">
                        <div className="flex items-center gap-2 pb-2 border-b">
                          {getCategoryIcon(category)}
                          <h3 className="font-semibold">{category} Risk</h3>
                        </div>
                        
                        <div className="space-y-3">
                          {factors.map((factor, index) => (
                            <div key={index} className="p-4 rounded-lg border bg-card">
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center gap-2">
                                  {getImpactIcon(factor.impact)}
                                  <h4 className="font-medium">{factor.factor}</h4>
                                </div>
                                <div className="text-right">
                                  <div className="text-lg font-semibold">{factor.score}%</div>
                                  <div className="text-xs text-muted-foreground">
                                    Weight: {(factor.weight * 100).toFixed(0)}%
                                  </div>
                                </div>
                              </div>
                              
                              <p className="text-sm text-muted-foreground mb-2">
                                {factor.description}
                              </p>
                              
                              {factor.mitigation && (
                                <Alert className="mt-2">
                                  <AlertCircle className="h-4 w-4" />
                                  <AlertDescription className="text-xs">
                                    <strong>Mitigation:</strong> {factor.mitigation}
                                  </AlertDescription>
                                </Alert>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No Assessment Available</h3>
                <p className="text-muted-foreground">
                  Please generate a risk assessment first using the Assessment tab.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          {assessment ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Strategic Recommendations
                  </CardTitle>
                  <CardDescription>
                    AI-generated recommendations based on risk analysis
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {assessment.recommendations.map((recommendation, index) => (
                      <Alert key={index}>
                        <CheckCircle className="h-4 w-4" />
                        <AlertDescription>{recommendation}</AlertDescription>
                      </Alert>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Mitigation Strategies
                  </CardTitle>
                  <CardDescription>
                    Actionable steps to reduce identified risks
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {assessment.mitigationStrategies.map((strategy, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-medium">
                          {index + 1}
                        </div>
                        <p className="text-sm">{strategy}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <TrendingUp className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No Recommendations Available</h3>
                <p className="text-muted-foreground">
                  Complete a risk assessment to receive strategic recommendations and mitigation strategies.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}