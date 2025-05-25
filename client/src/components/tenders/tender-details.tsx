import {
  CalendarIcon,
  Building,
  Briefcase,
  DollarSign,
  AlertTriangle,
  Check,
  LineChart,
  Users,
  Target,
  Shield,
  Brain,
  Newspaper,
  Download,
  Clock,
  BarChart3
} from "lucide-react";
import { Tender } from "@shared/schema";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

interface TenderDetailsProps {
  tender: Tender;
}

export function TenderDetails({ tender }: TenderDetailsProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return "text-green-600 dark:text-green-400";
    if (score < 60) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "Active":
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">{status}</Badge>;
      case "Under Review":
        return <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">{status}</Badge>;
      case "Draft Preparation":
        return <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">{status}</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{tender.title}</h2>
                {tender.blockchainVerified && (
                  <Shield className="h-5 w-5 text-green-600 dark:text-green-400" />
                )}
              </div>
              <p className="text-gray-600 dark:text-gray-400 mt-1">{tender.organization}</p>
            </div>
            <div className="flex flex-col items-end">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">{tender.value}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Reference: {tender.gemId}</div>
              {getStatusBadge(tender.status)}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-gray-700 dark:text-gray-300 mb-6">
            {tender.description}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            <div className="flex space-x-3">
              <CalendarIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
              <div>
                <div className="font-medium">Deadline</div>
                <div className="text-gray-600 dark:text-gray-400">{formatDate(tender.deadline)}</div>
              </div>
            </div>
            <div className="flex space-x-3">
              <Building className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
              <div>
                <div className="font-medium">Organization</div>
                <div className="text-gray-600 dark:text-gray-400">{tender.organization}</div>
              </div>
            </div>
            <div className="flex space-x-3">
              <Briefcase className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
              <div>
                <div className="font-medium">Eligibility</div>
                <div className="text-gray-600 dark:text-gray-400">{tender.eligibility}</div>
              </div>
            </div>
          </div>

          <Separator className="my-6" />

          <h3 className="text-lg font-semibold mb-4">AI Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <Card className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/30 border-none">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">AI Score</p>
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{tender.aiScore}%</p>
                  </div>
                  <Brain className="h-8 w-8 text-blue-500 dark:text-blue-400 opacity-70" />
                </div>
                <Progress value={tender.aiScore} className="h-1.5 mt-2" />
              </CardContent>
            </Card>

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
                    <p className={`text-2xl font-bold ${getRiskColor(tender.riskScore)}`}>{tender.riskScore}/100</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-orange-500 dark:text-orange-400 opacity-70" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-purple-50 to-purple-100 dark:from-purple-950/50 dark:to-purple-900/30 border-none">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Predicted Margin</p>
                    <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{tender.predictedMargin}%</p>
                  </div>
                  <LineChart className="h-8 w-8 text-purple-500 dark:text-purple-400 opacity-70" />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">NLP Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 dark:text-gray-300">{tender.nlpSummary}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">GPT-4 Recommendation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 dark:text-gray-300">{tender.gptAnalysis}</p>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-end space-x-4 mt-6">
            <Button variant="outline" className="space-x-2">
              <Download className="h-4 w-4" />
              <span>Download</span>
            </Button>
            <Button className="space-x-2">
              <Check className="h-4 w-4" />
              <span>Submit Bid</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
