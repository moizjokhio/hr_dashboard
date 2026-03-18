'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Loader2, AlertTriangle, Clock, FileX } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { getProcessFairness, type DAMISFilters } from '@/lib/da-mis-api';

interface ProcessFairnessSectionProps {
  filters: DAMISFilters;
}

export function ProcessFairnessSection({ filters }: ProcessFairnessSectionProps) {
  const [fairness, setFairness] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFairness();
  }, [filters]);

  const loadFairness = async () => {
    try {
      setLoading(true);
      const data = await getProcessFairness({
        year: filters.year,
      });
      setFairness(data);
    } catch (error) {
      console.error('Error loading process fairness:', error);
    } finally {
      setLoading(false);
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

  if (!fairness) {
    return <div>No data available</div>;
  }

  // Calculate completion rates
  const totalCases = fairness.lifecycle_funnel[0]?.count || 0;
  const completedCases = fairness.lifecycle_funnel[fairness.lifecycle_funnel.length - 1]?.count || 0;
  const completionRate = totalCases > 0 ? ((completedCases / totalCases) * 100).toFixed(1) : 0;

  const FUNNEL_COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Pending Decisions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{fairness.pending_decisions}</div>
            <p className="text-xs mt-1 opacity-90">Cases awaiting DAC decision</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <FileX className="h-4 w-4 mr-2" />
              Missing Letters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{fairness.missing_punishment_letters}</div>
            <p className="text-xs mt-1 opacity-90">Implemented without letter</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <Clock className="h-4 w-4 mr-2" />
              Completion Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{completionRate}%</div>
            <p className="text-xs mt-1 opacity-90">{completedCases} of {totalCases} cases</p>
          </CardContent>
        </Card>
      </div>

      {/* Lifecycle Funnel */}
      <Card>
        <CardHeader>
          <CardTitle>HR Process Lifecycle Funnel</CardTitle>
          <p className="text-sm text-gray-600">
            Track cases through the disciplinary process stages
          </p>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={fairness.lifecycle_funnel} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="stage" type="category" width={200} />
              <Tooltip />
              <Bar dataKey="count">
                {fairness.lifecycle_funnel.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={FUNNEL_COLORS[index % FUNNEL_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Funnel Visualization */}
          <div className="mt-6 space-y-3">
            {fairness.lifecycle_funnel.map((stage: any, idx: number) => {
              const percentage = totalCases > 0 ? ((stage.count / totalCases) * 100).toFixed(1) : 0;
              const dropOff = idx > 0 
                ? fairness.lifecycle_funnel[idx - 1].count - stage.count 
                : 0;
              
              return (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">{stage.stage}</span>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{stage.count} cases</Badge>
                      <Badge variant="outline">{percentage}%</Badge>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="h-4 rounded-full transition-all"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: FUNNEL_COLORS[idx % FUNNEL_COLORS.length],
                      }}
                    />
                  </div>
                  {dropOff > 0 && (
                    <p className="text-xs text-red-600">
                      ↓ {dropOff} cases dropped ({((dropOff / fairness.lifecycle_funnel[idx - 1].count) * 100).toFixed(1)}% attrition)
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Process Issues */}
      <Card className="border-2 border-yellow-500">
        <CardHeader>
          <CardTitle className="flex items-center text-yellow-700">
            <AlertTriangle className="h-5 w-5 mr-2" />
            Process Gaps & Issues
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {fairness.pending_decisions > 0 && (
              <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4">
                <div className="flex items-start">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-semibold text-yellow-800">Pending DAC Decisions</h4>
                    <p className="text-sm text-yellow-700 mt-1">
                      {fairness.pending_decisions} cases are awaiting Disciplinary Action Committee decisions.
                      This may indicate backlog or delays in the review process.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {fairness.missing_punishment_letters > 0 && (
              <div className="bg-red-50 border-l-4 border-red-500 p-4">
                <div className="flex items-start">
                  <FileX className="h-5 w-5 text-red-600 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-semibold text-red-800">Missing Punishment Letters</h4>
                    <p className="text-sm text-red-700 mt-1">
                      {fairness.missing_punishment_letters} cases have implemented punishments without formal letters.
                      This creates compliance and documentation risks.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {parseFloat(completionRate as string) < 70 && (
              <div className="bg-orange-50 border-l-4 border-orange-500 p-4">
                <div className="flex items-start">
                  <Clock className="h-5 w-5 text-orange-600 mt-0.5 mr-3" />
                  <div>
                    <h4 className="font-semibold text-orange-800">Low Completion Rate</h4>
                    <p className="text-sm text-orange-700 mt-1">
                      Only {completionRate}% of cases are fully completed. Consider reviewing process
                      efficiency and identifying bottlenecks.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {fairness.pending_decisions === 0 && 
             fairness.missing_punishment_letters === 0 && 
             parseFloat(completionRate as string) >= 70 && (
              <div className="bg-green-50 border-l-4 border-green-500 p-4">
                <div className="flex items-start">
                  <div className="h-5 w-5 bg-green-500 rounded-full flex items-center justify-center mr-3 mt-0.5">
                    <span className="text-white text-xs">✓</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-green-800">Process Health: Good</h4>
                    <p className="text-sm text-green-700 mt-1">
                      No major process gaps detected. Continue monitoring for consistency.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
