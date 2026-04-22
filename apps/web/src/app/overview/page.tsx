import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';

export default function OverviewPage() {
  return (
    <div className="flex flex-1 w-full h-full">
      <SidePanel side="left">
        <div className="p-5">
          <h2 className="text-sm font-semibold text-slate-900 mb-4 uppercase tracking-wider">Ask Operations</h2>
          <p className="text-slate-500 text-sm">Query your supply chain state.</p>
        </div>
      </SidePanel>
      <div className="flex-1 p-6 flex flex-col gap-6 bg-slate-50/50 overflow-y-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 mb-2">Overview</h1>
            <p className="text-slate-500">Live operational command center.</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card><CardContent><div className="h-20 bg-slate-50 rounded animate-pulse" /></CardContent></Card>
          <Card><CardContent><div className="h-20 bg-slate-50 rounded animate-pulse" /></CardContent></Card>
          <Card><CardContent><div className="h-20 bg-slate-50 rounded animate-pulse" /></CardContent></Card>
          <Card><CardContent><div className="h-20 bg-slate-50 rounded animate-pulse" /></CardContent></Card>
        </div>
        <Card>
          <CardHeader>Operational Impact Map</CardHeader>
          <CardContent>
            <div className="h-[400px] flex items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-lg bg-slate-50/50 italic text-sm">
              Impact Map Visualization Placeholder
            </div>
          </CardContent>
        </Card>
      </div>
      <SidePanel side="right">
        <div className="p-5">
          <h2 className="text-sm font-semibold text-slate-900 mb-4 uppercase tracking-wider">Issue Summary</h2>
          <p className="text-slate-500 text-sm">Select an issue to see details.</p>
        </div>
      </SidePanel>
    </div>
  );
}
