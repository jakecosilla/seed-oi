import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';

export default function ScenariosPage() {
  return (
    <div className="flex flex-1 w-full h-full">
      <SidePanel side="left">
        <div className="p-5">
          <h2 className="text-sm font-semibold text-slate-900 mb-4 uppercase tracking-wider">Scenario Planner</h2>
          <p className="text-slate-500 text-sm">Test actions and define levers.</p>
        </div>
      </SidePanel>
      <div className="flex-1 p-6 flex flex-col gap-6 bg-slate-50/50 overflow-y-auto">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Scenarios</h1>
          <p className="text-slate-500">Compare possible actions before executing them.</p>
        </div>
        <Card>
          <CardHeader>Compare scenarios</CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-lg bg-slate-50/50 italic text-sm">
              Comparison Workspace Placeholder
            </div>
          </CardContent>
        </Card>
      </div>
      <SidePanel side="right">
        <div className="p-5">
          <h2 className="text-sm font-semibold text-slate-900 mb-4 uppercase tracking-wider">Recommended Option</h2>
          <p className="text-slate-500 text-sm">Expected outcomes and confidence.</p>
        </div>
      </SidePanel>
    </div>
  );
}
