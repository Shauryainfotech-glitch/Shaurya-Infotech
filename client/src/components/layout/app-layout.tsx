import { useState } from "react";
import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar collapsed={sidebarCollapsed} />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar onToggleSidebar={toggleSidebar} />
        
        <main className="flex-1 overflow-auto bg-gray-50 dark:bg-gray-900 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
