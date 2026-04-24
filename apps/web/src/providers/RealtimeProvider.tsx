"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAuth } from './AuthProvider';

interface RealtimeContextType {
  isConnected: boolean;
  lastEventAt: Date | null;
  recentEvents: Array<{ type: string; timestamp: Date }>;
}

const RealtimeContext = createContext<RealtimeContextType>({
  isConnected: false,
  lastEventAt: null,
  recentEvents: [],
});

export function useRealtime() {
  return useContext(RealtimeContext);
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  const [isConnected, setIsConnected] = useState(false);
  const [lastEventAt, setLastEventAt] = useState<Date | null>(null);
  const [recentEvents, setRecentEvents] = useState<Array<{ type: string; timestamp: Date }>>([]);

  useEffect(() => {
    if (!user) return;

    // Use SSE for real-time updates
    const eventSource = new EventSource(`${API_BASE_URL}/events/stream`);

    eventSource.onopen = () => {
      setIsConnected(true);
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      // EventSource will automatically attempt to reconnect
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const eventType = data.event;
        const now = new Date();

        setLastEventAt(now);
        setRecentEvents((prev) => [{ type: eventType, timestamp: now }, ...prev].slice(0, 5));

        const tenantId = user.tenant_id;

        // Smart cache invalidation based on event type
        switch (eventType) {
          case 'source_sync_started':
          case 'source_sync_completed':
          case 'source_sync_failed':
          case 'freshness_changed':
            queryClient.invalidateQueries({ queryKey: ['sources', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['overview-summary', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['risks-summary', tenantId] });
            break;
          
          case 'issue_created':
          case 'issue_updated':
            queryClient.invalidateQueries({ queryKey: ['overview-summary', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['overview-issues', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['risks-summary', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['risks-timeline', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['risks-bottlenecks', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['scenarios-issues', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['scenarios-comparison'] });
            break;
            
          case 'recommendation_updated':
            queryClient.invalidateQueries({ queryKey: ['overview-issues', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['scenarios-comparison'] });
            break;

          default:
            // Fallback for unknown events, just invalidate everything to be safe
            queryClient.invalidateQueries({ queryKey: ['overview-summary', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['overview-issues', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['risks-summary', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['risks-timeline', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['risks-bottlenecks', tenantId] });
            queryClient.invalidateQueries({ queryKey: ['sources', tenantId] });
        }
      } catch (err) {
        console.error('Failed to parse SSE message', err);
      }
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [user, queryClient]);

  return (
    <RealtimeContext.Provider value={{ isConnected, lastEventAt, recentEvents }}>
      {children}
    </RealtimeContext.Provider>
  );
}
