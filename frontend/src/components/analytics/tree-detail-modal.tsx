"use client";

import { useState, useEffect } from "react";
import { X, Users, DollarSign, TrendingUp, MapPin, Briefcase } from "lucide-react";
import { getEmployeesBySubGroup } from "@/app/actions/analytics";

interface TreeDetailModalProps {
  node: any;
  graphType: string;
  onClose: () => void;
}

export function TreeDetailModal({ node, graphType, onClose }: TreeDetailModalProps) {
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchEmployees = async () => {
      setLoading(true);
      try {
        if (node.metadata?.type === "sub_group" && node.metadata?.deptGroup && node.metadata?.subGroup) {
          const data = await getEmployeesBySubGroup(
            node.metadata.deptGroup,
            node.metadata.subGroup
          );
          setEmployees(data);
        }
      } catch (error) {
        console.error("Error fetching employees:", error);
      } finally {
        setLoading(false);
      }
    };

    if (node.metadata?.type === "sub_group") {
      fetchEmployees();
    }
  }, [node]);

  const getNodeTitle = () => {
    const meta = node.metadata;
    if (meta?.type === "dept_group") return `Department Group: ${meta.deptGroup}`;
    if (meta?.type === "sub_group") return `Sub Group: ${meta.subGroup}`;
    if (meta?.type === "cluster") return `Cluster: ${meta.cluster}`;
    if (meta?.type === "branch") return `Branch: ${meta.branch}`;
    if (meta?.type === "region") return `Region: ${meta.region}`;
    if (meta?.type === "district") return `District: ${meta.district}`;
    if (meta?.type === "division") return `Division: ${meta.division}`;
    if (meta?.type === "department") return `Department: ${meta.department}`;
    return node.name;
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-card rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="sticky top-0 bg-card border-b p-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{getNodeTitle()}</h2>
            <p className="text-sm text-muted-foreground mt-1">Total Employees: {node.value}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-muted rounded-lg transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-950/30 p-4 rounded-lg border">
              <div className="flex items-center gap-2 mb-2">
                <Users className="h-5 w-5 text-blue-600" />
                <span className="text-sm font-medium">Total</span>
              </div>
              <p className="text-2xl font-bold">{node.metadata?.totalCount || node.value}</p>
            </div>

            {node.metadata?.femaleCount !== undefined && (
              <div className="bg-pink-50 dark:bg-pink-950/30 p-4 rounded-lg border">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-5 w-5 text-pink-600" />
                  <span className="text-sm font-medium">Female</span>
                </div>
                <p className="text-2xl font-bold">{node.metadata.femaleCount}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {((node.metadata.femaleCount / (node.metadata.totalCount || node.value)) * 100).toFixed(1)}%
                </p>
              </div>
            )}

            {node.metadata?.maleCount !== undefined && (
              <div className="bg-cyan-50 dark:bg-cyan-950/30 p-4 rounded-lg border">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-5 w-5 text-cyan-600" />
                  <span className="text-sm font-medium">Male</span>
                </div>
                <p className="text-2xl font-bold">{node.metadata.maleCount}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {((node.metadata.maleCount / (node.metadata.totalCount || node.value)) * 100).toFixed(1)}%
                </p>
              </div>
            )}

            {node.metadata?.avgSalary && (
              <div className="bg-green-50 dark:bg-green-950/30 p-4 rounded-lg border">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium">Avg Salary</span>
                </div>
                <p className="text-lg font-bold">PKR {node.metadata.avgSalary.toLocaleString()}</p>
              </div>
            )}
          </div>

          {/* Additional Stats */}
          {(node.metadata?.avgTenure || node.metadata?.branchCount || node.metadata?.deptCount) && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              {node.metadata?.avgTenure && (
                <div className="bg-amber-50 dark:bg-amber-950/30 p-4 rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-5 w-5 text-amber-600" />
                    <span className="text-sm font-medium">Avg Tenure</span>
                  </div>
                  <p className="text-2xl font-bold">{node.metadata.avgTenure.toFixed(1)} yrs</p>
                </div>
              )}

              {node.metadata?.branchCount && (
                <div className="bg-purple-50 dark:bg-purple-950/30 p-4 rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <MapPin className="h-5 w-5 text-purple-600" />
                    <span className="text-sm font-medium">Branches</span>
                  </div>
                  <p className="text-2xl font-bold">{node.metadata.branchCount}</p>
                </div>
              )}

              {node.metadata?.deptCount && (
                <div className="bg-indigo-50 dark:bg-indigo-950/30 p-4 rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <Briefcase className="h-5 w-5 text-indigo-600" />
                    <span className="text-sm font-medium">Departments</span>
                  </div>
                  <p className="text-2xl font-bold">{node.metadata.deptCount}</p>
                </div>
              )}
            </div>
          )}

          {/* Employees Table - Only for Sub-Group */}
          {node.metadata?.type === "sub_group" && (
            <div>
              <h3 className="font-semibold mb-4 text-lg">Employees</h3>
              {loading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  <p className="text-muted-foreground mt-2">Loading employees...</p>
                </div>
              ) : employees.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50 border-b">
                      <tr>
                        <th className="text-left p-3 font-semibold">Employee #</th>
                        <th className="text-left p-3 font-semibold">Gender</th>
                        <th className="text-left p-3 font-semibold">Grade</th>
                        <th className="text-left p-3 font-semibold">Cadre</th>
                        <th className="text-left p-3 font-semibold">Location</th>
                        <th className="text-left p-3 font-semibold">Salary</th>
                        <th className="text-left p-3 font-semibold">Tenure</th>
                        <th className="text-left p-3 font-semibold">Join Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {employees.map((emp, idx) => (
                        <tr key={idx} className="border-b hover:bg-muted/30 transition-colors">
                          <td className="p-3 font-mono text-xs">{emp.EMPLOYEE_NUMBER}</td>
                          <td className="p-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              emp.GENDER === 'F' || emp.GENDER === 'Female'
                                ? 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400'
                                : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                            }`}>
                              {emp.GENDER === 'F' ? 'Female' : emp.GENDER === 'M' ? 'Male' : emp.GENDER}
                            </span>
                          </td>
                          <td className="p-3">{emp.GRADE || 'N/A'}</td>
                          <td className="p-3">{emp.CADRE || 'N/A'}</td>
                          <td className="p-3">{emp.LOCATION_NAME || 'N/A'}</td>
                          <td className="p-3 font-semibold text-green-600">
                            PKR {parseFloat(emp.GROSS_SALARY || 0).toLocaleString()}
                          </td>
                          <td className="p-3">{emp.tenure_years ? `${emp.tenure_years} yrs` : 'N/A'}</td>
                          <td className="p-3 text-muted-foreground text-xs">
                            {emp.DATE_OF_JOIN ? new Date(emp.DATE_OF_JOIN).toLocaleDateString() : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No employees found in this sub-group.</p>
                </div>
              )}
            </div>
          )}

          {/* Info for other node types */}
          {node.metadata?.type !== "sub_group" && (
            <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 p-4 rounded-lg">
              <p className="text-sm text-amber-900 dark:text-amber-100">
                💡 Click on a <strong>Sub-Group</strong> to view individual employee details.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
