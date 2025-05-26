import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { CalendarIcon, Upload, Building, Users, Shield, Star, Phone, Mail, Globe } from "lucide-react";
import { format } from "date-fns";
import { insertFirmSchema } from "@shared/schema";
import { z } from "zod";

const formSchema = insertFirmSchema.extend({
  establishedDate: z.date().optional(),
  registrationDate: z.date().optional(),
  lastAuditDate: z.date().optional(),
  certificationExpiryDate: z.date().optional(),
  annualTurnover: z.string().optional(),
  employeeCount: z.string().optional(),
  branchCount: z.string().optional(),
  website: z.string().optional(),
  primaryContact: z.string().optional(),
  secondaryContact: z.string().optional(),
  emailAddress: z.string().optional(),
  alternateEmail: z.string().optional(),
  registrationNumber: z.string().optional(),
  panNumber: z.string().optional(),
  gstNumber: z.string().optional(),
  cinNumber: z.string().optional(),
  bankName: z.string().optional(),
  accountNumber: z.string().optional(),
  ifscCode: z.string().optional(),
  swiftCode: z.string().optional(),
  certifications: z.string().optional(),
  awards: z.string().optional(),
  keyPersonnel: z.string().optional(),
  businessDescription: z.string().optional(),
  coreCompetencies: z.string().optional(),
  pastProjects: z.string().optional(),
  clientReferences: z.string().optional(),
  riskAssessment: z.string().optional(),
  complianceNotes: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

interface FirmFormProps {
  onClose: () => void;
}

export function FirmForm({ onClose }: FirmFormProps) {
  const [selectedTab, setSelectedTab] = useState("basic");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      description: "",
      location: "",
      contactPerson: "",
      rating: 0,
      status: "Active",
      complianceStatus: "Pending",
      riskLevel: "Low",
      verified: false,
      paymentTerms: 30,
    },
  });

  const createFirmMutation = useMutation({
    mutationFn: async (data: FormData) => {
      const response = await fetch('/api/firms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to create firm');
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Success!",
        description: "New firm created successfully",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/firms'] });
      onClose();
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: FormData) => {
    createFirmMutation.mutate(data);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      toast({
        title: "File Uploaded",
        description: `${file.name} uploaded successfully`,
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-t-lg">
          <div className="flex items-center space-x-3">
            <Building className="h-6 w-6" />
            <div>
              <h2 className="text-2xl font-bold">New Firm & Vendor Profile</h2>
              <p className="text-green-100">Create comprehensive firm record</p>
            </div>
          </div>
          <Button 
            variant="ghost" 
            onClick={onClose}
            className="text-white hover:bg-white/20"
          >
            ✕
          </Button>
        </div>

        <form onSubmit={form.handleSubmit(onSubmit)} className="p-6">
          {/* Firm Name */}
          <div className="mb-6">
            <Label htmlFor="name" className="text-lg font-semibold text-gray-700">
              Firm/Company Name
            </Label>
            <Input
              id="name"
              {...form.register("name")}
              placeholder="Enter firm name..."
              className="mt-2 text-lg h-12"
            />
          </div>

          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="basic">BASIC INFORMATION</TabsTrigger>
              <TabsTrigger value="legal">LEGAL & COMPLIANCE</TabsTrigger>
              <TabsTrigger value="financial">FINANCIAL DETAILS</TabsTrigger>
              <TabsTrigger value="assessment">CAPABILITY ASSESSMENT</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center space-x-2">
                      <Building className="h-5 w-5" />
                      <span>Company Information</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="description">Company Description</Label>
                      <Textarea
                        id="description"
                        {...form.register("description")}
                        placeholder="Brief company description..."
                        className="mt-1"
                        rows={3}
                      />
                    </div>

                    <div>
                      <Label htmlFor="businessDescription">Business Description</Label>
                      <Textarea
                        id="businessDescription"
                        {...form.register("businessDescription")}
                        placeholder="Detailed business description..."
                        className="mt-1"
                        rows={3}
                      />
                    </div>

                    <div>
                      <Label htmlFor="location">Primary Location</Label>
                      <Input
                        id="location"
                        {...form.register("location")}
                        placeholder="Head office location"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="establishedDate">Established Date</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full mt-1 justify-start text-left font-normal"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            Select establishment date
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                          <Calendar mode="single" />
                        </PopoverContent>
                      </Popover>
                    </div>

                    <div>
                      <Label htmlFor="employeeCount">Employee Count</Label>
                      <Input
                        id="employeeCount"
                        {...form.register("employeeCount")}
                        placeholder="Number of employees"
                        className="mt-1"
                        type="number"
                      />
                    </div>

                    <div>
                      <Label htmlFor="branchCount">Branch/Office Count</Label>
                      <Input
                        id="branchCount"
                        {...form.register("branchCount")}
                        placeholder="Number of branches"
                        className="mt-1"
                        type="number"
                      />
                    </div>

                    <div>
                      <Label htmlFor="website">Website</Label>
                      <Input
                        id="website"
                        {...form.register("website")}
                        placeholder="https://company-website.com"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="coreCompetencies">Core Competencies</Label>
                      <Textarea
                        id="coreCompetencies"
                        {...form.register("coreCompetencies")}
                        placeholder="List of core competencies..."
                        className="mt-1"
                        rows={3}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center space-x-2">
                      <Users className="h-5 w-5" />
                      <span>Contact Information</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="contactPerson">Primary Contact Person</Label>
                      <Input
                        id="contactPerson"
                        {...form.register("contactPerson")}
                        placeholder="Contact person name"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="primaryContact">Primary Phone</Label>
                      <Input
                        id="primaryContact"
                        {...form.register("primaryContact")}
                        placeholder="+91 XXXXX XXXXX"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="secondaryContact">Secondary Phone</Label>
                      <Input
                        id="secondaryContact"
                        {...form.register("secondaryContact")}
                        placeholder="+91 XXXXX XXXXX"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="emailAddress">Primary Email</Label>
                      <Input
                        id="emailAddress"
                        {...form.register("emailAddress")}
                        placeholder="contact@company.com"
                        className="mt-1"
                        type="email"
                      />
                    </div>

                    <div>
                      <Label htmlFor="alternateEmail">Alternate Email</Label>
                      <Input
                        id="alternateEmail"
                        {...form.register("alternateEmail")}
                        placeholder="alternate@company.com"
                        className="mt-1"
                        type="email"
                      />
                    </div>

                    <div>
                      <Label htmlFor="keyPersonnel">Key Personnel</Label>
                      <Textarea
                        id="keyPersonnel"
                        {...form.register("keyPersonnel")}
                        placeholder="List key personnel with designations..."
                        className="mt-1"
                        rows={4}
                      />
                    </div>

                    <div>
                      <Label>Company Logo/Document</Label>
                      <div className="mt-1">
                        <input
                          type="file"
                          onChange={handleFileUpload}
                          className="hidden"
                          id="file-upload"
                          accept=".pdf,.doc,.docx,.jpg,.png"
                        />
                        <label htmlFor="file-upload">
                          <Button variant="outline" className="w-full cursor-pointer" type="button">
                            <Upload className="mr-2 h-4 w-4" />
                            Upload company documents
                          </Button>
                        </label>
                        {uploadedFile && (
                          <p className="text-sm text-green-600 mt-2">
                            ✓ {uploadedFile.name}
                          </p>
                        )}
                      </div>
                    </div>

                    <div>
                      <Label>Company Rating</Label>
                      <div className="flex items-center mt-2">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className="h-5 w-5 text-yellow-400 fill-current cursor-pointer"
                            onClick={() => form.setValue("rating", star)}
                          />
                        ))}
                        <span className="ml-2 text-sm text-gray-600">
                          {form.watch("rating")}/5
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="legal" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center space-x-2">
                      <Shield className="h-5 w-5" />
                      <span>Legal Registration</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="registrationNumber">Company Registration Number</Label>
                      <Input
                        id="registrationNumber"
                        {...form.register("registrationNumber")}
                        placeholder="Registration number"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="registrationDate">Registration Date</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full mt-1 justify-start text-left font-normal"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            Select registration date
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                          <Calendar mode="single" />
                        </PopoverContent>
                      </Popover>
                    </div>

                    <div>
                      <Label htmlFor="panNumber">PAN Number</Label>
                      <Input
                        id="panNumber"
                        {...form.register("panNumber")}
                        placeholder="ABCDE1234F"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="gstNumber">GST Number</Label>
                      <Input
                        id="gstNumber"
                        {...form.register("gstNumber")}
                        placeholder="GST registration number"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="cinNumber">CIN Number</Label>
                      <Input
                        id="cinNumber"
                        {...form.register("cinNumber")}
                        placeholder="Corporate Identification Number"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="status">Company Status</Label>
                      <Select onValueChange={(value) => form.setValue("status", value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Active">Active</SelectItem>
                          <SelectItem value="Inactive">Inactive</SelectItem>
                          <SelectItem value="Suspended">Suspended</SelectItem>
                          <SelectItem value="Under Review">Under Review</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center space-x-2">
                      <Shield className="h-5 w-5" />
                      <span>Compliance & Certifications</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="complianceStatus">Compliance Status</Label>
                      <Select onValueChange={(value) => form.setValue("complianceStatus", value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select compliance status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Compliant">Compliant</SelectItem>
                          <SelectItem value="Pending">Pending</SelectItem>
                          <SelectItem value="Non-Compliant">Non-Compliant</SelectItem>
                          <SelectItem value="Under Review">Under Review</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="certifications">Certifications & Licenses</Label>
                      <Textarea
                        id="certifications"
                        {...form.register("certifications")}
                        placeholder="List all certifications (ISO, etc.)..."
                        className="mt-1"
                        rows={3}
                      />
                    </div>

                    <div>
                      <Label htmlFor="certificationExpiryDate">Certification Expiry Date</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full mt-1 justify-start text-left font-normal"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            Select expiry date
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                          <Calendar mode="single" />
                        </PopoverContent>
                      </Popover>
                    </div>

                    <div>
                      <Label htmlFor="awards">Awards & Recognition</Label>
                      <Textarea
                        id="awards"
                        {...form.register("awards")}
                        placeholder="List awards and recognition..."
                        className="mt-1"
                        rows={3}
                      />
                    </div>

                    <div>
                      <Label htmlFor="complianceNotes">Compliance Notes</Label>
                      <Textarea
                        id="complianceNotes"
                        {...form.register("complianceNotes")}
                        placeholder="Additional compliance notes..."
                        className="mt-1"
                        rows={3}
                      />
                    </div>

                    <div className="flex items-center space-x-2">
                      <Checkbox 
                        checked={form.watch("verified")}
                        onCheckedChange={(checked) => form.setValue("verified", !!checked)}
                      />
                      <Label className="text-sm">Firm is verified and approved</Label>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="financial" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Financial Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="annualTurnover">Annual Turnover (₹)</Label>
                      <Input
                        id="annualTurnover"
                        {...form.register("annualTurnover")}
                        placeholder="Annual turnover amount"
                        className="mt-1"
                        type="number"
                      />
                    </div>

                    <div>
                      <Label htmlFor="paymentTerms">Payment Terms (Days)</Label>
                      <Input
                        {...form.register("paymentTerms", { valueAsNumber: true })}
                        placeholder="Payment terms in days"
                        className="mt-1"
                        type="number"
                      />
                    </div>

                    <div>
                      <Label htmlFor="lastAuditDate">Last Audit Date</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full mt-1 justify-start text-left font-normal"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            Select audit date
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                          <Calendar mode="single" />
                        </PopoverContent>
                      </Popover>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Banking Details</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="bankName">Bank Name</Label>
                      <Input
                        id="bankName"
                        {...form.register("bankName")}
                        placeholder="Primary bank name"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="accountNumber">Account Number</Label>
                      <Input
                        id="accountNumber"
                        {...form.register("accountNumber")}
                        placeholder="Bank account number"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="ifscCode">IFSC Code</Label>
                      <Input
                        id="ifscCode"
                        {...form.register("ifscCode")}
                        placeholder="IFSC code"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="swiftCode">SWIFT Code (if applicable)</Label>
                      <Input
                        id="swiftCode"
                        {...form.register("swiftCode")}
                        placeholder="SWIFT code for international"
                        className="mt-1"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="assessment" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Capability Assessment</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="riskLevel">Risk Level</Label>
                      <Select onValueChange={(value) => form.setValue("riskLevel", value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select risk level" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Low">Low Risk</SelectItem>
                          <SelectItem value="Medium">Medium Risk</SelectItem>
                          <SelectItem value="High">High Risk</SelectItem>
                          <SelectItem value="Critical">Critical Risk</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="pastProjects">Past Projects & Experience</Label>
                    <Textarea
                      id="pastProjects"
                      {...form.register("pastProjects")}
                      placeholder="Detail past projects and experience..."
                      className="mt-1"
                      rows={4}
                    />
                  </div>

                  <div>
                    <Label htmlFor="clientReferences">Client References</Label>
                    <Textarea
                      id="clientReferences"
                      {...form.register("clientReferences")}
                      placeholder="Previous client references..."
                      className="mt-1"
                      rows={4}
                    />
                  </div>

                  <div>
                    <Label htmlFor="riskAssessment">Risk Assessment Notes</Label>
                    <Textarea
                      id="riskAssessment"
                      {...form.register("riskAssessment")}
                      placeholder="Risk assessment details..."
                      className="mt-1"
                      rows={4}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          <div className="flex justify-end space-x-4 mt-8 pt-6 border-t">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={createFirmMutation.isPending}
              className="bg-green-600 hover:bg-green-700"
            >
              {createFirmMutation.isPending ? "Creating..." : "Create Firm"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}