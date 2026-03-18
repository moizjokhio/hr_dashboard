"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Users, TrendingUp, DollarSign, Building2, MapPin } from "lucide-react";
import { useRouter } from "next/navigation";

interface HierarchicalHeadcountProps {
  deptGroupHierarchy: any;
  clusterHierarchy: any;
  regionHierarchy: any;
  divisionHierarchy: any;
}

export function HierarchicalHeadcount({
  deptGroupHierarchy,
  clusterHierarchy,
  regionHierarchy,
  divisionHierarchy,
}: HierarchicalHeadcountProps) {
  const [activeSection, setActiveSection] = useState<string>("dept");

  const sections = [
    { id: "dept", label: "Department Groups", icon: Building2 },
    { id: "cluster", label: "Clusters", icon: MapPin },
    { id: "region", label: "Regions", icon: MapPin },
    { id: "division", label: "Divisions", icon: Building2 },
  ];

  return (
    <div className="space-y-6">
      {/* Section Selector */}
      <div className="flex gap-2 flex-wrap">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeSection === section.id
                ? "bg-primary text-primary-foreground"
                : "bg-card border hover:bg-muted"
            }`}
          >
            <section.icon className="h-4 w-4" />
            {section.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeSection === "dept" && <DeptGroupView data={deptGroupHierarchy} />}
      {activeSection === "cluster" && <ClusterView data={clusterHierarchy} />}
      {activeSection === "region" && <RegionView data={regionHierarchy} />}
      {activeSection === "division" && <DivisionView data={divisionHierarchy} />}
    </div>
  );
}

// Department Group View
function DeptGroupView({ data }: { data: any }) {
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const router = useRouter();

  const toggleGroup = (group: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(group)) {
      newExpanded.delete(group);
    } else {
      newExpanded.add(group);
    }
    setExpandedGroups(newExpanded);
  };

  const handleSubGroupClick = (deptGroup: string, subGroup: string) => {
    router.push(`/employee-details?dept_group=${encodeURIComponent(deptGroup)}&sub_group=${encodeURIComponent(subGroup)}`);
  };

  // Group sub-groups by dept_group
  const subGroupsByDept = data.subGroups?.reduce((acc: any, sg: any) => {
    if (!acc[sg.dept_group]) acc[sg.dept_group] = [];
    acc[sg.dept_group].push(sg);
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold flex items-center gap-2">
        <Building2 className="h-6 w-6 text-primary" />
        Headcount by Department Group
      </h3>

      <div className="grid gap-3">
        {data.deptGroups?.map((group: any) => (
          <div key={group.dept_group} className="bg-card border rounded-lg overflow-hidden shadow-sm">
            {/* Department Group Header */}
            <div
              onClick={() => toggleGroup(group.dept_group)}
              className="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {expandedGroups.has(group.dept_group) ? (
                    <ChevronDown className="h-5 w-5 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-muted-foreground" />
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg">{group.dept_group}</h4>
                    <div className="flex gap-6 mt-1 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        {group.total_count} employees
                      </span>
                      <span className="text-pink-600">
                        {group.female_count} Female ({((group.female_count / group.total_count) * 100).toFixed(1)}%)
                      </span>
                      <span className="text-blue-600">
                        {group.male_count} Male ({((group.male_count / group.total_count) * 100).toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <DollarSign className="h-4 w-4" />
                    <span>Avg Salary</span>
                  </div>
                  <div className="text-lg font-semibold text-green-600">
                    PKR {group.avg_salary?.toLocaleString() || 0}
                  </div>
                </div>
              </div>
            </div>

            {/* Sub-groups (Expandable) */}
            {expandedGroups.has(group.dept_group) && subGroupsByDept[group.dept_group] && (
              <div className="bg-muted/30 px-4 py-2 border-t">
                <div className="grid gap-2 ml-8">
                  {subGroupsByDept[group.dept_group].map((subGroup: any) => (
                    <div
                      key={subGroup.sub_group}
                      onClick={() => handleSubGroupClick(group.dept_group, subGroup.sub_group)}
                      className="p-3 bg-card rounded-lg hover:bg-primary/10 cursor-pointer transition-colors border border-transparent hover:border-primary"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium">{subGroup.sub_group}</h5>
                          <div className="flex gap-4 mt-1 text-sm text-muted-foreground">
                            <span>{subGroup.total_count} employees</span>
                            <span className="text-pink-600">{subGroup.female_count} F</span>
                            <span className="text-blue-600">{subGroup.male_count} M</span>
                          </div>
                        </div>
                        <div className="text-right text-sm">
                          <span className="text-green-600 font-medium">
                            PKR {subGroup.avg_salary?.toLocaleString() || 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Cluster View
function ClusterView({ data }: { data: any }) {
  const [expandedClusters, setExpandedClusters] = useState<Set<string>>(new Set());

  const toggleCluster = (cluster: string) => {
    const newExpanded = new Set(expandedClusters);
    if (newExpanded.has(cluster)) {
      newExpanded.delete(cluster);
    } else {
      newExpanded.add(cluster);
    }
    setExpandedClusters(newExpanded);
  };

  // Group branches by cluster
  const branchesByCluster = data.clusterBranches?.reduce((acc: any, branch: any) => {
    if (!acc[branch.cluster]) acc[branch.cluster] = [];
    acc[branch.cluster].push(branch);
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold flex items-center gap-2">
        <MapPin className="h-6 w-6 text-primary" />
        Headcount by Cluster
      </h3>

      <div className="grid gap-3">
        {data.clusters?.map((cluster: any) => (
          <div key={cluster.cluster} className="bg-card border rounded-lg overflow-hidden shadow-sm">
            {/* Cluster Header */}
            <div
              onClick={() => toggleCluster(cluster.cluster)}
              className="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {expandedClusters.has(cluster.cluster) ? (
                    <ChevronDown className="h-5 w-5 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-muted-foreground" />
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg">{cluster.cluster}</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-blue-500" />
                        <span className="text-sm">
                          <span className="font-semibold">{cluster.total_count}</span> employees
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-purple-500" />
                        <span className="text-sm">
                          <span className="font-semibold">{cluster.branch_count}</span> branches
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <DollarSign className="h-4 w-4 text-green-500" />
                        <span className="text-sm">
                          PKR <span className="font-semibold">{cluster.avg_salary?.toLocaleString()}</span>
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-amber-500" />
                        <span className="text-sm">
                          <span className="font-semibold">{cluster.avg_tenure}</span> yrs tenure
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-4 mt-2 text-sm">
                      <span className="text-pink-600 font-medium">
                        {cluster.female_count} Female ({((cluster.female_count / cluster.total_count) * 100).toFixed(1)}%)
                      </span>
                      <span className="text-blue-600 font-medium">
                        {cluster.male_count} Male ({((cluster.male_count / cluster.total_count) * 100).toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Branches (Expandable) */}
            {expandedClusters.has(cluster.cluster) && branchesByCluster[cluster.cluster] && (
              <div className="bg-muted/30 px-4 py-3 border-t">
                <h5 className="text-sm font-semibold mb-2 ml-8">Branches in {cluster.cluster}</h5>
                <div className="grid gap-2 ml-8 max-h-96 overflow-y-auto">
                  {branchesByCluster[cluster.cluster].map((branch: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 bg-card rounded-lg border hover:border-primary transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h6 className="font-medium">{branch.branch}</h6>
                          <div className="flex gap-4 mt-1 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                              {branch.branch_level || "N/A"}
                            </span>
                            <span>{branch.total_count} employees</span>
                            <span className="text-pink-600">{branch.female_count} Female</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Region View
function RegionView({ data }: { data: any }) {
  const [expandedRegions, setExpandedRegions] = useState<Set<string>>(new Set());

  const toggleRegion = (region: string) => {
    const newExpanded = new Set(expandedRegions);
    if (newExpanded.has(region)) {
      newExpanded.delete(region);
    } else {
      newExpanded.add(region);
    }
    setExpandedRegions(newExpanded);
  };

  // Group districts by region
  const districtsByRegion = data.regionDistricts?.reduce((acc: any, district: any) => {
    if (!acc[district.region]) acc[district.region] = [];
    acc[district.region].push(district);
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold flex items-center gap-2">
        <MapPin className="h-6 w-6 text-primary" />
        Headcount by Region
      </h3>

      <div className="grid gap-3">
        {data.regions?.map((region: any) => (
          <div key={region.region} className="bg-card border rounded-lg overflow-hidden shadow-sm">
            {/* Region Header */}
            <div
              onClick={() => toggleRegion(region.region)}
              className="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {expandedRegions.has(region.region) ? (
                    <ChevronDown className="h-5 w-5 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-muted-foreground" />
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg">{region.region}</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-blue-500" />
                        <span className="text-sm">
                          <span className="font-semibold">{region.total_count}</span> employees
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-purple-500" />
                        <span className="text-sm">
                          <span className="font-semibold">{region.district_count}</span> districts
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-amber-500" />
                        <span className="text-sm">
                          <span className="font-semibold">{region.branch_count}</span> branches
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <DollarSign className="h-4 w-4 text-green-500" />
                        <span className="text-sm">
                          PKR <span className="font-semibold">{region.avg_salary?.toLocaleString()}</span>
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-4 mt-2 text-sm">
                      <span className="text-pink-600 font-medium">
                        {region.female_count} Female ({((region.female_count / region.total_count) * 100).toFixed(1)}%)
                      </span>
                      <span className="text-blue-600 font-medium">
                        {region.male_count} Male ({((region.male_count / region.total_count) * 100).toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Districts (Expandable) */}
            {expandedRegions.has(region.region) && districtsByRegion[region.region] && (
              <div className="bg-muted/30 px-4 py-3 border-t">
                <h5 className="text-sm font-semibold mb-2 ml-8">Districts in {region.region}</h5>
                <div className="grid gap-2 ml-8 max-h-96 overflow-y-auto">
                  {districtsByRegion[region.region].map((district: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 bg-card rounded-lg border hover:border-primary transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h6 className="font-medium">{district.district}</h6>
                          <div className="flex gap-4 mt-1 text-sm text-muted-foreground">
                            <span>{district.total_count} employees</span>
                            <span className="text-pink-600">{district.female_count} Female</span>
                            <span>{district.branch_count} branches</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Division View
function DivisionView({ data }: { data: any }) {
  const [expandedDivisions, setExpandedDivisions] = useState<Set<string>>(new Set());

  const toggleDivision = (division: string) => {
    const newExpanded = new Set(expandedDivisions);
    if (newExpanded.has(division)) {
      newExpanded.delete(division);
    } else {
      newExpanded.add(division);
    }
    setExpandedDivisions(newExpanded);
  };

  // Group departments by division
  const deptsByDivision = data.divisionDepts?.reduce((acc: any, dept: any) => {
    if (!acc[dept.division]) acc[dept.division] = [];
    acc[dept.division].push(dept);
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold flex items-center gap-2">
        <Building2 className="h-6 w-6 text-primary" />
        Headcount by Division
      </h3>

      <div className="grid gap-3">
        {data.divisions?.map((division: any) => (
          <div key={division.division} className="bg-card border rounded-lg overflow-hidden shadow-sm">
            {/* Division Header */}
            <div
              onClick={() => toggleDivision(division.division)}
              className="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {expandedDivisions.has(division.division) ? (
                    <ChevronDown className="h-5 w-5 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-muted-foreground" />
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg">{division.division}</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-blue-500" />
                        <span className="text-sm">
                          <span className="font-semibold">{division.total_count}</span> employees
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-purple-500" />
                        <span className="text-sm">
                          <span className="font-semibold">{division.dept_count}</span> departments
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <DollarSign className="h-4 w-4 text-green-500" />
                        <span className="text-sm">
                          PKR <span className="font-semibold">{division.avg_salary?.toLocaleString()}</span>
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-amber-500" />
                        <span className="text-sm">
                          <span className="font-semibold">{division.avg_tenure}</span> yrs tenure
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-4 mt-2 text-sm">
                      <span className="text-pink-600 font-medium">
                        {division.female_count} Female ({((division.female_count / division.total_count) * 100).toFixed(1)}%)
                      </span>
                      <span className="text-blue-600 font-medium">
                        {division.male_count} Male ({((division.male_count / division.total_count) * 100).toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Departments (Expandable) */}
            {expandedDivisions.has(division.division) && deptsByDivision[division.division] && (
              <div className="bg-muted/30 px-4 py-3 border-t">
                <h5 className="text-sm font-semibold mb-2 ml-8">Departments in {division.division}</h5>
                <div className="grid gap-2 ml-8 max-h-96 overflow-y-auto">
                  {deptsByDivision[division.division].map((dept: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 bg-card rounded-lg border hover:border-primary transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h6 className="font-medium">{dept.department}</h6>
                          <div className="flex gap-4 mt-1 text-sm text-muted-foreground">
                            <span>{dept.total_count} employees</span>
                            <span className="text-pink-600">{dept.female_count} Female</span>
                          </div>
                        </div>
                        <div className="text-sm text-green-600 font-medium">
                          PKR {dept.avg_salary?.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
