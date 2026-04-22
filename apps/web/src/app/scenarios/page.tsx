import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';

export default function ScenariosPage() {
  return (
    <div style={{ display: 'flex', flex: 1, width: '100%' }}>
      <SidePanel side="left">
        <div style={{ padding: '1.25rem' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Scenario Planner</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Test actions and define levers.</p>
        </div>
      </SidePanel>
      <div style={{ flex: 1, padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Scenarios</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Compare possible actions before executing them.</p>
        </div>
        <Card>
          <CardHeader>Compare scenarios</CardHeader>
          <CardContent>
            <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-tertiary)', border: '1px dashed var(--border-strong)', borderRadius: 'var(--radius-md)' }}>
              Comparison Workspace Placeholder
            </div>
          </CardContent>
        </Card>
      </div>
      <SidePanel side="right">
        <div style={{ padding: '1.25rem' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Recommended Option</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Expected outcomes and confidence.</p>
        </div>
      </SidePanel>
    </div>
  );
}
