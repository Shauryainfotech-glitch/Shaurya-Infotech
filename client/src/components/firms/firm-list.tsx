import { Firm } from "@shared/schema";
import { 
  Building, 
  Star, 
  CheckCircle, 
  Brain,
  BadgeCheck
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface FirmListProps {
  firms: Firm[];
  onSelectFirm: (id: number) => void;
}

export function FirmList({ firms, onSelectFirm }: FirmListProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {firms.map(firm => (
        <Card key={firm.id} className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow cursor-pointer" onClick={() => onSelectFirm(firm.id)}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Building className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{firm.name}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{firm.specialization}</p>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-medium text-gray-900 dark:text-white">{firm.rating}</span>
            </div>
          </div>

          <div className="space-y-3 mb-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">AI Eligibility Score:</span>
              <div className="flex items-center space-x-2">
                <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${firm.eligibilityScore >= 90 ? 'bg-green-500 dark:bg-green-400' : firm.eligibilityScore >= 70 ? 'bg-yellow-500 dark:bg-yellow-400' : 'bg-red-500 dark:bg-red-400'}`}
                    style={{width: `${firm.eligibilityScore}%`}}
                  ></div>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-white">{firm.eligibilityScore}%</span>
              </div>
            </div>
            
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Risk Profile:</span>
              <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                firm.riskProfile === 'Low' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                firm.riskProfile === 'Medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' :
                'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
              }`}>
                {firm.riskProfile}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Market Position:</span>
              <span className="text-sm font-medium text-blue-600 dark:text-blue-400">{firm.marketPosition}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Financial Health:</span>
              <span className={`text-sm font-medium ${
                firm.financialHealth === 'Excellent' ? 'text-green-600 dark:text-green-400' :
                firm.financialHealth === 'Strong' ? 'text-blue-600 dark:text-blue-400' :
                firm.financialHealth === 'Good' ? 'text-yellow-600 dark:text-yellow-400' :
                'text-red-600 dark:text-red-400'
              }`}>
                {firm.financialHealth}
              </span>
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/50 dark:to-blue-950/50 p-3 rounded-lg mb-4">
            <div className="flex items-center space-x-2 mb-2">
              <Brain className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span className="text-sm font-medium text-purple-800 dark:text-purple-300">AI Recommendation</span>
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300">{firm.aiRecommendation}</p>
          </div>

          <div className="space-y-2 mb-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">Completed Projects:</span>
              <span className="font-medium text-gray-900 dark:text-white">{firm.completedProjects}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">Active Projects:</span>
              <span className="font-medium text-gray-900 dark:text-white">{firm.activeProjects}</span>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Certifications:</p>
            <div className="flex flex-wrap gap-1">
              {firm.certifications?.map((cert, index) => (
                <div key={index} className="flex items-center bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 px-2 py-1 rounded-full text-xs">
                  <BadgeCheck className="w-3 h-3 mr-1" />
                  {cert}
                </div>
              ))}
            </div>
          </div>

          <div className="flex space-x-2">
            <Button className="flex-1 ai-gradient text-white">
              AI Analysis
            </Button>
            <Button className="flex-1" variant="outline">
              View Details
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
}
