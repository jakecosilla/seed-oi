import { Card, CardContent, CardHeader } from '@/components/ui/Card';

export default function SourcesPage() {
  return (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
      <div>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Sources</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Understand data trust and traceability.</p>
      </div>
      <Card>
        <CardHeader>Connected Systems</CardHeader>
        <CardContent>
          <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-tertiary)', border: '1px dashed var(--border-strong)', borderRadius: 'var(--radius-md)' }}>
            System Sync Health Placeholder
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
