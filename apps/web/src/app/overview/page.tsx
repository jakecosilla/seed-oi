"use client";

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';
import { fetchApi } from '@/lib/api-client';
import { AlertCircle, Clock, DollarSign, Activity, ChevronRight, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';
import { AIAssistant } from '@/components/layout/AIAssistant';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/providers/AuthProvider';

export interface SummaryData {
  total_open_issues: number;
  critical_issues: number;
  total_revenue_at_risk: number;
  total_delay_days: number;
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
    refetchInterval: 10000,
  });

  const { data: issues = [] } = useQuery({
    queryKey: ['overview-issues', user?.tenant_id],
    queryFn: () => fetchApi<Issue[]>(`/overview/issues?tenant_id=${user?.tenant_id}`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    }),
    enabled: !!user && !!accessToken,
    refetchInterval: 10000,
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-slate-500">Revenue at Risk</span>
                  <DollarSign size={16} className="text-rose-500" />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? formatCurrency(summary.total_revenue_at_risk) : '...'}
                </span>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-slate-500">Total Delay Days</span>
                  <Clock size={16} className="text-amber-500" />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? summary.total_delay_days : '...'}
                </span>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-slate-500">Critical Issues</span>
                  <ShieldAlert size={16} className="text-rose-600" />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? summary.critical_issues : '...'}
                </span>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-slate-500">Total Open Issues</span>
                  <Activity size={16} className="text-indigo-500" />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? summary.total_open_issues : '...'}
                </span>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 flex-1">
            {/* What Needs Attention Now */}
            <Card className="flex flex-col h-[500px]">
              <CardHeader className="bg-slate-50/50">What Needs Attention Now</CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-0">
                {issues.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-2">
                    <CheckCircle2 size={32} />
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
                                <span className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-rose-100 text-rose-700">
                                  <AlertCircle size={12} /> Critical
                                </span>
                              ) : (
                                <span className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">
                                  <AlertCircle size={12} /> Warning
                                </span>
                              )}
                              <span className="text-xs text-slate-400 font-mono">
                                {issue.primary_entity_type || 'System'}
                              </span>
                            </div>
                            <h4 className="font-semibold text-slate-900">{issue.title}</h4>
                            <p className="text-sm text-slate-500 mt-1 line-clamp-1">{issue.description}</p>
                          </div>
                          <ChevronRight className={`text-slate-300 ${selectedIssueId === issue.id ? 'text-indigo-500' : ''}`} size={20} />
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>

            {/* Operational Impact Map (Simplified Visual) */}
            <Card className="flex flex-col h-[500px]">
              <CardHeader className="bg-slate-50/50">Operational Impact Map</CardHeader>
              <CardContent className="flex-1 p-6 overflow-y-auto flex items-center justify-center">
                 {selectedIssue && selectedIssue.risks && selectedIssue.risks.length > 0 ? (
                   <div className="w-full flex flex-col gap-4">
                      <div className="text-sm font-medium text-slate-500 mb-2">Impact Chain for: {selectedIssue.title}</div>
                      
                      {/* Source Node */}
                      <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-sm font-medium self-start shadow-sm">
                        [Source] {selectedIssue.primary_entity_type}: {selectedIssue.primary_entity_id?.substring(0,8)}
                      </div>
                      
                      {/* Edges & Downstream Nodes */}
                      <div className="pl-6 border-l-2 border-indigo-100 ml-4 space-y-4 py-2">
                         {selectedIssue.risks.map((risk: Risk) => (
                           <div key={risk.id} className="relative">
                              <div className="absolute -left-6 top-1/2 w-6 border-t-2 border-indigo-100" />
                              <div className="p-3 bg-white border border-slate-200 rounded-lg text-slate-700 text-sm shadow-sm flex items-center justify-between group hover:border-indigo-300 transition-colors">
                                <div>
                                  <span className="font-semibold text-indigo-700">{risk.affected_entity_type}</span>
                                  <span className="text-slate-400 ml-2 font-mono text-xs">{risk.affected_entity_id.substring(0,8)}</span>
                                </div>
                                <div className="flex gap-3 text-xs font-medium">
                                  {(risk.estimated_delay_days ?? 0) > 0 && <span className="text-amber-600 flex items-center gap-1"><Clock size={12}/> +{risk.estimated_delay_days}d</span>}
                                  {(risk.revenue_exposure ?? 0) > 0 && <span className="text-rose-600 flex items-center gap-1"><DollarSign size={12}/> {formatCurrency(risk.revenue_exposure || 0)}</span>}
                                </div>
                              </div>
                           </div>
                         ))}
                      </div>
                   </div>
                 ) : (
                   <div className="text-center text-slate-400 italic text-sm max-w-xs">
                      Select an issue from the list to visualize its downstream impact across the supply chain.
                   </div>
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
