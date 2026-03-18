'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Loader2 } from 'lucide-react';
import { getCases, type DAMISCase, type DAMISFilters } from '@/lib/da-mis-api';

interface PivotTableSectionProps {
  filters: DAMISFilters;
}

export function PivotTableSection({ filters }: PivotTableSectionProps) {
  const [pivotData, setPivotData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCell, setSelectedCell] = useState<any>(null);
  const [detailCases, setDetailCases] = useState<DAMISCase[]>([]);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    loadPivotData();
  }, [filters]);

  const loadPivotData = async () => {
    try {
      setLoading(true);
      // For simplicity, we'll fetch cases and build pivot table client-side
      // In production, you'd want to use the pivot-table API endpoint
      const response = await getCases(1, 500, filters);
      buildPivotTable(response.cases);
    } catch (error) {
      console.error('Error loading pivot data:', error);
    } finally {
      setLoading(false);
    }
  };

  const buildPivotTable = (cases: DAMISCase[]) => {
    // Build pivot: Rows = DAC Decision, Columns = Grade
    const pivot: any = {};
    const grades = new Set<string>();
    
    cases.forEach((c) => {
      const rowKey = c['DAC Decision'] || 'Unknown';
      const grade = c['Grade'] || 'Unknown';
      
      grades.add(grade);
      
      if (!pivot[rowKey]) {
        pivot[rowKey] = { rowKey, grades: {}, caseCount: 0, peopleCount: new Set() };
      }
      
      if (!pivot[rowKey].grades[grade]) {
        pivot[rowKey].grades[grade] = { caseCount: 0, peopleCount: new Set(), cases: [] };
      }
      
      pivot[rowKey].grades[grade].caseCount++;
      pivot[rowKey].grades[grade].cases.push(c);
      
      if (c['Emp. #']) {
        pivot[rowKey].grades[grade].peopleCount.add(c['Emp. #']);
        pivot[rowKey].peopleCount.add(c['Emp. #']);
      }
      
      pivot[rowKey].caseCount++;
    });
    
    const pivotArray = Object.values(pivot).map((row: any) => ({
      ...row,
      peopleCount: row.peopleCount.size,
      grades: Object.fromEntries(
        Object.entries(row.grades).map(([grade, data]: [string, any]) => [
          grade,
          { ...data, peopleCount: data.peopleCount.size }
        ])
      )
    }));
    
    setPivotData(pivotArray);
  };

  const handleCellClick = (row: any, grade: string) => {
    const cellData = row.grades[grade];
    if (cellData && cellData.cases.length > 0) {
      setDetailCases(cellData.cases);
      setSelectedCell({ row: row.rowKey, grade, ...cellData });
      setDrawerOpen(true);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </CardContent>
      </Card>
    );
  }

  const allGrades = Array.from(
    new Set(pivotData.flatMap(row => Object.keys(row.grades)))
  ).sort();

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Interactive Pivot Table - Case & People Involvement</CardTitle>
          <p className="text-sm text-gray-600">
            Rows: DAC Decision • Columns: Grade • Click cells for details
          </p>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="font-bold">DAC Decision</TableHead>
                  {allGrades.map(grade => (
                    <TableHead key={grade} className="text-center font-bold">
                      {grade}
                    </TableHead>
                  ))}
                  <TableHead className="text-center font-bold bg-blue-50">Total Cases</TableHead>
                  <TableHead className="text-center font-bold bg-purple-50">Total People</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pivotData.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={allGrades.length + 3} className="text-center py-8 text-gray-500">
                      No data available. Try adjusting filters or ensure data is loaded.
                    </TableCell>
                  </TableRow>
                ) : (
                  pivotData.map((row, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-medium">{row.rowKey}</TableCell>
                    {allGrades.map(grade => {
                      const cell = row.grades[grade];
                      return (
                        <TableCell
                          key={grade}
                          className="text-center cursor-pointer hover:bg-blue-100 transition-colors"
                          onClick={() => handleCellClick(row, grade)}
                        >
                          {cell ? (
                            <div className="space-y-1">
                              <div className="text-sm font-semibold text-blue-600">
                                {cell.caseCount}
                              </div>
                              <div className="text-xs text-purple-600">
                                ({cell.peopleCount})
                              </div>
                            </div>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                      );
                    })}
                    <TableCell className="text-center font-semibold bg-blue-50">
                      {row.caseCount}
                    </TableCell>
                    <TableCell className="text-center font-semibold bg-purple-50">
                      {row.peopleCount}
                    </TableCell>
                  </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Detail Drawer */}
      <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
        <SheetContent className="w-full sm:max-w-2xl overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Case Details</SheetTitle>
            {selectedCell && (
              <div className="text-sm text-gray-600">
                {selectedCell.row} • {selectedCell.grade} • {selectedCell.caseCount} cases, {selectedCell.peopleCount} people
              </div>
            )}
          </SheetHeader>
          <div className="mt-6 space-y-4">
            {detailCases.map((c, idx) => (
              <Card key={idx}>
                <CardContent className="pt-6 space-y-2">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div><span className="font-semibold">Case #:</span> {c['Case #']}</div>
                    <div><span className="font-semibold">Emp. #:</span> {c['Emp. #']}</div>
                    <div className="col-span-2"><span className="font-semibold">Name:</span> {c['Name of Staff Reported']}</div>
                    <div><span className="font-semibold">Grade:</span> {c['Grade']}</div>
                    <div><span className="font-semibold">FT:</span> {c['FT']}</div>
                    <div><span className="font-semibold">Branch:</span> {c['Branch / Office']}</div>
                    <div><span className="font-semibold">Region:</span> {c['Region']}</div>
                    <div><span className="font-semibold">Cluster:</span> {c['Cluster']}</div>
                    <div className="col-span-2"><span className="font-semibold">Misconduct Category:</span> {c['Misconduct Category']}</div>
                    <div className="col-span-2"><span className="font-semibold">Misconduct:</span> {c['Misconduct']}</div>
                    <div className="col-span-2"><span className="font-semibold">DAC Decision:</span> {c['DAC Decision']}</div>
                    <div className="col-span-2"><span className="font-semibold">Punishment:</span> {c['Punishment Implementation']}</div>
                    <div><span className="font-semibold">Year:</span> {c['Year']}</div>
                    <div><span className="font-semibold">Quarter:</span> {c['Quarter']}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
