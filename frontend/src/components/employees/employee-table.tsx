"use client";

import { useState } from "react";
import { useEmployeeStore } from "@/lib/store";
import { formatCurrency, getGradeColor, getPerformanceColor } from "@/lib/utils";
import {
  ChevronUp,
  ChevronDown,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";

interface Employee {
  employee_id: string;
  full_name: string;
  department: string;
  grade_level: string;
  designation: string;
  branch_city: string;
  branch_country: string;
  total_monthly_salary: number | null;
  performance_score: number | null;
  status: string;
  email?: string;
}

interface EmployeeTableProps {
  employees: Employee[];
  total: number;
  isLoading: boolean;
}

export function EmployeeTable({ employees, total, isLoading }: EmployeeTableProps) {
  const {
    selectedEmployees,
    toggleEmployee,
    selectAllEmployees,
    clearSelectedEmployees,
    sortBy,
    sortOrder,
    setSortBy,
    setSortOrder,
    page,
    pageSize,
    setPage,
    setPageSize,
  } = useEmployeeStore();

  const [openMenu, setOpenMenu] = useState<string | null>(null);

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const handleSelectAll = () => {
    if (selectedEmployees.length === employees.length) {
      clearSelectedEmployees();
    } else {
      selectAllEmployees(employees.map((e) => e.employee_id));
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  if (isLoading) {
    return (
      <div className="bg-card rounded-lg border overflow-hidden">
        <div className="p-8 text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading employees...</p>
        </div>
      </div>
    );
  }

  if (employees.length === 0) {
    return (
      <div className="bg-card rounded-lg border overflow-hidden">
        <div className="p-8 text-center">
          <p className="text-muted-foreground">No employees found matching your filters.</p>
        </div>
      </div>
    );
  }

  const columns = [
    { key: "employee_id", label: "ID", sortable: true },
    { key: "full_name", label: "Name", sortable: true },
    { key: "department", label: "Department", sortable: true },
    { key: "grade_level", label: "Grade", sortable: true },
    { key: "branch_city", label: "Location", sortable: true },
    { key: "total_monthly_salary", label: "Salary", sortable: true },
    { key: "performance_score", label: "Performance", sortable: true },
    { key: "status", label: "Status", sortable: true },
    { key: "actions", label: "", sortable: false },
  ];

  return (
    <div className="space-y-4">
      {/* Table */}
      <div className="bg-card rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-muted">
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedEmployees.length === employees.length && employees.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-gray-300 text-primary focus:ring-primary"
                  />
                </th>
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className={`px-4 py-3 text-left font-medium text-muted-foreground ${
                      col.sortable ? "cursor-pointer hover:text-foreground" : ""
                    }`}
                    onClick={() => col.sortable && handleSort(col.key)}
                  >
                    <div className="flex items-center gap-1">
                      {col.label}
                      {col.sortable && sortBy === col.key && (
                        sortOrder === "asc" ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {employees.map((employee) => (
                <tr
                  key={employee.employee_id}
                  className={`border-b hover:bg-muted/50 transition-colors ${
                    selectedEmployees.includes(employee.employee_id) ? "bg-primary/5" : ""
                  }`}
                >
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedEmployees.includes(employee.employee_id)}
                      onChange={() => toggleEmployee(employee.employee_id)}
                      className="rounded border-gray-300 text-primary focus:ring-primary"
                    />
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{employee.employee_id}</td>
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium">{employee.full_name}</p>
                      <p className="text-xs text-muted-foreground">{employee.designation}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3">{employee.department}</td>
                  <td className="px-4 py-3">
                    <span
                      className="px-2 py-1 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: `${getGradeColor(employee.grade_level)}20`,
                        color: getGradeColor(employee.grade_level),
                      }}
                    >
                      {employee.grade_level}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div>
                      <p>{employee.branch_city}</p>
                      <p className="text-xs text-muted-foreground">{employee.branch_country}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-medium">
                    {formatCurrency(employee.total_monthly_salary || 0)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: getPerformanceColor(employee.performance_score || 0) }}
                      ></div>
                      <span>{employee.performance_score?.toFixed(1) || "N/A"}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        employee.status === "Active"
                          ? "bg-green-100 text-green-700"
                          : employee.status === "On Leave"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {employee.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="relative">
                      <button
                        onClick={() => setOpenMenu(openMenu === employee.employee_id ? null : employee.employee_id)}
                        className="p-1 rounded hover:bg-muted transition-colors"
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </button>

                      {openMenu === employee.employee_id && (
                        <div className="absolute right-0 mt-1 w-48 bg-card border rounded-lg shadow-lg z-50">
                          <button className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-muted transition-colors">
                            <Eye className="h-4 w-4" />
                            View Details
                          </button>
                          <button className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-muted transition-colors">
                            <TrendingUp className="h-4 w-4" />
                            View Predictions
                          </button>
                          <button className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-muted transition-colors">
                            <Edit className="h-4 w-4" />
                            Edit
                          </button>
                          <button className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-muted text-red-600 transition-colors">
                            <Trash2 className="h-4 w-4" />
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Rows per page:</span>
          <select
            value={pageSize}
            onChange={(e) => setPageSize(Number(e.target.value))}
            className="px-2 py-1 border rounded-md text-sm"
          >
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={500}>500</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage(1)}
              disabled={page === 1}
              className="px-3 py-1 border rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-muted transition-colors"
            >
              First
            </button>
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              className="px-3 py-1 border rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-muted transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page === totalPages}
              className="px-3 py-1 border rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-muted transition-colors"
            >
              Next
            </button>
            <button
              onClick={() => setPage(totalPages)}
              disabled={page === totalPages}
              className="px-3 py-1 border rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-muted transition-colors"
            >
              Last
            </button>
          </div>
        </div>
      </div>

      {/* Selected actions */}
      {selectedEmployees.length > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-card border rounded-lg shadow-lg px-6 py-3 flex items-center gap-4">
          <span className="text-sm font-medium">
            {selectedEmployees.length} employee(s) selected
          </span>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90 transition-colors">
            <TrendingUp className="h-4 w-4" />
            View Predictions
          </button>
          <button className="flex items-center gap-2 px-4 py-2 border rounded-lg text-sm hover:bg-muted transition-colors">
            <AlertTriangle className="h-4 w-4" />
            Risk Analysis
          </button>
          <button
            onClick={clearSelectedEmployees}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Clear selection
          </button>
        </div>
      )}
    </div>
  );
}
