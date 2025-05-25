import { useState } from "react";
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
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  PlusIcon,
  MoreVerticalIcon,
  MailIcon,
  CheckIcon,
  ClockIcon,
  AlertCircleIcon,
  FileTextIcon,
  UserIcon,
  SendIcon
} from "lucide-react";
import { format, formatDistance } from "date-fns";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface EmailNotification {
  id: number;
  recipientEmail: string;
  subject: string;
  body: string;
  status: string;
  createdAt: string;
  sentAt: string | null;
  tenderId: number | null;
  userId: number | null;
  taskId: number | null;
}

interface Tender {
  id: number;
  title: string;
}

interface Task {
  id: number;
  title: string;
}

interface User {
  id: number;
  name: string;
}

export default function EmailNotifications() {
  const { toast } = useToast();
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [showEmailDialog, setShowEmailDialog] = useState(false);
  const [newEmail, setNewEmail] = useState({
    recipientEmail: "",
    subject: "",
    body: "",
    tenderId: "",
    userId: "",
    taskId: ""
  });

  // Fetch email notifications
  const { data: emails = [], isLoading: emailsLoading, refetch: refetchEmails } = useQuery({
    queryKey: ['/api/email-notifications'],
    refetchInterval: false,
  });

  // Fetch tenders
  const { data: tenders = [], isLoading: tendersLoading } = useQuery({
    queryKey: ['/api/tenders'],
    refetchInterval: false,
  });

  // Fetch tasks
  const { data: tasks = [], isLoading: tasksLoading } = useQuery({
    queryKey: ['/api/tasks'],
    refetchInterval: false,
  });

  // Fetch users
  const { data: users = [], isLoading: usersLoading } = useQuery({
    queryKey: ['/api/users'],
    refetchInterval: false,
  });

  const handleCreateEmail = async () => {
    try {
      await apiRequest(
        'POST',
        '/api/email-notifications',
        {
          ...newEmail,
          tenderId: newEmail.tenderId ? parseInt(newEmail.tenderId) : null,
          userId: newEmail.userId ? parseInt(newEmail.userId) : null,
          taskId: newEmail.taskId ? parseInt(newEmail.taskId) : null
        }
      );
      
      // Reset form and close dialog
      setNewEmail({
        recipientEmail: "",
        subject: "",
        body: "",
        tenderId: "",
        userId: "",
        taskId: ""
      });
      setShowEmailDialog(false);
      
      // Success toast
      toast({
        title: "Email notification created",
        description: "The email has been created and queued for sending.",
      });
      
      // Refetch emails
      queryClient.invalidateQueries({ queryKey: ['/api/email-notifications'] });
    } catch (error) {
      console.error("Error creating email:", error);
      toast({
        variant: "destructive",
        title: "Failed to create email",
        description: "There was an error creating the email notification.",
      });
    }
  };

  const handleSendEmail = async (emailId: number) => {
    try {
      await apiRequest(
        'POST',
        `/api/email-notifications/${emailId}/send`,
        {}
      );
      
      // Success toast
      toast({
        title: "Email sent",
        description: "The email has been sent successfully.",
      });
      
      // Refetch emails
      queryClient.invalidateQueries({ queryKey: ['/api/email-notifications'] });
    } catch (error) {
      console.error("Error sending email:", error);
      toast({
        variant: "destructive",
        title: "Failed to send email",
        description: "There was an error sending the email. Please check your SendGrid API key configuration.",
      });
    }
  };

  const handleDeleteEmail = async (emailId: number) => {
    try {
      await apiRequest(
        'DELETE',
        `/api/email-notifications/${emailId}`,
        undefined
      );
      
      // Success toast
      toast({
        title: "Email deleted",
        description: "The email notification has been deleted.",
      });
      
      // Refetch emails
      queryClient.invalidateQueries({ queryKey: ['/api/email-notifications'] });
    } catch (error) {
      console.error("Error deleting email:", error);
      toast({
        variant: "destructive",
        title: "Failed to delete email",
        description: "There was an error deleting the email notification.",
      });
    }
  };

  const getFilteredEmails = () => {
    if (!emails) return [];
    
    return emails.filter((email: EmailNotification) => {
      // Apply status filter
      if (statusFilter && email.status !== statusFilter) return false;
      
      return true;
    });
  };

  const getUserName = (userId: number | null) => {
    if (!userId || !users) return null;
    const user = users.find((u: User) => u.id === userId);
    return user ? user.name : null;
  };

  const getTenderTitle = (tenderId: number | null) => {
    if (!tenderId || !tenders) return null;
    const tender = tenders.find((t: Tender) => t.id === tenderId);
    return tender ? tender.title : null;
  };

  const getTaskTitle = (taskId: number | null) => {
    if (!taskId || !tasks) return null;
    const task = tasks.find((t: Task) => t.id === taskId);
    return task ? task.title : null;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "Sent":
        return (
          <Badge variant="outline" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
            <CheckIcon className="h-3 w-3 mr-1" />
            Sent
          </Badge>
        );
      case "Pending":
        return (
          <Badge variant="outline" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">
            <ClockIcon className="h-3 w-3 mr-1" />
            Pending
          </Badge>
        );
      case "Failed":
        return (
          <Badge variant="outline" className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300">
            <AlertCircleIcon className="h-3 w-3 mr-1" />
            Failed
          </Badge>
        );
      default:
        return (
          <Badge variant="outline">
            {status}
          </Badge>
        );
    }
  };

  const getTimeAgo = (date: string) => {
    return formatDistance(new Date(date), new Date(), { addSuffix: true });
  };

  if (emailsLoading || tendersLoading || tasksLoading || usersLoading) {
    return <div className="p-8">Loading email notifications...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Email Notifications</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Manage and track communications with clients and team members
          </p>
        </div>
        <Button onClick={() => setShowEmailDialog(true)}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Create Email
        </Button>
      </div>
      
      <Tabs defaultValue="all">
        <TabsList className="mb-6">
          <TabsTrigger value="all" onClick={() => setStatusFilter(null)}>All</TabsTrigger>
          <TabsTrigger value="pending" onClick={() => setStatusFilter("Pending")}>Pending</TabsTrigger>
          <TabsTrigger value="sent" onClick={() => setStatusFilter("Sent")}>Sent</TabsTrigger>
          <TabsTrigger value="failed" onClick={() => setStatusFilter("Failed")}>Failed</TabsTrigger>
        </TabsList>
        
        <TabsContent value="all">
          <div className="grid grid-cols-1 gap-4">
            {getFilteredEmails().map((email: EmailNotification) => (
              <EmailCard 
                key={email.id} 
                email={email} 
                getTenderTitle={getTenderTitle}
                getUserName={getUserName}
                getTaskTitle={getTaskTitle}
                getStatusBadge={getStatusBadge}
                getTimeAgo={getTimeAgo}
                onSend={handleSendEmail}
                onDelete={handleDeleteEmail}
              />
            ))}
            
            {getFilteredEmails().length === 0 && (
              <div className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <MailIcon className="h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-xl font-medium mb-2">No email notifications found</h3>
                <p className="text-gray-500 text-center mb-4">
                  {statusFilter
                    ? `No ${statusFilter.toLowerCase()} emails found. Try a different filter.`
                    : "Create your first email notification to get started"}
                </p>
                <Button onClick={() => setShowEmailDialog(true)}>
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Create Email
                </Button>
              </div>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="pending">
          <div className="grid grid-cols-1 gap-4">
            {getFilteredEmails().length === 0 && (
              <div className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <ClockIcon className="h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-xl font-medium mb-2">No pending emails</h3>
                <p className="text-gray-500 text-center mb-4">
                  There are no emails waiting to be sent
                </p>
              </div>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="sent">
          <div className="grid grid-cols-1 gap-4">
            {getFilteredEmails().length === 0 && (
              <div className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <CheckIcon className="h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-xl font-medium mb-2">No sent emails</h3>
                <p className="text-gray-500 text-center mb-4">
                  No emails have been sent yet
                </p>
              </div>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="failed">
          <div className="grid grid-cols-1 gap-4">
            {getFilteredEmails().length === 0 && (
              <div className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <AlertCircleIcon className="h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-xl font-medium mb-2">No failed emails</h3>
                <p className="text-gray-500 text-center mb-4">
                  No emails have failed to send
                </p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
      
      {/* New Email Dialog */}
      <Dialog open={showEmailDialog} onOpenChange={setShowEmailDialog}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Create New Email</DialogTitle>
            <DialogDescription>
              Compose your email and set delivery options. The email will be queued for sending.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="recipientEmail">Recipient Email</Label>
              <Input
                id="recipientEmail"
                type="email"
                value={newEmail.recipientEmail}
                onChange={(e) => setNewEmail({...newEmail, recipientEmail: e.target.value})}
                placeholder="recipient@example.com"
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="subject">Subject</Label>
              <Input
                id="subject"
                value={newEmail.subject}
                onChange={(e) => setNewEmail({...newEmail, subject: e.target.value})}
                placeholder="Enter email subject"
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="body">Email Body</Label>
              <Textarea
                id="body"
                rows={8}
                value={newEmail.body}
                onChange={(e) => setNewEmail({...newEmail, body: e.target.value})}
                placeholder="Enter email content..."
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="tenderId">Related Tender</Label>
                <Select
                  value={newEmail.tenderId}
                  onValueChange={(value) => setNewEmail({...newEmail, tenderId: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select tender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {tenders && tenders.map((tender: Tender) => (
                      <SelectItem key={tender.id} value={tender.id.toString()}>
                        {tender.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="userId">Related User</Label>
                <Select
                  value={newEmail.userId}
                  onValueChange={(value) => setNewEmail({...newEmail, userId: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select user" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {users && users.map((user: User) => (
                      <SelectItem key={user.id} value={user.id.toString()}>
                        {user.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="taskId">Related Task</Label>
                <Select
                  value={newEmail.taskId}
                  onValueChange={(value) => setNewEmail({...newEmail, taskId: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select task" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {tasks && tasks.map((task: Task) => (
                      <SelectItem key={task.id} value={task.id.toString()}>
                        {task.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button type="submit" onClick={handleCreateEmail}>
              Create Email
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Email Card Component
function EmailCard({
  email,
  getTenderTitle,
  getUserName,
  getTaskTitle,
  getStatusBadge,
  getTimeAgo,
  onSend,
  onDelete
}: {
  email: EmailNotification;
  getTenderTitle: (id: number | null) => string | null;
  getUserName: (id: number | null) => string | null;
  getTaskTitle: (id: number | null) => string | null;
  getStatusBadge: (status: string) => React.ReactNode;
  getTimeAgo: (date: string) => string;
  onSend: (id: number) => void;
  onDelete: (id: number) => void;
}) {
  const [showBody, setShowBody] = useState(false);
  
  return (
    <Card className="mb-4">
      <CardHeader className="pb-2 flex flex-row items-start justify-between">
        <div>
          <CardTitle className="text-lg font-medium">
            {email.subject}
          </CardTitle>
          <CardDescription>
            To: {email.recipientEmail}
          </CardDescription>
        </div>
        
        <div className="flex items-center gap-2">
          {getStatusBadge(email.status)}
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreVerticalIcon className="h-4 w-4" />
                <span className="sr-only">Email options</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {email.status === "Pending" && (
                <DropdownMenuItem onClick={() => onSend(email.id)}>
                  <SendIcon className="h-4 w-4 mr-2" />
                  Send Now
                </DropdownMenuItem>
              )}
              <DropdownMenuItem onClick={() => onDelete(email.id)}>
                Delete Email
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="flex flex-wrap gap-2 mb-3">
          {email.tenderId && (
            <Badge variant="outline" className="flex items-center gap-1">
              <FileTextIcon className="h-3 w-3" />
              {getTenderTitle(email.tenderId)}
            </Badge>
          )}
          
          {email.userId && (
            <Badge variant="outline" className="flex items-center gap-1">
              <UserIcon className="h-3 w-3" />
              {getUserName(email.userId)}
            </Badge>
          )}
          
          {email.taskId && (
            <Badge variant="outline" className="flex items-center gap-1">
              <ClockIcon className="h-3 w-3" />
              {getTaskTitle(email.taskId)}
            </Badge>
          )}
        </div>
        
        <div className="text-sm text-gray-500 dark:text-gray-400 mb-3">
          {email.status === "Sent"
            ? `Sent ${getTimeAgo(email.sentAt || email.createdAt)}`
            : `Created ${getTimeAgo(email.createdAt)}`}
        </div>
        
        {showBody && (
          <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-md whitespace-pre-wrap">
            {email.body}
          </div>
        )}
      </CardContent>
      
      <CardFooter className="pt-0 justify-between">
        <Button variant="ghost" size="sm" onClick={() => setShowBody(!showBody)}>
          {showBody ? "Hide Content" : "Show Content"}
        </Button>
        
        {email.status === "Pending" && (
          <Button size="sm" onClick={() => onSend(email.id)}>
            <SendIcon className="h-4 w-4 mr-2" />
            Send Now
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}