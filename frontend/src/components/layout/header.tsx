"use client";

import {
  Menu,
  Bell,
  Search,
  User,
  Moon,
  Sun,
  LogOut,
} from "lucide-react";
import { useUIStore, useFilterStore } from "@/lib/store";

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { theme, setTheme } = useUIStore();
  const { filterBlocks, updateFilterBlock } = useFilterStore();

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Update the first filter block's search term
    if (filterBlocks.length > 0) {
      updateFilterBlock(filterBlocks[0].id, { searchTerm: value });
    }
  };

  return (
    <header className="h-16 bg-card border-b flex items-center justify-between px-4">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="p-2 rounded-lg hover:bg-muted transition-colors lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>
        
        <div className="hidden md:flex items-center gap-2 bg-muted rounded-lg px-3 py-2">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search employees..."
            className="bg-transparent border-none outline-none text-sm w-64"
            value={filterBlocks[0]?.searchTerm || ""}
            onChange={handleSearch}
          />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* Theme toggle */}
        <button
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          className="p-2 rounded-lg hover:bg-muted transition-colors"
        >
          {theme === "light" ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </button>

        {/* Notifications */}
        <button className="p-2 rounded-lg hover:bg-muted transition-colors relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
        </button>

        {/* User menu */}
        <div className="flex items-center gap-2 ml-2 pl-2 border-l">
          <div className="hidden md:block text-right">
            <p className="text-sm font-medium">Admin User</p>
            <p className="text-xs text-muted-foreground">HR Analytics</p>
          </div>
          <button className="p-2 rounded-full bg-primary text-primary-foreground">
            <User className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
