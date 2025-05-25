import { useState } from "react";
import { TabsContent } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, Copy, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface OCRResultsProps {
  document: {
    id: number;
    name: string;
    ocrText: string;
    nlpAnalysis: string;
    gptAnalysis: string;
  };
  activeTab: string;
}

export function OCRResults({ document, activeTab }: OCRResultsProps) {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  // Try to parse JSON strings, but fall back to showing the raw text if parsing fails
  let nlpData = null;
  let gptData = null;
  
  try {
    if (document.nlpAnalysis) {
      nlpData = JSON.parse(document.nlpAnalysis);
    }
  } catch (e) {
    console.log("Could not parse NLP analysis as JSON");
  }
  
  try {
    if (document.gptAnalysis) {
      gptData = JSON.parse(document.gptAnalysis);
    }
  } catch (e) {
    console.log("Could not parse GPT analysis as JSON");
  }

  const handleCopyText = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast({
      title: "Copied to clipboard",
      description: `${type} text has been copied to your clipboard.`,
    });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (text: string, type: string) => {
    const element = document.createElement("a");
    const file = new Blob([text], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = `${document.name.split('.')[0]}-${type}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <>
      <TabsContent value="ocr" className="mt-0">
        <Card className="border-t-0 rounded-t-none">
          <CardContent className="p-6">
            <div className="flex justify-between items-center mb-4">
              <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">OCR Extraction</Badge>
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleCopyText(document.ocrText, "OCR")}
                >
                  {copied ? <Check className="h-4 w-4 mr-1" /> : <Copy className="h-4 w-4 mr-1" />}
                  Copy
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleDownload(document.ocrText, "OCR")}
                >
                  <Download className="h-4 w-4 mr-1" /> Download
                </Button>
              </div>
            </div>
            <pre className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg text-sm whitespace-pre-wrap font-mono max-h-96 overflow-y-auto">
              {document.ocrText}
            </pre>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="nlp" className="mt-0">
        <Card className="border-t-0 rounded-t-none">
          <CardContent className="p-6">
            <div className="flex justify-between items-center mb-4">
              <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">NLP Analysis</Badge>
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleCopyText(document.nlpAnalysis, "NLP")}
                >
                  {copied ? <Check className="h-4 w-4 mr-1" /> : <Copy className="h-4 w-4 mr-1" />}
                  Copy
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleDownload(document.nlpAnalysis, "NLP")}
                >
                  <Download className="h-4 w-4 mr-1" /> Download
                </Button>
              </div>
            </div>
            
            {nlpData ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                    <h3 className="font-medium mb-2">Document Sentiment</h3>
                    <div className="flex items-center">
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mr-2">
                        <div 
                          className="bg-green-600 dark:bg-green-500 h-2.5 rounded-full" 
                          style={{width: `${(nlpData.sentiment?.score || 0.5) * 100}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">
                        {nlpData.sentiment?.score ? (nlpData.sentiment.score * 100).toFixed(0) : 50}%
                      </span>
                    </div>
                    <p className="text-sm mt-1">
                      Sentiment: <span className="font-medium">{nlpData.sentiment?.label || "Neutral"}</span>
                    </p>
                  </div>
                  
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                    <h3 className="font-medium mb-2">Key Phrases</h3>
                    <div className="flex flex-wrap gap-2">
                      {nlpData.keyPhrases?.map((phrase: string, i: number) => (
                        <Badge key={i} variant="outline" className="bg-blue-100 dark:bg-blue-900 border-none">
                          {phrase}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                  <h3 className="font-medium mb-2">Entities</h3>
                  <div className="space-y-2">
                    {nlpData.entities?.map((entity: {type: string, text: string}, i: number) => (
                      <div key={i} className="flex items-center justify-between">
                        <span className="text-sm">{entity.text}</span>
                        <Badge variant="outline">
                          {entity.type}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
                  <h3 className="font-medium mb-2">Critical Clauses</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    {nlpData.criticalClauses?.map((clause: string, i: number) => (
                      <li key={i}>{clause}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                  <h3 className="font-medium mb-2">Compliance Requirements</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    {nlpData.complianceRequirements?.map((req: string, i: number) => (
                      <li key={i}>{req}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <pre className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg text-sm whitespace-pre-wrap font-mono max-h-96 overflow-y-auto">
                {document.nlpAnalysis}
              </pre>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="gpt" className="mt-0">
        <Card className="border-t-0 rounded-t-none">
          <CardContent className="p-6">
            <div className="flex justify-between items-center mb-4">
              <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300">GPT-4 Analysis</Badge>
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleCopyText(document.gptAnalysis, "GPT")}
                >
                  {copied ? <Check className="h-4 w-4 mr-1" /> : <Copy className="h-4 w-4 mr-1" />}
                  Copy
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleDownload(document.gptAnalysis, "GPT")}
                >
                  <Download className="h-4 w-4 mr-1" /> Download
                </Button>
              </div>
            </div>
            
            {gptData ? (
              <div className="space-y-6">
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/50 dark:to-blue-950/50 p-4 rounded-lg">
                  <h3 className="font-medium text-lg mb-2">Strategic Recommendation: <span className="text-purple-700 dark:text-purple-400">{gptData.recommendation}</span></h3>
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">{gptData.summary}</p>
                  
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mr-2">
                      <div 
                        className="bg-purple-600 dark:bg-purple-500 h-2.5 rounded-full" 
                        style={{width: `${gptData.score || 80}%`}}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{gptData.score || 80}%</span>
                  </div>
                </div>
                
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                  <h3 className="font-medium mb-3">Key Insights</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {gptData.insights?.map((insight: {category: string, score: number, details: string}, i: number) => (
                      <div key={i} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="flex justify-between items-center mb-1">
                          <h4 className="font-medium text-sm">{insight.category}</h4>
                          <Badge variant="outline">{insight.score}/10</Badge>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{insight.details}</p>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                    <h3 className="font-medium mb-3">Predictive Analytics</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Success Probability:</span>
                        <span className="text-sm font-medium">{gptData.predictiveAnalytics?.successProbability || 80}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Optimal Strategy:</span>
                        <span className="text-sm font-medium">{gptData.predictiveAnalytics?.optimalStrategy || "Balanced approach"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Resource Allocation:</span>
                        <span className="text-sm font-medium">{gptData.predictiveAnalytics?.resourceAllocation || "15 FTE"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Cash Flow Impact:</span>
                        <span className="text-sm font-medium">{gptData.predictiveAnalytics?.cashFlowImpact || "Positive from month 2"}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
                    <h3 className="font-medium mb-3">Risk Assessment</h3>
                    <div className="space-y-2">
                      {gptData.riskAssessment && Object.entries(gptData.riskAssessment).map(([key, value]: [string, any], i: number) => (
                        <div key={i} className="flex justify-between">
                          <span className="text-sm capitalize">{key} Risk:</span>
                          <Badge 
                            variant="outline" 
                            className={
                              value.level === "Low" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" : 
                              value.level === "Medium" ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300" :
                              "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
                            }
                          >
                            {value.level}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                  <h3 className="font-medium mb-3">Action Recommendations</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    {gptData.actionRecommendations?.map((action: string, i: number) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <pre className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/50 dark:to-blue-950/50 p-4 rounded-lg text-sm whitespace-pre-wrap font-mono max-h-96 overflow-y-auto">
                {document.gptAnalysis}
              </pre>
            )}
          </CardContent>
        </Card>
      </TabsContent>
    </>
  );
}
