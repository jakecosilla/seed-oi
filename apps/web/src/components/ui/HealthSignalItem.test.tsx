import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HealthSignalItem } from './HealthSignalItem';

describe('HealthSignalItem', () => {
  it('renders healthy signal correctly', () => {
    render(
      <HealthSignalItem
        category="Healthy"
        title="Stable Inventory"
        description="Inventory is stable"
        impactArea="Production"
        metricValue="98%"
      />
    );

    expect(screen.getByText('Stable Inventory')).toBeDefined();
    expect(screen.getByText('Inventory is stable')).toBeDefined();
    expect(screen.getByText('Healthy • Production')).toBeDefined();
    expect(screen.getByText('98%')).toBeDefined();
  });

  it('renders trend indicators correctly', () => {
    const { rerender } = render(
      <HealthSignalItem
        category="Improved"
        title="Lead Time"
        description="Decreased lead time"
        impactArea="Supply Chain"
        metricValue="-15%"
        metricTrend="down"
      />
    );

    expect(screen.getByText(/-15% ↓/)).toBeDefined();

    rerender(
      <HealthSignalItem
        category="Capacity"
        title="Line 4"
        description="Increased capacity"
        impactArea="Manufacturing"
        metricValue="20%"
        metricTrend="up"
      />
    );

    expect(screen.getByText(/20% ↑/)).toBeDefined();
  });
});
