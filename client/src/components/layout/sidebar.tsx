import { useState } from "react";
import { Link, useLocation } from "wouter";
import { 
  BarChart3, FileText, Users, Brain, Scan, AlertTriangle, 
  Target, Shield, Globe, Workflow, Database, Link as LinkIcon, 
  Coins, Settings, Zap, ChevronDown, ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

interface SidebarProps {
  collapsed: boolean;
}

interface MenuSection {
  title: string;
  items: MenuItem[];
}

interface MenuItem {
  id: string;
  icon: React.ElementType;
  label: string;
  badge?: string;
  path: string;
}

export function Sidebar({ collapsed }: SidebarProps) {
  const [location] = useLocation();
  const [openSections, setOpenSections] = useState<string[]>(["main"]);

  const toggleSection = (section: string) => {
    setOpenSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section) 
        : [...prev, section]
    );
  };

  const menuSections: MenuSection[] = [
    {
      title: "Main",
      items: [
        { id: "dashboard", icon: BarChart3, label: "AI Dashboard", badge: "AI", path: "/" },
        { id: "tenders", icon: FileText, label: "Smart Tenders", badge: "GPT-4", path: "/tenders" },
        { id: "firms", icon: Users, label: "Firm Intelligence", badge: "ML", path: "/firms" },
      ]
    },
    {
      title: "AI Suite",
      items: [
        { id: "ocr-nlp", icon: Scan, label: "OCR + NLP", badge: "Enhanced", path: "/ocr-analysis" },
        { id: "risk-assessment", icon: AlertTriangle, label: "Risk Assessment", badge: "AI", path: "/risk-assessment" },
        { id: "predictive", icon: Target, label: "Predictions", badge: "ML", path: "/predictions" },
        { id: "blockchain", icon: Shield, label: "Blockchain", badge: "Secure", path: "/blockchain" },
      ]
    },
    {
      title: "System",
      items: [
        { id: "gem-integration", icon: Globe, label: "GeM Pro", badge: "Integrated", path: "/gem-integration" },
        { id: "workflow", icon: Workflow, label: "Smart Workflow", badge: "Auto", path: "/workflow" },
        { id: "documents", icon: Database, label: "Doc Intelligence", badge: "AI", path: "/documents" },
        { id: "api", icon: LinkIcon, label: "API Hub", badge: "Connected", path: "/api-hub" },
        { id: "pricing", icon: Coins, label: "Pricing Plans", badge: "Premium", path: "/pricing" },
        { id: "settings", icon: Settings, label: "Settings", path: "/settings" },
      ]
    }
  ];

  return (
    <div className={cn(
      "h-screen bg-sidebar-background text-sidebar-foreground border-r border-sidebar-border transition-all duration-300 flex flex-col",
      collapsed ? "w-16" : "w-64"
    )}>
      <div className="p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 ai-gradient rounded-lg flex items-center justify-center flex-shrink-0">
            <Zap className="h-6 w-6 text-white" />
          </div>
          {!collapsed && (
            <div>
              <h1 className="font-bold text-lg">TenderAI Pro</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">AI-Powered Platform</p>
            </div>
          )}
        </div>
      </div>
      
      <nav className="mt-2 flex-1 overflow-y-auto">
        {menuSections.map((section) => (
          <div key={section.title} className="mb-4">
            {!collapsed ? (
              <Collapsible
                open={openSections.includes(section.title.toLowerCase())}
                onOpenChange={() => toggleSection(section.title.toLowerCase())}
              >
                <CollapsibleTrigger asChild>
                  <div className="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center justify-between cursor-pointer">
                    <span>{section.title}</span>
                    {openSections.includes(section.title.toLowerCase()) ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </div>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  {section.items.map(item => (
                    <Link 
                      key={item.id} 
                      href={item.path}
                    >
                      <a className={cn(
                        "flex items-center px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 dark:hover:from-blue-900/20 dark:hover:to-purple-900/20 transition-colors",
                        location === item.path && "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-600 dark:text-blue-400 border-r-2 border-blue-600 dark:border-blue-400"
                      )}>
                        <item.icon className="h-5 w-5" />
                        <div className="ml-3 flex-1 flex items-center justify-between">
                          <span>{item.label}</span>
                          {item.badge && (
                            <span className={cn(
                              "px-2 py-1 rounded-full text-xs",
                              item.badge === "New" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" :
                              item.badge === "AI" ? "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300" :
                              item.badge === "Premium" ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300" :
                              "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300"
                            )}>
                              {item.badge}
                            </span>
                          )}
                        </div>
                      </a>
                    </Link>
                  ))}
                </CollapsibleContent>
              </Collapsible>
            ) : (
              <div className="px-4 py-2">
                <div className="border-b border-gray-200 dark:border-gray-700 mb-2"></div>
              </div>
            )}
            
            {collapsed && section.items.map(item => (
              <Link 
                key={item.id} 
                href={item.path}
              >
                <a className={cn(
                  "flex items-center justify-center py-3 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 dark:hover:from-blue-900/20 dark:hover:to-purple-900/20 transition-colors",
                  location === item.path && "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-600 dark:text-blue-400 border-r-2 border-blue-600 dark:border-blue-400"
                )}>
                  <item.icon className="h-5 w-5" />
                </a>
              </Link>
            ))}
          </div>
        ))}
      </nav>

      <div className={cn(
        "border-t border-gray-200 dark:border-gray-700 p-4",
        collapsed ? "items-center justify-center" : ""
      )}>
        <div className={cn(
          "flex items-center",
          collapsed ? "justify-center" : "space-x-3"
        )}>
          <div className="w-10 h-10 ai-gradient rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-white font-medium">AI</span>
          </div>
          {!collapsed && (
            <div>
              <p className="font-medium text-sm">Admin User</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">admin@tenderai.com</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
