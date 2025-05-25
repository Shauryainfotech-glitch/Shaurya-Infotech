import { Switch, Route, useLocation } from "wouter";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/queryClient";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/components/ui/theme-provider";
import AppLayout from "@/components/layout/app-layout";
import Dashboard from "@/pages/dashboard";
import Tenders from "@/pages/tenders";
import Firms from "@/pages/firms";
import OcrAnalysis from "@/pages/ocr-analysis";
import NotFound from "@/pages/not-found";
import { AIChatbot } from "@/components/ui/ai-chatbot";

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <AppLayout>
            <Router />
          </AppLayout>
          <AIChatbot />
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

function Router() {
  const [location] = useLocation();

  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route path="/tenders" component={Tenders} />
      <Route path="/firms" component={Firms} />
      <Route path="/ocr-analysis" component={OcrAnalysis} />
      <Route component={NotFound} />
    </Switch>
  );
}

export default App;
