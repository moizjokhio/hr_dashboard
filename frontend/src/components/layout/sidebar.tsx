"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  BarChart3,
  Brain,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  AlertTriangle,
  Heart,
  DollarSign,
  ChevronDown,
  RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const navigation = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Employees",
    href: "/employees",
    icon: Users,
  },
  {
    name: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    name: "DA Cases",
    href: "/da-cases",
    icon: AlertTriangle,
  },
  {
    name: "AI Insights",
    href: "/ai",
    icon: Brain,
    children: [
      { name: "Chat", href: "/ai/chat", icon: Brain },
      { name: "Predictions", href: "/ai/predictions", icon: TrendingUp },
      { name: "Search", href: "/ai/search", icon: Brain },
    ],
  },
  {
    name: "Reports",
    href: "/reports",
    icon: FileText,
  },
  {
    name: "Data Management",
    href: "/data-management",
    icon: RefreshCw,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
];

const enableAiFeatures = process.env.NEXT_PUBLIC_ENABLE_AI_FEATURES === "true";

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const visibleNavigation = enableAiFeatures
    ? navigation
    : navigation.filter((item) => item.href !== "/ai");

  const toggleExpanded = (itemName: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemName)) {
      newExpanded.delete(itemName);
    } else {
      newExpanded.add(itemName);
    }
    setExpandedItems(newExpanded);
  };

  return (
    <aside
      className={cn(
        "bg-card border-r transition-all duration-300 flex flex-col",
        isOpen ? "w-64" : "w-16"
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b">
        {isOpen && (
          <span className="font-bold text-xl text-primary">HR Analytics</span>
        )}
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-muted transition-colors"
        >
          {isOpen ? (
            <ChevronLeft className="h-5 w-5" />
          ) : (
            <ChevronRight className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-auto py-4">
        <ul className="space-y-1 px-2">
          {visibleNavigation.map((item) => {
            const isActive =
              pathname === item.href ||
              pathname.startsWith(item.href + "/") ||
              item.children?.some((child) => pathname === child.href);
            const isExpanded = expandedItems.has(item.name) || isActive;

            return (
              <li key={item.name}>
                {item.children ? (
                  <button
                    onClick={() => toggleExpanded(item.name)}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors w-full text-left",
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "hover:bg-muted text-muted-foreground hover:text-foreground"
                    )}
                  >
                    <item.icon className="h-5 w-5 flex-shrink-0" />
                    {isOpen && <span className="flex-1">{item.name}</span>}
                    {isOpen && item.children && (
                      <ChevronDown
                        className={cn(
                          "h-4 w-4 transition-transform",
                          isExpanded ? "rotate-180" : ""
                        )}
                      />
                    )}
                  </button>
                ) : (
                  <Link
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "hover:bg-muted text-muted-foreground hover:text-foreground"
                    )}
                  >
                    <item.icon className="h-5 w-5 flex-shrink-0" />
                    {isOpen && <span>{item.name}</span>}
                  </Link>
                )}

                {/* Submenu */}
                {isOpen && isExpanded && item.children && (
                  <ul className="mt-1 ml-6 space-y-1">
                    {item.children.map((child) => (
                      <li key={child.name}>
                        <Link
                          href={child.href}
                          className={cn(
                            "flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors",
                            pathname === child.href
                              ? "bg-primary/20 text-primary"
                              : "hover:bg-muted text-muted-foreground hover:text-foreground"
                          )}
                        >
                          <child.icon className="h-4 w-4" />
                          {child.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      {isOpen && (
        <div className="p-4 border-t">
          <div className="text-xs text-muted-foreground">
            <p>Version 1.0.0</p>
            <p>© 2024 HR Analytics</p>
          </div>
        </div>
      )}
    </aside>
  );
}
