import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SourcesPage from './page';

// Mock fetch
global.fetch = vi.fn();

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

describe('SourcesPage', () => {
  it('renders correctly', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <SourcesPage />
      </QueryClientProvider>
    );
    expect(screen.getByText('Sources')).toBeInTheDocument();
  });
});
