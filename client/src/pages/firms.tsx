import { useQuery } from "@tanstack/react-query";
import { FirmList } from "@/components/firms/firm-list";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Brain, Plus } from "lucide-react";
import { useState } from "react";
import { FirmDetails } from "@/components/firms/firm-details";
import { Firm } from "@shared/schema";

export default function Firms() {
  const [selectedFirmId, setSelectedFirmId] = useState<number | null>(null);

  const { data: firms, isLoading } = useQuery<Firm[]>({
    queryKey: ['/api/firms'],
  });

  const selectedFirm = selectedFirmId ? 
    firms?.find(firm => firm.id === selectedFirmId) : null;

  const handleSelectFirm = (id: number) => {
    setSelectedFirmId(id);
  };

  const handleBack = () => {
    setSelectedFirmId(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI Firm Intelligence</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">ML-powered firm analysis and recommendations</p>
        </div>
        <div className="flex space-x-4">
          {!selectedFirm ? (
            <>
              <Button className="ai-gradient text-white">
                <Brain className="w-4 h-4 mr-2" />
                AI Matchmaker
              </Button>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Firm
              </Button>
            </>
          ) : (
            <Button variant="outline" onClick={handleBack}>
              Back to List
            </Button>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
              <div className="flex items-center mb-4">
                <Skeleton className="h-12 w-12 rounded-full" />
                <div className="ml-3">
                  <Skeleton className="h-5 w-40" />
                  <Skeleton className="h-4 w-24 mt-1" />
                </div>
              </div>
              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-10 w-full mt-4" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
          {!selectedFirm ? (
            <FirmList firms={firms || []} onSelectFirm={handleSelectFirm} />
          ) : (
            <FirmDetails firm={selectedFirm} />
          )}
        </>
      )}
    </div>
  );
}
