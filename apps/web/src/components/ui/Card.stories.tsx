import type { Meta, StoryObj } from '@storybook/react';
import { Card, CardHeader, CardContent } from './Card';

const meta: Meta<typeof Card> = {
  title: 'UI/Card',
  component: Card,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof Card>;

export const Default: Story = {
  render: () => (
    <Card style={{ width: '300px' }}>
      <CardHeader><h3 style={{ margin: 0, fontSize: '1rem' }}>Card Header</h3></CardHeader>
      <CardContent>
        <p style={{ margin: 0, color: 'var(--text-secondary)' }}>This is the content inside the card.</p>
      </CardContent>
    </Card>
  )
};
