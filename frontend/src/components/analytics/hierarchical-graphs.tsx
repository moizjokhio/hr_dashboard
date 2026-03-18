import React, { useState } from "react";
import ReactECharts from "echarts-for-react";
import { BarChart3, ChevronLeft, X } from "lucide-react";

interface TreeDetailModalProps {
  node: any;
  graphType: string;
  onClose: () => void;
}

function TreeDetailModal({ node, graphType, onClose }: TreeDetailModalProps) {
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      if (node.metadata?.type === "sub_group" && node.metadata?.deptGroup && node.metadata?.subGroup) {
        const { getEmployeesBySubGroup } = await import("@/app/actions/analytics");
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

  React.useEffect(() => {
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
                <svg className="h-5 w-5 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
                <span className="text-sm font-medium">Total</span>
              </div>
              <p className="text-2xl font-bold">{node.metadata?.totalCount || node.value}</p>
            </div>

            {node.metadata?.femaleCount !== undefined && (
              <div className="bg-pink-50 dark:bg-pink-950/30 p-4 rounded-lg border">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="h-5 w-5 text-pink-600" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
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
                  <svg className="h-5 w-5 text-cyan-600" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
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
                  <svg className="h-5 w-5 text-green-600" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M0 0h24v24H0z" fill="none"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                  </svg>
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
                    <svg className="h-5 w-5 text-amber-600" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M16 6l2.29 2.29-4.29 4.29 4.29 4.29L16 18h6V6z"/>
                    </svg>
                    <span className="text-sm font-medium">Avg Tenure</span>
                  </div>
                  <p className="text-2xl font-bold">{node.metadata.avgTenure.toFixed(1)} yrs</p>
                </div>
              )}

              {node.metadata?.branchCount && (
                <div className="bg-purple-50 dark:bg-purple-950/30 p-4 rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <svg className="h-5 w-5 text-purple-600" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm0-13c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5z"/>
                    </svg>
                    <span className="text-sm font-medium">Branches</span>
                  </div>
                  <p className="text-2xl font-bold">{node.metadata.branchCount}</p>
                </div>
              )}

              {node.metadata?.deptCount && (
                <div className="bg-indigo-50 dark:bg-indigo-950/30 p-4 rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <svg className="h-5 w-5 text-indigo-600" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M20 13H4c-.55 0-1 .45-1 1v6c0 .55.45 1 1 1h16c.55 0 1-.45 1-1v-6c0-.55-.45-1-1-1zm0-2V4c0-.55-.45-1-1-1H5c-.55 0-1 .45-1 1v7H3V4c0-1.11.89-2 2-2h14c1.11 0 2 .89 2 2v7h-2z"/>
                    </svg>
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
                  <svg className="h-12 w-12 mx-auto mb-2 opacity-50" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
                  </svg>
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

interface HierarchicalGraphProps {
  deptGroupHierarchy: any;
  clusterHierarchy: any;
  regionHierarchy: any;
  divisionHierarchy: any;
}

export function HierarchicalGraphs({
  deptGroupHierarchy,
  clusterHierarchy,
  regionHierarchy,
  divisionHierarchy,
}: HierarchicalGraphProps) {
  const [activeGraph, setActiveGraph] = useState("dept");
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const graphs = [
    { id: "dept", label: "Department Groups", icon: "🏢" },
    { id: "cluster", label: "Clusters", icon: "🎯" },
    { id: "region", label: "Regions", icon: "🌍" },
    { id: "division", label: "Divisions", icon: "📊" },
  ];

  // Build tree data for Department Groups
  const buildDeptGroupTree = () => {
    const subGroupsByDept = deptGroupHierarchy.subGroups?.reduce((acc: any, sg: any) => {
      if (!acc[sg.dept_group]) acc[sg.dept_group] = [];
      acc[sg.dept_group].push(sg);
      return acc;
    }, {});

    return {
      name: "Company",
      value: deptGroupHierarchy.deptGroups?.reduce((sum: number, g: any) => sum + g.total_count, 0) || 0,
      metadata: { type: "company" },
      children: deptGroupHierarchy.deptGroups?.map((group: any) => ({
        name: group.dept_group,
        value: group.total_count,
        itemStyle: { color: "#3b82f6" },
        metadata: {
          type: "dept_group",
          deptGroup: group.dept_group,
          totalCount: group.total_count,
          femaleCount: group.female_count,
          maleCount: group.male_count,
          avgSalary: group.avg_salary,
        },
        children: subGroupsByDept?.[group.dept_group]?.map((sg: any) => ({
          name: sg.sub_group,
          value: sg.total_count,
          itemStyle: { color: "#60a5fa" },
          metadata: {
            type: "sub_group",
            deptGroup: group.dept_group,
            subGroup: sg.sub_group,
            totalCount: sg.total_count,
            femaleCount: sg.female_count,
            maleCount: sg.male_count,
            avgSalary: sg.avg_salary,
          },
        })) || [],
      })) || [],
    };
  };

  // Build tree data for Clusters
  const buildClusterTree = () => {
    const branchesByCluster = clusterHierarchy.clusterBranches?.reduce((acc: any, b: any) => {
      if (!acc[b.cluster]) acc[b.cluster] = [];
      acc[b.cluster].push(b);
      return acc;
    }, {});

    return {
      name: "All Clusters",
      value: clusterHierarchy.clusters?.reduce((sum: number, c: any) => sum + c.total_count, 0) || 0,
      metadata: { type: "company" },
      children: clusterHierarchy.clusters?.map((cluster: any) => ({
        name: cluster.cluster,
        value: cluster.total_count,
        itemStyle: { color: "#8b5cf6" },
        metadata: {
          type: "cluster",
          cluster: cluster.cluster,
          totalCount: cluster.total_count,
          femaleCount: cluster.female_count,
          maleCount: cluster.male_count,
          avgSalary: cluster.avg_salary,
          branchCount: cluster.branch_count,
          avgTenure: cluster.avg_tenure,
        },
        children: branchesByCluster?.[cluster.cluster]?.slice(0, 15)?.map((branch: any) => ({
          name: branch.branch,
          value: branch.total_count,
          itemStyle: { color: "#a78bfa" },
          metadata: {
            type: "branch",
            cluster: cluster.cluster,
            branch: branch.branch,
            branchLevel: branch.branch_level,
            totalCount: branch.total_count,
            femaleCount: branch.female_count,
          },
        })) || [],
      })) || [],
    };
  };

  // Build tree data for Regions
  const buildRegionTree = () => {
    const districtsByRegion = regionHierarchy.regionDistricts?.reduce((acc: any, d: any) => {
      if (!acc[d.region]) acc[d.region] = [];
      acc[d.region].push(d);
      return acc;
    }, {});

    return {
      name: "All Regions",
      value: regionHierarchy.regions?.reduce((sum: number, r: any) => sum + r.total_count, 0) || 0,
      metadata: { type: "company" },
      children: regionHierarchy.regions?.map((region: any) => ({
        name: region.region,
        value: region.total_count,
        itemStyle: { color: "#06b6d4" },
        metadata: {
          type: "region",
          region: region.region,
          totalCount: region.total_count,
          femaleCount: region.female_count,
          maleCount: region.male_count,
          avgSalary: region.avg_salary,
          districtCount: region.district_count,
          branchCount: region.branch_count,
        },
        children: districtsByRegion?.[region.region]?.slice(0, 15)?.map((district: any) => ({
          name: district.district,
          value: district.total_count,
          itemStyle: { color: "#22d3ee" },
          metadata: {
            type: "district",
            region: region.region,
            district: district.district,
            totalCount: district.total_count,
            femaleCount: district.female_count,
            branchCount: district.branch_count,
          },
        })) || [],
      })) || [],
    };
  };

  // Build tree data for Divisions
  const buildDivisionTree = () => {
    const deptsByDivision = divisionHierarchy.divisionDepts?.reduce((acc: any, d: any) => {
      if (!acc[d.division]) acc[d.division] = [];
      acc[d.division].push(d);
      return acc;
    }, {});

    return {
      name: "All Divisions",
      value: divisionHierarchy.divisions?.reduce((sum: number, d: any) => sum + d.total_count, 0) || 0,
      metadata: { type: "company" },
      children: divisionHierarchy.divisions?.map((division: any) => ({
        name: division.division,
        value: division.total_count,
        itemStyle: { color: "#10b981" },
        metadata: {
          type: "division",
          division: division.division,
          totalCount: division.total_count,
          femaleCount: division.female_count,
          maleCount: division.male_count,
          avgSalary: division.avg_salary,
          deptCount: division.dept_count,
          avgTenure: division.avg_tenure,
        },
        children: deptsByDivision?.[division.division]?.slice(0, 15)?.map((dept: any) => ({
          name: dept.department,
          value: dept.total_count,
          itemStyle: { color: "#34d399" },
          metadata: {
            type: "department",
            division: division.division,
            department: dept.department,
            totalCount: dept.total_count,
            femaleCount: dept.female_count,
            avgSalary: dept.avg_salary,
          },
        })) || [],
      })) || [],
    };
  };

  // Treemap option - better for large hierarchical data
  const getTreemapOption = (treeData: any, title: string) => ({
    tooltip: {
      trigger: "item",
      formatter: (params: any) => {
        const meta = params.data?.metadata;
        let info = `<strong>${params.name}</strong><br/>`;
        info += `Employees: ${params.value}<br/>`;
        
        if (meta?.femaleCount !== undefined) {
          info += `Female: ${meta.femaleCount}<br/>`;
          info += `Male: ${meta.maleCount || 0}<br/>`;
        }
        if (meta?.avgSalary) {
          info += `Avg Salary: PKR ${Math.round(meta.avgSalary).toLocaleString()}<br/>`;
        }
        if (meta?.branchCount) {
          info += `Branches: ${meta.branchCount}<br/>`;
        }
        if (meta?.deptCount) {
          info += `Departments: ${meta.deptCount}<br/>`;
        }
        return info;
      },
    },
    title: {
      text: title,
      left: "center",
      top: 10,
      textStyle: {
        fontSize: 16,
        fontWeight: "bold",
      },
    },
    toolbox: {
      show: true,
      feature: {
        restore: {
          show: true,
          title: "Reset Zoom",
        },
      },
      right: 20,
      top: 10,
    },
    series: [
      {
        type: "treemap",
        data: treeData.children || [treeData],
        top: 60,
        left: 10,
        right: 10,
        bottom: 10,
        width: "auto",
        height: "auto",
        roam: true,
        scaleLimit: {
          min: 0.5,
          max: 10,
        },
        nodeClick: "link",
        zoom: 1,
        breadcrumb: {
          show: true,
          top: 35,
          height: 20,
          itemStyle: {
            color: "rgba(0,0,0,0.7)",
            borderColor: "rgba(255,255,255,0.7)",
            borderWidth: 1,
            textStyle: {
              color: "#fff",
            },
          },
        },
        label: {
          show: true,
          formatter: (params: any) => {
            const lines = [`{name|${params.name}}`];
            if (params.value) {
              lines.push(`{value|${params.value} emp}`);
            }
            return lines.join("\n");
          },
          rich: {
            name: {
              fontSize: 12,
              fontWeight: "bold",
              color: "#fff",
            },
            value: {
              fontSize: 10,
              color: "rgba(255,255,255,0.9)",
            },
          },
        },
        upperLabel: {
          show: true,
          height: 30,
          color: "#fff",
          fontWeight: "bold",
        },
        itemStyle: {
          borderColor: "#fff",
          borderWidth: 2,
          gapWidth: 2,
        },
        levels: [
          {
            itemStyle: {
              borderWidth: 0,
              gapWidth: 5,
            },
          },
          {
            itemStyle: {
              gapWidth: 1,
            },
            colorSaturation: [0.35, 0.5],
          },
          {
            itemStyle: {
              gapWidth: 1,
              borderColorSaturation: 0.6,
            },
            colorSaturation: [0.3, 0.5],
          },
        ],
      },
    ],
  });

  const handleNodeClick = (event: any) => {
    const clickedNode = event.data;
    if (clickedNode?.metadata?.type !== "company") {
      setSelectedNode(clickedNode);
      setShowDetailModal(true);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-card border rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-bold flex items-center gap-2 mb-4">
          <BarChart3 className="h-6 w-6 text-primary" />
          Organizational Hierarchy Treemap
        </h3>
        <p className="text-sm text-muted-foreground mb-4">
          Interactive treemap visualization - box size represents employee count. Click any section to explore details.
        </p>

        {/* Graph Type Selector */}
        <div className="flex gap-2 flex-wrap mb-6">
          {graphs.map((graph) => (
            <button
              key={graph.id}
              onClick={() => setActiveGraph(graph.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeGraph === graph.id
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted border hover:bg-muted/80"
              }`}
            >
              <span className="text-lg">{graph.icon}</span>
              {graph.label}
            </button>
          ))}
        </div>

        {/* Treemap Charts */}
        <div className="bg-background rounded-lg border p-4" style={{ height: "650px" }}>
          {activeGraph === "dept" && (
            <ReactECharts
              option={getTreemapOption(buildDeptGroupTree(), "Department Groups & Sub-Groups")}
              style={{ height: "100%", width: "100%" }}
              onEvents={{ click: handleNodeClick }}
            />
          )}
          {activeGraph === "cluster" && (
            <ReactECharts
              option={getTreemapOption(buildClusterTree(), "Clusters & Branches")}
              style={{ height: "100%", width: "100%" }}
              onEvents={{ click: handleNodeClick }}
            />
          )}
          {activeGraph === "region" && (
            <ReactECharts
              option={getTreemapOption(buildRegionTree(), "Regions & Districts")}
              style={{ height: "100%", width: "100%" }}
              onEvents={{ click: handleNodeClick }}
            />
          )}
          {activeGraph === "division" && (
            <ReactECharts
              option={getTreemapOption(buildDivisionTree(), "Divisions & Departments")}
              style={{ height: "100%", width: "100%" }}
              onEvents={{ click: handleNodeClick }}
            />
          )}
        </div>

        <div className="mt-4 p-3 bg-muted/50 rounded-lg border">
          <p className="text-xs text-muted-foreground flex items-center gap-2">
            <span className="text-base">💡</span>
            <span>
              <strong>How to use:</strong> Click on any colored box to drill down and see details. 
              <strong>Pinch or scroll</strong> to zoom in/out on small groups. Drag to pan around. 
              Click "Reset Zoom" icon (top-right) to restore view.
            </span>
          </p>
        </div>
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedNode && (
        <TreeDetailModal
          node={selectedNode}
          graphType={activeGraph}
          onClose={() => {
            setShowDetailModal(false);
            setSelectedNode(null);
          }}
        />
      )}

      {/* Summary Stats */}
      <div className="bg-card border rounded-lg p-6 shadow-sm">
        <h4 className="font-semibold mb-4">Organization Overview</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 dark:bg-blue-950/30 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <p className="text-sm text-muted-foreground">Department Groups</p>
            <p className="text-2xl font-bold">{deptGroupHierarchy.deptGroups?.length || 0}</p>
          </div>
          <div className="bg-purple-50 dark:bg-purple-950/30 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
            <p className="text-sm text-muted-foreground">Clusters</p>
            <p className="text-2xl font-bold">{clusterHierarchy.clusters?.length || 0}</p>
          </div>
          <div className="bg-cyan-50 dark:bg-cyan-950/30 p-4 rounded-lg border border-cyan-200 dark:border-cyan-800">
            <p className="text-sm text-muted-foreground">Regions</p>
            <p className="text-2xl font-bold">{regionHierarchy.regions?.length || 0}</p>
          </div>
          <div className="bg-green-50 dark:bg-green-950/30 p-4 rounded-lg border border-green-200 dark:border-green-800">
            <p className="text-sm text-muted-foreground">Divisions</p>
            <p className="text-2xl font-bold">{divisionHierarchy.divisions?.length || 0}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
