import { useQuery } from "@tanstack/react-query";
import { InsightCard } from "@/components/dashboard/insight-card";
import { TenderSummary } from "@/components/dashboard/tender-summary";
import { PerformanceMetrics } from "@/components/dashboard/performance-metrics";
import { MarketIntelligence } from "@/components/dashboard/market-intelligence";
import { Brain, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tender, Firm } from "@shared/schema";

export default function Dashboard() {
  const { data: tenders, isLoading: tendersLoading } = useQuery<Tender[]>({
    queryKey: ['/api/tenders'],
  });

  const { data: firms, isLoading: firmsLoading } = useQuery<Firm[]>({
    queryKey: ['/api/firms'],
  });

  const aiInsights = [
    { metric: "Success Prediction", value: "87%", trend: "up", color: "green" },
    { metric: "Risk Score", value: "23/100", trend: "down", color: "blue" },
    { metric: "Market Position", value: "#3/25", trend: "up", color: "purple" },
    { metric: "Profit Margin", value: "18.5%", trend: "up", color: "orange" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI-Powered Tender Intelligence</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Enhanced with GPT-4, NLP, and Predictive Analytics</p>
        </div>
        <div className="flex space-x-4">
          <Button className="ai-gradient text-white" variant="default">
            <Brain className="w-4 h-4 mr-2" />
            AI Analysis
          </Button>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Tender
          </Button>
        </div>
      </div>

      {/* AI Insights Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {aiInsights.map((insight, index) => (
          <InsightCard 
            key={index}
            metric={insight.metric}
            value={insight.value}
            trend={insight.trend as "up" | "down"}
            color={insight.color as "green" | "blue" | "purple" | "orange"}
          />
        ))}
      </div>

      {/* Real-time Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {tendersLoading ? (
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
            <div className="space-y-4">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
            </div>
          </div>
        ) : (
          <TenderSummary tenders={tenders || []} />
        )}

        <PerformanceMetrics />
      </div>

      {/* Market Intelligence */}
      <MarketIntelligence />
    </div>
  );
}
