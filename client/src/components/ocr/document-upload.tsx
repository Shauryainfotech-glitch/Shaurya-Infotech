import { useState, useRef } from "react";
import { Upload, Scan, FileText, X, File, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface DocumentUploadProps {
  onDocumentProcessed: (document: any) => void;
  onProcessingStart: () => void;
  tenderId?: number;
  firmId?: number;
}

export function DocumentUpload({ 
  onDocumentProcessed, 
  onProcessingStart,
  tenderId, 
  firmId 
}: DocumentUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png', 'image/tiff'];
      
      if (allowedTypes.includes(file.type)) {
        setSelectedFile(file);
      } else {
        toast({
          title: "Invalid file type",
          description: "Please upload a PDF, DOC, DOCX, JPG, PNG, or TIFF file",
          variant: "destructive",
        });
      }
    }
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setIsUploading(true);
    onProcessingStart();

    // Create FormData object
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    if (tenderId) {
      formData.append('tenderId', tenderId.toString());
    }
    
    if (firmId) {
      formData.append('firmId', firmId.toString());
    }

    try {
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      onDocumentProcessed(data);
      
      toast({
        title: "Document processed successfully",
        description: "AI analysis complete with OCR, NLP, and GPT-4 insights",
      });
      
    } catch (error) {
      console.error("Error uploading document:", error);
      toast({
        title: "Document processing failed",
        description: error instanceof Error ? error.message : "An unknown error occurred",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const getFileIcon = (file: File) => {
    if (file.type.includes('pdf')) {
      return <FileText className="h-8 w-8 text-red-500 dark:text-red-400" />;
    } else if (file.type.includes('word') || file.type.includes('doc')) {
      return <FileText className="h-8 w-8 text-blue-500 dark:text-blue-400" />;
    } else if (file.type.includes('image')) {
      return <File className="h-8 w-8 text-green-500 dark:text-green-400" />;
    } else {
      return <File className="h-8 w-8 text-gray-500 dark:text-gray-400" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Smart Document Upload</CardTitle>
      </CardHeader>
      <CardContent>
        <div 
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging 
              ? 'border-blue-400 bg-blue-50 dark:border-blue-600 dark:bg-blue-900/20' 
              : 'border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {!selectedFile ? (
            <>
              <Upload className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-4">Drag and drop your tender documents here</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mb-4">Supports: PDF, DOC, DOCX, JPG, PNG, TIFF</p>
              <input
                type="file"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                ref={fileInputRef}
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.tiff"
              />
              <Button 
                className="ai-gradient text-white"
                onClick={() => fileInputRef.current?.click()}
              >
                Choose File
              </Button>
            </>
          ) : (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getFileIcon(selectedFile)}
                <div className="text-left">
                  <p className="font-medium dark:text-white">{selectedFile.name}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Size: {(selectedFile.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  size="icon" 
                  onClick={handleClearFile}
                  disabled={isUploading}
                >
                  <X className="h-4 w-4" />
                </Button>
                <Button 
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="ai-gradient text-white"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Scan className="mr-2 h-4 w-4" />
                      Analyze with AI
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
        </div>

        {!selectedFile && (
          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Scan className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              <h3 className="font-medium text-gray-900 dark:text-white">Advanced AI Processing</h3>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Upload your tender documents to leverage our AI-powered analysis:
            </p>
            <ul className="mt-2 space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></span>
                <span>OCR extraction with 99.7% accuracy</span>
              </li>
              <li className="flex items-center">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></span>
                <span>NLP entity recognition and key phrase extraction</span>
              </li>
              <li className="flex items-center">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mr-2"></span>
                <span>GPT-4 strategic analysis and insights</span>
              </li>
              <li className="flex items-center">
                <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mr-2"></span>
                <span>Automated risk assessment and scoring</span>
              </li>
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
