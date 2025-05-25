import { TrendingUp, FileText, Award } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function MarketIntelligence() {
  const marketCards = [
    {
      icon: TrendingUp,
      value: "+23%",
      label: "IT Tender Growth",
      color: "from-green-50 to-green-100 dark:from-green-900/40 dark:to-green-900/20",
      iconColor: "text-green-600 dark:text-green-400"
    },
    {
      icon: FileText,
      value: "847",
      label: "Active Opportunities",
      color: "from-blue-50 to-blue-100 dark:from-blue-900/40 dark:to-blue-900/20",
      iconColor: "text-blue-600 dark:text-blue-400"
    },
    {
      icon: Award,
      value: "₹125Cr",
      label: "Total Pipeline Value",
      color: "from-purple-50 to-purple-100 dark:from-purple-900/40 dark:to-purple-900/20",
      iconColor: "text-purple-600 dark:text-purple-400"
    }
  ];

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>AI Market Intelligence</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {marketCards.map((card, index) => (
            <div 
              key={index} 
              className={`text-center p-4 bg-gradient-to-br ${card.color} rounded-lg`}
            >
              <card.icon className={`w-8 h-8 ${card.iconColor} mx-auto mb-2`} />
              <p className={`text-2xl font-bold ${card.iconColor}`}>{card.value}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">{card.label}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
