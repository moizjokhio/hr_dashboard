'use client';

import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  FileText, 
  Download, 
  FileSpreadsheet, 
  File, 
  Calendar,
  Filter,
  Loader2,
  CheckCircle,
  AlertCircle,
  Plus,
  Trash2,
  Clock,
  Eye
} from 'lucide-react';
import { api } from '@/lib/api';
import { useFilterStore } from '@/lib/store';

type ReportType = 
  | 'employee_roster'
  | 'headcount_summary'
  | 'compensation_analysis'
  | 'performance_review'
  | 'attrition_report'
  | 'diversity_report'
  | 'custom';

type ExportFormat = 'pdf' | 'word' | 'excel';

interface ReportConfig {
  id: string;
  name: string;
  description: string;
  type: ReportType;
  icon: React.ReactNode;
  availableFormats: ExportFormat[];
}

interface ScheduledReport {
  id: string;
  name: string;
  type: ReportType;
  format: ExportFormat;
  schedule: string;
  lastRun: string | null;
  nextRun: string;
  status: 'active' | 'paused';
}

interface GeneratedReport {
  id: string;
  name: string;
  type: ReportType;
  format: ExportFormat;
  generatedAt: string;
  size: string;
  status: 'ready' | 'generating' | 'failed';
}

const reportConfigs: ReportConfig[] = [
  {
    id: 'employee_roster',
    name: 'Employee Roster',
    description: 'Complete list of all employees with key details',
    type: 'employee_roster',
    icon: <FileText className="h-6 w-6" />,
    availableFormats: ['pdf', 'excel', 'word'],
  },
  {
    id: 'headcount_summary',
    name: 'Headcount Summary',
    description: 'Organization headcount by department, grade, and location',
    type: 'headcount_summary',
    icon: <FileSpreadsheet className="h-6 w-6" />,
    availableFormats: ['pdf', 'excel'],
  },
  {
    id: 'compensation_analysis',
    name: 'Compensation Analysis',
    description: 'Salary distribution, bands, and compensation trends',
    type: 'compensation_analysis',
    icon: <FileSpreadsheet className="h-6 w-6" />,
    availableFormats: ['pdf', 'excel'],
  },
  {
    id: 'performance_review',
    name: 'Performance Review',
    description: 'Employee performance scores and ratings summary',
    type: 'performance_review',
    icon: <FileText className="h-6 w-6" />,
    availableFormats: ['pdf', 'excel', 'word'],
  },
  {
    id: 'attrition_report',
    name: 'Attrition Report',
    description: 'Employee turnover analysis with risk predictions',
    type: 'attrition_report',
    icon: <FileText className="h-6 w-6" />,
    availableFormats: ['pdf', 'excel'],
  },
  {
    id: 'diversity_report',
    name: 'Diversity Report',
    description: 'Gender and demographic distribution analysis',
    type: 'diversity_report',
    icon: <FileSpreadsheet className="h-6 w-6" />,
    availableFormats: ['pdf', 'excel'],
  },
];

const formatIcons: Record<ExportFormat, React.ReactNode> = {
  pdf: <File className="h-5 w-5 text-red-500" />,
  word: <FileText className="h-5 w-5 text-blue-500" />,
  excel: <FileSpreadsheet className="h-5 w-5 text-green-500" />,
};

const formatLabels: Record<ExportFormat, string> = {
  pdf: 'PDF',
  word: 'Word',
  excel: 'Excel',
};

export default function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState<ReportConfig | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('pdf');
  const [includeCharts, setIncludeCharts] = useState(true);
  const [applyFilters, setApplyFilters] = useState(false);
  const [dateRange, setDateRange] = useState({ from: '', to: '' });
  
  const { filterBlocks } = useFilterStore();

  // Fetch recent reports
  const { data: recentReports, isLoading: loadingRecent } = useQuery<GeneratedReport[]>({
    queryKey: ['recent-reports'],
    queryFn: () => api.get('/reports/recent'),
    placeholderData: [
      {
        id: '1',
        name: 'Employee Roster - March 2024',
        type: 'employee_roster',
        format: 'excel',
        generatedAt: '2024-03-15T10:30:00Z',
        size: '2.4 MB',
        status: 'ready',
      },
      {
        id: '2',
        name: 'Compensation Analysis Q1',
        type: 'compensation_analysis',
        format: 'pdf',
        generatedAt: '2024-03-14T15:45:00Z',
        size: '1.8 MB',
        status: 'ready',
      },
    ],
  });

  // Fetch scheduled reports
  const { data: scheduledReports, isLoading: loadingScheduled } = useQuery<ScheduledReport[]>({
    queryKey: ['scheduled-reports'],
    queryFn: () => api.get('/reports/scheduled'),
    placeholderData: [
      {
        id: '1',
        name: 'Monthly Headcount',
        type: 'headcount_summary',
        format: 'excel',
        schedule: 'Monthly (1st)',
        lastRun: '2024-03-01T00:00:00Z',
        nextRun: '2024-04-01T00:00:00Z',
        status: 'active',
      },
    ],
  });

  // Generate report mutation
  const generateMutation = useMutation({
    mutationFn: async ({ type, format, options }: { 
      type: ReportType; 
      format: ExportFormat; 
      options: Record<string, unknown>;
    }) => {
      const response = await api.post(`/reports/generate/${type}`, {
        format,
        ...options,
      });
      return response;
    },
    onSuccess: (data) => {
      // Trigger download
      if (data.downloadUrl) {
        window.location.href = data.downloadUrl;
      }
    },
  });

  const handleGenerateReport = () => {
    if (!selectedReport) return;

    generateMutation.mutate({
      type: selectedReport.type,
      format: selectedFormat,
      options: {
        includeCharts,
        filters: applyFilters ? filterBlocks : [],
        dateRange: dateRange.from && dateRange.to ? dateRange : undefined,
      },
    });
  };

  const getStatusBadge = (status: 'ready' | 'generating' | 'failed') => {
    switch (status) {
      case 'ready':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
            <CheckCircle className="h-3 w-3" /> Ready
          </span>
        );
      case 'generating':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
            <Loader2 className="h-3 w-3 animate-spin" /> Generating
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-red-100 text-red-700 rounded-full">
            <AlertCircle className="h-3 w-3" /> Failed
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <p className="mt-1 text-sm text-gray-500">
          Generate and download HR reports in various formats
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Report Types */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Available Reports</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reportConfigs.map((report) => (
              <button
                key={report.id}
                onClick={() => setSelectedReport(report)}
                className={`p-4 rounded-xl border-2 text-left transition-all ${
                  selectedReport?.id === report.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-2 rounded-lg ${
                    selectedReport?.id === report.id
                      ? 'bg-indigo-100 text-indigo-600'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {report.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{report.name}</h3>
                    <p className="mt-1 text-sm text-gray-500">{report.description}</p>
                    <div className="mt-2 flex items-center gap-2">
                      {report.availableFormats.map((fmt) => (
                        <span key={fmt} className="text-xs text-gray-400 uppercase">
                          {fmt}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Report Configuration Panel */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Generate Report</h2>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
            {selectedReport ? (
              <>
                <div>
                  <h3 className="font-medium text-gray-900">{selectedReport.name}</h3>
                  <p className="text-sm text-gray-500">{selectedReport.description}</p>
                </div>

                {/* Format Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Export Format
                  </label>
                  <div className="flex gap-2">
                    {selectedReport.availableFormats.map((fmt) => (
                      <button
                        key={fmt}
                        onClick={() => setSelectedFormat(fmt)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                          selectedFormat === fmt
                            ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {formatIcons[fmt]}
                        <span className="text-sm font-medium">{formatLabels[fmt]}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Date Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="h-4 w-4 inline mr-1" />
                    Date Range (Optional)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="date"
                      value={dateRange.from}
                      onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    <input
                      type="date"
                      value={dateRange.to}
                      onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>

                {/* Options */}
                <div className="space-y-3">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={includeCharts}
                      onChange={(e) => setIncludeCharts(e.target.checked)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">Include charts and visualizations</span>
                  </label>
                  
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={applyFilters}
                      onChange={(e) => setApplyFilters(e.target.checked)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">
                      Apply current filters ({filterBlocks.length} active)
                    </span>
                  </label>
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerateReport}
                  disabled={generateMutation.isPending}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {generateMutation.isPending ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Download className="h-5 w-5" />
                      Generate & Download
                    </>
                  )}
                </button>

                {generateMutation.isError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">
                      Failed to generate report. Please try again.
                    </p>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>Select a report type to configure</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Reports */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Recent Reports</h2>
          <button className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">
            View All
          </button>
        </div>
        
        {loadingRecent ? (
          <div className="p-8 text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-indigo-600" />
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {recentReports?.map((report) => (
              <div 
                key={report.id}
                className="p-4 flex items-center justify-between hover:bg-gray-50"
              >
                <div className="flex items-center gap-4">
                  {formatIcons[report.format]}
                  <div>
                    <h3 className="font-medium text-gray-900">{report.name}</h3>
                    <p className="text-sm text-gray-500">
                      {new Date(report.generatedAt).toLocaleDateString()} • {report.size}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {getStatusBadge(report.status)}
                  {report.status === 'ready' && (
                    <div className="flex items-center gap-2">
                      <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="p-2 text-indigo-600 hover:text-indigo-700 rounded-lg hover:bg-indigo-50">
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {(!recentReports || recentReports.length === 0) && (
              <div className="p-8 text-center text-gray-500">
                <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No recent reports</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Scheduled Reports */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Scheduled Reports</h2>
          <button className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg">
            <Plus className="h-4 w-4" />
            Add Schedule
          </button>
        </div>
        
        {loadingScheduled ? (
          <div className="p-8 text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-indigo-600" />
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {scheduledReports?.map((report) => (
              <div 
                key={report.id}
                className="p-4 flex items-center justify-between hover:bg-gray-50"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <Clock className="h-5 w-5 text-gray-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{report.name}</h3>
                    <p className="text-sm text-gray-500">
                      {report.schedule} • Next: {new Date(report.nextRun).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    report.status === 'active' 
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {report.status === 'active' ? 'Active' : 'Paused'}
                  </span>
                  <div className="flex items-center gap-1">
                    {formatIcons[report.format]}
                    <span className="text-xs text-gray-500 uppercase">{report.format}</span>
                  </div>
                  <button className="p-2 text-gray-400 hover:text-red-500 rounded-lg hover:bg-gray-100">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
            
            {(!scheduledReports || scheduledReports.length === 0) && (
              <div className="p-8 text-center text-gray-500">
                <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No scheduled reports</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
