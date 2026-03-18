'use client';

import { useState, useEffect } from 'react';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Loader2, ShieldAlert } from 'lucide-react';
import { 
  getDashboardSummary, 
  getFilterOptions,
  type DashboardSummary,
  type FilterOptions,
  type DAMISFilters 
} from '@/lib/da-mis-api';
import { PivotTableSection } from '@/components/da-cases/pivot-table-section';
import { ProblematicAreasSection } from '@/components/da-cases/problematic-areas-section';
import { MisconductIntelligenceSection } from '@/components/da-cases/misconduct-intelligence-section';
import { ProcessFairnessSection } from '@/components/da-cases/process-fairness-section';
import { GlobalFilters } from '@/components/da-cases/global-filters';

export default function DACasesPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [activeFilters, setActiveFilters] = useState<DAMISFilters>({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [summaryData, options] = await Promise.all([
        getDashboardSummary(),
        getFilterOptions(),
      ]);
      setSummary(summaryData);
      setFilterOptions(options);
    } catch (error) {
      console.error('Error loading DA MIS data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (filters: DAMISFilters) => {
    setActiveFilters(filters);
  };

  if (loading) {
    return (
      <div className="flex h-screen bg-background">
        <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
          <main className="flex-1 flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        <main className="flex-1 overflow-auto">
          {/* Page header */}
          <div className="bg-card border-b px-6 py-4">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-red-500/10 rounded-lg">
                <ShieldAlert className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Disciplinary Action Cases</h1>
                <p className="text-sm text-muted-foreground">
                  Management & Intelligence System for DA Cases
                </p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Summary Cards */}
            {summary && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Total Cases</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{summary.total_cases}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-muted-foreground">People Involved</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{summary.total_people_involved}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Pending Decisions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{summary.pending_decisions}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Completion Rate</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{summary.completion_rate}%</div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Global Filters */}
            {filterOptions && (
              <GlobalFilters
                options={filterOptions}
                onFilterChange={handleFilterChange}
                activeFilters={activeFilters}
              />
            )}

            {/* Main Content Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="problematic-areas">Problematic Areas</TabsTrigger>
                <TabsTrigger value="misconduct">Misconduct Intelligence</TabsTrigger>
                <TabsTrigger value="process">HR Process & Fairness</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <PivotTableSection filters={activeFilters} />
              </TabsContent>

              <TabsContent value="problematic-areas" className="space-y-4">
                <ProblematicAreasSection filters={activeFilters} />
              </TabsContent>

              <TabsContent value="misconduct" className="space-y-4">
                <MisconductIntelligenceSection filters={activeFilters} />
              </TabsContent>

              <TabsContent value="process" className="space-y-4">
                <ProcessFairnessSection filters={activeFilters} />
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>
    </div>
  );
}
