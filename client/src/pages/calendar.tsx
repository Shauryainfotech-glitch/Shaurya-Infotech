import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  Card, 
  CardContent
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
import { Checkbox } from "@/components/ui/checkbox";
import {
  PlusIcon,
  ClockIcon,
  MapPinIcon,
  CalendarIcon,
  FileTextIcon,
  UserIcon
} from "lucide-react";
import { 
  format, 
  startOfMonth, 
  endOfMonth, 
  startOfWeek, 
  endOfWeek, 
  eachDayOfInterval,
  isSameMonth,
  isSameDay,
  isToday,
  addMonths,
  subMonths,
  parseISO
} from "date-fns";
import { apiRequest, queryClient } from "@/lib/queryClient";

interface CalendarEvent {
  id: number;
  title: string;
  description: string | null;
  startDate: string;
  endDate: string;
  allDay: boolean;
  location: string | null;
  userId: number | null;
  tenderId: number | null;
  taskId: number | null;
  color: string;
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

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [showEventDialog, setShowEventDialog] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: "",
    description: "",
    startDate: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
    endDate: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
    allDay: false,
    location: "",
    userId: "",
    tenderId: "",
    taskId: "",
    color: "#4F46E5"
  });

  // Fetch calendar events
  const { data: events = [], isLoading: eventsLoading, refetch: refetchEvents } = useQuery({
    queryKey: ['/api/calendar-events'],
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

  const handlePreviousMonth = () => {
    setCurrentDate(subMonths(currentDate, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(addMonths(currentDate, 1));
  };

  const handleCreateEvent = async () => {
    try {
      await apiRequest('/api/calendar-events', {
        method: 'POST',
        body: JSON.stringify({
          ...newEvent,
          userId: newEvent.userId ? parseInt(newEvent.userId) : null,
          tenderId: newEvent.tenderId ? parseInt(newEvent.tenderId) : null,
          taskId: newEvent.taskId ? parseInt(newEvent.taskId) : null
        })
      });
      
      // Reset form and close dialog
      setNewEvent({
        title: "",
        description: "",
        startDate: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
        endDate: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
        allDay: false,
        location: "",
        userId: "",
        tenderId: "",
        taskId: "",
        color: "#4F46E5"
      });
      setShowEventDialog(false);
      
      // Refetch events
      queryClient.invalidateQueries({ queryKey: ['/api/calendar-events'] });
    } catch (error) {
      console.error("Error creating event:", error);
    }
  };

  // Generate calendar grid for the current month
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(monthStart);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);
  
  const calendarDays = eachDayOfInterval({
    start: calendarStart,
    end: calendarEnd
  });

  // Group events by date
  const getEventsForDate = (date: Date) => {
    if (!events) return [];
    
    return events.filter((event: CalendarEvent) => {
      const eventStartDate = parseISO(event.startDate);
      const eventEndDate = parseISO(event.endDate);
      
      // Check if the given date falls between the event's start and end dates
      return (
        isSameDay(date, eventStartDate) ||
        isSameDay(date, eventEndDate) ||
        (date > eventStartDate && date < eventEndDate)
      );
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

  if (eventsLoading || tendersLoading || tasksLoading) {
    return <div className="p-8">Loading calendar...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Calendar</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Manage your schedule and tender deadlines
          </p>
        </div>
        <Button onClick={() => setShowEventDialog(true)}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Event
        </Button>
      </div>
      
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">
          {format(currentDate, "MMMM yyyy")}
        </h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handlePreviousMonth}>
            Previous
          </Button>
          <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date())}>
            Today
          </Button>
          <Button variant="outline" size="sm" onClick={handleNextMonth}>
            Next
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-7 gap-1">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div key={day} className="p-2 text-center font-semibold">
            {day}
          </div>
        ))}
        
        {calendarDays.map((day) => {
          const dayEvents = getEventsForDate(day);
          const isCurrentMonth = isSameMonth(day, monthStart);
          
          return (
            <div 
              key={day.toISOString()}
              className={`
                min-h-[120px] border border-gray-200 dark:border-gray-700 p-2 
                ${!isCurrentMonth ? "bg-gray-50 dark:bg-gray-800/50 text-gray-400 dark:text-gray-600" : ""}
                ${isToday(day) ? "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800" : ""}
              `}
            >
              <div className="text-right text-sm mb-1">
                {format(day, "d")}
              </div>
              
              <div className="space-y-1">
                {dayEvents.slice(0, 3).map((event: CalendarEvent) => (
                  <div 
                    key={event.id}
                    className="text-xs p-1 rounded-sm text-white truncate"
                    style={{ backgroundColor: event.color }}
                  >
                    {event.allDay ? "All Day: " : `${format(parseISO(event.startDate), "h:mm a")}: `}
                    {event.title}
                  </div>
                ))}
                
                {dayEvents.length > 3 && (
                  <div className="text-xs text-center p-1 rounded-sm bg-gray-100 dark:bg-gray-700">
                    + {dayEvents.length - 3} more
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Upcoming Events Section */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Upcoming Events</h2>
        <div className="space-y-3">
          {events.filter((event: CalendarEvent) => {
            const eventDate = parseISO(event.startDate);
            return eventDate >= new Date();
          }).sort((a: CalendarEvent, b: CalendarEvent) => {
            return new Date(a.startDate).getTime() - new Date(b.startDate).getTime();
          }).slice(0, 5).map((event: CalendarEvent) => (
            <Card key={event.id}>
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{event.title}</h3>
                    {event.description && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{event.description}</p>
                    )}
                    
                    <div className="flex flex-wrap gap-2 mt-2">
                      <Badge variant="outline" className="flex items-center gap-1">
                        <CalendarIcon className="h-3 w-3" />
                        {event.allDay ? (
                          format(parseISO(event.startDate), "MMM d, yyyy")
                        ) : (
                          `${format(parseISO(event.startDate), "MMM d, h:mm a")} - ${format(parseISO(event.endDate), "h:mm a")}`
                        )}
                      </Badge>
                      
                      {event.location && (
                        <Badge variant="outline" className="flex items-center gap-1">
                          <MapPinIcon className="h-3 w-3" />
                          {event.location}
                        </Badge>
                      )}
                      
                      {event.userId && (
                        <Badge variant="outline" className="flex items-center gap-1">
                          <UserIcon className="h-3 w-3" />
                          {getUserName(event.userId)}
                        </Badge>
                      )}
                      
                      {event.tenderId && (
                        <Badge variant="outline" className="flex items-center gap-1">
                          <FileTextIcon className="h-3 w-3" />
                          {getTenderTitle(event.tenderId)}
                        </Badge>
                      )}
                      
                      {event.taskId && (
                        <Badge variant="outline" className="flex items-center gap-1">
                          <ClockIcon className="h-3 w-3" />
                          {getTaskTitle(event.taskId)}
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  <div 
                    className="w-3 h-3 rounded-full mt-1"
                    style={{ backgroundColor: event.color }}
                  ></div>
                </div>
              </CardContent>
            </Card>
          ))}
          
          {events.length === 0 && (
            <div className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <CalendarIcon className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-xl font-medium mb-2">No upcoming events</h3>
              <p className="text-gray-500 text-center mb-4">
                Create your first event to get started
              </p>
              <Button onClick={() => setShowEventDialog(true)}>
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Event
              </Button>
            </div>
          )}
        </div>
      </div>
      
      {/* New Event Dialog */}
      <Dialog open={showEventDialog} onOpenChange={setShowEventDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create New Event</DialogTitle>
            <DialogDescription>
              Add event details. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="title">Event Title</Label>
              <Input
                id="title"
                value={newEvent.title}
                onChange={(e) => setNewEvent({...newEvent, title: e.target.value})}
                placeholder="Enter event title"
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={newEvent.description}
                onChange={(e) => setNewEvent({...newEvent, description: e.target.value})}
                placeholder="Enter event description"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Checkbox
                id="allDay"
                checked={newEvent.allDay}
                onCheckedChange={(checked) => 
                  setNewEvent({...newEvent, allDay: checked as boolean})
                }
              />
              <Label htmlFor="allDay">All Day Event</Label>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="startDate">Start Date & Time</Label>
                <Input
                  id="startDate"
                  type={newEvent.allDay ? "date" : "datetime-local"}
                  value={newEvent.startDate}
                  onChange={(e) => setNewEvent({...newEvent, startDate: e.target.value})}
                />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="endDate">End Date & Time</Label>
                <Input
                  id="endDate"
                  type={newEvent.allDay ? "date" : "datetime-local"}
                  value={newEvent.endDate}
                  onChange={(e) => setNewEvent({...newEvent, endDate: e.target.value})}
                />
              </div>
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                value={newEvent.location}
                onChange={(e) => setNewEvent({...newEvent, location: e.target.value})}
                placeholder="Enter location"
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="color">Color</Label>
              <div className="flex gap-2">
                {["#4F46E5", "#10B981", "#F59E0B", "#EF4444", "#6366F1", "#8B5CF6", "#EC4899"].map((color) => (
                  <div
                    key={color}
                    onClick={() => setNewEvent({...newEvent, color})}
                    className={`w-8 h-8 rounded-full cursor-pointer ${
                      newEvent.color === color ? "ring-2 ring-offset-2 ring-gray-400" : ""
                    }`}
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="userId">Assigned To</Label>
              <Select
                value={newEvent.userId}
                onValueChange={(value) => setNewEvent({...newEvent, userId: value})}
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
              <Label htmlFor="tenderId">Related Tender</Label>
              <Select
                value={newEvent.tenderId}
                onValueChange={(value) => setNewEvent({...newEvent, tenderId: value})}
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
              <Label htmlFor="taskId">Related Task</Label>
              <Select
                value={newEvent.taskId}
                onValueChange={(value) => setNewEvent({...newEvent, taskId: value})}
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
          
          <DialogFooter>
            <Button type="submit" onClick={handleCreateEvent}>
              Create Event
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}