import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { TenderList } from "@/components/tenders/tender-list";
import { TenderDetails } from "@/components/tenders/tender-details";
import { AIAnalysis } from "@/components/tenders/ai-analysis";
import { TenderForm } from "@/components/tenders/tender-form";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Filter, Brain, Plus } from "lucide-react";
import { Tender } from "@shared/schema";

export default function Tenders() {
  const [selectedTenderId, setSelectedTenderId] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<"list" | "details" | "ai">("list");
  const [showTenderForm, setShowTenderForm] = useState(false);

  const { data: tenders, isLoading } = useQuery<Tender[]>({
    queryKey: ['/api/tenders'],
  });

  const selectedTender = selectedTenderId ? 
    tenders?.find(tender => tender.id === selectedTenderId) : null;

  const handleSelectTender = (id: number) => {
    setSelectedTenderId(id);
    setViewMode("details");
  };

  const handleBack = () => {
    if (viewMode === "ai") {
      setViewMode("details");
    } else {
      setViewMode("list");
      setSelectedTenderId(null);
    }
  };

  const handleAIAnalysis = () => {
    setViewMode("ai");
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Smart Tender Management</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Enhanced with GPT-4 Analysis & Predictive Intelligence</p>
        </div>
        <div className="flex space-x-4">
          {viewMode === "list" && (
            <>
              <Button variant="outline">
                <Filter className="w-4 h-4 mr-2" />
                AI Filter
              </Button>
              <Button className="ai-gradient text-white">
                <Brain className="w-4 h-4 mr-2" />
                AI Analysis
              </Button>
              <Button onClick={() => setShowTenderForm(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Tender
              </Button>
            </>
          )}
          {(viewMode === "details" || viewMode === "ai") && (
            <>
              <Button variant="outline" onClick={handleBack}>
                Back to {viewMode === "ai" ? "Details" : "List"}
              </Button>
              {viewMode === "details" && (
                <Button className="ai-gradient text-white" onClick={handleAIAnalysis}>
                  <Brain className="w-4 h-4 mr-2" />
                  AI Analysis
                </Button>
              )}
            </>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
          <Skeleton className="h-8 w-60 mb-4" />
          <div className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        </div>
      ) : (
        <>
          {viewMode === "list" && <TenderList tenders={tenders || []} onSelectTender={handleSelectTender} />}
          {viewMode === "details" && selectedTender && <TenderDetails tender={selectedTender} />}
          {viewMode === "ai" && selectedTender && <AIAnalysis tender={selectedTender} />}
        </>
      )}

      {/* Comprehensive Tender Form with all fields from your image */}
      {showTenderForm && (
        <TenderForm onClose={() => setShowTenderForm(false)} />
      )}
    </div>
  );
}
