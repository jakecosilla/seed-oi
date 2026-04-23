'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { fetchApi } from '@/lib/api-client';
import { Save, UploadCloud, ShieldAlert, History, User, AlertTriangle, Play, Database, Factory, Users, Settings as SettingsIcon, Brain } from 'lucide-react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/providers/AuthProvider';

type SettingResponse = {
  id: string;
  tenant_id: string;
  plant_id: string | null;
  category: string;
  status: string;
  payload: any;
  created_at: string;
  updated_at: string;
};

type RiskRulesPayload = {
  material_shortage_days: number;
  delay_exposure_usd: number;
  bottleneck_utilization_percent: number;
  severity_model: string;
  escalation_logic: string;
};

const DEFAULT_RISK_RULES: RiskRulesPayload = {
  material_shortage_days: 14,
  delay_exposure_usd: 50000,
  bottleneck_utilization_percent: 85,
  severity_model: 'Standard (Time + Cost)',
  escalation_logic: 'Auto-escalate Critical'
};

const NAV_ITEMS = [
  { id: 'organization', label: 'Organization', icon: SettingsIcon },
  { id: 'plants', label: 'Plants & Sites', icon: Factory },
  { id: 'risk_rules', label: 'Risk Rules', icon: ShieldAlert },
  { id: 'alerts', label: 'Alerts & Notifications', icon: AlertTriangle },
  { id: 'users', label: 'Users & Roles', icon: Users },
  { id: 'ai', label: 'AI Assistant', icon: Brain },
  { id: 'mapping', label: 'Data Mapping', icon: Database },
  { id: 'audit', label: 'Audit & Governance', icon: History },
];

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('risk_rules');
  const [localDraft, setLocalDraft] = useState<RiskRulesPayload | null>(null);

  const tenantId = user?.tenant_id || '00000000-0000-0000-0000-000000000000';

  // Fetch Risk Rules Setting
  const { data: settings = [], isLoading } = useQuery({
    queryKey: ['settings', tenantId, 'risk_rules'],
    queryFn: () => fetchApi<SettingResponse[]>(`/settings/${tenantId}?category=risk_rules`),
    enabled: !!user,
  });

  const currentSetting = settings[0]; // Assuming one global risk rule setting for simplicity
  const serverPayload = currentSetting?.payload as RiskRulesPayload || DEFAULT_RISK_RULES;
  const isPublished = currentSetting?.status === 'published';

  // Sync server data to local draft on load
  useEffect(() => {
    if (!localDraft && settings.length > 0) {
      setLocalDraft(settings[0].payload);
    } else if (!localDraft && !isLoading) {
      setLocalDraft(DEFAULT_RISK_RULES);
    }
  }, [settings, isLoading, localDraft]);

  // Mutations
  const saveDraftMutation = useMutation({
    mutationFn: (payload: RiskRulesPayload) => {
      if (currentSetting) {
        return fetchApi(`/settings/${tenantId}/${currentSetting.id}`, {
          method: 'PUT',
          body: JSON.stringify({ payload }),
        });
      } else {
        return fetchApi(`/settings/${tenantId}`, {
          method: 'POST',
          body: JSON.stringify({ category: 'risk_rules', payload }),
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', tenantId, 'risk_rules'] });
    }
  });

  const publishMutation = useMutation({
    mutationFn: (settingId: string) => fetchApi(`/settings/${tenantId}/${settingId}/publish`, { method: 'POST' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', tenantId, 'risk_rules'] });
    }
  });

  const handleSaveDraft = () => {
    if (localDraft) saveDraftMutation.mutate(localDraft);
  };

  const handlePublish = () => {
    if (currentSetting) publishMutation.mutate(currentSetting.id);
  };

  const updateDraft = (key: keyof RiskRulesPayload, value: any) => {
    if (localDraft) {
      setLocalDraft({ ...localDraft, [key]: value });
    }
  };

  const isDirty = localDraft && JSON.stringify(localDraft) !== JSON.stringify(serverPayload);

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <div className="flex h-full w-full bg-slate-50 overflow-hidden">
        
        {/* Left Navigation */}
        <div className="w-64 bg-white border-r border-slate-200 overflow-y-auto shrink-0 hidden md:block">
          <div className="p-6">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">Configuration</h2>
            <nav className="flex flex-col gap-1">
              {NAV_ITEMS.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                      isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`}
                  >
                    <Icon size={18} className={isActive ? 'text-blue-600' : 'text-slate-400'} />
                    {item.label}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Main Workspace */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl">
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-slate-900 mb-2">Risk Rules</h1>
              <p className="text-slate-500">Define how the system evaluates delays, shortages, and bottlenecks.</p>
            </div>

            {activeTab === 'risk_rules' && localDraft ? (
              <div className="flex flex-col gap-6">
                
                <Card>
                  <CardHeader className="border-b border-slate-100 bg-white">
                    <h3 className="font-semibold text-slate-900">Material Shortage Rules</h3>
                  </CardHeader>
                  <CardContent className="pt-6">
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-slate-700">Warning Horizon (Days)</label>
                      <p className="text-xs text-slate-500 mb-2">Flag inventory running below minimum safety stock within this window.</p>
                      <input 
                        type="number" 
                        value={localDraft.material_shortage_days}
                        onChange={(e) => updateDraft('material_shortage_days', parseInt(e.target.value) || 0)}
                        className="w-full max-w-xs border border-slate-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="border-b border-slate-100 bg-white">
                    <h3 className="font-semibold text-slate-900">Delay Exposure Rules</h3>
                  </CardHeader>
                  <CardContent className="pt-6">
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-slate-700">Critical Financial Threshold (USD)</label>
                      <p className="text-xs text-slate-500 mb-2">Delays impacting orders exceeding this value are automatically escalated.</p>
                      <input 
                        type="number" 
                        value={localDraft.delay_exposure_usd}
                        onChange={(e) => updateDraft('delay_exposure_usd', parseInt(e.target.value) || 0)}
                        className="w-full max-w-xs border border-slate-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="border-b border-slate-100 bg-white">
                    <h3 className="font-semibold text-slate-900">Bottleneck Rules</h3>
                  </CardHeader>
                  <CardContent className="pt-6">
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-slate-700">Utilization Trigger (%)</label>
                      <p className="text-xs text-slate-500 mb-2">Work centers operating above this capacity percentage are flagged as bottlenecks.</p>
                      <input 
                        type="number" 
                        value={localDraft.bottleneck_utilization_percent}
                        onChange={(e) => updateDraft('bottleneck_utilization_percent', parseInt(e.target.value) || 0)}
                        className="w-full max-w-xs border border-slate-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="border-b border-slate-100 bg-white">
                    <h3 className="font-semibold text-slate-900">Severity Model & Escalation</h3>
                  </CardHeader>
                  <CardContent className="pt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-slate-700">Severity Model</label>
                      <select 
                        value={localDraft.severity_model}
                        onChange={(e) => updateDraft('severity_model', e.target.value)}
                        className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
                      >
                        <option>Standard (Time + Cost)</option>
                        <option>Aggressive (Time Only)</option>
                        <option>Conservative (Cost Only)</option>
                      </select>
                    </div>
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-slate-700">Escalation Logic</label>
                      <select 
                        value={localDraft.escalation_logic}
                        onChange={(e) => updateDraft('escalation_logic', e.target.value)}
                        className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
                      >
                        <option>Auto-escalate Critical</option>
                        <option>Require Manual Review</option>
                        <option>Notify Only</option>
                      </select>
                    </div>
                  </CardContent>
                </Card>

              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-slate-400 italic text-sm">
                {isLoading ? 'Loading settings...' : 'Select a configuration category.'}
              </div>
            )}
          </div>
        </div>

        {/* Right Summary Panel */}
        <div className="w-80 bg-white border-l border-slate-200 overflow-y-auto shrink-0 hidden lg:block shadow-[-4px_0_15px_-3px_rgba(0,0,0,0.02)]">
          <div className="p-6 flex flex-col gap-6">
            
            <div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">Status Summary</h3>
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-sm text-slate-600 font-medium">Current State</span>
                <Badge variant={isPublished && !isDirty ? 'success' : isDirty ? 'warning' : 'neutral'}>
                  {isDirty ? 'Unsaved Changes' : (currentSetting?.status || 'New')}
                </Badge>
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <button 
                onClick={handleSaveDraft}
                disabled={!isDirty || saveDraftMutation.isPending}
                className={`flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isDirty 
                    ? 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200' 
                    : 'bg-slate-50 text-slate-400 cursor-not-allowed border border-slate-100'
                }`}
              >
                <Save size={16} /> 
                {saveDraftMutation.isPending ? 'Saving...' : 'Save Draft'}
              </button>
              <button 
                onClick={handlePublish}
                disabled={isDirty || !currentSetting || isPublished || publishMutation.isPending}
                className={`flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-sm font-medium transition-all shadow-sm ${
                  !isDirty && currentSetting && !isPublished
                    ? 'bg-slate-900 text-white hover:bg-slate-800'
                    : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                }`}
              >
                <UploadCloud size={16} />
                {publishMutation.isPending ? 'Publishing...' : 'Publish Rules'}
              </button>
            </div>

            <div className="border-t border-slate-100 pt-6">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">Impact Preview</h3>
              <div className="p-4 bg-blue-50/50 border border-blue-100 rounded-lg">
                <div className="flex items-start gap-3">
                  <Play size={16} className="text-blue-600 mt-0.5 shrink-0" />
                  <p className="text-xs text-blue-900 leading-relaxed font-medium">
                    Applying these rules will recalculate risk scores across <strong>1,245</strong> active work orders. Estimated completion time is ~2 minutes.
                  </p>
                </div>
              </div>
            </div>

            {currentSetting && (
              <div className="border-t border-slate-100 pt-6">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">Audit Info</h3>
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500">
                    <User size={14} />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-slate-900">System Admin</span>
                    <span className="text-xs text-slate-500">Last updated {new Date(currentSetting.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
