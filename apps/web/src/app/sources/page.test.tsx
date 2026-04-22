import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SourcesPage from './page';

// Mock fetch
global.fetch = vi.fn();

describe('SourcesPage', () => {
  it('renders correctly', () => {
    (global.fetch as any).mockResolvedValue({
      json: async () => [],
    });

    render(<SourcesPage />);
    expect(screen.getByText('Sources')).toBeInTheDocument();
  });
});
