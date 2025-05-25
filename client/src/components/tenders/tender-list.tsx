import { 
  Brain, Shield, Eye, Download, AlertTriangle, 
  Check, Clock, File, FileCheck 
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tender } from "@shared/schema";

interface TenderListProps {
  tenders: Tender[];
  onSelectTender: (id: number) => void;
}

export function TenderList({ tenders, onSelectTender }: TenderListProps) {
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

  const getRiskClass = (score: number) => {
    if (score < 30) return "text-green-600 dark:text-green-400";
    if (score < 60) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Tender Details</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">AI Insights</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Risk & Success</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Value & Margin</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {tenders.map(tender => (
              <tr key={tender.id} className="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer" onClick={() => onSelectTender(tender.id)}>
                <td className="px-6 py-4">
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <p className="font-medium text-gray-900 dark:text-white">{tender.title}</p>
                      {tender.blockchainVerified && (
                        <Shield className="w-4 h-4 text-green-600 dark:text-green-400" title="Blockchain Verified" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{tender.organization}</p>
                    <p className="text-xs text-blue-600 dark:text-blue-400">{tender.gemId}</p>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <Brain className="w-3 h-3 text-purple-600 dark:text-purple-400" />
                      <Badge variant="outline" className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300 border-none text-xs">
                        GPT-4
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Progress value={tender.aiScore} className="h-1.5 w-full" />
                      <span className="text-xs font-medium">{tender.aiScore}%</span>
                    </div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">{tender.competition} Competition</p>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600 dark:text-gray-400">Success:</span>
                      <span className="text-xs font-medium text-green-600 dark:text-green-400">{tender.successProbability}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600 dark:text-gray-400">Risk:</span>
                      <span className={`text-xs font-medium ${getRiskClass(tender.riskScore)}`}>
                        {tender.riskScore}/100
                      </span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div>
                    <p className="font-bold text-green-600 dark:text-green-400">{tender.value}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Margin: {tender.predictedMargin}%</p>
                  </div>
                </td>
                <td className="px-6 py-4">
                  {getStatusBadge(tender.status)}
                </td>
                <td className="px-6 py-4">
                  <div className="flex space-x-2">
                    <Button variant="ghost" size="icon" className="h-8 w-8" title="View Details">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8" title="Download">
                      <Download className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8" title="GPT-4 Analysis">
                      <Brain className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8" title="Risk Assessment">
                      <AlertTriangle className="w-4 h-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
