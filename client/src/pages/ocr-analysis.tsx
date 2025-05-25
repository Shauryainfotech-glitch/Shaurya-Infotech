import { useState } from "react";
import { DocumentUpload } from "@/components/ocr/document-upload";
import { OCRResults } from "@/components/ocr/ocr-results";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface ProcessedDocument {
  id: number;
  name: string;
  ocrText: string;
  nlpAnalysis: string;
  gptAnalysis: string;
}

export default function OcrAnalysis() {
  const [processedDocument, setProcessedDocument] = useState<ProcessedDocument | null>(null);
  const [activeTab, setActiveTab] = useState<string>("ocr");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleProcessedDocument = (document: ProcessedDocument) => {
    setProcessedDocument(document);
    setIsProcessing(false);
  };

  const handleProcessingStart = () => {
    setIsProcessing(true);
    setProcessedDocument(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Advanced OCR + NLP Intelligence</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">AI-powered document extraction with GPT-4 analysis</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 dark:bg-green-400 rounded-full animate-ai-pulse"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">99.7% Accuracy</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DocumentUpload 
          onDocumentProcessed={handleProcessedDocument} 
          onProcessingStart={handleProcessingStart} 
        />

        <Card>
          <CardHeader>
            <CardTitle>AI Processing Pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center p-4 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 rounded-lg">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center mr-4 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium dark:text-white">Advanced OCR Engine</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">99.7% accuracy with multilingual support</p>
                </div>
              </div>
              
              <div className="flex items-center p-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-950 dark:to-green-900 rounded-lg">
                <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center mr-4 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium dark:text-white">NLP Intelligence</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Entity extraction and sentiment analysis</p>
                </div>
              </div>
              
              <div className="flex items-center p-4 bg-gradient-to-r from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 rounded-lg">
                <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center mr-4 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium dark:text-white">GPT-4 Analysis</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Strategic insights and recommendations</p>
                </div>
              </div>
              
              <div className="flex items-center p-4 bg-gradient-to-r from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900 rounded-lg">
                <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center mr-4 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium dark:text-white">Risk Assessment</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Automated risk detection and scoring</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Results Display */}
      {(isProcessing || processedDocument) && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            {isProcessing ? (
              <div className="flex flex-col items-center justify-center p-8">
                <div className="w-16 h-16 border-4 border-t-blue-500 border-b-blue-700 border-l-blue-600 border-r-blue-600 rounded-full animate-spin mb-4"></div>
                <p className="text-lg font-medium text-gray-900 dark:text-white">Processing Document...</p>
                <p className="text-gray-600 dark:text-gray-400">This may take a few moments</p>
              </div>
            ) : processedDocument && (
              <Tabs defaultValue={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="w-full justify-start mb-4">
                  <TabsTrigger value="ocr">OCR Results</TabsTrigger>
                  <TabsTrigger value="nlp">NLP Analysis</TabsTrigger>
                  <TabsTrigger value="gpt">GPT-4 Analysis</TabsTrigger>
                </TabsList>
                <OCRResults 
                  document={processedDocument} 
                  activeTab={activeTab} 
                />
              </Tabs>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
