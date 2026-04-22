import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';

export default function RisksPage() {
  return (
    <div className="flex flex-1 w-full h-full">
      <SidePanel side="left">
        <div className="p-5">
          <h2 className="text-sm font-semibold text-slate-900 mb-4 uppercase tracking-wider">Risk Horizon</h2>
          <p className="text-slate-500 text-sm">Forward-looking vulnerability analysis.</p>
        </div>
      </SidePanel>
      <div className="flex-1 p-6 flex flex-col gap-6 bg-slate-50/50 overflow-y-auto">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Risks</h1>
          <p className="text-slate-500">Identify upcoming bottlenecks and material shortages.</p>
        </div>
        <Card>
          <CardHeader>Risk Horizon Timeline</CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-lg bg-slate-50/50 italic text-sm">
              Timeline Visualization Placeholder
            </div>
          </CardContent>
        </Card>
      </div>
      <SidePanel side="right">
        <div className="p-5">
          <h2 className="text-sm font-semibold text-slate-900 mb-4 uppercase tracking-wider">Risk Details</h2>
          <p className="text-slate-500 text-sm">Root cause and exposure metrics.</p>
        </div>
      </SidePanel>
    </div>
  );
}
