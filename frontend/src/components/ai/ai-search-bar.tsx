"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { aiApi } from "@/lib/api";
import { useAIChatStore } from "@/lib/store";
import { Brain, Send, Sparkles, Loader2 } from "lucide-react";
import { toast } from "sonner";

const suggestions = [
  "Show me employees in IT department with salary > 150k",
  "What's the gender distribution across departments?",
  "Find high performers in Operations who joined in 2022",
  "Compare attrition rates between Karachi and Lahore",
  "Show top 10 departments by average performance score",
  "List employees eligible for promotion",
];

export function AISearchBar() {
  const [query, setQuery] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { addMessage, setIsLoading, isLoading } = useAIChatStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    addMessage({ role: "user", content: query });

    try {
      const response = await aiApi.processQuery(query);
      addMessage({
        role: "assistant",
        content: response.analysis || "Query processed successfully.",
        data: response.results,
        visualizations: response.visualizations,
      });
      
      // Show toast with quick summary
      toast.success(`Found ${response.results?.length || 0} results`);
    } catch (error: any) {
      toast.error(error.message || "Failed to process query");
      addMessage({
        role: "assistant",
        content: "Sorry, I couldn't process your query. Please try again.",
      });
    } finally {
      setIsLoading(false);
      setQuery("");
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
  };

  return (
    <div className="relative">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2">
            <Brain className="h-5 w-5 text-primary" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Ask anything about your workforce... (e.g., 'Show me attrition risk by department')"
            className="w-full h-14 pl-12 pr-14 rounded-xl border-2 border-primary/20 focus:border-primary focus:outline-none bg-card text-foreground placeholder:text-muted-foreground transition-colors"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </div>
      </form>

      {/* Suggestions dropdown */}
      {showSuggestions && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-card rounded-lg border shadow-lg z-50">
          <div className="p-2">
            <p className="text-xs text-muted-foreground px-2 py-1 flex items-center gap-1">
              <Sparkles className="h-3 w-3" />
              Suggested queries
            </p>
            {suggestions.map((suggestion, i) => (
              <button
                key={i}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full text-left px-3 py-2 text-sm hover:bg-muted rounded-md transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
