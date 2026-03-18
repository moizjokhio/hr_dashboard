"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { Users, ArrowLeft, DollarSign, Calendar, MapPin, Briefcase } from "lucide-react";
import { useRouter } from "next/navigation";

interface EmployeeListContentProps {
  employees: any[];
  deptGroup: string;
  subGroup: string;
}

export function EmployeeListContent({ employees, deptGroup, subGroup }: EmployeeListContentProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const router = useRouter();

  const stats = {
    total: employees.length,
    female: employees.filter(e => e.GENDER === 'F' || e.GENDER === 'Female').length,
    male: employees.filter(e => e.GENDER === 'M' || e.GENDER === 'Male').length,
    avgSalary: employees.reduce((sum, e) => sum + (parseFloat(e.GROSS_SALARY) || 0), 0) / employees.length,
    avgTenure: employees.reduce((sum, e) => sum + (parseFloat(e.tenure_years) || 0), 0) / employees.length,
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        <main className="flex-1 overflow-auto">
          <div className="p-6">
            {/* Header */}
            <div className="mb-6">
              <button
                onClick={() => router.back()}
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-4"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Analytics
              </button>
              
              <h1 className="text-3xl font-bold">Employee Details</h1>
              <p className="text-muted-foreground mt-1">
                {deptGroup} → {subGroup}
              </p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-4 rounded-lg text-white">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-5 w-5" />
                  <span className="text-sm opacity-90">Total Employees</span>
                </div>
                <p className="text-3xl font-bold">{stats.total}</p>
              </div>
              
              <div className="bg-gradient-to-br from-pink-500 to-pink-600 p-4 rounded-lg text-white">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-5 w-5" />
                  <span className="text-sm opacity-90">Female</span>
                </div>
                <p className="text-3xl font-bold">{stats.female}</p>
                <p className="text-xs opacity-80">{((stats.female / stats.total) * 100).toFixed(1)}%</p>
              </div>
              
              <div className="bg-gradient-to-br from-cyan-500 to-cyan-600 p-4 rounded-lg text-white">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-5 w-5" />
                  <span className="text-sm opacity-90">Male</span>
                </div>
                <p className="text-3xl font-bold">{stats.male}</p>
                <p className="text-xs opacity-80">{((stats.male / stats.total) * 100).toFixed(1)}%</p>
              </div>
              
              <div className="bg-gradient-to-br from-green-500 to-green-600 p-4 rounded-lg text-white">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="h-5 w-5" />
                  <span className="text-sm opacity-90">Avg Salary</span>
                </div>
                <p className="text-2xl font-bold">PKR {stats.avgSalary.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
              </div>
              
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-4 rounded-lg text-white">
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="h-5 w-5" />
                  <span className="text-sm opacity-90">Avg Tenure</span>
                </div>
                <p className="text-3xl font-bold">{stats.avgTenure.toFixed(1)}</p>
                <p className="text-xs opacity-80">years</p>
              </div>
            </div>

            {/* Employee Table */}
            <div className="bg-card rounded-lg border shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted/50 border-b">
                    <tr>
                      <th className="text-left p-4 font-semibold">Employee #</th>
                      <th className="text-left p-4 font-semibold">Gender</th>
                      <th className="text-left p-4 font-semibold">Department</th>
                      <th className="text-left p-4 font-semibold">Grade</th>
                      <th className="text-left p-4 font-semibold">Cadre</th>
                      <th className="text-left p-4 font-semibold">Location</th>
                      <th className="text-left p-4 font-semibold">Region</th>
                      <th className="text-left p-4 font-semibold">Contract</th>
                      <th className="text-left p-4 font-semibold">Salary</th>
                      <th className="text-left p-4 font-semibold">Tenure</th>
                      <th className="text-left p-4 font-semibold">Join Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {employees.map((employee, idx) => (
                      <tr key={idx} className="border-b hover:bg-muted/30 transition-colors">
                        <td className="p-4 font-mono text-sm">{employee.EMPLOYEE_NUMBER}</td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            employee.GENDER === 'F' || employee.GENDER === 'Female' 
                              ? 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400'
                              : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                          }`}>
                            {employee.GENDER === 'F' ? 'Female' : employee.GENDER === 'M' ? 'Male' : employee.GENDER}
                          </span>
                        </td>
                        <td className="p-4 text-sm">{employee.DEPARTMENT_NAME || 'N/A'}</td>
                        <td className="p-4 text-sm font-medium">{employee.GRADE || 'N/A'}</td>
                        <td className="p-4 text-sm">{employee.CADRE || 'N/A'}</td>
                        <td className="p-4 text-sm flex items-center gap-1">
                          <MapPin className="h-3 w-3 text-muted-foreground" />
                          {employee.LOCATION_NAME || 'N/A'}
                        </td>
                        <td className="p-4 text-sm">{employee.REGION || 'N/A'}</td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            employee.CONTRACT_TYPE?.toLowerCase().includes('permanent')
                              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                              : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                          }`}>
                            {employee.CONTRACT_TYPE || 'N/A'}
                          </span>
                        </td>
                        <td className="p-4 text-sm font-semibold text-green-600">
                          PKR {parseFloat(employee.GROSS_SALARY || 0).toLocaleString()}
                        </td>
                        <td className="p-4 text-sm">
                          {employee.tenure_years ? `${employee.tenure_years} yrs` : 'N/A'}
                        </td>
                        <td className="p-4 text-sm text-muted-foreground">
                          {employee.DATE_OF_JOIN ? new Date(employee.DATE_OF_JOIN).toLocaleDateString() : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {employees.length === 0 && (
                <div className="p-12 text-center text-muted-foreground">
                  <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No employees found in this sub-group.</p>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
