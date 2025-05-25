import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  CardDescription,
  CardFooter
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { CalendarIcon, CheckCircleIcon, FileIcon, AlertCircleIcon } from "lucide-react";
import { formatDistance } from "date-fns";

interface PipelineStage {
  id: number;
  name: string;
  description: string | null;
  displayOrder: number;
  color: string;
}

interface Tender {
  id: number;
  title: string;
  organization: string;
  value: string;
  deadline: string;
  status: string;
  pipelineStageId: number | null;
  successProbability: number;
  riskScore: number;
}

export default function Pipeline() {
  const [draggedTender, setDraggedTender] = useState<Tender | null>(null);
  
  // Fetch pipeline stages
  const { data: stages, isLoading: stagesLoading } = useQuery({
    queryKey: ['/api/pipeline-stages'],
    refetchInterval: false,
  });
  
  // Fetch tenders
  const { data: tenders, isLoading: tendersLoading, refetch: refetchTenders } = useQuery({
    queryKey: ['/api/tenders'],
    refetchInterval: false,
  });
  
  const handleDragStart = (tender: Tender) => {
    setDraggedTender(tender);
  };
  
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };
  
  const handleDrop = async (e: React.DragEvent, stageId: number) => {
    e.preventDefault();
    if (!draggedTender) return;
    
    try {
      // Update tender with new pipeline stage
      const response = await fetch(`/api/tenders/${draggedTender.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...draggedTender,
          pipelineStageId: stageId
        }),
      });
      
      if (response.ok) {
        // Refetch tenders to update the UI
        refetchTenders();
      }
    } catch (error) {
      console.error("Error updating tender stage:", error);
    }
    
    setDraggedTender(null);
  };
  
  const getTendersInStage = (stageId: number) => {
    if (!tenders) return [];
    return tenders.filter((tender: Tender) => tender.pipelineStageId === stageId);
  };
  
  const getRiskBadgeColor = (riskScore: number) => {
    if (riskScore < 30) return "bg-green-500";
    if (riskScore < 70) return "bg-yellow-500";
    return "bg-red-500";
  };
  
  const getProbabilityBadgeColor = (probability: number) => {
    if (probability > 80) return "bg-green-500";
    if (probability > 50) return "bg-blue-500";
    return "bg-gray-500";
  };
  
  if (stagesLoading || tendersLoading) {
    return <div className="p-8">Loading pipeline data...</div>;
  }
  
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Tender Pipeline</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Manage and track tenders through their lifecycle stages
          </p>
        </div>
        <Button>Add New Tender</Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
        {stages && stages.map((stage: PipelineStage) => (
          <div 
            key={stage.id}
            className="flex flex-col h-full"
          >
            <div 
              className="p-3 rounded-t-lg text-white font-medium mb-2"
              style={{ backgroundColor: stage.color }}
            >
              <div className="flex justify-between items-center">
                <h3>{stage.name}</h3>
                <Badge variant="outline" className="bg-white/20 text-white">
                  {getTendersInStage(stage.id).length}
                </Badge>
              </div>
            </div>
            
            <div 
              className="flex-1 bg-gray-50 dark:bg-gray-800/50 rounded-lg p-2 min-h-[400px]"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, stage.id)}
            >
              {getTendersInStage(stage.id).map((tender: Tender) => (
                <Card 
                  key={tender.id}
                  className="mb-3 cursor-move hover:shadow-md transition-shadow"
                  draggable
                  onDragStart={() => handleDragStart(tender)}
                >
                  <CardHeader className="p-3 pb-0">
                    <CardTitle className="text-base font-medium">{tender.title}</CardTitle>
                    <CardDescription className="text-xs">{tender.organization}</CardDescription>
                  </CardHeader>
                  <CardContent className="p-3 pt-2">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-500 dark:text-gray-400">Value:</span>
                      <span className="font-medium">{tender.value}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-400">Deadline:</span>
                      <span className="font-medium">{
                        formatDistance(new Date(tender.deadline), new Date(), { addSuffix: true })
                      }</span>
                    </div>
                  </CardContent>
                  <Separator />
                  <CardFooter className="p-3 pt-2 flex justify-between">
                    <Badge variant="outline" className={`${getRiskBadgeColor(tender.riskScore)} text-white`}>
                      Risk: {tender.riskScore}%
                    </Badge>
                    <Badge variant="outline" className={`${getProbabilityBadgeColor(tender.successProbability)} text-white`}>
                      Success: {tender.successProbability}%
                    </Badge>
                  </CardFooter>
                </Card>
              ))}
              
              {getTendersInStage(stage.id).length === 0 && (
                <div className="flex flex-col items-center justify-center h-full p-6 text-center text-gray-400">
                  <FileIcon className="mb-2 h-8 w-8 opacity-50" />
                  <p className="text-sm">Drag tenders here</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}