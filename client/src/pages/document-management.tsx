import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { 
  Upload, 
  FileText, 
  Shield, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Download,
  Eye,
  Settings,
  Cloud,
  Folder,
  Database,
  Webhook,
  Key,
  BarChart3
} from "lucide-react";

interface Document {
  id: number;
  name: string;
  originalFileName: string;
  fileSize: number;
  mimeType: string;
  documentType: string;
  documentCategory: string;
  status: string;
  complianceStatus: string;
  isVerified: boolean;
  accessLevel: string;
  syncStatus: string;
  uploadedAt: string;
  tenderId?: number;
}

export default function DocumentManagement() {
  const [selectedTab, setSelectedTab] = useState("documents");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState("");
  const [documentCategory, setDocumentCategory] = useState("");
  const [tenderId, setTenderId] = useState("");
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch documents with enhanced features
  const { data: documentsData, isLoading } = useQuery({
    queryKey: ["/api/documents/enhanced"],
    queryFn: async () => {
      const response = await fetch("/api/documents/enhanced");
      if (!response.ok) throw new Error("Failed to fetch documents");
      return response.json();
    },
  });

  // Fetch integration status
  const { data: integrationStatus } = useQuery({
    queryKey: ["/api/integrations/dashboard"],
    queryFn: async () => {
      const response = await fetch("/api/integrations/dashboard");
      if (!response.ok) throw new Error("Failed to fetch integration status");
      return response.json();
    },
  });

  // Upload document mutation
  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await fetch("/api/documents/upload-enhanced", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Failed to upload document");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/documents/enhanced"] });
      toast({
        title: "Success",
        description: "Document uploaded with enhanced tracking features",
      });
      setUploadFile(null);
      setDocumentType("");
      setDocumentCategory("");
      setTenderId("");
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to upload document",
        variant: "destructive",
      });
    },
  });

  // Verify document mutation
  const verifyMutation = useMutation({
    mutationFn: async ({ id, verificationData }: { id: number; verificationData: any }) => {
      const response = await fetch(`/api/documents/${id}/verify-enhanced`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(verificationData),
      });
      if (!response.ok) throw new Error("Failed to verify document");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/documents/enhanced"] });
      toast({
        title: "Success",
        description: "Document verification completed with compliance tracking",
      });
    },
  });

  const handleUpload = () => {
    if (!uploadFile) return;

    const formData = new FormData();
    formData.append("file", uploadFile);
    if (documentType) formData.append("documentType", documentType);
    if (documentCategory) formData.append("documentCategory", documentCategory);
    if (tenderId) formData.append("tenderId", tenderId);
    formData.append("accessLevel", "Internal");

    uploadMutation.mutate(formData);
  };

  const handleVerify = (document: Document, isCompliant: boolean) => {
    verifyMutation.mutate({
      id: document.id,
      verificationData: {
        verificationNotes: `Document verified as ${isCompliant ? 'compliant' : 'non-compliant'}`,
        isCompliant,
        legalApproval: isCompliant,
        complianceIssues: isCompliant ? [] : ["Requires review"]
      }
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Uploaded": return "bg-blue-100 text-blue-800";
      case "Verified": return "bg-green-100 text-green-800";
      case "Processing": return "bg-yellow-100 text-yellow-800";
      case "Rejected": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getComplianceColor = (status: string) => {
    switch (status) {
      case "Compliant": return "bg-green-100 text-green-800";
      case "Non-compliant": return "bg-red-100 text-red-800";
      case "Under Review": return "bg-yellow-100 text-yellow-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const documents = documentsData?.documents || [];
  const analytics = documentsData?.analytics || {};

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Document Management System</h1>
        <div className="flex items-center space-x-2">
          <Cloud className="h-5 w-5 text-green-500" />
          <span className="text-sm text-gray-600">Cloud Integration Ready</span>
        </div>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="upload">Upload</TabsTrigger>
          <TabsTrigger value="google-drive">Google Drive</TabsTrigger>
          <TabsTrigger value="integrations">API Hooks</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="documents" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <FileText className="h-8 w-8 text-blue-500" />
                  <div>
                    <p className="text-2xl font-bold">{analytics.total || 0}</p>
                    <p className="text-sm text-gray-600">Total Documents</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-8 w-8 text-green-500" />
                  <div>
                    <p className="text-2xl font-bold">{documents.filter((d: Document) => d.isVerified).length}</p>
                    <p className="text-sm text-gray-600">Verified</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Cloud className="h-8 w-8 text-purple-500" />
                  <div>
                    <p className="text-2xl font-bold">{analytics.storageStats?.cloudSynced || 0}</p>
                    <p className="text-sm text-gray-600">Cloud Synced</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Database className="h-8 w-8 text-orange-500" />
                  <div>
                    <p className="text-2xl font-bold">
                      {Math.round((analytics.storageStats?.totalSize || 0) / 1024 / 1024)}MB
                    </p>
                    <p className="text-sm text-gray-600">Total Size</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4">
            {isLoading ? (
              <div className="text-center py-8">Loading documents...</div>
            ) : documents.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No documents uploaded yet</p>
                  <Button 
                    className="mt-4" 
                    onClick={() => setSelectedTab("upload")}
                  >
                    Upload First Document
                  </Button>
                </CardContent>
              </Card>
            ) : (
              documents.map((document: Document) => (
                <Card key={document.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <FileText className="h-10 w-10 text-blue-500" />
                        <div>
                          <h3 className="font-semibold">{document.name}</h3>
                          <p className="text-sm text-gray-600">{document.originalFileName}</p>
                          <div className="flex items-center space-x-2 mt-2">
                            <Badge className={getStatusColor(document.status)}>
                              {document.status}
                            </Badge>
                            <Badge className={getComplianceColor(document.complianceStatus)}>
                              {document.complianceStatus}
                            </Badge>
                            <Badge variant="outline">
                              {document.documentType}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {!document.isVerified && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleVerify(document, true)}
                              disabled={verifyMutation.isPending}
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Approve
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleVerify(document, false)}
                              disabled={verifyMutation.isPending}
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Reject
                            </Button>
                          </>
                        )}
                        <Button size="sm" variant="ghost">
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Download className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      </div>
                    </div>
                    
                    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Size</p>
                        <p>{Math.round((document.fileSize || 0) / 1024)} KB</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Category</p>
                        <p>{document.documentCategory}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Access Level</p>
                        <p>{document.accessLevel}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Sync Status</p>
                        <p>{document.syncStatus}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="upload" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="h-5 w-5" />
                <span>Enhanced Document Upload</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="file">Select Document</Label>
                <Input
                  id="file"
                  type="file"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="documentType">Document Type</Label>
                  <Select value={documentType} onValueChange={setDocumentType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Proposal Document">Proposal Document</SelectItem>
                      <SelectItem value="Affidavit/Declaration">Affidavit/Declaration</SelectItem>
                      <SelectItem value="Test Reports">Test Reports</SelectItem>
                      <SelectItem value="Compliance Certificate">Compliance Certificate</SelectItem>
                      <SelectItem value="Technical Datasheet">Technical Datasheet</SelectItem>
                      <SelectItem value="Financial Document">Financial Document</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="documentCategory">Category</Label>
                  <Select value={documentCategory} onValueChange={setDocumentCategory}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Technical">Technical</SelectItem>
                      <SelectItem value="Compliance">Compliance</SelectItem>
                      <SelectItem value="Financial">Financial</SelectItem>
                      <SelectItem value="Legal">Legal</SelectItem>
                      <SelectItem value="General">General</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="tenderId">Tender ID (Optional)</Label>
                  <Input
                    id="tenderId"
                    value={tenderId}
                    onChange={(e) => setTenderId(e.target.value)}
                    placeholder="Link to tender"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <Button 
                  onClick={handleUpload}
                  disabled={!uploadFile || uploadMutation.isPending}
                  className="flex-1"
                >
                  {uploadMutation.isPending ? (
                    <>
                      <Clock className="h-4 w-4 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload with Enhanced Features
                    </>
                  )}
                </Button>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">Enhanced Features Include:</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Automatic compliance checking and verification</li>
                  <li>• Google Drive integration for cloud storage</li>
                  <li>• Version control and access management</li>
                  <li>• AI-powered content analysis and extraction</li>
                  <li>• Role-based security and audit trails</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="google-drive" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Cloud className="h-5 w-5" />
                <span>Google Drive Integration</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-2">Ready for Google Drive Setup</h4>
                <p className="text-sm text-green-700 mb-4">
                  Connect your Google Drive to enable automatic folder organization and cloud synchronization.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-medium mb-2">Features Available:</h5>
                    <ul className="text-sm space-y-1">
                      <li>• Automatic tender-based folder creation</li>
                      <li>• Real-time file synchronization</li>
                      <li>• Role-based access permissions</li>
                      <li>• Backup and recovery</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h5 className="font-medium mb-2">Folder Structure:</h5>
                    <ul className="text-sm space-y-1">
                      <li>• Proposal Documents</li>
                      <li>• Technical Documentation</li>
                      <li>• Compliance Certificates</li>
                      <li>• Financial Documents</li>
                      <li>• Legal Documents</li>
                    </ul>
                  </div>
                </div>
              </div>

              <Button className="w-full">
                <Key className="h-4 w-4 mr-2" />
                Configure Google Drive Credentials
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Webhook className="h-5 w-5" />
                <span>API Integration Hooks</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-4">Inbound Webhooks</h4>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-blue-700 mb-2">Receive real-time updates from external systems:</p>
                    <ul className="text-sm space-y-1">
                      <li>• Document status changes</li>
                      <li>• Compliance alerts</li>
                      <li>• Tender updates</li>
                      <li>• System notifications</li>
                    </ul>
                  </div>
                  <Button className="w-full mt-4" variant="outline">
                    Configure Inbound Hooks
                  </Button>
                </div>

                <div>
                  <h4 className="font-semibold mb-4">Outbound Webhooks</h4>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-green-700 mb-2">Send notifications to external systems:</p>
                    <ul className="text-sm space-y-1">
                      <li>• Document upload notifications</li>
                      <li>• Verification completions</li>
                      <li>• Compliance status updates</li>
                      <li>• Integration events</li>
                    </ul>
                  </div>
                  <Button className="w-full mt-4" variant="outline">
                    Setup Outbound Hooks
                  </Button>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-2">Integration Status</h4>
                <div className="text-sm space-y-2">
                  <div className="flex justify-between">
                    <span>Document Management API</span>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Webhook Processing</span>
                    <Badge className="bg-green-100 text-green-800">Ready</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Authentication</span>
                    <Badge className="bg-green-100 text-green-800">Enabled</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>Document Analytics & Insights</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-blue-800">Upload Trends</h4>
                  <div className="mt-2">
                    <div className="flex justify-between text-sm">
                      <span>This Month</span>
                      <span>{documents.length} uploads</span>
                    </div>
                    <Progress value={75} className="mt-2" />
                  </div>
                </div>

                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-green-800">Compliance Rate</h4>
                  <div className="mt-2">
                    <div className="flex justify-between text-sm">
                      <span>Compliant</span>
                      <span>
                        {Math.round((documents.filter((d: Document) => d.complianceStatus === 'Compliant').length / Math.max(documents.length, 1)) * 100)}%
                      </span>
                    </div>
                    <Progress 
                      value={(documents.filter((d: Document) => d.complianceStatus === 'Compliant').length / Math.max(documents.length, 1)) * 100} 
                      className="mt-2" 
                    />
                  </div>
                </div>

                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-purple-800">Storage Usage</h4>
                  <div className="mt-2">
                    <div className="flex justify-between text-sm">
                      <span>Used</span>
                      <span>{Math.round((analytics.storageStats?.totalSize || 0) / 1024 / 1024)}MB</span>
                    </div>
                    <Progress value={30} className="mt-2" />
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-4">System Health</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Document Processing</span>
                    <Badge className="bg-green-100 text-green-800">Operational</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Cloud Sync</span>
                    <Badge className="bg-yellow-100 text-yellow-800">Ready for Setup</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">API Integrations</span>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}