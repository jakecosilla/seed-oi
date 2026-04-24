import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import React from 'react';
import { RealtimeProvider, useRealtime } from './RealtimeProvider';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const mockEventSourceInstance = {
  url: '',
  onopen: null as any,
  onmessage: null as any,
  onerror: null as any,
  close: vi.fn(),
};

vi.stubGlobal('EventSource', function(url: string) {
  mockEventSourceInstance.url = url;
  mockEventSourceInstance.onopen = null;
  mockEventSourceInstance.onmessage = null;
  mockEventSourceInstance.onerror = null;
  mockEventSourceInstance.close.mockClear();
  return mockEventSourceInstance;
});

const mockInvalidateQueries = vi.fn();
vi.mock('@tanstack/react-query', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@tanstack/react-query')>();
  return {
    ...actual,
    useQueryClient: () => ({
      invalidateQueries: mockInvalidateQueries,
    }),
  };
});

vi.mock('./AuthProvider', () => ({
  useAuth: () => ({
    user: { tenant_id: 'tenant-123', id: '1', email: 'test@example.com', name: 'Test', role: 'admin' },
  }),
}));

describe('RealtimeProvider', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient();
    mockInvalidateQueries.mockClear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => {
    return (
      <QueryClientProvider client={queryClient}>
        <RealtimeProvider>
          {children}
        </RealtimeProvider>
      </QueryClientProvider>
    );
  };

  it('invalidates relevant queries on issue_created event', () => {
    const { result } = renderHook(() => useRealtime(), { wrapper });
    
    act(() => {
      mockEventSourceInstance.onmessage?.({
        data: JSON.stringify({ event: 'issue_created', data: { id: 'issue-1' } })
      });
    });

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['overview-summary', 'tenant-123'] });
    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['overview-issues', 'tenant-123'] });
    
    expect(result.current.recentEvents[0]?.type).toBe('issue_created');
  });
});
