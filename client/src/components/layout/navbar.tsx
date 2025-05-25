import { useState } from "react";
import { Menu, Bell, HelpCircle, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";

interface NavbarProps {
  onToggleSidebar: () => void;
}

export function Navbar({ onToggleSidebar }: NavbarProps) {
  const [notifications, setNotifications] = useState([
    { id: 1, type: 'ai', text: 'GPT-4 analysis completed for tender #T001', time: '2 min ago', priority: 'high' },
    { id: 2, type: 'risk', text: 'High-risk tender detected: Review required', time: '5 min ago', priority: 'critical' },
    { id: 3, type: 'blockchain', text: 'Tender submission verified on blockchain', time: '10 min ago', priority: 'medium' },
    { id: 4, type: 'prediction', text: 'Market trend alert: Construction tenders up 15%', time: '15 min ago', priority: 'low' }
  ]);

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={onToggleSidebar}>
          <Menu className="h-5 w-5" />
        </Button>
        <div className="flex items-center space-x-2 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/30 dark:to-blue-900/30 px-3 py-1 rounded-full">
          <div className="w-2 h-2 bg-green-500 dark:bg-green-400 rounded-full animate-ai-pulse"></div>
          <span className="text-sm text-green-600 dark:text-green-400 font-medium">AI Systems Online</span>
        </div>
      </div>
      
      <div className="relative w-1/3 hidden md:block">
        <Search className="h-4 w-4 absolute left-3 top-2.5 text-gray-400 dark:text-gray-500" />
        <Input 
          type="text" 
          placeholder="Search tenders, firms, documents..." 
          className="pl-10 pr-4 py-1 h-9"
        />
      </div>
      
      <div className="flex items-center space-x-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {notifications.length}
              </span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <DropdownMenuLabel>Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {notifications.map(notification => (
              <DropdownMenuItem key={notification.id} className="flex items-start p-3 cursor-pointer">
                <div className={`w-2 h-2 rounded-full mt-1.5 mr-2 flex-shrink-0 ${
                  notification.priority === 'critical' ? 'bg-red-500' :
                  notification.priority === 'high' ? 'bg-orange-500' :
                  notification.priority === 'medium' ? 'bg-blue-500' : 'bg-green-500'
                }`} />
                <div>
                  <p className="font-medium text-sm">{notification.text}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{notification.time}</p>
                </div>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
        
        <Button variant="ghost" size="icon">
          <HelpCircle className="h-5 w-5" />
        </Button>
        
        <ThemeToggle />
        
        <div className="border-l border-gray-300 dark:border-gray-600 h-8 mx-2"></div>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <div className="flex items-center space-x-2 cursor-pointer">
              <div className="w-10 h-10 ai-gradient rounded-full flex items-center justify-center">
                <span className="text-white font-medium">AI</span>
              </div>
              <div className="hidden md:block">
                <span className="font-medium text-sm">Admin User</span>
              </div>
            </div>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuItem>Subscription</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Log out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
