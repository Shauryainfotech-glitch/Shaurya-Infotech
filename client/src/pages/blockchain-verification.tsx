import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { 
  Shield, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  FileCheck,
  Lock,
  Key,
  Link,
  Search,
  Award,
  Eye,
  Download,
  Fingerprint,
  Database
} from "lucide-react";

interface BlockchainStats {
  totalBlocks: number;
  totalTenders: number;
  chainIntegrity: boolean;
  latestBlock: any;
}

interface AuditRecord {
  timestamp: Date;
  action: string;
  details: any;
  blockHash: string;
  verified: boolean;
}

export default function BlockchainVerification() {
  const [selectedTab, setSelectedTab] = useState("verification");
  const [tenderId, setTenderId] = useState("");
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [auditTrail, setAuditTrail] = useState<any>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch blockchain statistics
  const { data: blockchainStats, isLoading: statsLoading } = useQuery({
    queryKey: ['/api/blockchain/stats'],
    enabled: true
  });

  // Verify tender record
  const verifyTenderMutation = useMutation({
    mutationFn: async (tenderId: string) => {
      const response = await fetch(`/api/blockchain/verify/${tenderId}`);
      if (!response.ok) throw new Error('Failed to verify tender');
      return response.json();
    },
    onSuccess: (data) => {
      setVerificationResult(data);
      toast({
        title: "Verification Complete",
        description: data.isValid ? "Tender record is valid and tamper-proof" : "Integrity issues detected",
      });
    },
    onError: () => {
      toast({
        title: "Verification Failed",
        description: "Could not verify tender record",
        variant: "destructive",
      });
    }
  });

  // Get audit trail
  const getAuditTrailMutation = useMutation({
    mutationFn: async (tenderId: string) => {
      const response = await fetch(`/api/blockchain/audit-trail/${tenderId}`);
      if (!response.ok) throw new Error('Failed to get audit trail');
      return response.json();
    },
    onSuccess: (data) => {
      setAuditTrail(data);
      toast({
        title: "Audit Trail Retrieved",
        description: `Found ${data.totalBlocks} blockchain records`,
      });
    },
    onError: () => {
      toast({
        title: "Audit Trail Failed",
        description: "Could not retrieve audit trail",
        variant: "destructive",
      });
    }
  });

  // Record tender on blockchain
  const recordTenderMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await fetch('/api/blockchain/record-tender', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Failed to record tender');
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Blockchain Record Created",
        description: `Tender recorded with hash: ${data.blockHash.substring(0, 16)}...`,
      });
      queryClient.invalidateQueries({ queryKey: ['/api/blockchain/stats'] });
    }
  });

  const handleVerifyTender = () => {
    if (!tenderId.trim()) {
      toast({
        title: "Input Required",
        description: "Please enter a tender ID to verify",
        variant: "destructive",
      });
      return;
    }
    verifyTenderMutation.mutate(tenderId);
  };

  const handleGetAuditTrail = () => {
    if (!tenderId.trim()) {
      toast({
        title: "Input Required", 
        description: "Please enter a tender ID for audit trail",
        variant: "destructive",
      });
      return;
    }
    getAuditTrailMutation.mutate(tenderId);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Blockchain Verification</h1>
          <p className="text-gray-600 mt-2">Secure tender verification and audit trails</p>
        </div>
        <Badge className="bg-green-100 text-green-800 px-4 py-2">
          <Shield className="h-4 w-4 mr-2" />
          Blockchain Secured
        </Badge>
      </div>

      {/* Blockchain Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Database className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-2xl font-bold">{blockchainStats?.totalBlocks || 0}</p>
                <p className="text-sm text-gray-600">Total Blocks</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <FileCheck className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-2xl font-bold">{blockchainStats?.totalTenders || 0}</p>
                <p className="text-sm text-gray-600">Verified Tenders</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-2xl font-bold">
                  {blockchainStats?.chainIntegrity ? "100%" : "0%"}
                </p>
                <p className="text-sm text-gray-600">Chain Integrity</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Lock className="h-8 w-8 text-red-600" />
              <div>
                <p className="text-2xl font-bold">256</p>
                <p className="text-sm text-gray-600">Bit Encryption</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="verification">Verify Records</TabsTrigger>
          <TabsTrigger value="audit">Audit Trail</TabsTrigger>
          <TabsTrigger value="signatures">Digital Signatures</TabsTrigger>
          <TabsTrigger value="contracts">Smart Contracts</TabsTrigger>
        </TabsList>

        <TabsContent value="verification" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Search className="h-5 w-5" />
                <span>Tender Record Verification</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex space-x-4">
                <div className="flex-1">
                  <Label htmlFor="tenderId">Tender ID</Label>
                  <Input
                    id="tenderId"
                    value={tenderId}
                    onChange={(e) => setTenderId(e.target.value)}
                    placeholder="Enter tender ID to verify..."
                    className="mt-1"
                  />
                </div>
                <div className="flex items-end">
                  <Button 
                    onClick={handleVerifyTender}
                    disabled={verifyTenderMutation.isPending}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {verifyTenderMutation.isPending ? (
                      <Clock className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Shield className="h-4 w-4 mr-2" />
                    )}
                    Verify
                  </Button>
                </div>
              </div>

              {verificationResult && (
                <div className="border rounded-lg p-4 space-y-4">
                  <div className="flex items-center space-x-2">
                    {verificationResult.isValid ? (
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-6 w-6 text-red-600" />
                    )}
                    <span className="font-semibold">
                      {verificationResult.isValid ? "Record Verified" : "Integrity Issues Found"}
                    </span>
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">Blockchain Records Found: {verificationResult.records?.length || 0}</p>
                    
                    {verificationResult.auditTrail && (
                      <div className="bg-gray-50 rounded p-3">
                        <h4 className="font-medium mb-2">Verification Log:</h4>
                        <div className="space-y-1">
                          {verificationResult.auditTrail.map((log: string, index: number) => (
                            <p key={index} className="text-sm font-mono">{log}</p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Eye className="h-5 w-5" />
                <span>Audit Trail</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex space-x-4">
                <div className="flex-1">
                  <Label htmlFor="auditTenderId">Tender ID</Label>
                  <Input
                    id="auditTenderId"
                    value={tenderId}
                    onChange={(e) => setTenderId(e.target.value)}
                    placeholder="Enter tender ID for audit trail..."
                    className="mt-1"
                  />
                </div>
                <div className="flex items-end">
                  <Button 
                    onClick={handleGetAuditTrail}
                    disabled={getAuditTrailMutation.isPending}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    {getAuditTrailMutation.isPending ? (
                      <Clock className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Eye className="h-4 w-4 mr-2" />
                    )}
                    Get Trail
                  </Button>
                </div>
              </div>

              {auditTrail && (
                <div className="border rounded-lg p-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">Complete Audit Trail</span>
                    <Badge className="bg-blue-100 text-blue-800">
                      {auditTrail.totalBlocks} Records
                    </Badge>
                  </div>

                  <div className="space-y-3">
                    {auditTrail.timeline?.map((record: AuditRecord, index: number) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4 py-2 bg-gray-50 rounded-r">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium">{record.action.replace(/_/g, ' ').toUpperCase()}</p>
                            <p className="text-sm text-gray-600">
                              {new Date(record.timestamp).toLocaleString()}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {record.verified ? (
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            ) : (
                              <AlertTriangle className="h-4 w-4 text-red-600" />
                            )}
                            <Badge variant="secondary" className="text-xs">
                              {record.blockHash.substring(0, 8)}...
                            </Badge>
                          </div>
                        </div>
                        {record.details && (
                          <div className="mt-2 text-sm text-gray-700">
                            <pre className="bg-white p-2 rounded border text-xs overflow-x-auto">
                              {JSON.stringify(record.details, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="signatures" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Fingerprint className="h-5 w-5" />
                <span>Digital Signature Verification</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Digital Signature Features:</h4>
                <ul className="space-y-1 text-sm text-blue-800">
                  <li>• SHA-256 cryptographic hashing</li>
                  <li>• Tamper-proof document verification</li>
                  <li>• Non-repudiation guarantee</li>
                  <li>• Legal compliance support</li>
                </ul>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button className="h-20 bg-green-600 hover:bg-green-700">
                  <div className="text-center">
                    <Key className="h-6 w-6 mx-auto mb-2" />
                    <span>Sign Document</span>
                  </div>
                </Button>
                <Button variant="outline" className="h-20">
                  <div className="text-center">
                    <Shield className="h-6 w-6 mx-auto mb-2" />
                    <span>Verify Signature</span>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contracts" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Award className="h-5 w-5" />
                <span>Smart Contract Management</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-medium text-purple-900 mb-2">Smart Contract Features:</h4>
                <ul className="space-y-1 text-sm text-purple-800">
                  <li>• Automated compliance checking</li>
                  <li>• Self-executing contract terms</li>
                  <li>• Transparent execution rules</li>
                  <li>• Automatic milestone tracking</li>
                </ul>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button className="h-20 bg-purple-600 hover:bg-purple-700">
                  <div className="text-center">
                    <Link className="h-6 w-6 mx-auto mb-2" />
                    <span>Create Contract</span>
                  </div>
                </Button>
                <Button variant="outline" className="h-20">
                  <div className="text-center">
                    <Eye className="h-6 w-6 mx-auto mb-2" />
                    <span>View Contracts</span>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}