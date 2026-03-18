import { create } from "zustand";
import { persist } from "zustand/middleware";

// ============= Filter Store =============
interface FilterBlock {
  id: string;
  departments: string[];
  grades: string[];
  countries: string[];
  cities: string[];
  statuses: string[];
  employmentTypes: string[];
  salaryMin: number | null;
  salaryMax: number | null;
  experienceMin: number | null;
  experienceMax: number | null;
  performanceMin: number | null;
  performanceMax: number | null;
  searchTerm: string;
}

interface FilterState {
  filterBlocks: FilterBlock[];
  activeFilters: FilterBlock;
  filterOptions: {
    departments: string[];
    grades: string[];
    countries: string[];
    cities: string[];
    statuses: string[];
    employmentTypes: string[];
    religions: string[];
    educationLevels: string[];
    maritalStatuses: string[];
  };
  addFilterBlock: () => void;
  removeFilterBlock: (id: string) => void;
  updateFilterBlock: (id: string, updates: Partial<FilterBlock>) => void;
  setActiveFilters: (filters: FilterBlock) => void;
  clearAllFilters: () => void;
  setFilterOptions: (options: FilterState["filterOptions"]) => void;
}

const createEmptyFilterBlock = (): FilterBlock => ({
  id: Math.random().toString(36).substr(2, 9),
  departments: [],
  grades: [],
  countries: [],
  cities: [],
  statuses: [],
  employmentTypes: [],
  salaryMin: null,
  salaryMax: null,
  experienceMin: null,
  experienceMax: null,
  performanceMin: null,
  performanceMax: null,
  searchTerm: "",
});

export const useFilterStore = create<FilterState>()(
  persist(
    (set) => ({
      filterBlocks: [createEmptyFilterBlock()],
      activeFilters: createEmptyFilterBlock(),
      filterOptions: {
        departments: [],
        grades: [],
        countries: [],
        cities: [],
        statuses: [],
        employmentTypes: [],
        religions: [],
        educationLevels: [],
        maritalStatuses: [],
      },

      addFilterBlock: () =>
        set((state) => ({
          filterBlocks: [...state.filterBlocks, createEmptyFilterBlock()],
        })),

      removeFilterBlock: (id) =>
        set((state) => ({
          filterBlocks: state.filterBlocks.filter((block) => block.id !== id),
        })),

      updateFilterBlock: (id, updates) =>
        set((state) => ({
          filterBlocks: state.filterBlocks.map((block) =>
            block.id === id ? { ...block, ...updates } : block
          ),
        })),

      setActiveFilters: (filters) =>
        set(() => ({
          activeFilters: filters,
        })),

      clearAllFilters: () =>
        set(() => ({
          filterBlocks: [createEmptyFilterBlock()],
          activeFilters: createEmptyFilterBlock(),
        })),

      setFilterOptions: (options) =>
        set(() => ({
          filterOptions: options,
        })),
    }),
    {
      name: "hr-analytics-filters",
    }
  )
);

// ============= Dashboard Store =============
interface DashboardState {
  selectedDashboard: string;
  timeRange: string;
  comparisonMode: boolean;
  comparisonSegments: string[];
  setSelectedDashboard: (dashboard: string) => void;
  setTimeRange: (range: string) => void;
  setComparisonMode: (mode: boolean) => void;
  setComparisonSegments: (segments: string[]) => void;
}

export const useDashboardStore = create<DashboardState>()((set) => ({
  selectedDashboard: "overview",
  timeRange: "12m",
  comparisonMode: false,
  comparisonSegments: [],

  setSelectedDashboard: (dashboard) => set({ selectedDashboard: dashboard }),
  setTimeRange: (range) => set({ timeRange: range }),
  setComparisonMode: (mode) => set({ comparisonMode: mode }),
  setComparisonSegments: (segments) => set({ comparisonSegments: segments }),
}));

// ============= AI Chat Store =============
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  data?: any;
  visualizations?: any[];
}

interface AIChatState {
  messages: Message[];
  conversationId: string | null;
  isLoading: boolean;
  addMessage: (message: Omit<Message, "id" | "timestamp">) => void;
  setConversationId: (id: string) => void;
  setIsLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

export const useAIChatStore = create<AIChatState>()((set) => ({
  messages: [],
  conversationId: null,
  isLoading: false,

  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: Math.random().toString(36).substr(2, 9),
          timestamp: new Date(),
        },
      ],
    })),

  setConversationId: (id) => set({ conversationId: id }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  clearMessages: () => set({ messages: [], conversationId: null }),
}));

// ============= UI Store =============
interface UIState {
  sidebarOpen: boolean;
  theme: "light" | "dark";
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: "light" | "dark") => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: "light",

      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: "hr-analytics-ui",
    }
  )
);

// ============= Employee Store =============
interface EmployeeState {
  selectedEmployees: string[];
  viewMode: "table" | "grid" | "cards";
  sortBy: string;
  sortOrder: "asc" | "desc";
  page: number;
  pageSize: number;
  toggleEmployee: (id: string) => void;
  selectAllEmployees: (ids: string[]) => void;
  clearSelectedEmployees: () => void;
  setViewMode: (mode: "table" | "grid" | "cards") => void;
  setSortBy: (field: string) => void;
  setSortOrder: (order: "asc" | "desc") => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
}

export const useEmployeeStore = create<EmployeeState>()((set) => ({
  selectedEmployees: [],
  viewMode: "table",
  sortBy: "employee_id",
  sortOrder: "asc",
  page: 1,
  pageSize: 50,

  toggleEmployee: (id) =>
    set((state) => ({
      selectedEmployees: state.selectedEmployees.includes(id)
        ? state.selectedEmployees.filter((e) => e !== id)
        : [...state.selectedEmployees, id],
    })),

  selectAllEmployees: (ids) => set({ selectedEmployees: ids }),
  clearSelectedEmployees: () => set({ selectedEmployees: [] }),
  setViewMode: (mode) => set({ viewMode: mode }),
  setSortBy: (field) => set({ sortBy: field }),
  setSortOrder: (order) => set({ sortOrder: order }),
  setPage: (page) => set({ page }),
  setPageSize: (size) => set({ pageSize: size, page: 1 }),
}));
