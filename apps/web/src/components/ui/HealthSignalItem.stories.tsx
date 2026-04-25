import type { Meta, StoryObj } from '@storybook/react';
import { HealthSignalItem } from './HealthSignalItem';

const meta: Meta<typeof HealthSignalItem> = {
  title: 'UI/HealthSignalItem',
  component: HealthSignalItem,
  tags: ['autodocs'],
  argTypes: {
    category: {
      control: 'select',
      options: ['Healthy', 'Improved', 'Capacity', 'Opportunity'],
    },
    metricTrend: {
      control: 'select',
      options: ['up', 'down', 'stable'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof HealthSignalItem>;

export const Healthy: Story = {
  args: {
    category: 'Healthy',
    title: 'Material Inventory: Southern Site',
    description: 'Inventory levels for core components are stable with 14 days of safety stock.',
    impactArea: 'Production',
    metricValue: '98%',
    metricTrend: 'stable',
  },
};

export const Improved: Story = {
  args: {
    category: 'Improved',
    title: 'Lead Time: Vendor Alpha',
    description: 'Average lead time has decreased by 2 days over the last 30 days.',
    impactArea: 'Supply Chain',
    metricValue: '-15%',
    metricTrend: 'down',
  },
};

export const Capacity: Story = {
  args: {
    category: 'Capacity',
    title: 'Line 4 Availability',
    description: 'Line 4 has 20% available capacity next week due to early maintenance completion.',
    impactArea: 'Manufacturing',
    metricValue: '20%',
    metricTrend: 'up',
  },
};

export const Opportunity: Story = {
  args: {
    category: 'Opportunity',
    title: 'Consolidated Shipping',
    description: 'Opportunity to consolidate 5 pending shipments from Vendor Beta to save $12k.',
    impactArea: 'Logistics',
    metricValue: '$12,000',
    metricTrend: 'up',
  },
};
