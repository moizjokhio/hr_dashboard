'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Settings,
  Database,
  Cpu,
  HardDrive,
  Users,
  Shield,
  Bell,
  Palette,
  RefreshCw,
  Check,
  AlertTriangle,
  Loader2,
  Save,
  RotateCcw,
  Download,
  Upload,
  Trash2,
  Key,
  Globe,
  Clock
} from 'lucide-react';
import { api } from '@/lib/api';

interface SystemStatus {
  database: {
    status: 'healthy' | 'degraded' | 'down';
    connections: number;
    maxConnections: number;
    latencyMs: number;
  };
  cache: {
    status: 'healthy' | 'degraded' | 'down';
    hitRate: number;
    memoryUsed: string;
  };
  vectorDb: {
    status: 'healthy' | 'degraded' | 'down';
    totalVectors: number;
    collections: number;
  };
  models: {
    embedding: { loaded: boolean; name: string };
    llm: { loaded: boolean; name: string; gpuLayers: number };
    prediction: { loaded: boolean; models: string[] };
  };
  system: {
    cpuUsage: number;
    memoryUsed: string;
    memoryTotal: string;
    gpuAvailable: boolean;
    gpuMemory: string;
  };
}

interface AppSettings {
  general: {
    siteName: string;
    pageSize: number;
    timezone: string;
    dateFormat: string;
  };
  security: {
    sessionTimeout: number;
    maxLoginAttempts: number;
    passwordMinLength: number;
    requireMfa: boolean;
  };
  notifications: {
    emailEnabled: boolean;
    slackEnabled: boolean;
    alertsEnabled: boolean;
  };
  ai: {
    llmModel: string;
    embeddingModel: string;
    maxTokens: number;
    temperature: number;
  };
}

type TabId = 'general' | 'system' | 'security' | 'ai' | 'data';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabId>('general');
  const [settings, setSettings] = useState<AppSettings>({
    general: {
      siteName: 'HR Analytics System',
      pageSize: 50,
      timezone: 'Asia/Karachi',
      dateFormat: 'DD/MM/YYYY'
    },
    security: {
      sessionTimeout: 30,
      maxLoginAttempts: 5,
      passwordMinLength: 8,
      requireMfa: false
    },
    notifications: {
      emailEnabled: false,
      slackEnabled: false,
      alertsEnabled: true
    },
    ai: {
      llmModel: 'Qwen2-72B-Instruct',
      embeddingModel: 'BAAI/bge-large-en-v1.5',
      maxTokens: 2048,
      temperature: 0.7
    }
  });

  const queryClient = useQueryClient();

  // Fetch system status
  const { data: systemStatus, isLoading: loadingStatus, refetch: refetchStatus } = useQuery<SystemStatus>({
    queryKey: ['system-status'],
    queryFn: () => api.get('/health/detailed'),
    refetchInterval: 30000, // Refresh every 30 seconds
    placeholderData: {
      database: { status: 'healthy', connections: 15, maxConnections: 100, latencyMs: 5 },
      cache: { status: 'healthy', hitRate: 0.85, memoryUsed: '256 MB' },
      vectorDb: { status: 'healthy', totalVectors: 100000, collections: 3 },
      models: {
        embedding: { loaded: true, name: 'bge-large-en-v1.5' },
        llm: { loaded: true, name: 'Qwen2-72B-Q4', gpuLayers: 80 },
        prediction: { loaded: true, models: ['attrition', 'performance', 'promotion'] }
      },
      system: {
        cpuUsage: 35,
        memoryUsed: '48 GB',
        memoryTotal: '128 GB',
        gpuAvailable: true,
        gpuMemory: '42 GB / 80 GB'
      }
    }
  });

  // Save settings mutation
  const saveMutation = useMutation({
    mutationFn: (newSettings: AppSettings) => api.put('/settings', newSettings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    }
  });

  // Clear cache mutation
  const clearCacheMutation = useMutation({
    mutationFn: () => api.post('/admin/clear-cache'),
    onSuccess: () => {
      refetchStatus();
    }
  });

  // Reindex vectors mutation
  const reindexMutation = useMutation({
    mutationFn: () => api.post('/admin/reindex-vectors'),
  });

  const tabs = [
    { id: 'general' as TabId, name: 'General', icon: Settings },
    { id: 'system' as TabId, name: 'System Status', icon: Cpu },
    { id: 'security' as TabId, name: 'Security', icon: Shield },
    { id: 'ai' as TabId, name: 'AI Models', icon: Cpu },
    { id: 'data' as TabId, name: 'Data Management', icon: Database },
  ];

  const getStatusColor = (status: 'healthy' | 'degraded' | 'down') => {
    switch (status) {
      case 'healthy': return 'text-green-500 bg-green-50';
      case 'degraded': return 'text-yellow-500 bg-yellow-50';
      case 'down': return 'text-red-500 bg-red-50';
    }
  };

  const getStatusIcon = (status: 'healthy' | 'degraded' | 'down') => {
    switch (status) {
      case 'healthy': return <Check className="h-4 w-4" />;
      case 'degraded': return <AlertTriangle className="h-4 w-4" />;
      case 'down': return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const handleSettingChange = (
    section: keyof AppSettings,
    key: string,
    value: string | number | boolean
  ) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage system configuration and preferences
          </p>
        </div>
        <button
          onClick={() => saveMutation.mutate(settings)}
          disabled={saveMutation.isPending}
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {saveMutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          Save Changes
        </button>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-64 flex-shrink-0">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeTab === tab.id
                    ? 'bg-indigo-50 text-indigo-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          {/* General Settings */}
          {activeTab === 'general' && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">General Settings</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Site Name
                  </label>
                  <input
                    type="text"
                    value={settings.general.siteName}
                    onChange={(e) => handleSettingChange('general', 'siteName', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Page Size
                  </label>
                  <select
                    value={settings.general.pageSize}
                    onChange={(e) => handleSettingChange('general', 'pageSize', parseInt(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                    <option value={200}>200</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Globe className="h-4 w-4 inline mr-1" />
                    Timezone
                  </label>
                  <select
                    value={settings.general.timezone}
                    onChange={(e) => handleSettingChange('general', 'timezone', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="Asia/Karachi">Asia/Karachi (PKT)</option>
                    <option value="Asia/Dubai">Asia/Dubai (GST)</option>
                    <option value="UTC">UTC</option>
                    <option value="Asia/Singapore">Asia/Singapore (SGT)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Clock className="h-4 w-4 inline mr-1" />
                    Date Format
                  </label>
                  <select
                    value={settings.general.dateFormat}
                    onChange={(e) => handleSettingChange('general', 'dateFormat', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                    <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  </select>
                </div>
              </div>

              {/* Notifications */}
              <div className="pt-6 border-t border-gray-200">
                <h3 className="text-md font-medium text-gray-900 mb-4">
                  <Bell className="h-4 w-4 inline mr-2" />
                  Notifications
                </h3>
                <div className="space-y-4">
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={settings.notifications.alertsEnabled}
                      onChange={(e) => handleSettingChange('notifications', 'alertsEnabled', e.target.checked)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">Enable system alerts</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={settings.notifications.emailEnabled}
                      onChange={(e) => handleSettingChange('notifications', 'emailEnabled', e.target.checked)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">Email notifications (requires SMTP config)</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* System Status */}
          {activeTab === 'system' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
                <button
                  onClick={() => refetchStatus()}
                  className="inline-flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  <RefreshCw className={`h-4 w-4 ${loadingStatus ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>

              {/* Status Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Database */}
                <div className="p-4 border border-gray-200 rounded-xl">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Database className="h-5 w-5 text-gray-600" />
                      <span className="font-medium">PostgreSQL</span>
                    </div>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${getStatusColor(systemStatus?.database.status || 'healthy')}`}>
                      {getStatusIcon(systemStatus?.database.status || 'healthy')}
                      {systemStatus?.database.status}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Connections</span>
                      <span>{systemStatus?.database.connections} / {systemStatus?.database.maxConnections}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Latency</span>
                      <span>{systemStatus?.database.latencyMs}ms</span>
                    </div>
                  </div>
                </div>

                {/* Cache */}
                <div className="p-4 border border-gray-200 rounded-xl">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <HardDrive className="h-5 w-5 text-gray-600" />
                      <span className="font-medium">Redis Cache</span>
                    </div>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${getStatusColor(systemStatus?.cache.status || 'healthy')}`}>
                      {getStatusIcon(systemStatus?.cache.status || 'healthy')}
                      {systemStatus?.cache.status}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Hit Rate</span>
                      <span>{((systemStatus?.cache.hitRate || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Memory</span>
                      <span>{systemStatus?.cache.memoryUsed}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => clearCacheMutation.mutate()}
                    disabled={clearCacheMutation.isPending}
                    className="mt-3 w-full text-sm text-indigo-600 hover:text-indigo-700"
                  >
                    {clearCacheMutation.isPending ? 'Clearing...' : 'Clear Cache'}
                  </button>
                </div>

                {/* Vector DB */}
                <div className="p-4 border border-gray-200 rounded-xl">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Cpu className="h-5 w-5 text-gray-600" />
                      <span className="font-medium">Qdrant</span>
                    </div>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${getStatusColor(systemStatus?.vectorDb.status || 'healthy')}`}>
                      {getStatusIcon(systemStatus?.vectorDb.status || 'healthy')}
                      {systemStatus?.vectorDb.status}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Total Vectors</span>
                      <span>{systemStatus?.vectorDb.totalVectors.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Collections</span>
                      <span>{systemStatus?.vectorDb.collections}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* System Resources */}
              <div className="p-4 border border-gray-200 rounded-xl">
                <h3 className="font-medium text-gray-900 mb-4">System Resources</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <span className="text-sm text-gray-500">CPU Usage</span>
                    <div className="mt-1 flex items-center gap-2">
                      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-indigo-600 rounded-full"
                          style={{ width: `${systemStatus?.system.cpuUsage || 0}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{systemStatus?.system.cpuUsage}%</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-500">Memory</span>
                    <p className="mt-1 font-medium">
                      {systemStatus?.system.memoryUsed} / {systemStatus?.system.memoryTotal}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-500">GPU</span>
                    <p className="mt-1 font-medium">
                      {systemStatus?.system.gpuAvailable ? systemStatus.system.gpuMemory : 'Not Available'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Security Settings */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">Security Settings</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Session Timeout (minutes)
                  </label>
                  <input
                    type="number"
                    value={settings.security.sessionTimeout}
                    onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
                    min={5}
                    max={480}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Login Attempts
                  </label>
                  <input
                    type="number"
                    value={settings.security.maxLoginAttempts}
                    onChange={(e) => handleSettingChange('security', 'maxLoginAttempts', parseInt(e.target.value))}
                    min={3}
                    max={10}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Password Length
                  </label>
                  <input
                    type="number"
                    value={settings.security.passwordMinLength}
                    onChange={(e) => handleSettingChange('security', 'passwordMinLength', parseInt(e.target.value))}
                    min={6}
                    max={32}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div className="flex items-center">
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={settings.security.requireMfa}
                      onChange={(e) => handleSettingChange('security', 'requireMfa', e.target.checked)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">Require Multi-Factor Authentication</span>
                  </label>
                </div>
              </div>

              <div className="pt-6 border-t border-gray-200">
                <h3 className="text-md font-medium text-gray-900 mb-4">
                  <Key className="h-4 w-4 inline mr-2" />
                  API Keys
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  Manage API keys for external integrations
                </p>
                <button className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <Key className="h-4 w-4" />
                  Generate New API Key
                </button>
              </div>
            </div>
          )}

          {/* AI Models Settings */}
          {activeTab === 'ai' && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">AI Model Configuration</h2>

              {/* Model Status */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border border-gray-200 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">Embedding Model</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      systemStatus?.models.embedding.loaded ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {systemStatus?.models.embedding.loaded ? 'Loaded' : 'Not Loaded'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{systemStatus?.models.embedding.name}</p>
                </div>

                <div className="p-4 border border-gray-200 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">LLM Model</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      systemStatus?.models.llm.loaded ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {systemStatus?.models.llm.loaded ? 'Loaded' : 'Not Loaded'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{systemStatus?.models.llm.name}</p>
                  <p className="text-xs text-gray-400">GPU Layers: {systemStatus?.models.llm.gpuLayers}</p>
                </div>

                <div className="p-4 border border-gray-200 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">Prediction Models</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      systemStatus?.models.prediction.loaded ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {systemStatus?.models.prediction.loaded ? 'Loaded' : 'Not Loaded'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    {systemStatus?.models.prediction.models.join(', ')}
                  </p>
                </div>
              </div>

              {/* Model Parameters */}
              <div className="pt-4 border-t border-gray-200">
                <h3 className="font-medium text-gray-900 mb-4">Generation Parameters</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Tokens
                    </label>
                    <input
                      type="number"
                      value={settings.ai.maxTokens}
                      onChange={(e) => handleSettingChange('ai', 'maxTokens', parseInt(e.target.value))}
                      min={256}
                      max={8192}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                    <p className="mt-1 text-xs text-gray-500">Maximum tokens for LLM response</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Temperature: {settings.ai.temperature}
                    </label>
                    <input
                      type="range"
                      value={settings.ai.temperature}
                      onChange={(e) => handleSettingChange('ai', 'temperature', parseFloat(e.target.value))}
                      min={0}
                      max={1}
                      step={0.1}
                      className="w-full"
                    />
                    <p className="mt-1 text-xs text-gray-500">Lower = more deterministic, Higher = more creative</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Data Management */}
          {activeTab === 'data' && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">Data Management</h2>

              {/* Import/Export */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-6 border border-gray-200 rounded-xl">
                  <h3 className="font-medium text-gray-900 mb-2">
                    <Upload className="h-4 w-4 inline mr-2" />
                    Import Data
                  </h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Upload employee data from CSV or Excel files
                  </p>
                  <label className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 cursor-pointer">
                    <Upload className="h-4 w-4" />
                    Select File
                    <input type="file" accept=".csv,.xlsx" className="hidden" />
                  </label>
                </div>

                <div className="p-6 border border-gray-200 rounded-xl">
                  <h3 className="font-medium text-gray-900 mb-2">
                    <Download className="h-4 w-4 inline mr-2" />
                    Export Data
                  </h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Download all employee data as backup
                  </p>
                  <button className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    <Download className="h-4 w-4" />
                    Export All Data
                  </button>
                </div>
              </div>

              {/* Vector Index */}
              <div className="p-6 border border-gray-200 rounded-xl">
                <h3 className="font-medium text-gray-900 mb-2">
                  <RefreshCw className="h-4 w-4 inline mr-2" />
                  Vector Index
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  Rebuild vector embeddings for AI search. This may take several minutes for large datasets.
                </p>
                <button
                  onClick={() => reindexMutation.mutate()}
                  disabled={reindexMutation.isPending}
                  className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  {reindexMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4" />
                  )}
                  Rebuild Vector Index
                </button>
              </div>

              {/* Danger Zone */}
              <div className="p-6 border border-red-200 rounded-xl bg-red-50">
                <h3 className="font-medium text-red-900 mb-2">
                  <AlertTriangle className="h-4 w-4 inline mr-2" />
                  Danger Zone
                </h3>
                <p className="text-sm text-red-700 mb-4">
                  These actions are irreversible. Proceed with caution.
                </p>
                <div className="space-x-4">
                  <button className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-red-300 text-red-700 rounded-lg hover:bg-red-50">
                    <Trash2 className="h-4 w-4" />
                    Clear All Analytics Cache
                  </button>
                  <button className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                    <Trash2 className="h-4 w-4" />
                    Reset Database
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
