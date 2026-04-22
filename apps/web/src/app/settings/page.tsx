import { Card, CardContent, CardHeader } from '@/components/ui/Card';

export default function SettingsPage() {
  return (
    <div className="flex flex-col flex-1 h-full w-full bg-slate-50/50 overflow-y-auto p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Settings</h1>
        <p className="text-slate-500">Configure your organization, plants, and risk thresholds.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>General</CardHeader>
          <CardContent><div className="h-32 flex items-center justify-center text-slate-400 italic text-xs">Configuration UI Placeholder</div></CardContent>
        </Card>
        <Card>
          <CardHeader>Plants & Sites</CardHeader>
          <CardContent><div className="h-32 flex items-center justify-center text-slate-400 italic text-xs">Configuration UI Placeholder</div></CardContent>
        </Card>
        <Card>
          <CardHeader>Risk Rules</CardHeader>
          <CardContent><div className="h-32 flex items-center justify-center text-slate-400 italic text-xs">Configuration UI Placeholder</div></CardContent>
        </Card>
      </div>
    </div>
  );
}
