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
import { CalendarIcon, Upload, FileText, Clock, Star, Building } from "lucide-react";
import { format } from "date-fns";
import { insertTenderSchema } from "@shared/schema";
import { z } from "zod";

const formSchema = insertTenderSchema.extend({
  estimateValue: z.string().optional(),
  emdAmount: z.string().optional(),
  feesAmount: z.string().optional(),
  startDate: z.date().optional(),
  endDate: z.date().optional(),
  preBidMeetingDate: z.date().optional(),
  preBidMeetingTime: z.string().optional(),
  meetingLink: z.string().optional(),
  hardcopyRequirement: z.string().optional(),
  eligibilityRemark: z.string().optional(),
  remarkNotes: z.string().optional(),
  approverName: z.string().optional(),
  submissionRemark: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

interface TenderFormProps {
  onClose: () => void;
}

export function TenderForm({ onClose }: TenderFormProps) {
  const [selectedTab, setSelectedTab] = useState("details");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      departmentName: "",
      organization: "",
      description: "",
      tenderType: "Open",
      value: "",
      status: "Draft",
      submissionMethod: "Online",
      tenderSourcePortal: "Manual",
      tenderClassification: "Goods",
      emdRequired: false,
      affidavitRequired: false,
      preBidAttended: false,
      corrigendumIssued: false,
      workOrderReceived: false,
      agreementSigned: false,
      invoiceRaised: false,
      paymentReceived: false,
      recoveryLegalStatus: "Normal",
    },
  });

  const createTenderMutation = useMutation({
    mutationFn: async (data: FormData) => {
      const response = await fetch('/api/tenders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to create tender');
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Success!",
        description: "New tender created successfully",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/tenders'] });
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
    createTenderMutation.mutate(data);
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
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
          <div className="flex items-center space-x-3">
            <FileText className="h-6 w-6" />
            <div>
              <h2 className="text-2xl font-bold">New Tender & Bid Tracker</h2>
              <p className="text-blue-100">Create comprehensive tender record</p>
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
          {/* Tender Name */}
          <div className="mb-6">
            <Label htmlFor="title" className="text-lg font-semibold text-gray-700">
              Tender Name
            </Label>
            <Input
              id="title"
              {...form.register("title")}
              placeholder="Enter tender name..."
              className="mt-2 text-lg h-12"
            />
          </div>

          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="details">BID/TENDER DETAILS</TabsTrigger>
              <TabsTrigger value="additional">ADDITIONAL INFORMATION</TabsTrigger>
              <TabsTrigger value="criteria">CRITERIA EVALUATION</TabsTrigger>
              <TabsTrigger value="approval">APPROVAL DETAILS</TabsTrigger>
            </TabsList>

            <TabsContent value="details" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center space-x-2">
                      <Building className="h-5 w-5" />
                      <span>Basic Information</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="description">Description</Label>
                      <Textarea
                        id="description"
                        {...form.register("description")}
                        placeholder="Tender description..."
                        className="mt-1"
                        rows={3}
                      />
                    </div>

                    <div>
                      <Label htmlFor="tenderClassification">Enquiry Type</Label>
                      <Select onValueChange={(value) => form.setValue("tenderClassification", value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select enquiry type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Goods">Goods</SelectItem>
                          <SelectItem value="Services">Services</SelectItem>
                          <SelectItem value="Works">Works</SelectItem>
                          <SelectItem value="Consultancy">Consultancy</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="organization">Contact</Label>
                      <Input
                        id="organization"
                        {...form.register("organization")}
                        placeholder="Contact person/organization"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="departmentName">Phone</Label>
                      <Input
                        id="departmentName"
                        {...form.register("departmentName")}
                        placeholder="Phone number"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label>Email</Label>
                      <Input
                        placeholder="Email address"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label>Start Date</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full mt-1 justify-start text-left font-normal"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            Select start date
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                          <Calendar mode="single" />
                        </PopoverContent>
                      </Popover>
                    </div>

                    <div>
                      <Label>End Date & Time</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full mt-1 justify-start text-left font-normal"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            Select end date
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                          <Calendar mode="single" />
                        </PopoverContent>
                      </Popover>
                    </div>

                    <div>
                      <Label>Document</Label>
                      <div className="mt-1">
                        <input
                          type="file"
                          onChange={handleFileUpload}
                          className="hidden"
                          id="file-upload"
                          accept=".pdf,.doc,.docx,.xls,.xlsx"
                        />
                        <label htmlFor="file-upload">
                          <Button variant="outline" className="w-full cursor-pointer" type="button">
                            <Upload className="mr-2 h-4 w-4" />
                            Upload your file
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
                      <Label>Responsible</Label>
                      <Input
                        placeholder="Responsible person"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label>Company</Label>
                      <Input
                        defaultValue="AYF CREATIVE BRAND CONSULTANCY PRIVATE LIMITED"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label>Priority</Label>
                      <div className="flex items-center mt-2">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className="h-5 w-5 text-yellow-400 fill-current cursor-pointer"
                          />
                        ))}
                      </div>
                    </div>

                    <div>
                      <Label>Tags</Label>
                      <div className="mt-2 flex flex-wrap gap-2">
                        <Badge variant="secondary">New</Badge>
                        <Badge variant="secondary">High Priority</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center space-x-2">
                      <Clock className="h-5 w-5" />
                      <span>Financial Details</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="estimateValue">Estimate Value</Label>
                      <Input
                        id="estimateValue"
                        {...form.register("estimateValue")}
                        placeholder="0.00"
                        className="mt-1"
                        type="number"
                        step="0.01"
                      />
                    </div>

                    <div>
                      <Label>Requirement of EMD</Label>
                      <div className="mt-2 flex items-center space-x-2">
                        <Checkbox 
                          checked={form.watch("emdRequired")}
                          onCheckedChange={(checked) => form.setValue("emdRequired", !!checked)}
                        />
                        <span className="text-sm">EMD Required</span>
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="emdAmount">EMD Amount</Label>
                      <Input
                        id="emdAmount"
                        {...form.register("emdAmount")}
                        placeholder="0.00"
                        className="mt-1"
                        type="number"
                        step="0.01"
                      />
                    </div>

                    <div>
                      <Label htmlFor="feesAmount">Fees Amount</Label>
                      <Input
                        id="feesAmount"
                        {...form.register("feesAmount")}
                        placeholder="0.00"
                        className="mt-1"
                        type="number"
                        step="0.01"
                      />
                    </div>

                    <div>
                      <Label>Form of EMD</Label>
                      <Select>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select EMD form" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="bank-guarantee">Bank Guarantee</SelectItem>
                          <SelectItem value="fixed-deposit">Fixed Deposit</SelectItem>
                          <SelectItem value="online-payment">Online Payment</SelectItem>
                          <SelectItem value="msme-exemption">MSME Exemption</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>EMD in Favour of</Label>
                      <Input
                        placeholder="Beneficiary name"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label>Stamp Paper Require</Label>
                      <div className="mt-2 flex items-center space-x-2">
                        <Checkbox />
                        <span className="text-sm">Required</span>
                      </div>
                    </div>

                    <div>
                      <Label>Number of Stamp</Label>
                      <Input
                        placeholder="0"
                        className="mt-1"
                        type="number"
                      />
                    </div>

                    <div>
                      <Label>Pre-Bid Meeting</Label>
                      <div className="mt-2 flex items-center space-x-2">
                        <Checkbox 
                          checked={form.watch("preBidAttended")}
                          onCheckedChange={(checked) => form.setValue("preBidAttended", !!checked)}
                        />
                        <span className="text-sm">Meeting Required</span>
                      </div>
                    </div>

                    <div>
                      <Label>Pre-Bid Meeting Date</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full mt-1 justify-start text-left font-normal"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            Select meeting date
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                          <Calendar mode="single" />
                        </PopoverContent>
                      </Popover>
                    </div>

                    <div>
                      <Label htmlFor="meetingLink">Meeting Link</Label>
                      <Input
                        id="meetingLink"
                        {...form.register("meetingLink")}
                        placeholder="Meeting link URL"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="hardcopyRequirement">Hardcopy Requirement</Label>
                      <Textarea
                        id="hardcopyRequirement"
                        {...form.register("hardcopyRequirement")}
                        placeholder="Hardcopy requirements..."
                        className="mt-1"
                        rows={2}
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="additional" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Additional Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="tenderSourcePortal">Tender Source Portal</Label>
                      <Select onValueChange={(value) => form.setValue("tenderSourcePortal", value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select source portal" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="GeM">GeM Portal</SelectItem>
                          <SelectItem value="CPPP">CPPP Portal</SelectItem>
                          <SelectItem value="eProc">eProc Portal</SelectItem>
                          <SelectItem value="TenderTiger">TenderTiger</SelectItem>
                          <SelectItem value="Manual">Manual Entry</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="submissionMethod">Submission Method</Label>
                      <Select onValueChange={(value) => form.setValue("submissionMethod", value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select submission method" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Online">Online</SelectItem>
                          <SelectItem value="Offline">Offline</SelectItem>
                          <SelectItem value="Email">Email</SelectItem>
                          <SelectItem value="Hand Delivery">Hand Delivery</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="postBidRequirement">Post-Bid Requirement</Label>
                      <Input
                        id="postBidRequirement"
                        {...form.register("postBidRequirement")}
                        placeholder="Post-bid requirements"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="consortiumPartner">Consortium Partner</Label>
                      <Input
                        id="consortiumPartner"
                        {...form.register("consortiumPartner")}
                        placeholder="Consortium partner details"
                        className="mt-1"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="bidClarificationNotes">Bid Clarification Notes</Label>
                    <Textarea
                      id="bidClarificationNotes"
                      {...form.register("bidClarificationNotes")}
                      placeholder="Any clarifications or notes..."
                      className="mt-1"
                      rows={3}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="criteria" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Criteria Evaluation</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="eligibilityRemark">Eligibility Remark</Label>
                    <Textarea
                      id="eligibilityRemark"
                      {...form.register("eligibilityRemark")}
                      placeholder="Eligibility criteria and remarks..."
                      className="mt-1"
                      rows={4}
                    />
                  </div>

                  <div>
                    <Label htmlFor="remarkNotes">Remark Notes</Label>
                    <Textarea
                      id="remarkNotes"
                      {...form.register("remarkNotes")}
                      placeholder="Additional remarks and notes..."
                      className="mt-1"
                      rows={4}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="approval" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Approval Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="approverName">Approver Name</Label>
                      <Input
                        id="approverName"
                        {...form.register("approverName")}
                        placeholder="Approver name"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="status">Status</Label>
                      <Select onValueChange={(value) => form.setValue("status", value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Draft">Draft</SelectItem>
                          <SelectItem value="Submitted">Submitted</SelectItem>
                          <SelectItem value="Under Review">Under Review</SelectItem>
                          <SelectItem value="Approved">Approved</SelectItem>
                          <SelectItem value="Rejected">Rejected</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="submissionRemark">Submission Remark</Label>
                    <Textarea
                      id="submissionRemark"
                      {...form.register("submissionRemark")}
                      placeholder="Submission remarks and final notes..."
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
              disabled={createTenderMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {createTenderMutation.isPending ? "Creating..." : "Create Tender"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}