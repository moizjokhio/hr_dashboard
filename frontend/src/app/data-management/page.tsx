'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Upload,
  CheckCircle2,
  XCircle,
  Loader2,
  RefreshCw,
  FileSpreadsheet,
  Users,
  AlertTriangle,
  Clock,
  Info,
} from 'lucide-react';
import { api } from '@/lib/api';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';
import { toast } from 'sonner';

// ── types ──────────────────────────────────────────────────────────────────

interface UploadResult {
  status: string;
  data_source: string;
  filename: string;
  rows_in_file: number;
  rows_loaded_to_odbc?: number;
  employees_synced?: number;
  rows_inserted?: number;
  rows_skipped?: number;
  rows_error?: number;
  sync_error?: string | null;
  processing_seconds?: number;
  uploaded_at: string;
}

interface UploadStatusItem {
  last_uploaded_at: string | null;
  description: string;
}

interface UploadStatus {
  odbc: UploadStatusItem;
  da_cases: UploadStatusItem;
}

// ── helpers ─────────────────────────────────────────────────────────────────

function formatDate(iso: string | null) {
  if (!iso) return 'Never';
  return new Date(iso).toLocaleString();
}

// ── sub-component: UploadCard ────────────────────────────────────────────────

interface UploadCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  accept: string;
  lastUploadedAt: string | null;
  onUpload: (file: File) => void;
  isUploading: boolean;
  uploadingFile: File | null;
  uploadProgress: number;
  result: UploadResult | null;
  error: string | null;
  colorClass: string;
}

function UploadCard({
  title,
  description,
  icon,
  accept,
  lastUploadedAt,
  onUpload,
  isUploading,
  uploadingFile,
  uploadProgress,
  result,
  error,
  colorClass,
}: UploadCardProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Real-time timer for upload progress
  useEffect(() => {
    if (isUploading) {
      setElapsedSeconds(0);
      const interval = setInterval(() => {
        setElapsedSeconds(prev => prev + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isUploading]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) onUpload(file);
    },
    [onUpload]
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
      e.target.value = '';
    }
  };

  return (
    <div className="bg-card border rounded-xl p-6 flex flex-col gap-4 shadow-sm">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${colorClass}`}>{icon}</div>
        <div>
          <h2 className="font-semibold text-lg">{title}</h2>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      </div>

      {/* Last updated */}
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Clock className="h-3.5 w-3.5" />
        <span>Last refreshed: <span className="font-medium">{formatDate(lastUploadedAt)}</span></span>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => !isUploading && inputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${dragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/30 hover:border-primary/60 hover:bg-muted/30'}
          ${isUploading ? 'pointer-events-none opacity-60' : ''}
        `}
      >
        {isUploading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <div className="text-center space-y-2 w-full px-4">
              <p className="text-sm font-medium text-foreground">
                {uploadProgress === 0 ? 'Reading file...' : uploadProgress < 100 ? 'Uploading file...' : 'Processing Excel file...'}
              </p>
              {uploadingFile && (
                <>
                  <p className="text-xs text-muted-foreground">
                    {uploadingFile.name} ({(uploadingFile.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                  {uploadProgress === 0 ? (
                    <>
                      <p className="text-xs font-mono text-amber-600">
                        {elapsedSeconds}s - Browser is loading file into memory...
                      </p>
                      <p className="text-xs text-muted-foreground italic">
                        Large files (&gt;30 MB) may take 30-60s to load in browser
                      </p>
                    </>
                  ) : uploadProgress < 100 ? (
                    <>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all duration-300" 
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                      <p className="text-xs font-mono text-primary">
                        {uploadProgress}% uploaded | {elapsedSeconds}s elapsed
                      </p>
                    </>
                  ) : (
                    <>
                      <p className="text-xs font-mono text-primary">
                        {elapsedSeconds}s elapsed...
                      </p>
                      <p className="text-xs text-muted-foreground italic">
                        {uploadingFile.size > 10 * 1024 * 1024 
                          ? 'Parsing large Excel file - may take 30-60 seconds'
                          : 'Processing typically takes 10-30 seconds'}
                      </p>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm font-medium">Drag & drop or click to browse</p>
            <p className="text-xs text-muted-foreground">Accepted: {accept}</p>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {/* Result */}
      {result && !error && (
        <div className="rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 p-4 space-y-1 text-sm">
          <div className="flex items-center gap-2 font-semibold text-green-700 dark:text-green-400">
            <CheckCircle2 className="h-4 w-4" />
            Upload successful — {result.filename}
          </div>
          <div className="text-muted-foreground pl-6 space-y-0.5">
            <p>Rows in file: <span className="font-medium text-foreground">{result.rows_in_file}</span></p>
            {result.rows_loaded_to_odbc !== undefined && (
              <p>Rows loaded: <span className="font-medium text-foreground">{result.rows_loaded_to_odbc}</span></p>
            )}
            {result.employees_synced !== undefined && (
              <p>Employees synced: <span className="font-medium text-foreground">{result.employees_synced}</span></p>
            )}
            {result.processing_seconds !== undefined && (
              <p>Processed in: <span className="font-medium text-foreground">{result.processing_seconds.toFixed(2)}s</span></p>
            )}
            {result.rows_inserted !== undefined && (
              <p>Cases inserted: <span className="font-medium text-foreground">{result.rows_inserted}</span></p>
            )}
            {result.rows_skipped !== undefined && result.rows_skipped > 0 && (
              <p>Rows skipped: <span className="font-medium text-foreground">{result.rows_skipped}</span></p>
            )}
            {result.rows_error !== undefined && result.rows_error > 0 && (
              <p className="text-amber-600">Rows with errors: {result.rows_error}</p>
            )}
            {result.sync_error && (
              <p className="text-amber-600">Sync warning: {result.sync_error}</p>
            )}
            <p>Refreshed at: <span className="font-medium text-foreground">{formatDate(result.uploaded_at)}</span></p>
          </div>
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 p-4 text-sm">
          <div className="flex items-center gap-2 font-semibold text-red-700 dark:text-red-400">
            <XCircle className="h-4 w-4" />
            Upload failed
          </div>
          <p className="text-muted-foreground pl-6 mt-1">{error}</p>
        </div>
      )}
    </div>
  );
}

// ── main page ────────────────────────────────────────────────────────────────

export default function DataManagementPage() {
  const queryClient = useQueryClient();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [odbcResult, setOdbcResult] = useState<UploadResult | null>(null);
  const [odbcError, setOdbcError] = useState<string | null>(null);
  const [odbcUploadingFile, setOdbcUploadingFile] = useState<File | null>(null);
  const [odbcUploadProgress, setOdbcUploadProgress] = useState(0);
  const [daResult, setDaResult] = useState<UploadResult | null>(null);
  const [daError, setDaError] = useState<string | null>(null);
  const [daUploadingFile, setDaUploadingFile] = useState<File | null>(null);
  const [daUploadProgress, setDaUploadProgress] = useState(0);

  // Fetch last upload status
  const { data: status, refetch: refetchStatus } = useQuery<UploadStatus>({
    queryKey: ['upload-status'],
    queryFn: async () => {
      const res = await api.get('/upload/status');
      return res.data;
    },
    refetchInterval: 30_000,
  });

  // ODBC upload mutation
  const odbcMutation = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append('file', file);
      const res = await api.post('/upload/odbc', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300000, // 5 minute timeout for large files
        maxBodyLength: Infinity,
        maxContentLength: Infinity,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setOdbcUploadProgress(percentCompleted);
          }
        },
      });
      return res.data as UploadResult;
    },
    onSuccess: (data) => {
      setOdbcResult(data);
      setOdbcError(null);
      setOdbcUploadingFile(null);
      setOdbcUploadProgress(0);
      queryClient.invalidateQueries({ queryKey: ['upload-status'] });
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      toast.success('ODBC data refreshed successfully');
    },
    onError: (err: any) => {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        'Upload failed. Please try again.';
      setOdbcError(msg);
      setOdbcResult(null);
      setOdbcUploadingFile(null);
      setOdbcUploadProgress(0);
      toast.error(msg);
    },
  });

  // DA Cases upload mutation
  const daMutation = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append('file', file);
      const res = await api.post('/upload/da-cases', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300000, // 5 minute timeout
        maxBodyLength: Infinity,
        maxContentLength: Infinity,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setDaUploadProgress(percentCompleted);
          }
        },
      });
      return res.data as UploadResult;
    },
    onSuccess: (data) => {
      setDaResult(data);
      setDaError(null);
      setDaUploadingFile(null);
      setDaUploadProgress(0);
      queryClient.invalidateQueries({ queryKey: ['upload-status'] });
      queryClient.invalidateQueries({ queryKey: ['da-cases'] });
      toast.success('DA MIS Cases refreshed successfully');
    },
    onError: (err: any) => {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        'Upload failed. Please try again.';
      setDaError(msg);
      setDaResult(null);
      setDaUploadingFile(null);
      setDaUploadProgress(0);
      toast.error(msg);
    },
  });

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 overflow-auto">
          <div className="p-6 max-w-4xl mx-auto space-y-6">
            {/* Page header */}
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <RefreshCw className="h-6 w-6 text-primary" />
                Data Management
              </h1>
              <p className="text-muted-foreground mt-1">
                Upload updated Excel files to refresh analytics in real time. The database is
                replaced with the latest data from your file instantly.
              </p>
            </div>

            {/* Info banner */}
            <div className="flex gap-3 rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/30 p-4 text-sm text-blue-800 dark:text-blue-300">
              <Info className="h-4 w-4 mt-0.5 shrink-0" />
              <div className="space-y-1">
                <p>
                  Uploading a file <strong>replaces all existing records</strong> for that data source.
                  Make sure the file is the complete, up-to-date export before uploading.
                </p>
                <p className="text-xs">
                  💡 <strong>Tip:</strong> Use <code className="px-1 py-0.5 bg-blue-100 dark:bg-blue-900 rounded">.xlsx</code> format for faster processing (2-3x faster than .xlsb)
                </p>
                <p className="text-xs text-amber-700 dark:text-amber-400">
                  ⚠️ <strong>Large files (&gt;30 MB):</strong> May take 30-60s to load in browser before upload begins
                </p>
              </div>
            </div>

            {/* Upload cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <UploadCard
                title="ODBC / Employee Data"
                description="Upload the latest ODBC master export to refresh all employee records and HR analytics."
                icon={<Users className="h-5 w-5 text-blue-600" />}
                accept=".xlsx,.xlsb,.xls"
                lastUploadedAt={status?.odbc?.last_uploaded_at ?? null}
                onUpload={(file) => {
                  setOdbcResult(null);
                  setOdbcError(null);
                  setOdbcUploadingFile(file);
                  setOdbcUploadProgress(0);
                  odbcMutation.mutate(file);
                }}
                isUploading={odbcMutation.isPending}
                uploadingFile={odbcUploadingFile}
                uploadProgress={odbcUploadProgress}
                result={odbcResult}
                error={odbcError}
                colorClass="bg-blue-100 dark:bg-blue-900/40"
              />

              <UploadCard
                title="DA MIS Cases"
                description="Upload the latest Disciplinary Action MIS export to refresh case analytics and reports."
                icon={<AlertTriangle className="h-5 w-5 text-amber-600" />}
                accept=".xlsx,.xls"
                lastUploadedAt={status?.da_cases?.last_uploaded_at ?? null}
                onUpload={(file) => {
                  setDaResult(null);
                  setDaError(null);
                  setDaUploadingFile(file);
                  setDaUploadProgress(0);
                  daMutation.mutate(file);
                }}
                isUploading={daMutation.isPending}
                uploadingFile={daUploadingFile}
                uploadProgress={daUploadProgress}
                result={daResult}
                error={daError}
                colorClass="bg-amber-100 dark:bg-amber-900/40"
              />
            </div>

            {/* How it works */}
            <div className="rounded-xl border bg-card p-6 space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <FileSpreadsheet className="h-4 w-4 text-muted-foreground" />
                How it works
              </h3>
              <ol className="space-y-2 text-sm text-muted-foreground list-decimal list-inside">
                <li>Export your latest ODBC data as <strong>.xlsx</strong> (recommended for faster processing), <strong>.xlsb</strong>, or <strong>.xls</strong>.</li>
                <li>Drag-and-drop the file onto the relevant card above (or click to browse).</li>
                <li>The server parses the Excel file, replaces the database, and re-syncs employee search data. Processing time: 10-30s for small files (&lt;10 MB), 30-60s for large files (&gt;10 MB).</li>
                <li>All dashboards and reports automatically reflect the new data — no restart needed.</li>
              </ol>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}