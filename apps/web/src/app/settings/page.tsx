import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { SidePanel } from '@/components/ui/SidePanel';

export default function SettingsPage() {
  return (
    <div style={{ display: 'flex', flex: 1, width: '100%' }}>
      <SidePanel side="left">
        <div style={{ padding: '1.25rem' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Settings</h2>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, color: 'var(--text-secondary)', fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <li style={{ color: 'var(--primary)', fontWeight: 500 }}>Risk Rules</li>
            <li>Organization</li>
            <li>Alerts & Notifications</li>
            <li>Users & Roles</li>
          </ul>
        </div>
      </SidePanel>
      <div style={{ flex: 1, padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Risk Rules</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Configure how Seed OI evaluates material shortages and delay exposure.</p>
        </div>
        <Card>
          <CardHeader>Material Shortage Rules</CardHeader>
          <CardContent>
            <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-tertiary)', border: '1px dashed var(--border-strong)', borderRadius: 'var(--radius-md)' }}>
              Configuration Workspace Placeholder
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
