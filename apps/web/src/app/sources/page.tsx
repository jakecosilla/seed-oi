'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';
import { Badge } from '@/components/ui/Badge';
import { AlertCircle, CheckCircle, Database, RefreshCw, XCircle } from 'lucide-react';
import styles from './page.module.css';

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
    <div className={styles.container}>
      <div className={styles.mainContent}>
        <div className={styles.header}>
          <h1>Sources</h1>
          <p>Understand data trust, completeness, and synchronization health across your supply chain connections.</p>
        </div>

        {/* Summary Cards */}
        <div className={styles.summaryCards}>
          <Card>
            <div className={styles.statCard}>
              <div className={styles.statIcon} style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary)' }}>
                <Database size={20} />
              </div>
              <div>
                <p className={styles.statValue}>{sources.length}</p>
                <p className={styles.statLabel}>Connected Systems</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className={styles.statCard}>
              <div className={styles.statIcon} style={{ background: 'rgba(34, 197, 94, 0.1)', color: 'var(--success)' }}>
                <CheckCircle size={20} />
              </div>
              <div>
                <p className={styles.statValue}>{activeCount}</p>
                <p className={styles.statLabel}>Healthy Syncs</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className={styles.statCard}>
              <div className={styles.statIcon} style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)' }}>
                <XCircle size={20} />
              </div>
              <div>
                <p className={styles.statValue}>{failedCount}</p>
                <p className={styles.statLabel}>Failed Syncs</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className={styles.statCard}>
              <div className={styles.statIcon} style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' }}>
                <AlertCircle size={20} />
              </div>
              <div>
                <p className={styles.statValue}>{warningCount}</p>
                <p className={styles.statLabel}>Stale Sources</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Source List */}
        <div className={styles.sourceList}>
          {loading ? (
            <p>Loading sources...</p>
          ) : (
            sources.map(source => (
              <div key={source.id} onClick={() => setSelectedSource(source)}>
                <Card className={`${styles.sourceCard} ${selectedSource?.id === source.id ? styles.selected : ''}`}>
                  <CardContent>
                    <div className={styles.sourceCardHeader}>
                      <div className={styles.sourceTitle}>
                        <Database size={18} color="var(--text-secondary)" />
                        {source.name}
                        <Badge variant={
                          source.status === 'active' ? 'success' :
                          source.status === 'warning' ? 'warning' : 'danger'
                        }>{source.status}</Badge>
                      </div>
                      <div>
                        <Badge variant="info">{source.system_type}</Badge>
                      </div>
                    </div>
                    
                    <div className={styles.sourceMetrics}>
                      <div className={styles.metric}>
                        <span className={styles.metricLabel}>Last Synced</span>
                        <span className={styles.metricValue}>
                          {source.last_synced_at ? new Date(source.last_synced_at).toLocaleString() : 'Never'}
                        </span>
                      </div>
                      <div className={styles.metric}>
                        <span className={styles.metricLabel}>Freshness</span>
                        <span className={styles.metricValue}>{(source.data_freshness_score * 100).toFixed(0)}%</span>
                      </div>
                      <div className={styles.metric}>
                        <span className={styles.metricLabel}>Mapping Completeness</span>
                        <span className={styles.metricValue}>{(source.mapping_completeness_score * 100).toFixed(0)}%</span>
                      </div>
                      <div className={styles.metric}>
                        <span className={styles.metricLabel}>Active Errors</span>
                        <span className={styles.metricValue} style={{ color: source.active_errors > 0 ? 'var(--danger)' : 'inherit' }}>
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
        <SidePanel side="right">
          <div className={styles.panelContent}>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{selectedSource.name}</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Source details and health</p>
            </div>

            <button className={styles.actionButton} onClick={handleRetrySync}>
              <RefreshCw size={16} /> Retry Sync
            </button>

            <div className={styles.panelSection}>
              <h3>Recent Sync History</h3>
              <div className={styles.historyList}>
                {history.length === 0 ? <p style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>No recent syncs.</p> : null}
                {history.map(entry => (
                  <div key={entry.id} className={styles.historyItem}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <strong>{new Date(entry.started_at).toLocaleDateString()}</strong>
                      <Badge variant={entry.status === 'success' ? 'success' : 'danger'}>{entry.status}</Badge>
                    </div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                      Processed: {entry.records_processed.toLocaleString()} records
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.panelSection}>
              <h3>Validation Errors</h3>
              <div className={styles.errorList}>
                {errors.length === 0 ? <p style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>No active errors.</p> : null}
                {errors.map(err => (
                  <div key={err.id} className={styles.errorItem}>
                    <div className={styles.errorMeta}>
                      <span>{err.validation_type}</span>
                      <span>{new Date(err.created_at).toLocaleDateString()}</span>
                    </div>
                    <div>{err.message}</div>
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
