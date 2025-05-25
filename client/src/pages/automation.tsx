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
import { Switch } from "@/components/ui/switch";
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
import {
  PlusIcon,
  MoreVerticalIcon,
  BotIcon,
  ZapIcon,
  ActivityIcon,
  AlertTriangleIcon,
  CheckIcon,
  ClockIcon,
  MailIcon,
  CalendarIcon,
  BellIcon
} from "lucide-react";
import { format } from "date-fns";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface AutomationRule {
  id: number;
  name: string;
  description: string | null;
  triggerType: string;
  triggerValue: string | null;
  actionType: string;
  actionParams: string;
  enabled: boolean;
  createdAt: string;
}

export default function Automation() {
  const { toast } = useToast();
  const [showRuleDialog, setShowRuleDialog] = useState(false);
  const [newRule, setNewRule] = useState({
    name: "",
    description: "",
    triggerType: "deadline_approaching",
    triggerValue: "3",
    actionType: "email_notification",
    actionParams: "",
    enabled: true
  });

  // Fetch automation rules
  const { data: rules = [], isLoading: rulesLoading } = useQuery({
    queryKey: ['/api/automation-rules'],
    refetchInterval: false,
  });

  const handleCreateRule = async () => {
    try {
      await apiRequest('/api/automation-rules', {
        method: 'POST',
        data: newRule
      });
      
      // Reset form and close dialog
      setNewRule({
        name: "",
        description: "",
        triggerType: "deadline_approaching",
        triggerValue: "3",
        actionType: "email_notification",
        actionParams: "",
        enabled: true
      });
      setShowRuleDialog(false);
      
      // Success toast
      toast({
        title: "Automation rule created",
        description: "The rule has been created and is now active.",
      });
      
      // Refetch rules
      queryClient.invalidateQueries({ queryKey: ['/api/automation-rules'] });
    } catch (error) {
      console.error("Error creating automation rule:", error);
      toast({
        variant: "destructive",
        title: "Failed to create rule",
        description: "There was an error creating the automation rule.",
      });
    }
  };

  const handleToggleRule = async (ruleId: number, enabled: boolean) => {
    try {
      await apiRequest(`/api/automation-rules/${ruleId}/toggle`, {
        method: 'POST',
        data: { enabled }
      });
      
      // Success toast
      toast({
        title: enabled ? "Rule enabled" : "Rule disabled",
        description: enabled 
          ? "The automation rule is now active" 
          : "The automation rule has been disabled",
      });
      
      // Refetch rules
      queryClient.invalidateQueries({ queryKey: ['/api/automation-rules'] });
    } catch (error) {
      console.error("Error toggling automation rule:", error);
      toast({
        variant: "destructive",
        title: "Failed to update rule",
        description: "There was an error updating the automation rule status.",
      });
    }
  };

  const handleDeleteRule = async (ruleId: number) => {
    try {
      await apiRequest(`/api/automation-rules/${ruleId}`, {
        method: 'DELETE'
      });
      
      // Success toast
      toast({
        title: "Rule deleted",
        description: "The automation rule has been deleted.",
      });
      
      // Refetch rules
      queryClient.invalidateQueries({ queryKey: ['/api/automation-rules'] });
    } catch (error) {
      console.error("Error deleting automation rule:", error);
      toast({
        variant: "destructive",
        title: "Failed to delete rule",
        description: "There was an error deleting the automation rule.",
      });
    }
  };

  const getTriggerTypeLabel = (triggerType: string) => {
    switch (triggerType) {
      case "deadline_approaching":
        return "Deadline Approaching";
      case "status_change":
        return "Status Changed";
      case "new_tender":
        return "New Tender Created";
      case "risk_score_change":
        return "Risk Score Changed";
      case "document_uploaded":
        return "Document Uploaded";
      default:
        return triggerType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  };

  const getActionTypeLabel = (actionType: string) => {
    switch (actionType) {
      case "email_notification":
        return "Send Email";
      case "create_task":
        return "Create Task";
      case "create_calendar_event":
        return "Create Calendar Event";
      case "update_tender_status":
        return "Update Tender Status";
      case "set_reminder":
        return "Set Reminder";
      default:
        return actionType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  };

  const getTriggerIcon = (triggerType: string) => {
    switch (triggerType) {
      case "deadline_approaching":
        return <ClockIcon className="h-5 w-5" />;
      case "status_change":
        return <ActivityIcon className="h-5 w-5" />;
      case "new_tender":
        return <PlusIcon className="h-5 w-5" />;
      case "risk_score_change":
        return <AlertTriangleIcon className="h-5 w-5" />;
      case "document_uploaded":
        return <CheckIcon className="h-5 w-5" />;
      default:
        return <ZapIcon className="h-5 w-5" />;
    }
  };

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case "email_notification":
        return <MailIcon className="h-5 w-5" />;
      case "create_task":
        return <CheckIcon className="h-5 w-5" />;
      case "create_calendar_event":
        return <CalendarIcon className="h-5 w-5" />;
      case "update_tender_status":
        return <ActivityIcon className="h-5 w-5" />;
      case "set_reminder":
        return <BellIcon className="h-5 w-5" />;
      default:
        return <BotIcon className="h-5 w-5" />;
    }
  };

  const getTriggerDescription = (rule: AutomationRule) => {
    switch (rule.triggerType) {
      case "deadline_approaching":
        return `When a tender deadline is within ${rule.triggerValue} days`;
      case "status_change":
        return `When a tender status changes to "${rule.triggerValue}"`;
      case "new_tender":
        return "When a new tender is created";
      case "risk_score_change":
        return `When risk score changes by more than ${rule.triggerValue}%`;
      case "document_uploaded":
        return "When a new document is uploaded";
      default:
        return rule.triggerType;
    }
  };

  const getActionDescription = (rule: AutomationRule) => {
    switch (rule.actionType) {
      case "email_notification":
        return "Send an email notification";
      case "create_task":
        return "Create a new task";
      case "create_calendar_event":
        return "Add an event to the calendar";
      case "update_tender_status":
        return `Update tender status to "${rule.actionParams}"`;
      case "set_reminder":
        return "Set a reminder notification";
      default:
        return rule.actionType;
    }
  };

  if (rulesLoading) {
    return <div className="p-8">Loading automation rules...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Automation Rules</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Create and manage automated workflows for your tender processes
          </p>
        </div>
        <Button onClick={() => setShowRuleDialog(true)}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Create New Rule
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {rules && rules.length > 0 ? (
          rules.map((rule: AutomationRule) => (
            <Card key={rule.id} className="relative">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{rule.name}</CardTitle>
                    {rule.description && (
                      <CardDescription>{rule.description}</CardDescription>
                    )}
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreVerticalIcon className="h-4 w-4" />
                        <span className="sr-only">Rule options</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => handleDeleteRule(rule.id)}>
                        Delete Rule
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                
                <div className="absolute top-4 right-14">
                  <Switch
                    checked={rule.enabled}
                    onCheckedChange={(checked) => handleToggleRule(rule.id, checked)}
                  />
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="flex items-center gap-2 mb-4 mt-2">
                  <Badge variant="outline" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                    {getTriggerIcon(rule.triggerType)}
                    <span className="ml-1">{getTriggerTypeLabel(rule.triggerType)}</span>
                  </Badge>
                  
                  <span className="text-gray-400">→</span>
                  
                  <Badge variant="outline" className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300">
                    {getActionIcon(rule.actionType)}
                    <span className="ml-1">{getActionTypeLabel(rule.actionType)}</span>
                  </Badge>
                </div>
                
                <div className="text-sm">
                  <p className="text-gray-600 dark:text-gray-400 mb-1">
                    <span className="font-medium">When:</span> {getTriggerDescription(rule)}
                  </p>
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Then:</span> {getActionDescription(rule)}
                  </p>
                </div>
              </CardContent>
              
              <CardFooter className="text-xs text-gray-500 border-t pt-3">
                Created {format(new Date(rule.createdAt), "MMM d, yyyy")}
              </CardFooter>
            </Card>
          ))
        ) : (
          <div className="col-span-1 md:col-span-2 xl:col-span-3 flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <BotIcon className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-xl font-medium mb-2">No automation rules found</h3>
            <p className="text-gray-500 text-center mb-4 max-w-md">
              Create your first automation rule to streamline your tender management workflow
            </p>
            <Button onClick={() => setShowRuleDialog(true)}>
              <PlusIcon className="h-4 w-4 mr-2" />
              Create New Rule
            </Button>
          </div>
        )}
      </div>
      
      {/* New Rule Dialog */}
      <Dialog open={showRuleDialog} onOpenChange={setShowRuleDialog}>
        <DialogContent className="sm:max-w-[550px]">
          <DialogHeader>
            <DialogTitle>Create Automation Rule</DialogTitle>
            <DialogDescription>
              Set up an automated workflow to respond to events in your tender management process.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Rule Name</Label>
              <Input
                id="name"
                value={newRule.name}
                onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                placeholder="Enter rule name"
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                value={newRule.description}
                onChange={(e) => setNewRule({...newRule, description: e.target.value})}
                placeholder="Describe what this automation rule does"
              />
            </div>
            
            <div className="grid gap-4 border-t border-b py-4 my-2">
              <h3 className="font-medium flex items-center">
                <ZapIcon className="h-4 w-4 mr-2 text-blue-500" />
                Trigger (When)
              </h3>
              
              <div className="grid gap-2">
                <Label htmlFor="triggerType">Trigger Type</Label>
                <Select
                  value={newRule.triggerType}
                  onValueChange={(value) => setNewRule({...newRule, triggerType: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select trigger type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="deadline_approaching">Deadline Approaching</SelectItem>
                    <SelectItem value="status_change">Status Changed</SelectItem>
                    <SelectItem value="new_tender">New Tender Created</SelectItem>
                    <SelectItem value="risk_score_change">Risk Score Changed</SelectItem>
                    <SelectItem value="document_uploaded">Document Uploaded</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {(newRule.triggerType === "deadline_approaching" || 
                newRule.triggerType === "risk_score_change" || 
                newRule.triggerType === "status_change") && (
                <div className="grid gap-2">
                  <Label htmlFor="triggerValue">
                    {newRule.triggerType === "deadline_approaching" 
                      ? "Days Before Deadline" 
                      : newRule.triggerType === "risk_score_change"
                        ? "Change Percentage"
                        : "Status Value"}
                  </Label>
                  {newRule.triggerType === "status_change" ? (
                    <Select
                      value={newRule.triggerValue || ""}
                      onValueChange={(value) => setNewRule({...newRule, triggerValue: value})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Draft">Draft</SelectItem>
                        <SelectItem value="In Review">In Review</SelectItem>
                        <SelectItem value="Submitted">Submitted</SelectItem>
                        <SelectItem value="Won">Won</SelectItem>
                        <SelectItem value="Lost">Lost</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      id="triggerValue"
                      type="number"
                      value={newRule.triggerValue || ""}
                      onChange={(e) => setNewRule({...newRule, triggerValue: e.target.value})}
                      placeholder={newRule.triggerType === "deadline_approaching" 
                        ? "e.g. 3 (days)" 
                        : "e.g. 10 (percent)"}
                    />
                  )}
                </div>
              )}
            </div>
            
            <div className="grid gap-4 border-b pb-4 mb-2">
              <h3 className="font-medium flex items-center">
                <BotIcon className="h-4 w-4 mr-2 text-purple-500" />
                Action (Then)
              </h3>
              
              <div className="grid gap-2">
                <Label htmlFor="actionType">Action Type</Label>
                <Select
                  value={newRule.actionType}
                  onValueChange={(value) => setNewRule({...newRule, actionType: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select action type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email_notification">Send Email</SelectItem>
                    <SelectItem value="create_task">Create Task</SelectItem>
                    <SelectItem value="create_calendar_event">Create Calendar Event</SelectItem>
                    <SelectItem value="update_tender_status">Update Tender Status</SelectItem>
                    <SelectItem value="set_reminder">Set Reminder</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {newRule.actionType === "update_tender_status" && (
                <div className="grid gap-2">
                  <Label htmlFor="actionParams">New Status</Label>
                  <Select
                    value={newRule.actionParams}
                    onValueChange={(value) => setNewRule({...newRule, actionParams: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select new status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="In Review">In Review</SelectItem>
                      <SelectItem value="Ready for Submission">Ready for Submission</SelectItem>
                      <SelectItem value="Submitted">Submitted</SelectItem>
                      <SelectItem value="Follow Up">Follow Up</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
              
              {newRule.actionType === "email_notification" && (
                <div className="grid gap-2">
                  <Label htmlFor="actionParams">Email Subject Template</Label>
                  <Input
                    id="actionParams"
                    value={newRule.actionParams}
                    onChange={(e) => setNewRule({...newRule, actionParams: e.target.value})}
                    placeholder="e.g. [Tender Alert] Deadline approaching for {{tender.title}}"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Use {{tender.title}}, {{tender.deadline}}, etc. as placeholders
                  </p>
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch
                id="enabled"
                checked={newRule.enabled}
                onCheckedChange={(checked) => setNewRule({...newRule, enabled: checked})}
              />
              <Label htmlFor="enabled">Enable rule after creation</Label>
            </div>
          </div>
          
          <DialogFooter>
            <Button type="submit" onClick={handleCreateRule}>
              Create Rule
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}