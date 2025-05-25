import { 
  Building, 
  Star, 
  CheckCircle, 
  AlertTriangle, 
  Award, 
  Users, 
  Clock, 
  BarChart3, 
  Briefcase, 
  FileText, 
  Brain, 
  Target, 
  TrendingUp, 
  BadgeCheck,
  Shield,
  DollarSign
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from "@/components/ui/tabs";
import { Firm } from "@shared/schema";

interface FirmDetailsProps {
  firm: Firm;
}

export function FirmDetails({ firm }: FirmDetailsProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-2">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <Building className="w-5 h-5 text-white" />
                </div>
                <CardTitle>{firm.name}</CardTitle>
              </div>
              <CardDescription className="mt-1">{firm.specialization}</CardDescription>
            </div>
            <div className="flex items-center space-x-1">
              <Star className="w-5 h-5 text-yellow-400" />
              <span className="font-bold text-xl">{firm.rating}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="overview" className="mt-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="capabilities">Capabilities</TabsTrigger>
              <TabsTrigger value="ai-insights">AI Insights</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="bg-green-50 dark:bg-green-900/20 border-none">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Projects Completed</p>
                        <p className="text-2xl font-bold text-green-600 dark:text-green-400">{firm.completedProjects}</p>
                      </div>
                      <Award className="h-8 w-8 text-green-500 dark:text-green-400 opacity-70" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-blue-50 dark:bg-blue-900/20 border-none">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Active Projects</p>
                        <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{firm.activeProjects}</p>
                      </div>
                      <Briefcase className="h-8 w-8 text-blue-500 dark:text-blue-400 opacity-70" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-purple-50 dark:bg-purple-900/20 border-none">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">AI Score</p>
                        <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{firm.eligibilityScore}%</p>
                      </div>
                      <Brain className="h-8 w-8 text-purple-500 dark:text-purple-400 opacity-70" />
                    </div>
                    <Progress value={firm.eligibilityScore} className="h-1.5 mt-2" />
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">Company Profile</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Specialization:</span>
                        <span className="font-medium">{firm.specialization}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Market Position:</span>
                        <span className="font-medium text-blue-600 dark:text-blue-400">{firm.marketPosition}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Financial Health:</span>
                        <span className={`font-medium ${
                          firm.financialHealth === 'Excellent' ? 'text-green-600 dark:text-green-400' :
                          firm.financialHealth === 'Strong' ? 'text-blue-600 dark:text-blue-400' :
                          firm.financialHealth === 'Good' ? 'text-yellow-600 dark:text-yellow-400' :
                          'text-red-600 dark:text-red-400'
                        }`}>
                          {firm.financialHealth}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Risk Profile:</span>
                        <Badge className={
                          firm.riskProfile === 'Low' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                          firm.riskProfile === 'Medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' :
                          'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                        }>
                          {firm.riskProfile}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">Certifications & Compliance</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {firm.certifications?.map((cert, index) => (
                        <div key={index} className="flex items-center bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 px-3 py-1.5 rounded-full text-sm">
                          <BadgeCheck className="w-4 h-4 mr-1.5" />
                          {cert}
                        </div>
                      ))}
                    </div>
                    
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="flex items-center space-x-2 mb-1">
                        <Shield className="w-4 h-4 text-green-600 dark:text-green-400" />
                        <span className="font-medium text-green-700 dark:text-green-300">Compliance Status</span>
                      </div>
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        All required certifications are valid and up-to-date. Last verification completed on {new Date().toLocaleDateString()}.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/40 dark:to-green-900/20 rounded-lg">
                      <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400 mb-2" />
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">98%</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">On-time Delivery</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/40 dark:to-blue-900/20 rounded-lg">
                      <Target className="w-6 h-6 text-blue-600 dark:text-blue-400 mb-2" />
                      <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">95%</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Quality Score</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/40 dark:to-purple-900/20 rounded-lg">
                      <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400 mb-2" />
                      <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">91%</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Client Satisfaction</p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Budget Adherence</span>
                        <span className="text-sm font-medium">92%</span>
                      </div>
                      <Progress value={92} className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Technical Compliance</span>
                        <span className="text-sm font-medium">96%</span>
                      </div>
                      <Progress value={96} className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Documentation Quality</span>
                        <span className="text-sm font-medium">89%</span>
                      </div>
                      <Progress value={89} className="h-1.5" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="capabilities" className="space-y-6 mt-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Technical Capabilities</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">{firm.specialization}</span>
                        <span className="text-sm font-medium">98%</span>
                      </div>
                      <Progress value={98} className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Project Management</span>
                        <span className="text-sm font-medium">94%</span>
                      </div>
                      <Progress value={94} className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Quality Assurance</span>
                        <span className="text-sm font-medium">92%</span>
                      </div>
                      <Progress value={92} className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Innovation</span>
                        <span className="text-sm font-medium">88%</span>
                      </div>
                      <Progress value={88} className="h-1.5" />
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">Resource Capacity</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Technical Staff</span>
                        <Badge variant="outline">120+ Specialists</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Project Managers</span>
                        <Badge variant="outline">25+ Certified</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Quality Engineers</span>
                        <Badge variant="outline">30+ Experts</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Support Staff</span>
                        <Badge variant="outline">45+ Personnel</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">Past Performance</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium">Government Projects</span>
                          <Badge variant="outline">{Math.round(firm.completedProjects * 0.6)}+</Badge>
                        </div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Successfully delivered to various government departments</p>
                      </div>
                      <div className="p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium">Private Sector</span>
                          <Badge variant="outline">{Math.round(firm.completedProjects * 0.4)}+</Badge>
                        </div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Delivered to enterprise clients across industries</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Project Portfolio</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-lg border-l-4 border-blue-500 dark:border-blue-400">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium">{firm.specialization.includes('IT') ? 'Enterprise Cloud Migration' : firm.specialization.includes('Construction') ? 'Smart City Infrastructure' : 'Medical Equipment Supply'}</h4>
                        <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Completed</Badge>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {firm.specialization.includes('IT') ? 'Complete digital transformation with cloud migration for a government department' : 
                          firm.specialization.includes('Construction') ? 'Smart city infrastructure development project with IoT integration' : 
                          'Comprehensive medical equipment supply and installation for a government hospital'}
                      </p>
                      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                        <span>Value: ₹{firm.specialization.includes('IT') ? '3.2 Crores' : firm.specialization.includes('Construction') ? '12.5 Crores' : '2.7 Crores'}</span>
                        <span>Duration: {firm.specialization.includes('IT') ? '12 months' : firm.specialization.includes('Construction') ? '24 months' : '8 months'}</span>
                        <span>Client: {firm.specialization.includes('IT') ? 'Ministry of Electronics & IT' : firm.specialization.includes('Construction') ? 'State PWD' : 'Health Department'}</span>
                      </div>
                    </div>
                    
                    <div className="p-4 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-lg border-l-4 border-blue-500 dark:border-blue-400">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium">{firm.specialization.includes('IT') ? 'Government ERP Implementation' : firm.specialization.includes('Construction') ? 'Green Building Development' : 'Diagnostic Center Setup'}</h4>
                        <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Completed</Badge>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {firm.specialization.includes('IT') ? 'End-to-end ERP implementation for a large government department' : 
                          firm.specialization.includes('Construction') ? 'LEED-certified government building construction project' : 
                          'Comprehensive diagnostic center setup with advanced equipment'}
                      </p>
                      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                        <span>Value: ₹{firm.specialization.includes('IT') ? '4.5 Crores' : firm.specialization.includes('Construction') ? '18.3 Crores' : '3.8 Crores'}</span>
                        <span>Duration: {firm.specialization.includes('IT') ? '18 months' : firm.specialization.includes('Construction') ? '30 months' : '12 months'}</span>
                        <span>Client: {firm.specialization.includes('IT') ? 'Finance Department' : firm.specialization.includes('Construction') ? 'Municipal Corporation' : 'AIIMS'}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="ai-insights" className="space-y-6 mt-6">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-700 dark:to-purple-700 p-6 rounded-xl text-white">
                <div className="flex items-center space-x-3 mb-3">
                  <Brain className="h-7 w-7" />
                  <h2 className="text-xl font-bold">AI-Generated Intelligence Report</h2>
                </div>
                <p className="text-blue-100 dark:text-blue-200 mb-4">
                  Enhanced analysis of {firm.name} capabilities, performance metrics, and suitability for various tender types.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-white/10 p-3 rounded-lg">
                    <div className="flex items-center space-x-2 mb-1">
                      <Target className="h-4 w-4" />
                      <span className="font-medium">Eligibility Score</span>
                    </div>
                    <p className="text-3xl font-bold">{firm.eligibilityScore}%</p>
                    <p className="text-sm text-blue-100">Based on capability analysis</p>
                  </div>
                  <div className="bg-white/10 p-3 rounded-lg">
                    <div className="flex items-center space-x-2 mb-1">
                      <Shield className="h-4 w-4" />
                      <span className="font-medium">Risk Profile</span>
                    </div>
                    <p className="text-3xl font-bold">{firm.riskProfile}</p>
                    <p className="text-sm text-blue-100">Based on performance history</p>
                  </div>
                  <div className="bg-white/10 p-3 rounded-lg">
                    <div className="flex items-center space-x-2 mb-1">
                      <Award className="h-4 w-4" />
                      <span className="font-medium">Success Rate</span>
                    </div>
                    <p className="text-3xl font-bold">{Math.round(firm.rating * 20)}%</p>
                    <p className="text-sm text-blue-100">For similar tender types</p>
                  </div>
                </div>
              </div>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">AI Recommendation</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/50 dark:to-blue-950/50 rounded-lg mb-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <Brain className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                      <h3 className="font-semibold text-purple-700 dark:text-purple-300">Strategic Assessment</h3>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300">
                      {firm.aiRecommendation}
                    </p>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="p-3 border-l-4 border-green-500 dark:border-green-400 bg-green-50 dark:bg-green-950/30 rounded-r-lg">
                      <h4 className="font-medium text-green-700 dark:text-green-300 mb-2">Key Strengths</h4>
                      <ul className="space-y-1 text-sm">
                        <li className="flex items-start">
                          <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                          <span>{firm.specialization.includes('IT') ? 'Strong technical expertise and certifications' : 
                            firm.specialization.includes('Construction') ? 'Extensive infrastructure development experience' : 
                            'Specialized healthcare equipment knowledge'}</span>
                        </li>
                        <li className="flex items-start">
                          <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                          <span>Proven track record with {firm.completedProjects} completed projects</span>
                        </li>
                        <li className="flex items-start">
                          <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                          <span>Strong financial position with {firm.financialHealth.toLowerCase()} financial health</span>
                        </li>
                      </ul>
                    </div>
                    
                    <div className="p-3 border-l-4 border-yellow-500 dark:border-yellow-400 bg-yellow-50 dark:bg-yellow-950/30 rounded-r-lg">
                      <h4 className="font-medium text-yellow-700 dark:text-yellow-300 mb-2">Areas to Consider</h4>
                      <ul className="space-y-1 text-sm">
                        <li className="flex items-start">
                          <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
                          <span>Currently managing {firm.activeProjects} active projects - resource availability may be limited</span>
                        </li>
                        <li className="flex items-start">
                          <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
                          <span>{firm.riskProfile === 'Low' ? 'No significant risk factors identified' : 
                            firm.riskProfile === 'Medium' ? 'Some financial exposure on large projects' : 
                            'High-risk profile requires careful contract management'}</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Tender Compatibility Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">{firm.specialization} Tenders</span>
                        <span className="text-sm font-medium">98%</span>
                      </div>
                      <Progress value={98} className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">High-Value Tenders (₹5Cr+)</span>
                        <span className="text-sm font-medium">
                          {firm.financialHealth === 'Excellent' ? '95%' : 
                            firm.financialHealth === 'Strong' ? '88%' : 
                            firm.financialHealth === 'Good' ? '75%' : '50%'}
                        </span>
                      </div>
                      <Progress value={
                        firm.financialHealth === 'Excellent' ? 95 : 
                        firm.financialHealth === 'Strong' ? 88 : 
                        firm.financialHealth === 'Good' ? 75 : 50
                      } className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">International Projects</span>
                        <span className="text-sm font-medium">
                          {firm.rating >= 4.8 ? '92%' : 
                            firm.rating >= 4.5 ? '85%' : 
                            firm.rating >= 4.0 ? '75%' : '60%'}
                        </span>
                      </div>
                      <Progress value={
                        firm.rating >= 4.8 ? 92 : 
                        firm.rating >= 4.5 ? 85 : 
                        firm.rating >= 4.0 ? 75 : 60
                      } className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Long-term Projects (2yr+)</span>
                        <span className="text-sm font-medium">
                          {firm.riskProfile === 'Low' ? '90%' : 
                            firm.riskProfile === 'Medium' ? '75%' : '60%'}
                        </span>
                      </div>
                      <Progress value={
                        firm.riskProfile === 'Low' ? 90 : 
                        firm.riskProfile === 'Medium' ? 75 : 60
                      } className="h-1.5" />
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <div className="flex justify-end space-x-4 mt-4">
                <Button variant="outline" className="space-x-2">
                  <FileText className="h-4 w-4" />
                  <span>Export Report</span>
                </Button>
                <Button className="ai-gradient text-white space-x-2">
                  <Brain className="h-4 w-4" />
                  <span>Run Detailed Analysis</span>
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
