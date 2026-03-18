"use client";

import { useState, useRef, useEffect } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { useAIChatStore } from "@/lib/store";
import { aiApi } from "@/lib/api";
import { formatNumber } from "@/lib/utils";
import {
  Brain,
  Send,
  Loader2,
  Trash2,
  Sparkles,
  Table,
  BarChart3,
  Download,
  Copy,
  Check,
} from "lucide-react";
import { toast } from "sonner";
import ReactECharts from "echarts-for-react";

const suggestions = [
  "What is the average salary by department?",
  "Show me the top 10 employees with highest attrition risk",
  "Compare headcount between Technology and Operations",
  "What percentage of employees are female in leadership roles?",
  "Which departments have the highest performance scores?",
  "Find employees who joined in 2023 with salary above 200k",
  "Show attrition trends over the last 12 months",
  "What is the gender pay gap by grade level?",
];

export default function AIChatPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [input, setInput] = useState("");
  const [copied, setCopied] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { messages, addMessage, isLoading, setIsLoading, clearMessages } = useAIChatStore();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const query = input.trim();
    setInput("");
    
    addMessage({ role: "user", content: query });
    setIsLoading(true);

    try {
      const response = await aiApi.processQuery(query);
      
      addMessage({
        role: "assistant",
        content: response.analysis || "Here are the results of your query:",
        data: response.results,
        visualizations: response.visualizations,
      });
    } catch (error: any) {
      addMessage({
        role: "assistant",
        content: `Sorry, I encountered an error: ${error.message || "Unknown error"}. Please try again.`,
      });
      toast.error("Failed to process query");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
    toast.success("Copied to clipboard");
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Page header */}
          <div className="bg-card border-b px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Brain className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">AI Assistant</h1>
                  <p className="text-sm text-muted-foreground">
                    Ask questions about your workforce in natural language
                  </p>
                </div>
              </div>

              <button
                onClick={clearMessages}
                className="flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
              >
                <Trash2 className="h-4 w-4" />
                Clear chat
              </button>
            </div>
          </div>

          {/* Chat area */}
          <div className="flex-1 overflow-auto p-6">
            {messages.length === 0 ? (
              // Empty state with suggestions
              <div className="max-w-3xl mx-auto">
                <div className="text-center mb-8">
                  <div className="inline-flex items-center justify-center p-4 bg-primary/10 rounded-full mb-4">
                    <Brain className="h-12 w-12 text-primary" />
                  </div>
                  <h2 className="text-2xl font-bold mb-2">HR Analytics AI Assistant</h2>
                  <p className="text-muted-foreground">
                    I can help you analyze your workforce data using natural language.
                    Ask me anything about employees, compensation, performance, or attrition.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {suggestions.map((suggestion, i) => (
                    <button
                      key={i}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="flex items-start gap-3 p-4 text-left bg-card border rounded-lg hover:border-primary hover:shadow-sm transition-all"
                    >
                      <Sparkles className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{suggestion}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              // Chat messages
              <div className="max-w-4xl mx-auto space-y-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[85%] ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground rounded-2xl rounded-br-md"
                          : "bg-card border rounded-2xl rounded-bl-md"
                      } p-4`}
                    >
                      {/* Message content */}
                      <p className="whitespace-pre-wrap">{message.content}</p>

                      {/* Data table */}
                      {message.data && message.data.length > 0 && (
                        <div className="mt-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Table className="h-4 w-4" />
                            <span className="text-sm font-medium">
                              {formatNumber(message.data.length)} results
                            </span>
                          </div>
                          <div className="overflow-x-auto border rounded-lg">
                            <table className="w-full text-sm">
                              <thead>
                                <tr className="bg-muted">
                                  {Object.keys(message.data[0]).map((key) => (
                                    <th key={key} className="px-3 py-2 text-left font-medium">
                                      {key}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {message.data.slice(0, 10).map((row: any, i: number) => (
                                  <tr key={i} className="border-t">
                                    {Object.values(row).map((val: any, j: number) => (
                                      <td key={j} className="px-3 py-2">
                                        {typeof val === "number"
                                          ? val.toLocaleString()
                                          : String(val)}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                            {message.data.length > 10 && (
                              <div className="px-3 py-2 text-xs text-muted-foreground border-t">
                                Showing 10 of {message.data.length} results
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Visualizations */}
                      {message.visualizations && message.visualizations.length > 0 && (
                        <div className="mt-4 space-y-4">
                          {message.visualizations.map((viz: any, i: number) => (
                            <div key={i} className="border rounded-lg p-4">
                              <div className="flex items-center gap-2 mb-2">
                                <BarChart3 className="h-4 w-4" />
                                <span className="text-sm font-medium">{viz.title || "Chart"}</span>
                              </div>
                              <ReactECharts
                                option={viz.option}
                                style={{ height: "300px" }}
                              />
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Message actions */}
                      {message.role === "assistant" && (
                        <div className="flex items-center gap-2 mt-3 pt-3 border-t">
                          <button
                            onClick={() => copyToClipboard(message.content, message.id)}
                            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                          >
                            {copied === message.id ? (
                              <Check className="h-3 w-3" />
                            ) : (
                              <Copy className="h-3 w-3" />
                            )}
                            Copy
                          </button>
                          {message.data && (
                            <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
                              <Download className="h-3 w-3" />
                              Export
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-card border rounded-2xl rounded-bl-md p-4">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm text-muted-foreground">
                          Analyzing your query...
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input area */}
          <div className="border-t bg-card p-4">
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
              <div className="relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask anything about your workforce..."
                  className="w-full h-14 pl-4 pr-14 rounded-xl border-2 focus:border-primary focus:outline-none bg-background text-foreground placeholder:text-muted-foreground transition-colors"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
                >
                  {isLoading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </button>
              </div>
              <p className="text-xs text-center text-muted-foreground mt-2">
                AI responses are generated locally using your data. No information is sent externally.
              </p>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}
