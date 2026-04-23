"use client";

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';
import { fetchApi } from '@/lib/api-client';
import { AlertCircle, Clock, DollarSign, Activity, TrendingUp, AlertTriangle, Filter, Layers } from 'lucide-react';
import { AIAssistant } from '@/components/layout/AIAssistant';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export interface RiskSummary {
  total_active_risks: number;
  critical_bottlenecks: number;
  upcoming_delay_days: number;
  total_exposure_usd: number;
}

export interface TimelineEvent {
  id: string;
  date: string;
  title: string;
  severity: string;
  delay_days: number;
  revenue_exposure: number;
}

export interface BottleneckItem {
  entity_id: string;
  entity_type: string;
  risk_count: number;
  total_delay_days: number;
}

const fetchRiskSummary = async () => fetchApi<RiskSummary>('/risks/summary');
const fetchTimeline = async () => fetchApi<TimelineEvent[]>('/risks/timeline');
const fetchBottlenecks = async () => fetchApi<BottleneckItem[]>('/risks/bottlenecks');

export default function RisksPage() {
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  const { data: summary } = useQuery({
    queryKey: ['risks-summary'],
    queryFn: fetchRiskSummary,
    refetchInterval: 10000,
  });

  const { data: timeline = [] } = useQuery({
    queryKey: ['risks-timeline'],
    queryFn: fetchTimeline,
    refetchInterval: 10000,
  });

  const { data: bottlenecks = [] } = useQuery({
    queryKey: ['risks-bottlenecks'],
    queryFn: fetchBottlenecks,
    refetchInterval: 10000,
  });

  const formatCurrency = (val: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  const selectedEvent = timeline.find((e) => e.id === selectedEventId);

  return (
    <ProtectedRoute>
      <div className="flex flex-1 w-full h-full overflow-hidden bg-slate-50">
        
        {/* LEFT PANEL: AI Assistant */}
        <SidePanel side="left">
          <AIAssistant 
            title="Risk Analysis"
            context={selectedEvent ? { event_id: selectedEvent.id, severity: selectedEvent.severity, type: 'risk_drilldown' } : { page: 'risks' }}
            initialMessage={selectedEvent ? `Analyzing the risk: "${selectedEvent.title}". How would you like to explore the impact?` : "I'm projecting risks for the next 30 days. You can ask about material shortages or site-specific delays."}
          />
        </SidePanel>

        {/* CENTER WORKSPACE */}
        <div className="flex-1 p-6 flex flex-col gap-6 overflow-y-auto">
          
          {/* Header */}
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight mb-1">Operational Risks</h1>
            <p className="text-slate-500 text-sm">Forward-looking vulnerability analysis identifying bottlenecks and material shortages.</p>
          </div>

          {/* Top Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-slate-500">Total Active Risks</span>
                  <Activity size={16} className="text-indigo-500" />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? summary.total_active_risks : '...'}
                </span>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-slate-500">Critical Bottlenecks</span>
                  <AlertTriangle size={16} className="text-amber-500" />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? summary.critical_bottlenecks : '...'}
                </span>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-slate-500">Upcoming Delay (Days)</span>
                  <Clock size={16} className="text-rose-500" />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? summary.upcoming_delay_days : '...'}
                </span>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 flex flex-col gap-1">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-slate-500">Total Exposure</span>
                  <DollarSign size={16} className="text-emerald-600" />
                </div>
                <span className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary ? formatCurrency(summary.total_exposure_usd) : '...'}
                </span>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 flex-1 min-h-[400px]">
            {/* Risk Horizon Timeline */}
            <Card className="flex flex-col h-full">
              <CardHeader className="bg-slate-50/50 flex flex-row items-center justify-between">
                 <span>Risk Horizon Timeline</span>
                 <span className="text-xs font-normal text-slate-400">Next 30 Days</span>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-5">
                {timeline.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-slate-400 italic text-sm">No upcoming risks detected.</div>
                ) : (
                  <div className="relative border-l-2 border-slate-200 ml-3 space-y-6">
                    {timeline.map((event) => (
                      <div 
                        key={event.id} 
                        className="relative pl-6 cursor-pointer group"
                        onClick={() => setSelectedEventId(event.id)}
                      >
                        {/* Timeline Dot */}
                        <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-white ${event.severity === 'Critical' ? 'bg-rose-500' : 'bg-amber-500'} group-hover:scale-110 transition-transform`} />
                        
                        <div className={`bg-white border rounded-lg p-3 shadow-sm transition-all ${selectedEventId === event.id ? 'border-indigo-400 ring-1 ring-indigo-100' : 'border-slate-200 hover:border-slate-300'}`}>
                          <div className="flex justify-between items-start mb-1">
                            <span className="text-xs font-bold text-slate-500 uppercase">{event.date}</span>
                            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${event.severity === 'Critical' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'}`}>
                              {event.severity}
                            </span>
                          </div>
                          <h4 className="font-semibold text-slate-900 text-sm">{event.title}</h4>
                          <div className="flex gap-4 mt-2 text-xs font-medium">
                            {event.delay_days > 0 && <span className="text-slate-600 flex items-center gap-1"><Clock size={12}/> +{event.delay_days}d</span>}
                            {event.revenue_exposure > 0 && <span className="text-rose-600 flex items-center gap-1"><DollarSign size={12}/> {formatCurrency(event.revenue_exposure)}</span>}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Bottleneck Explorer / Heatmap */}
            <Card className="flex flex-col h-full">
              <CardHeader className="bg-slate-50/50 flex flex-row items-center justify-between">
                <span>Bottleneck Explorer</span>
                <TrendingUp size={16} className="text-slate-400" />
              </CardHeader>
              <CardContent className="flex-1 p-6 overflow-y-auto">
                 <div className="space-y-5">
                   {bottlenecks.length === 0 ? (
                      <div className="flex items-center justify-center h-full text-slate-400 italic text-sm mt-10">No active bottlenecks identified.</div>
                   ) : (
                      bottlenecks.map((btn, idx) => {
                        // Calculate width percentage relative to the worst bottleneck
                        const maxDelay = Math.max(...bottlenecks.map(b => b.total_delay_days), 1);
                        const widthPct = Math.max((btn.total_delay_days / maxDelay) * 100, 10);
                        
                        return (
                          <div key={idx} className="flex flex-col gap-1">
                            <div className="flex justify-between items-end text-sm">
                              <span className="font-medium text-slate-800">{btn.entity_type}: <span className="font-mono text-slate-500">{btn.entity_id.substring(0,8)}</span></span>
                              <span className="text-rose-600 font-semibold">{btn.total_delay_days} Days Total</span>
                            </div>
                            <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-gradient-to-r from-rose-400 to-rose-600 rounded-full transition-all duration-500" 
                                style={{ width: `${widthPct}%` }}
                              />
                            </div>
                            <span className="text-xs text-slate-500">{btn.risk_count} colliding risks at this node.</span>
                          </div>
                        );
                      })
                   )}
                 </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* RIGHT PANEL: Risk Details */}
        <SidePanel side="right">
          <div className="p-5 h-full flex flex-col overflow-y-auto">
            <div className="flex items-center gap-2 mb-4 text-indigo-600">
               <AlertCircle size={18} />
               <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900">Risk Details</h2>
            </div>
            
            {!selectedEvent ? (
              <div className="text-slate-500 text-sm mt-4 bg-slate-50 p-4 rounded-lg border border-slate-100 text-center">
                Select an event on the timeline to view root cause and exposure metrics.
              </div>
            ) : (
              <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-right-4 duration-300">
                
                <div>
                  <h3 className="font-semibold text-lg text-slate-900 leading-tight mb-2">{selectedEvent.title}</h3>
                  <div className="flex items-center gap-2 mb-4">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600`}>
                      Date: {selectedEvent.date}
                    </span>
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${selectedEvent.severity === 'Critical' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'}`}>
                      Severity: {selectedEvent.severity}
                    </span>
                  </div>
                </div>

                <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
                   <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 font-semibold text-slate-800 text-sm">
                     Exposure Metrics
                   </div>
                   <div className="p-4 space-y-4">
                      <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                        <span className="text-sm text-slate-500">Estimated Delay</span>
                        <span className="font-bold text-amber-600 flex items-center gap-1">
                          <Clock size={14} /> +{selectedEvent.delay_days} Days
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-500">Revenue at Risk</span>
                        <span className="font-bold text-rose-600 flex items-center gap-1">
                          <DollarSign size={14} /> {formatCurrency(selectedEvent.revenue_exposure)}
                        </span>
                      </div>
                   </div>
                </div>
                
                <div className="p-4 bg-indigo-50 border border-indigo-100 rounded-lg text-sm text-indigo-800">
                  <strong>Next Step:</strong> Navigate to the Overview tab to review AI-generated mitigation strategies for this risk.
                </div>

              </div>
            )}
          </div>
        </SidePanel>
      </div>
    </ProtectedRoute>
  );
}
