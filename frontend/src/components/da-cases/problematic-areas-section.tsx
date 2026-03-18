'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Loader2, ChevronRight } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { getLocationHierarchy, getCases, type DAMISFilters, type DAMISCase } from '@/lib/da-mis-api';

interface ProblematicAreasSectionProps {
  filters: DAMISFilters;
}

export function ProblematicAreasSection({ filters }: ProblematicAreasSectionProps) {
  const [clusterData, setClusterData] = useState<any[]>([]);
  const [regionData, setRegionData] = useState<any[]>([]);
  const [branchData, setBranchData] = useState<any[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailDrawerOpen, setDetailDrawerOpen] = useState(false);
  const [detailCases, setDetailCases] = useState<DAMISCase[]>([]);
  const [metric, setMetric] = useState<'case_count' | 'people_count'>('case_count');

  useEffect(() => {
    loadClusterData();
  }, [filters, metric]);

  useEffect(() => {
    if (selectedCluster) {
      loadRegionData(selectedCluster);
    }
  }, [selectedCluster, filters, metric]);

  useEffect(() => {
    if (selectedRegion) {
      loadBranchData(selectedRegion);
    }
  }, [selectedRegion, filters, metric]);

  const loadClusterData = async () => {
    try {
      setLoading(true);
      const data = await getLocationHierarchy('cluster', metric, {
        year: filters.year,
        quarter: filters.quarter,
      });
      setClusterData(data.data);
    } catch (error) {
      console.error('Error loading cluster data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRegionData = async (cluster: string) => {
    try {
      const data = await getLocationHierarchy('region', metric, {
        parent_cluster: cluster,
        year: filters.year,
        quarter: filters.quarter,
      });
      setRegionData(data.data);
    } catch (error) {
      console.error('Error loading region data:', error);
    }
  };

  const loadBranchData = async (region: string) => {
    try {
      const data = await getLocationHierarchy('branch', metric, {
        parent_cluster: selectedCluster || undefined,
        parent_region: region,
        year: filters.year,
        quarter: filters.quarter,
      });
      setBranchData(data.data);
    } catch (error) {
      console.error('Error loading branch data:', error);
    }
  };

  const handleClusterClick = (cluster: string) => {
    setSelectedCluster(cluster);
    setSelectedRegion(null);
    setBranchData([]);
  };

  const handleRegionClick = (region: string) => {
    setSelectedRegion(region);
  };

  const handleBranchClick = async (branch: string) => {
    try {
      const combinedFilters = {
        ...filters,
        cluster: selectedCluster || undefined,
        region: selectedRegion || undefined,
        branch_office: branch,
      };
      const response = await getCases(1, 100, combinedFilters);
      setDetailCases(response.cases);
      setDetailDrawerOpen(true);
    } catch (error) {
      console.error('Error loading branch details:', error);
    }
  };

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Cluster Level */}
        <Card className={selectedCluster ? 'ring-2 ring-blue-500' : ''}>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Cluster Level
              <span className="text-sm font-normal text-gray-600">
                {metric === 'case_count' ? 'Cases' : 'People'}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={clusterData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar
                  dataKey="count"
                  onClick={(data: any) => handleClusterClick(data.name)}
                  cursor="pointer"
                >
                  {clusterData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={selectedCluster === entry.name ? '#ef4444' : COLORS[index % COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Region Level */}
        <Card className={selectedRegion ? 'ring-2 ring-purple-500' : ''}>
          <CardHeader>
            <CardTitle className="flex items-center">
              Region Level
              {selectedCluster && (
                <span className="ml-2 text-sm font-normal text-blue-600">
                  ({selectedCluster})
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {regionData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={regionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar
                    dataKey="count"
                    onClick={(data: any) => handleRegionClick(data.name)}
                    cursor="pointer"
                  >
                    {regionData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={selectedRegion === entry.name ? '#ef4444' : COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                <div className="text-center">
                  <ChevronRight className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Select a cluster to view regions</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Branch Level */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              Branch Level
              {selectedRegion && (
                <span className="ml-2 text-sm font-normal text-purple-600">
                  ({selectedRegion})
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {branchData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={branchData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar
                    dataKey="count"
                    onClick={(data: any) => data?.name && handleBranchClick(data.name)}
                    cursor="pointer"
                    fill="#ec4899"
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                <div className="text-center">
                  <ChevronRight className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Select a region to view branches</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Detail Drawer */}
      <Sheet open={detailDrawerOpen} onOpenChange={setDetailDrawerOpen}>
        <SheetContent className="w-full sm:max-w-3xl overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Branch Detail Cases</SheetTitle>
          </SheetHeader>
          <div className="mt-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Case #</TableHead>
                  <TableHead>Emp. #</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Grade</TableHead>
                  <TableHead>Misconduct</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {detailCases.map((c, idx) => (
                  <TableRow key={idx}>
                    <TableCell>{c['Case #']}</TableCell>
                    <TableCell>{c['Emp. #']}</TableCell>
                    <TableCell>{c['Name of Staff Reported']}</TableCell>
                    <TableCell>{c['Grade']}</TableCell>
                    <TableCell>{c['Misconduct Category']}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
