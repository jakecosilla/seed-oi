"use client";

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';
import { fetchApi } from '@/lib/api-client';
import { Activity, ArrowRight, ShieldCheck, Search, Clock, RefreshCw, Zap, TableProperties } from 'lucide-react';
import { AIAssistant } from '@/components/layout/AIAssistant';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/providers/AuthProvider';

export interface IssueSimple {
  id: string;
  title: string;
  severity: string;
  detected_at: string;
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
  status: string;
  net_cost_impact: number;
  delay_days_avoided: number;
  recommendations: Recommendation[];
}

export interface BaselineMetrics {
  total_delay_days: number;
  revenue_at_risk: number;
}

export interface ScenarioComparison {
  issue_id: string;
  issue_title: string;
  issue_description?: string;
  last_synced_at?: string;
  baseline: BaselineMetrics;
  options: Scenario[];
}

export default function ScenariosPage() {
  const { user, accessToken } = useAuth();
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);
  const [selectedOptionId, setSelectedOptionId] = useState<string | null>(null);

  const { data: issues = [] } = useQuery({
    queryKey: ['scenarios-issues', user?.tenant_id],
    queryFn: () => fetchApi<IssueSimple[]>(`/scenarios/issues?tenant_id=${user?.tenant_id}`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    }),
    enabled: !!user && !!accessToken,
    refetchInterval: 15000,
  });

  const { data: comparison, isFetching: isComparisonFetching } = useQuery({
    queryKey: ['scenarios-comparison', selectedIssueId, user?.tenant_id],
    queryFn: () => fetchApi<ScenarioComparison>(`/scenarios/${selectedIssueId}/comparison?tenant_id=${user?.tenant_id}`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    }),
    enabled: !!selectedIssueId && !!user && !!accessToken,
    refetchInterval: 15000, // Near-real-time refresh
  });

  const formatCurrency = (val: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  // Auto-select the top-ranked option when comparison loads
  React.useEffect(() => {
    if (comparison && comparison.options.length > 0) {
      // Assuming first option is best because API ordered by net_cost_impact (or rank)
      setSelectedOptionId(comparison.options[0].id);
    }
  }, [comparison]);

  const selectedOption = comparison?.options.find(o => o.id === selectedOptionId);

  return (
    <ProtectedRoute>
      <div className="flex flex-1 w-full h-full overflow-hidden bg-slate-50">
        
        {/* LEFT PANEL: Scenario Setup & AI Assistant */}
        <SidePanel side="left" width="340px">
          <div className="flex flex-col h-full">
            <div className="p-5 border-b border-slate-100 bg-white">
              <div className="flex items-center gap-2 mb-4 text-indigo-600">
                <Search size={18} />
                <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900">Scenario Setup</h2>
              </div>
              
              <div className="text-xs font-bold text-slate-400 uppercase tracking-tight mb-2">Select Issue to Evaluate</div>
              <div className="max-h-[220px] overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                {issues.length === 0 ? (
                  <div className="text-slate-400 text-sm italic">No open issues require evaluation.</div>
                ) : (
                  issues.map(issue => (
                    <div 
                      key={issue.id}
                      onClick={() => setSelectedIssueId(issue.id)}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${selectedIssueId === issue.id ? 'bg-indigo-50 border-indigo-300 ring-1 ring-indigo-100 shadow-sm' : 'bg-white border-slate-200 hover:border-slate-300'}`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`w-1.5 h-1.5 rounded-full ${issue.severity === 'Critical' ? 'bg-rose-500' : 'bg-amber-500'}`} />
                        <span className="text-[10px] font-bold text-slate-400 uppercase">{new Date(issue.detected_at).toLocaleDateString()}</span>
                      </div>
                      <h4 className="font-semibold text-slate-800 text-xs leading-tight">{issue.title}</h4>
                    </div>
                  ))
                )}
              </div>
            </div>
            
            <div className="flex-1 bg-white">
               <AIAssistant 
                 title="Scenario Guide"
                 context={comparison ? { issue_id: selectedIssueId, option_id: selectedOptionId, page: 'scenarios' } : { page: 'scenarios' }}
                 initialMessage={selectedOption ? `I've analyzed "${selectedOption.name}". It recovers ${selectedOption.delay_days_avoided} days but costs ${formatCurrency(selectedOption.net_cost_impact)}. Would you like to see cheaper alternatives?` : "Select an issue and scenario to compare tradeoffs. I can help explain the confidence scores."}
               />
            </div>
          </div>
        </SidePanel>

        {/* CENTER WORKSPACE: Comparison */}
        <div className="flex-1 p-6 flex flex-col gap-6 overflow-y-auto">
          
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight mb-1">Scenario Comparison</h1>
            <p className="text-slate-500 text-sm">Compare tradeoffs clearly before executing operational decisions.</p>
          </div>

          {!comparison ? (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 gap-4 border-2 border-dashed border-slate-200 rounded-xl bg-slate-50/50">
              <Activity size={32} className="opacity-50" />
              <p className="text-sm font-medium">Select an issue from the setup panel to generate AI scenarios.</p>
            </div>
          ) : (
            <div className="flex flex-col gap-6">
              
              {/* Freshness Indicator */}
              <div className="flex items-center justify-between bg-white border border-slate-200 p-3 rounded-lg shadow-sm">
                <div className="flex items-center gap-3">
                   <h2 className="font-semibold text-slate-900">{comparison.issue_title}</h2>
                   <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-bold border border-slate-200 uppercase tracking-tight">
                      Baseline Revenue at Risk: {formatCurrency(comparison.baseline.revenue_at_risk)}
                   </span>
                </div>
                <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase">
                  {isComparisonFetching && <RefreshCw size={12} className="animate-spin text-indigo-500" />}
                  <span>Sync: {new Date(comparison.last_synced_at || '').toLocaleTimeString()}</span>
                </div>
              </div>

              {/* Comparison Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                 {/* Baseline Card */}
                 <Card className="border-slate-200 border-2">
                   <CardHeader className="pb-2">
                      <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Baseline (Do Nothing)</div>
                   </CardHeader>
                   <CardContent>
                      <div className="space-y-3 mt-2">
                        <div className="flex justify-between text-sm font-medium">
                          <span className="text-slate-500">Net Cost Impact</span>
                          <span className="text-slate-900">$0</span>
                        </div>
                        <div className="flex justify-between text-sm font-medium">
                          <span className="text-slate-500">Delay Avoided</span>
                          <span className="text-slate-900">0 Days</span>
                        </div>
                        <div className="pt-3 mt-3 border-t border-slate-100">
                          <span className="text-[11px] font-bold text-rose-600 uppercase tracking-tight">Remaining Risk: {formatCurrency(comparison.baseline.revenue_at_risk)}</span>
                        </div>
                      </div>
                   </CardContent>
                 </Card>

                 {/* Option Cards */}
                 {comparison.options.map(option => {
                   const remainingRisk = Math.max(0, comparison.baseline.revenue_at_risk - (option.delay_days_avoided > 0 ? comparison.baseline.revenue_at_risk * 0.8 : 0)); // Simulated logic for UI
                   
                   return (
                     <Card 
                      key={option.id} 
                      className={`cursor-pointer transition-all ${selectedOptionId === option.id ? 'border-indigo-500 ring-2 ring-indigo-100 bg-indigo-50/10' : 'hover:border-indigo-300 border-2 border-transparent'}`}
                      onClick={() => setSelectedOptionId(option.id)}
                     >
                       <CardHeader className="pb-2 flex flex-row items-center justify-between">
                          <div className="text-[10px] font-bold text-slate-800 uppercase tracking-wider">{option.name}</div>
                          {selectedOptionId === option.id && <ShieldCheck size={14} className="text-indigo-600" />}
                       </CardHeader>
                       <CardContent>
                          <div className="space-y-3 mt-2">
                            <div className="flex justify-between text-sm font-medium">
                              <span className="text-slate-500">Execution Cost</span>
                              <span className="text-rose-600">{formatCurrency(option.net_cost_impact)}</span>
                            </div>
                            <div className="flex justify-between text-sm font-medium">
                              <span className="text-slate-500">Delay Avoided</span>
                              <span className="text-emerald-600">{option.delay_days_avoided} Days</span>
                            </div>
                            <div className="pt-3 mt-3 border-t border-slate-100">
                              <span className="text-[11px] font-bold text-amber-600 uppercase tracking-tight">Est. Remaining Risk: {formatCurrency(remainingRisk)}</span>
                            </div>
                          </div>
                       </CardContent>
                     </Card>
                   )
                 })}
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 flex-1">
                {/* Scenario Scorecard */}
                <Card>
                  <CardHeader className="bg-slate-50/50 flex flex-row items-center justify-between py-3">
                     <span className="text-sm font-bold flex items-center gap-2"><TableProperties size={16}/> Scenario Scorecard</span>
                  </CardHeader>
                  <CardContent className="p-0 overflow-hidden">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-slate-50 text-slate-500 text-[10px] uppercase font-bold">
                        <tr>
                          <th className="px-4 py-3 tracking-wider">Metric</th>
                          <th className="px-4 py-3 text-center border-l border-slate-200 tracking-wider">Baseline</th>
                          <th className="px-4 py-3 text-center border-l border-indigo-100 bg-indigo-50/50 text-indigo-700 tracking-wider">
                            {selectedOption?.name || 'Selected'}
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        <tr>
                          <td className="px-4 py-3 font-medium text-slate-700">Days Delayed</td>
                          <td className="px-4 py-3 text-center text-rose-600 font-bold border-l border-slate-200">+{comparison.baseline.total_delay_days}</td>
                          <td className="px-4 py-3 text-center text-emerald-600 font-extrabold border-l border-indigo-100 bg-indigo-50/30">
                            +{Math.max(0, comparison.baseline.total_delay_days - (selectedOption?.delay_days_avoided || 0))}
                          </td>
                        </tr>
                        <tr>
                          <td className="px-4 py-3 font-medium text-slate-700">Revenue at Risk</td>
                          <td className="px-4 py-3 text-center text-rose-600 font-bold border-l border-slate-200">{formatCurrency(comparison.baseline.revenue_at_risk)}</td>
                          <td className="px-4 py-3 text-center text-slate-700 font-extrabold border-l border-indigo-100 bg-indigo-50/30">
                            {selectedOption?.delay_days_avoided && selectedOption.delay_days_avoided > 0 ? formatCurrency(comparison.baseline.revenue_at_risk * 0.2) : formatCurrency(comparison.baseline.revenue_at_risk)}
                          </td>
                        </tr>
                        <tr>
                          <td className="px-4 py-3 font-medium text-slate-700">Execution Cost</td>
                          <td className="px-4 py-3 text-center text-slate-400 border-l border-slate-200">$0</td>
                          <td className="px-4 py-3 text-center text-rose-600 font-extrabold border-l border-indigo-100 bg-indigo-50/30">
                            {formatCurrency(selectedOption?.net_cost_impact || 0)}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </CardContent>
                </Card>

                {/* Impact Map Diff */}
                <Card>
                  <CardHeader className="bg-slate-50/50 py-3">
                     <span className="text-sm font-bold flex items-center gap-2"><Zap size={16}/> Impact Map Diff</span>
                  </CardHeader>
                  <CardContent className="p-6">
                     <div className="flex flex-col gap-6">
                        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-widest text-center">Graph Transformation Preview</div>
                        
                        <div className="flex items-center justify-between gap-4">
                           {/* Before */}
                           <div className="flex-1 bg-rose-50 border border-rose-200 rounded-lg p-4 text-center">
                             <div className="text-[10px] font-bold text-rose-800 uppercase mb-2">Before</div>
                             <div className="flex flex-col gap-2 items-center">
                               <div className="w-full bg-white p-2 rounded shadow-sm text-[10px] text-slate-600 border border-slate-200 font-medium">Material X</div>
                               <div className="h-4 w-px bg-rose-300" />
                               <div className="w-full bg-white p-2 rounded shadow-sm text-[10px] text-rose-600 font-bold border border-rose-200">WorkOrder (Delayed)</div>
                             </div>
                           </div>
                           
                           <ArrowRight className="text-slate-300 flex-shrink-0" />
                           
                           {/* After */}
                           <div className="flex-1 bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-center">
                             <div className="text-[10px] font-bold text-emerald-800 uppercase mb-2">After</div>
                             <div className="flex flex-col gap-2 items-center">
                               <div className="w-full bg-white p-2 rounded shadow-sm text-[10px] text-slate-600 border border-slate-200 font-medium">Material X</div>
                               <div className="h-4 w-px bg-emerald-300" />
                               <div className="w-full bg-white p-2 rounded shadow-sm text-[10px] text-emerald-600 font-bold border border-emerald-200">WorkOrder (On Time)</div>
                             </div>
                           </div>
                        </div>
                     </div>
                  </CardContent>
                </Card>
              </div>
              
            </div>
          )}
        </div>

        {/* RIGHT PANEL: Recommended Option Details */}
        <SidePanel side="right">
          <div className="p-5 h-full flex flex-col overflow-y-auto">
            <div className="flex items-center gap-2 mb-6 text-indigo-600">
               <ShieldCheck size={18} />
               <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900">Execution Plan</h2>
            </div>
            
            {!selectedOption ? (
              <div className="text-slate-500 text-xs mt-4 bg-slate-50 p-4 rounded-lg border border-slate-100 text-center font-medium">
                Select an option from the comparison workspace to view execution steps.
              </div>
            ) : (
              <div className="flex flex-col gap-6 animate-in fade-in duration-300">
                
                <div>
                  <h3 className="font-semibold text-base text-slate-900 leading-tight mb-2">{selectedOption.name}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {selectedOption.description}
                  </p>
                </div>

                <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
                   <div className="bg-slate-50 px-4 py-2.5 border-b border-slate-200 font-bold text-slate-800 text-[10px] uppercase tracking-wider">
                     Required Actions
                   </div>
                   <div className="p-4 space-y-4">
                      {selectedOption.recommendations.map((rec, idx) => (
                        <div key={rec.id} className="flex gap-3">
                          <div className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-[10px] font-bold mt-0.5">
                            {idx + 1}
                          </div>
                          <div>
                            <div className="font-bold text-slate-800 text-xs">{rec.action_type}</div>
                            <div className="text-[11px] text-slate-500 mt-1 space-y-1">
                              {rec.action_details && Object.entries(rec.action_details).map(([k, v]) => (
                                <div key={k}><span className="font-semibold text-slate-600 uppercase text-[9px]">{k}:</span> {v}</div>
                              ))}
                            </div>
                            {rec.confidence_score && (
                              <div className="mt-2 inline-flex items-center gap-1 bg-slate-100 px-2 py-0.5 rounded text-[9px] font-bold text-slate-500 uppercase">
                                AI Confidence: {(rec.confidence_score * 100).toFixed(0)}%
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                   </div>
                </div>
                
                <div className="mt-auto pt-6">
                  <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-lg text-xs font-bold transition-colors flex items-center justify-center gap-2 shadow-sm uppercase tracking-wider">
                    <ShieldCheck size={14} /> Execute Scenario
                  </button>
                  <button className="w-full mt-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 py-2.5 rounded-lg text-xs font-bold transition-colors uppercase tracking-wider">
                    Save as Draft
                  </button>
                </div>

              </div>
            )}
          </div>
        </SidePanel>
      </div>
    </ProtectedRoute>
  );
}
