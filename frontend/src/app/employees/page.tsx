"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { EmployeeTable } from "@/components/employees/employee-table";
import { FilterPanel } from "@/components/employees/filter-panel";
import { getEmployees, getFilterOptions } from "@/app/actions/employees";
import { useFilterStore, useEmployeeStore } from "@/lib/store";
import { formatNumber } from "@/lib/utils";
import {
  Users,
  Filter,
  Download,
  Plus,
  Grid,
  List,
  LayoutGrid,
} from "lucide-react";
import { toast } from "sonner";

export default function EmployeesPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showFilters, setShowFilters] = useState(true);
  const { filterBlocks, filterOptions, setFilterOptions } = useFilterStore();
  const { viewMode, setViewMode, page, pageSize, sortBy, sortOrder } =
    useEmployeeStore();

  // Fetch filter options
  useEffect(() => {
    getFilterOptions()
      .then((options) =>
        setFilterOptions({
          ...options,
          cities: [],
          employmentTypes: [],
          religions: [],
          educationLevels: [],
          maritalStatuses: [],
        })
      )
      .catch(console.error);
  }, [setFilterOptions]);

  // Build filters from filter blocks
  const buildFilters = () => {
    const activeBlock = filterBlocks[0]; // For now, just use first block
    return {
      departments: activeBlock.departments.length > 0 ? activeBlock.departments : undefined,
      grades: activeBlock.grades.length > 0 ? activeBlock.grades : undefined,
      countries: activeBlock.countries.length > 0 ? activeBlock.countries : undefined,
      statuses: activeBlock.statuses.length > 0 ? activeBlock.statuses : undefined,
      salary_min: activeBlock.salaryMin || undefined,
      salary_max: activeBlock.salaryMax || undefined,
      experience_min: activeBlock.experienceMin || undefined,
      experience_max: activeBlock.experienceMax || undefined,
      search_term: activeBlock.searchTerm || undefined,
    };
  };

  // Fetch employees
  const { data: employeesData, isLoading, refetch, error } = useQuery({
    queryKey: ["employees", filterBlocks, page, pageSize, sortBy, sortOrder],
    queryFn: () =>
      getEmployees({
        page,
        pageSize,
        sortBy,
        sortOrder,
        filters: buildFilters(),
      }),
  });

  useEffect(() => {
    console.log("Employees Query Debug:", {
      isLoading,
      hasData: !!employeesData,
      dataLength: employeesData?.data?.length,
      total: employeesData?.total,
      error,
      filterBlocks
    });
  }, [employeesData, isLoading, error, filterBlocks]);

  // Export handlers
  const handleExport = async (format: "csv" | "xlsx" | "json") => {
    toast.info("Export functionality coming soon");
    // try {
    //   const blob = await employeeApi.exportEmployees({
    //     filters: buildFilters(),
    //     format,
    //     columns: null, // Export all columns
    //   });

    //   const url = window.URL.createObjectURL(blob);
    //   const link = document.createElement("a");
    //   link.href = url;
    //   link.download = `employees_export.${format}`;
    //   document.body.appendChild(link);
    //   link.click();
    //   document.body.removeChild(link);
    //   window.URL.revokeObjectURL(url);

    //   toast.success(`Exported ${format.toUpperCase()} successfully`);
    // } catch (error) {
    //   toast.error("Export failed");
    // }
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        <main className="flex-1 overflow-auto">
          {/* Page header */}
          <div className="bg-card border-b px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Users className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">Employees</h1>
                  <p className="text-sm text-muted-foreground">
                    {isLoading ? (
                      "Loading..."
                    ) : (
                      <>
                        Showing {formatNumber(employeesData?.data?.length || 0)} of{" "}
                        {formatNumber(employeesData?.total || 0)} employees
                      </>
                    )}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* View mode toggle */}
                <div className="flex items-center bg-muted rounded-lg p-1">
                  <button
                    onClick={() => setViewMode("table")}
                    className={`p-2 rounded-md transition-colors ${
                      viewMode === "table" ? "bg-background shadow-sm" : ""
                    }`}
                  >
                    <List className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setViewMode("grid")}
                    className={`p-2 rounded-md transition-colors ${
                      viewMode === "grid" ? "bg-background shadow-sm" : ""
                    }`}
                  >
                    <Grid className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setViewMode("cards")}
                    className={`p-2 rounded-md transition-colors ${
                      viewMode === "cards" ? "bg-background shadow-sm" : ""
                    }`}
                  >
                    <LayoutGrid className="h-4 w-4" />
                  </button>
                </div>

                {/* Filter toggle */}
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
                    showFilters ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                  }`}
                >
                  <Filter className="h-4 w-4" />
                  Filters
                </button>

                {/* Export dropdown */}
                <div className="relative group">
                  <button className="flex items-center gap-2 px-4 py-2 rounded-lg border hover:bg-muted transition-colors">
                    <Download className="h-4 w-4" />
                    Export
                  </button>
                  <div className="absolute right-0 mt-2 w-40 bg-card border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                    <button
                      onClick={() => handleExport("csv")}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-muted transition-colors rounded-t-lg"
                    >
                      Export CSV
                    </button>
                    <button
                      onClick={() => handleExport("xlsx")}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-muted transition-colors"
                    >
                      Export Excel
                    </button>
                    <button
                      onClick={() => handleExport("json")}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-muted transition-colors rounded-b-lg"
                    >
                      Export JSON
                    </button>
                  </div>
                </div>

                {/* Add employee button */}
                <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                  <Plus className="h-4 w-4" />
                  Add Employee
                </button>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="flex">
            {/* Filter panel */}
            {showFilters && (
              <div className="w-80 border-r bg-card p-4 overflow-auto">
                <FilterPanel />
              </div>
            )}

            {/* Employee table/grid */}
            <div className="flex-1 p-6">
              <EmployeeTable
                employees={employeesData?.data || []}
                total={employeesData?.total || 0}
                isLoading={isLoading}
              />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
