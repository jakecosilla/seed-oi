'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';
import { Badge } from '@/components/ui/Badge';
import { AlertCircle, CheckCircle, Database, RefreshCw, XCircle } from 'lucide-react';

// Types aligning with backend Step 9
type SourceConnection = {
  id: string;
  name: string;
  system_type: string;
  status: string;
  last_synced_at: string | null;
  data_freshness_score: number;
  mapping_completeness_score: number;
  active_errors: number;
};

type SyncHistory = {
  id: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  records_processed: number;
  error_message: string | null;
};

type SourceError = {
  id: string;
  validation_type: string;
  message: string;
  severity: string;
  created_at: string;
};

export default function SourcesPage() {
  const [sources, setSources] = useState<SourceConnection[]>([]);
  const [selectedSource, setSelectedSource] = useState<SourceConnection | null>(null);
  const [history, setHistory] = useState<SyncHistory[]>([]);
  const [errors, setErrors] = useState<SourceError[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch Sources list
  useEffect(() => {
    fetch('http://localhost:8000/sources')
      .then((res) => res.json())
      .then((data) => {
        setSources(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch sources', err);
        setLoading(false);
      });
  }, []);

  // Fetch details when source is selected
  useEffect(() => {
    if (!selectedSource) return;

    fetch(`http://localhost:8000/sources/${selectedSource.id}/history`)
      .then((res) => res.json())
      .then((data) => setHistory(data))
      .catch(console.error);

    fetch(`http://localhost:8000/sources/${selectedSource.id}/errors`)
      .then((res) => res.json())
      .then((data) => setErrors(data))
      .catch(console.error);
  }, [selectedSource]);

  const handleRetrySync = async () => {
    if (!selectedSource) return;
    try {
      await fetch(`http://localhost:8000/sources/${selectedSource.id}/retry-sync`, { method: 'POST' });
      alert('Sync retry queued.');
    } catch (err) {
      console.error(err);
    }
  };

  const activeCount = sources.filter(s => s.status === 'active').length;
  const warningCount = sources.filter(s => s.status === 'warning').length;
  const failedCount = sources.filter(s => s.status === 'failed').length;

  return (
    <div className="flex flex-1 h-full w-full overflow-hidden">
      <div className="flex-1 p-6 overflow-y-auto bg-slate-50/50">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Sources</h1>
          <p className="text-slate-500 max-w-2xl">Understand data trust, completeness, and synchronization health across your supply chain connections.</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <div className="flex items-center gap-4 p-4">
              <div className="p-2.5 rounded-lg bg-blue-50 text-blue-600">
                <Database size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{sources.length}</p>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Connected Systems</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4 p-4">
              <div className="p-2.5 rounded-lg bg-green-50 text-green-600">
                <CheckCircle size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{activeCount}</p>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Healthy Syncs</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4 p-4">
              <div className="p-2.5 rounded-lg bg-red-50 text-red-600">
                <XCircle size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{failedCount}</p>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Failed Syncs</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4 p-4">
              <div className="p-2.5 rounded-lg bg-amber-50 text-amber-600">
                <AlertCircle size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{warningCount}</p>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Stale Sources</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Source List */}
        <div className="flex flex-col gap-4">
          {loading ? (
            <p className="text-slate-500 text-sm">Loading sources...</p>
          ) : (
            sources.map(source => (
              <div key={source.id} onClick={() => setSelectedSource(source)} className="cursor-pointer">
                <Card className={`transition-all ${selectedSource?.id === source.id ? 'ring-2 ring-blue-500 border-blue-500' : 'hover:border-slate-300'}`}>
                  <CardContent>
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-slate-100 rounded text-slate-600">
                          <Database size={18} />
                        </div>
                        <span className="font-semibold text-slate-900">{source.name}</span>
                        <Badge variant={
                          source.status === 'active' ? 'success' :
                          source.status === 'warning' ? 'warning' : 'danger'
                        }>{source.status}</Badge>
                      </div>
                      <div>
                        <Badge variant="info">{source.system_type}</Badge>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                      <div className="flex flex-col gap-1">
                        <span className="text-xs text-slate-500 uppercase tracking-wider">Last Synced</span>
                        <span className="text-sm font-medium text-slate-900">
                          {source.last_synced_at ? new Date(source.last_synced_at).toLocaleString() : 'Never'}
                        </span>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-xs text-slate-500 uppercase tracking-wider">Freshness</span>
                        <span className="text-sm font-medium text-slate-900">{(source.data_freshness_score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-xs text-slate-500 uppercase tracking-wider">Mapping Completeness</span>
                        <span className="text-sm font-medium text-slate-900">{(source.mapping_completeness_score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-xs text-slate-500 uppercase tracking-wider">Active Errors</span>
                        <span className={`text-sm font-medium ${source.active_errors > 0 ? 'text-red-600' : 'text-slate-900'}`}>
                          {source.active_errors}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Side Panel Details */}
      {selectedSource && (
        <SidePanel side="right" width="400px">
          <div className="p-6 flex flex-col gap-8 h-full overflow-y-auto">
            <div className="flex flex-col gap-1">
              <h2 className="text-xl font-bold text-slate-900">{selectedSource.name}</h2>
              <p className="text-sm text-slate-500">Source details and health</p>
            </div>

            <button 
              className="flex items-center justify-center gap-2 w-full py-2.5 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors shadow-sm"
              onClick={handleRetrySync}
            >
              <RefreshCw size={16} /> Retry Sync
            </button>

            <div className="flex flex-col gap-4">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Recent Sync History</h3>
              <div className="flex flex-col gap-3">
                {history.length === 0 ? <p className="text-xs text-slate-400 italic">No recent syncs.</p> : null}
                {history.map(entry => (
                  <div key={entry.id} className="p-4 rounded-lg bg-slate-50 border border-slate-100">
                    <div className="flex items-center justify-between mb-2">
                      <strong className="text-sm text-slate-900">{new Date(entry.started_at).toLocaleDateString()}</strong>
                      <Badge variant={entry.status === 'success' ? 'success' : 'danger'}>{entry.status}</Badge>
                    </div>
                    <div className="text-xs text-slate-500">
                      Processed: {entry.records_processed.toLocaleString()} records
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-4">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Validation Errors</h3>
              <div className="flex flex-col gap-3">
                {errors.length === 0 ? <p className="text-xs text-slate-400 italic">No active errors.</p> : null}
                {errors.map(err => (
                  <div key={err.id} className="p-4 rounded-lg bg-red-50/50 border border-red-100 flex flex-col gap-2">
                    <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-tight text-red-600">
                      <span>{err.validation_type}</span>
                      <span>{new Date(err.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="text-xs text-red-900 leading-relaxed font-medium">{err.message}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SidePanel>
      )}
    </div>
  );
}
