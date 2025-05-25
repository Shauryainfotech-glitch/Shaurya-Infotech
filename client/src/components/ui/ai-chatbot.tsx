import { useState, useRef, useEffect } from "react";
import { 
  MessageSquare, 
  X, 
  Send, 
  Mic, 
  Bot, 
  Brain, 
  ChevronDown, 
  ChevronUp,
  Loader2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { generateAIResponse } from "@/lib/ai-utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  timestamp: Date;
}

export function AIChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { 
      id: "1", 
      type: "bot", 
      content: "Hello! I'm your AI tender assistant. How can I help you today?", 
      timestamp: new Date() 
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Focus input when chat is opened
  useEffect(() => {
    if (isOpen && !isMinimized && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen, isMinimized]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setIsMinimized(false);
    }
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = async () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue.trim(),
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Get AI response
      const response = await generateAIResponse(inputValue.trim());
      
      // Add bot message
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: response,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("Error generating AI response:", error);
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: "I'm sorry, I encountered an error processing your request. Please try again later.",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      {/* Chat Toggle Button */}
      {!isOpen && (
        <button
          onClick={toggleChat}
          className="fixed bottom-6 right-6 w-14 h-14 ai-gradient text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center z-50"
        >
          <MessageSquare className="w-6 h-6" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div 
          className={cn(
            "fixed bottom-6 right-6 z-50 transition-all duration-300 w-80 md:w-96",
            isMinimized ? "h-16" : "h-[30rem]"
          )}
        >
          <Card className="h-full flex flex-col shadow-xl border-gray-200 dark:border-gray-700">
            {/* Chat Header */}
            <CardHeader className="ai-gradient text-white p-4 flex flex-row items-center justify-between rounded-t-lg space-y-0">
              <div className="flex items-center space-x-2">
                <Bot className="h-5 w-5" />
                <CardTitle className="text-base font-medium">AI Assistant</CardTitle>
                <Badge variant="outline" className="bg-white/20 text-white border-none text-xs">
                  GPT-4
                </Badge>
              </div>
              <div className="flex items-center space-x-1">
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-7 w-7 text-white hover:bg-white/20 rounded-full"
                  onClick={toggleMinimize}
                >
                  {isMinimized ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-7 w-7 text-white hover:bg-white/20 rounded-full"
                  onClick={toggleChat}
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </CardHeader>

            {/* Chat Content */}
            {!isMinimized && (
              <>
                <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message) => (
                    <div 
                      key={message.id} 
                      className={cn(
                        "flex",
                        message.type === "user" ? "justify-end" : "justify-start"
                      )}
                    >
                      <div 
                        className={cn(
                          "max-w-[80%] rounded-lg p-3",
                          message.type === "user" 
                            ? "bg-blue-600 text-white" 
                            : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                        )}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1 text-right">
                          {formatTimestamp(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
                        <div className="flex items-center space-x-2">
                          <Loader2 className="h-4 w-4 animate-spin text-blue-600 dark:text-blue-400" />
                          <p className="text-sm text-gray-600 dark:text-gray-400">AI is thinking...</p>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </CardContent>

                {/* Chat Input */}
                <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex space-x-2">
                    <Textarea
                      ref={inputRef}
                      value={inputValue}
                      onChange={handleInputChange}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask me anything about tenders..."
                      className="flex-1 resize-none h-10 min-h-[2.5rem] py-2"
                      maxRows={4}
                      disabled={isLoading}
                    />
                    <div className="flex items-center space-x-1">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                              disabled={isLoading}
                            >
                              <Mic className="h-5 w-5" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>Voice input (coming soon)</TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                      <Button 
                        onClick={handleSubmit} 
                        disabled={!inputValue.trim() || isLoading}
                        className="ai-gradient text-white"
                      >
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="flex items-center justify-center mt-2">
                    <div className="flex items-center space-x-1">
                      <Brain className="h-3 w-3 text-purple-600 dark:text-purple-400" />
                      <span className="text-xs text-gray-500 dark:text-gray-400">Powered by GPT-4</span>
                    </div>
                  </div>
                </div>
              </>
            )}
          </Card>
        </div>
      )}
    </>
  );
}
