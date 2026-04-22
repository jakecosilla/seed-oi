import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';

export default function OverviewPage() {
  return (
    <div style={{ display: 'flex', flex: 1, width: '100%' }}>
      <SidePanel side="left">
        <div style={{ padding: '1.25rem' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Ask Operations</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Filters and AI chat placeholder.</p>
        </div>
      </SidePanel>
      <div style={{ flex: 1, padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Overview</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Command center for current issues and downstream impact.</p>
        </div>
        <Card>
          <CardHeader>Operational Impact Map</CardHeader>
          <CardContent>
            <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-tertiary)', border: '1px dashed var(--border-strong)', borderRadius: 'var(--radius-md)' }}>
              Visualization Placeholder
            </div>
          </CardContent>
        </Card>
      </div>
      <SidePanel side="right">
        <div style={{ padding: '1.25rem' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Issue Summary</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Context and next best actions.</p>
        </div>
      </SidePanel>
    </div>
  );
}
