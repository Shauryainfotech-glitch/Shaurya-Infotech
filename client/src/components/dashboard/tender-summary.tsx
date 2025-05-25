import { Shield, Eye, Download, Brain, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tender } from "@shared/schema";

interface TenderSummaryProps {
  tenders: Tender[];
}

export function TenderSummary({ tenders }: TenderSummaryProps) {
  return (
    <Card className="lg:col-span-2">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle>Live Tender Intelligence</CardTitle>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 dark:bg-green-400 rounded-full animate-ai-pulse"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">Real-time AI Analysis</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {tenders.slice(0, 3).map(tender => (
            <div 
              key={tender.id} 
              className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-lg border-l-4 border-blue-500 dark:border-blue-400"
            >
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <p className="font-medium text-gray-900 dark:text-white">{tender.title}</p>
                  {tender.blockchainVerified && (
                    <Shield className="w-4 h-4 text-green-600 dark:text-green-400" />
                  )}
                  <Badge variant="outline" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 border-none">
                    GPT-4 Analyzed
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{tender.nlpSummary}</p>
                <div className="flex space-x-4 text-xs text-gray-500 dark:text-gray-400">
                  <span>Success: {tender.successProbability}%</span>
                  <span>Risk: {tender.riskScore}/100</span>
                  <span>Margin: {tender.predictedMargin}%</span>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-green-600 dark:text-green-400">{tender.value}</p>
                <div className="flex items-center mt-1">
                  <Brain className="w-3 h-3 text-blue-500 dark:text-blue-400 mr-1" />
                  <span className="text-xs text-blue-600 dark:text-blue-400">AI Score: {tender.aiScore}%</span>
                </div>
                <div className="flex space-x-2 mt-2">
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <AlertTriangle className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
