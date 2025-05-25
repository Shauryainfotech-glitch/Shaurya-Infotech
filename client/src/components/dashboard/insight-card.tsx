import { TrendingUp, Brain } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface InsightCardProps {
  metric: string;
  value: string;
  trend: "up" | "down";
  color: "green" | "blue" | "purple" | "orange";
}

export function InsightCard({ metric, value, trend, color }: InsightCardProps) {
  const bgColors = {
    green: "from-green-500 to-green-600 dark:from-green-600 dark:to-green-700",
    blue: "from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700",
    purple: "from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700",
    orange: "from-orange-500 to-orange-600 dark:from-orange-600 dark:to-orange-700"
  };

  const textColors = {
    green: "text-green-100 dark:text-green-100",
    blue: "text-blue-100 dark:text-blue-100",
    purple: "text-purple-100 dark:text-purple-100",
    orange: "text-orange-100 dark:text-orange-100"
  };

  return (
    <Card className={cn(
      "bg-gradient-to-r p-6 rounded-xl text-white relative overflow-hidden shadow-lg",
      bgColors[color]
    )}>
      <div className="flex items-center justify-between relative z-10">
        <div>
          <p className={textColors[color]}>{metric}</p>
          <p className="text-3xl font-bold">{value}</p>
          <div className="flex items-center mt-2">
            <TrendingUp className="w-4 h-4 mr-1" />
            <span className="text-xs">AI Powered</span>
          </div>
        </div>
        <div className="opacity-20">
          <Brain className="w-16 h-16" />
        </div>
      </div>
    </Card>
  );
}
