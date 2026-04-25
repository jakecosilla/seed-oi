"use client";

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';
import { fetchApi } from '@/lib/api-client';
import { AlertCircle, Clock, DollarSign, Activity, ChevronRight, ShieldAlert, CheckCircle2, ArrowRight, TrendingUp, Zap, Lightbulb, Sparkles, Heart } from 'lucide-react';
import { AIAssistant } from '@/components/layout/AIAssistant';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/providers/AuthProvider';
import { HealthSignalItem } from '@/components/ui/HealthSignalItem';

export interface SummaryData {
  total_open_issues: number;
  critical_issues: number;
  total_revenue_at_risk: number;
  total_delay_days: number;
  on_track_percentage: number;
  improved_count: number;
  available_capacity_pct: number;
  active_opportunities: number;
}

export interface HealthSignal {
  id: string;
  category: 'Healthy' | 'Improved' | 'Capacity' | 'Opportunity';
  title: string;
  description: string;
  metric_value?: string;
  metric_trend?: 'up' | 'down' | 'stable';
  impact_area: string;
}

export interface Recommendation {
  id: string;
  action_type: string;
  action_details?: Record<string, string>;
  confidence_score?: number;
  rank?: number;
}

export interface Scenario {
  id: string;
  name: string;
  description?: string;
  net_cost_impact?: number;
  delay_days_avoided?: number;
  recommendations: Recommendation[];
}

export interface Risk {
  id: string;
  risk_type: string;
  affected_entity_type: string;
  affected_entity_id: string;
  revenue_exposure?: number;
  estimated_delay_days?: number;
}

export interface Issue {
  id: string;
  title: string;
  description?: string;
  severity: 'Critical' | 'Warning' | 'Monitor';
  status: string;
  primary_entity_type?: string;
  primary_entity_id?: string;
  risks: Risk[];
  top_scenario?: Scenario;
}

export default function OverviewPage() {
  const { user, accessToken } = useAuth();
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);

  // Queries with near-real-time refresh (10 seconds)
  const { data: summary } = useQuery({
    queryKey: ['overview-summary', user?.tenant_id],
    queryFn: () => fetchApi<SummaryData>(`/overview/summary?tenant_id=${user?.tenant_id}`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    }),
    enabled: !!user && !!accessToken,
    refetchInterval: 60000, // Fallback polling (primary updates via SSE)
  });

  const { data: issues = [] } = useQuery({
    queryKey: ['overview-issues', user?.tenant_id],
    queryFn: () => fetchApi<Issue[]>(`/overview/issues?tenant_id=${user?.tenant_id}`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    }),
    enabled: !!user && !!accessToken,
    refetchInterval: 60000,
  });

  const { data: healthSignals = [] } = useQuery({
    queryKey: ['overview-health', user?.tenant_id],
    queryFn: () => fetchApi<HealthSignal[]>(`/overview/health?tenant_id=${user?.tenant_id}`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    }),
    enabled: !!user && !!accessToken,
    refetchInterval: 60000,
  });

  const selectedIssue = issues.find((i: Issue) => i.id === selectedIssueId);

  const formatCurrency = (val: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <ProtectedRoute>
      <div className="flex flex-1 w-full h-full overflow-hidden bg-slate-50">
        
        {/* LEFT PANEL: Ask Operations */}
        <SidePanel side="left">
          <AIAssistant 
            context={selectedIssue ? { issue_id: selectedIssue.id, severity: selectedIssue.severity, type: 'issue_analysis' } : { page: 'overview' }}
            initialMessage={selectedIssue ? `I see you've selected "${selectedIssue.title}". How can I help you analyze this issue?` : undefined}
          />
        </SidePanel>

        {/* CENTER WORKSPACE */}
        <div className="flex-1 p-6 flex flex-col gap-6 overflow-y-auto">
          
          {/* Header */}
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight mb-1">Operations Overview</h1>
            <p className="text-slate-500 text-sm">Live operational command center displaying active risks and recommended actions.</p>
          </div>

          {/* Top Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Risk Metrics */}
            <Card className="border-l-4 border-l-rose-500">
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start text-slate-500">
                  <span className="text-xs font-bold uppercase tracking-wider">Revenue at Risk</span>
                  <DollarSign size={16} />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? formatCurrency(summary.total_revenue_at_risk) : '...'}
                </span>
                <div className="text-xs text-rose-600 font-medium flex items-center gap-1 mt-1">
                  <AlertCircle size={12} /> {summary?.critical_issues} critical issues
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-l-4 border-l-amber-500">
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start text-slate-500">
                  <span className="text-xs font-bold uppercase tracking-wider">On-Track Orders</span>
                  <CheckCircle2 size={16} />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? `${summary.on_track_percentage}%` : '...'}
                </span>
                <div className="text-xs text-emerald-600 font-medium flex items-center gap-1 mt-1">
                  <TrendingUp size={12} /> +1.2% from last week
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-indigo-500">
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start text-slate-500">
                  <span className="text-xs font-bold uppercase tracking-wider">Avail. Capacity</span>
                  <Zap size={16} />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? `${summary.available_capacity_pct}%` : '...'}
                </span>
                <div className="text-xs text-indigo-600 font-medium flex items-center gap-1 mt-1">
                  <Activity size={12} /> Optimized for demand
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-emerald-500">
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start text-slate-500">
                  <span className="text-xs font-bold uppercase tracking-wider">Opportunities</span>
                  <Lightbulb size={16} />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? summary.active_opportunities : '...'}
                </span>
                <div className="text-xs text-emerald-600 font-medium flex items-center gap-1 mt-1">
                  <Sparkles size={12} /> {summary?.improved_count} improvements detected
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 flex-1">
            {/* What Needs Attention Now (Risks/Exceptions) */}
            <Card className="flex flex-col h-[600px]">
              <CardHeader className="bg-slate-50/50 flex flex-row items-center justify-between py-3">
                <div className="flex items-center gap-2">
                  <AlertCircle size={18} className="text-rose-500" />
                  <span className="font-bold text-slate-800">What Needs Attention Now</span>
                </div>
                <span className="bg-rose-100 text-rose-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                  {issues.length} Risks Detected
                </span>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-0">
                {issues.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-2">
                    <CheckCircle2 size={32} className="text-emerald-500" />
                    <span>No active issues detected.</span>
                  </div>
                ) : (
                  <ul className="divide-y divide-slate-100">
                    {issues.map((issue: Issue) => (
                      <li 
                        key={issue.id} 
                        onClick={() => setSelectedIssueId(issue.id)}
                        className={`p-4 hover:bg-slate-50 cursor-pointer transition-colors ${selectedIssueId === issue.id ? 'bg-indigo-50/50 border-l-4 border-indigo-500' : 'border-l-4 border-transparent'}`}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              {issue.severity === 'Critical' ? (
                                <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-100 text-rose-700">
                                  Critical
                                </span>
                              ) : (
                                <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-100 text-amber-700">
                                  Warning
                                </span>
                              )}
                              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                {issue.primary_entity_type || 'System'}
                              </span>
                            </div>
                            <h4 className="font-bold text-slate-900">{issue.title}</h4>
                            <p className="text-xs text-slate-500 mt-1 line-clamp-2">{issue.description}</p>
                          </div>
                          <ChevronRight className={`text-slate-300 mt-2 ${selectedIssueId === issue.id ? 'text-indigo-500' : ''}`} size={20} />
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>

            {/* Business Health & Opportunities (Positive Signals) */}
            <Card className="flex flex-col h-[600px]">
              <CardHeader className="bg-slate-50/50 flex flex-row items-center justify-between py-3">
                <div className="flex items-center gap-2">
                  <Sparkles size={18} className="text-emerald-500" />
                  <span className="font-bold text-slate-800">Business Health & Opportunities</span>
                </div>
                <span className="bg-emerald-100 text-emerald-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                  {healthSignals.length} Positive Signals
                </span>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-0">
                {healthSignals.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-2">
                    <Activity size={32} />
                    <span>Gathering health data...</span>
                  </div>
                ) : (
                  <ul className="divide-y divide-slate-100">
                    {healthSignals.map((signal: HealthSignal) => (
                      <HealthSignalItem
                        key={signal.id}
                        category={signal.category}
                        title={signal.title}
                        description={signal.description}
                        impactArea={signal.impact_area}
                        metricValue={signal.metric_value}
                        metricTrend={signal.metric_trend}
                      />
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* RIGHT PANEL: Issue Summary & Recommendations */}
        <SidePanel side="right">
          <div className="p-5 h-full flex flex-col overflow-y-auto">
            <h2 className="text-sm font-bold text-slate-900 mb-4 uppercase tracking-wider">Action Center</h2>
            
            {!selectedIssue ? (
              <div className="text-slate-500 text-sm mt-4">Select an issue to view AI-ranked recommendations.</div>
            ) : (
              <div className="flex flex-col gap-6">
                
                {/* Selected Issue Info */}
                <div>
                  <h3 className="font-semibold text-lg text-slate-900 leading-tight mb-2">{selectedIssue.title}</h3>
                  <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded-md border border-slate-100">
                    {selectedIssue.description}
                  </p>
                </div>

                {/* Recommendations */}
                <div>
                  <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                    Top Recommended Strategy
                    {selectedIssue.top_scenario && <span className="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded text-[10px]">AI Ranked</span>}
                  </h4>

                  {!selectedIssue.top_scenario ? (
                    <div className="text-sm text-slate-500 italic">Evaluating strategies...</div>
                  ) : (
                    <div className="bg-white border border-indigo-200 rounded-lg shadow-sm overflow-hidden ring-1 ring-indigo-50">
                      <div className="bg-indigo-50/50 p-4 border-b border-indigo-100">
                        <div className="flex justify-between items-start mb-1">
                          <h5 className="font-bold text-indigo-900">{selectedIssue.top_scenario.name}</h5>
                          {(selectedIssue.top_scenario.delay_days_avoided ?? 0) > 0 && (
                             <span className="text-xs font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full flex items-center gap-1">
                               Saves {selectedIssue.top_scenario.delay_days_avoided}d
                             </span>
                          )}
                        </div>
                        <p className="text-xs text-indigo-700/80">{selectedIssue.top_scenario.description}</p>
                      </div>
                      
                      <div className="p-4 space-y-3">
                        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Execution Steps</div>
                        {selectedIssue.top_scenario.recommendations.map((rec: Recommendation, idx: number) => (
                          <div key={rec.id} className="flex gap-3 text-sm">
                            <div className="flex-shrink-0 w-5 h-5 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs font-medium">
                              {idx + 1}
                            </div>
                            <div>
                              <span className="font-semibold text-slate-800">{rec.action_type}</span>
                              <div className="text-slate-500 text-xs mt-0.5">
                                 {rec.action_details ? Object.entries(rec.action_details).map(([k, v]) => `${k}: ${v}`).join(', ') : ''}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="p-3 bg-slate-50 border-t border-slate-100 flex justify-between items-center">
                         <div className="text-xs text-slate-500 font-medium">
                           Est. Cost: <span className="text-slate-900 font-bold">{formatCurrency(selectedIssue.top_scenario.net_cost_impact || 0)}</span>
                         </div>
                         <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-1.5 rounded-md text-xs font-semibold transition-colors flex items-center gap-1 shadow-sm">
                           Approve Action <ArrowRight size={12} />
                         </button>
                      </div>
                    </div>
                  )}
                </div>

              </div>
            )}
          </div>
        </SidePanel>
      </div>
    </ProtectedRoute>
  );
}
