'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Loader2 } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { getMisconductAnalysis, type DAMISFilters } from '@/lib/da-mis-api';

interface MisconductIntelligenceSectionProps {
  filters: DAMISFilters;
}

export function MisconductIntelligenceSection({ filters }: MisconductIntelligenceSectionProps) {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  useEffect(() => {
    loadAnalysis();
  }, [filters]);

  const loadAnalysis = async () => {
    try {
      setLoading(true);
      const data = await getMisconductAnalysis({
        year: filters.year,
        cluster: filters.cluster,
      });
      setAnalysis(data);
    } catch (error) {
      console.error('Error loading misconduct analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#f43f5e', '#8b5cf6'];

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </CardContent>
      </Card>
    );
  }

  if (!analysis) {
    return <div>No data available</div>;
  }

  const gradeData = Object.entries(analysis.grade_breakdown || {}).map(([grade, count]) => ({
    name: grade,
    value: count as number,
  }));

  const ftData = Object.entries(analysis.ft_breakdown || {}).map(([ft, count]) => ({
    name: ft || 'Unknown',
    value: count as number,
  }));

  return (
    <div className="space-y-6">
      {/* Top Misconduct Categories */}
      <Card>
        <CardHeader>
          <CardTitle>Most Common Misconduct Categories</CardTitle>
          <p className="text-sm text-gray-600">Click on a category to see breakdown</p>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={analysis.most_common_categories}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" angle={-45} textAnchor="end" height={120} />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey="count"
                onClick={(data: any) => setSelectedCategory(data.category)}
                cursor="pointer"
              >
                {analysis.most_common_categories.map((entry: any, index: number) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={selectedCategory === entry.category ? '#ef4444' : COLORS[index % COLORS.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Most Severe Misconducts */}
      <Card>
        <CardHeader>
          <CardTitle>Most Severe Misconducts (by Punishment)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analysis.most_severe_misconducts.slice(0, 10).map((item: any, idx: number) => (
              <div key={idx} className="border-l-4 border-red-500 pl-4 py-2 bg-red-50">
                <div className="font-semibold text-sm">{item.misconduct}</div>
                <div className="text-xs text-gray-600 mt-1">
                  Punishment: {item.punishment} • Cases: {item.count}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Breakdown Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Grade Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Grade-wise Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={gradeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {gradeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* FT vs Non-FT */}
        <Card>
          <CardHeader>
            <CardTitle>FT vs Non-FT Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ftData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Selected Category Details */}
      {selectedCategory && (
        <Card className="border-2 border-blue-500">
          <CardHeader>
            <CardTitle>Deep Dive: {selectedCategory}</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="grade">
              <TabsList>
                <TabsTrigger value="grade">By Grade</TabsTrigger>
                <TabsTrigger value="ft">By FT Status</TabsTrigger>
              </TabsList>
              <TabsContent value="grade">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={gradeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </TabsContent>
              <TabsContent value="ft">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={ftData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#8b5cf6" />
                  </BarChart>
                </ResponsiveContainer>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
