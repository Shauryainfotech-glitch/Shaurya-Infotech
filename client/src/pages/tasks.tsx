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
import { Checkbox } from "@/components/ui/checkbox";
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
  CalendarIcon,
  PlusIcon,
  MoreVerticalIcon,
  ClockIcon,
  UserIcon,
  FileTextIcon
} from "lucide-react";
import { format, isToday, isPast, isThisWeek, addDays } from "date-fns";
import { apiRequest, queryClient } from "@/lib/queryClient";

interface Task {
  id: number;
  title: string;
  description: string | null;
  status: string;
  priority: string;
  dueDate: string | null;
  assignedUserId: number | null;
  tenderId: number | null;
  completedAt: string | null;
  createdAt: string;
}

interface User {
  id: number;
  name: string;
}

interface Tender {
  id: number;
  title: string;
}

export default function Tasks() {
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string | null>(null);
  const [showTaskDialog, setShowTaskDialog] = useState(false);
  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    status: "Pending",
    priority: "Medium",
    dueDate: format(addDays(new Date(), 7), "yyyy-MM-dd"),
    assignedUserId: "",
    tenderId: ""
  });

  // Fetch tasks
  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['/api/tasks'],
    refetchInterval: false,
  });

  // Fetch users for assignment
  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ['/api/users'],
    refetchInterval: false,
  });

  // Fetch tenders for linking
  const { data: tenders, isLoading: tendersLoading } = useQuery({
    queryKey: ['/api/tenders'],
    refetchInterval: false,
  });

  const handleCreateTask = async () => {
    try {
      await apiRequest(
        'POST',
        '/api/tasks',
        {
          ...newTask,
          assignedUserId: newTask.assignedUserId ? parseInt(newTask.assignedUserId) : null,
          tenderId: newTask.tenderId ? parseInt(newTask.tenderId) : null
        }
      );
      
      // Reset form and close dialog
      setNewTask({
        title: "",
        description: "",
        status: "Pending",
        priority: "Medium",
        dueDate: format(addDays(new Date(), 7), "yyyy-MM-dd"),
        assignedUserId: "",
        tenderId: ""
      });
      setShowTaskDialog(false);
      
      // Refetch tasks
      queryClient.invalidateQueries({ queryKey: ['/api/tasks'] });
    } catch (error) {
      console.error("Error creating task:", error);
    }
  };

  const handleCompleteTask = async (taskId: number) => {
    try {
      await apiRequest(
        'POST',
        `/api/tasks/${taskId}/complete`,
        {}
      );
      
      // Refetch tasks
      queryClient.invalidateQueries({ queryKey: ['/api/tasks'] });
    } catch (error) {
      console.error("Error completing task:", error);
    }
  };

  const getFilteredTasks = () => {
    if (!tasks) return [];
    
    return tasks.filter((task: Task) => {
      // Apply status filter
      if (statusFilter && task.status !== statusFilter) return false;
      
      // Apply priority filter
      if (priorityFilter && task.priority !== priorityFilter) return false;
      
      return true;
    });
  };

  const getUserName = (userId: number | null) => {
    if (!userId || !users) return "Unassigned";
    const user = users.find((u: User) => u.id === userId);
    return user ? user.name : "Unknown";
  };

  const getTenderTitle = (tenderId: number | null) => {
    if (!tenderId || !tenders) return null;
    const tender = tenders.find((t: Tender) => t.id === tenderId);
    return tender ? tender.title : null;
  };

  const getDueDateDisplay = (dueDate: string | null) => {
    if (!dueDate) return "No deadline";
    
    const date = new Date(dueDate);
    if (isToday(date)) return "Today";
    if (isPast(date)) return `Overdue: ${format(date, "MMM d")}`;
    if (isThisWeek(date)) return format(date, "EEEE");
    
    return format(date, "MMM d, yyyy");
  };

  const getDueDateColor = (dueDate: string | null) => {
    if (!dueDate) return "text-gray-500";
    
    const date = new Date(dueDate);
    if (isPast(date)) return "text-red-500";
    if (isToday(date)) return "text-amber-500";
    
    return "text-green-500";
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "High": return "bg-red-500";
      case "Medium": return "bg-amber-500";
      case "Low": return "bg-green-500";
      default: return "bg-blue-500";
    }
  };

  if (tasksLoading) {
    return <div className="p-8">Loading tasks...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Task Management</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Organize and track your tender-related tasks
          </p>
        </div>
        <Button onClick={() => setShowTaskDialog(true)}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Add New Task
        </Button>
      </div>
      
      <div className="flex gap-4 mb-6">
        <Select
          value={statusFilter || ""}
          onValueChange={(value) => setStatusFilter(value || null)}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Statuses</SelectItem>
            <SelectItem value="Pending">Pending</SelectItem>
            <SelectItem value="In Progress">In Progress</SelectItem>
            <SelectItem value="Completed">Completed</SelectItem>
          </SelectContent>
        </Select>
        
        <Select
          value={priorityFilter || ""}
          onValueChange={(value) => setPriorityFilter(value || null)}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Priorities</SelectItem>
            <SelectItem value="High">High</SelectItem>
            <SelectItem value="Medium">Medium</SelectItem>
            <SelectItem value="Low">Low</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div className="grid grid-cols-1 gap-4">
        {getFilteredTasks().map((task: Task) => (
          <Card key={task.id} className="mb-4">
            <CardHeader className="pb-2 flex flex-row items-start justify-between">
              <div className="flex items-center gap-2">
                <Checkbox 
                  checked={task.status === "Completed"}
                  onCheckedChange={() => {
                    if (task.status !== "Completed") {
                      handleCompleteTask(task.id);
                    }
                  }}
                />
                <div>
                  <CardTitle className={task.status === "Completed" ? "line-through text-gray-500" : ""}>
                    {task.title}
                  </CardTitle>
                  {task.tenderId && (
                    <CardDescription>
                      <FileTextIcon className="h-3 w-3 inline mr-1" />
                      {getTenderTitle(task.tenderId)}
                    </CardDescription>
                  )}
                </div>
              </div>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <MoreVerticalIcon className="h-4 w-4" />
                    <span className="sr-only">Task options</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>Edit Task</DropdownMenuItem>
                  <DropdownMenuItem>Delete Task</DropdownMenuItem>
                  {task.status !== "Completed" && (
                    <DropdownMenuItem onClick={() => handleCompleteTask(task.id)}>
                      Mark as Completed
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </CardHeader>
            
            <CardContent>
              {task.description && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{task.description}</p>
              )}
              
              <div className="flex flex-wrap gap-3">
                <Badge variant="outline" className={`${getPriorityColor(task.priority)} text-white`}>
                  {task.priority}
                </Badge>
                
                <Badge variant="outline" className="bg-gray-100 dark:bg-gray-800">
                  <UserIcon className="h-3 w-3 mr-1" />
                  {getUserName(task.assignedUserId)}
                </Badge>
                
                {task.dueDate && (
                  <Badge variant="outline" className="bg-gray-100 dark:bg-gray-800">
                    <CalendarIcon className="h-3 w-3 mr-1" />
                    <span className={getDueDateColor(task.dueDate)}>
                      {getDueDateDisplay(task.dueDate)}
                    </span>
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
        
        {getFilteredTasks().length === 0 && (
          <div className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <ClockIcon className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-xl font-medium mb-2">No tasks found</h3>
            <p className="text-gray-500 text-center mb-4">
              {statusFilter || priorityFilter
                ? "Try changing your filters to see more tasks"
                : "Create your first task to get started"}
            </p>
            <Button onClick={() => setShowTaskDialog(true)}>
              <PlusIcon className="h-4 w-4 mr-2" />
              Add New Task
            </Button>
          </div>
        )}
      </div>
      
      {/* New Task Dialog */}
      <Dialog open={showTaskDialog} onOpenChange={setShowTaskDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
            <DialogDescription>
              Add task details. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="title">Task Title</Label>
              <Input
                id="title"
                value={newTask.title}
                onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                placeholder="Enter task title"
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={newTask.description}
                onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                placeholder="Enter task description"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="priority">Priority</Label>
                <Select
                  value={newTask.priority}
                  onValueChange={(value) => setNewTask({...newTask, priority: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="High">High</SelectItem>
                    <SelectItem value="Medium">Medium</SelectItem>
                    <SelectItem value="Low">Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="status">Status</Label>
                <Select
                  value={newTask.status}
                  onValueChange={(value) => setNewTask({...newTask, status: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Pending">Pending</SelectItem>
                    <SelectItem value="In Progress">In Progress</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="dueDate">Due Date</Label>
              <Input
                id="dueDate"
                type="date"
                value={newTask.dueDate}
                onChange={(e) => setNewTask({...newTask, dueDate: e.target.value})}
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="assignee">Assign To</Label>
              <Select
                value={newTask.assignedUserId}
                onValueChange={(value) => setNewTask({...newTask, assignedUserId: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select assignee" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Unassigned</SelectItem>
                  {users && users.map((user: User) => (
                    <SelectItem key={user.id} value={user.id.toString()}>
                      {user.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="tender">Related Tender</Label>
              <Select
                value={newTask.tenderId}
                onValueChange={(value) => setNewTask({...newTask, tenderId: value})}
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
          </div>
          
          <DialogFooter>
            <Button type="submit" onClick={handleCreateTask}>
              Create Task
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}