# Seed OI Real-Time Data Strategy

To provide a seamless, live operations command center, Seed OI utilizes Server-Sent Events (SSE) for one-way, low-latency updates from the server to the web client.

## Core Events
The application layer publishes the following core events through `EventPublisher`:
- `source_sync_started`
- `source_sync_completed`
- `source_sync_failed`
- `freshness_changed`
- `issue_created`
- `issue_updated`
- `recommendation_updated`

## Implementation Details
- **Protocol:** SSE over HTTP/1.1 or HTTP/2. SSE is chosen over WebSockets because Seed OI requires one-way broadcast updates (server to client) for UI reactivity. It is simpler to load balance and proxy than WebSockets, and natively supported by browsers.
- **Application Boundary:** Worker services or API endpoints push data into `EventPublisher`. *Note: In production, this publisher will be backed by Redis Pub/Sub so that multiple horizontal API/Worker instances can distribute events properly.*

## Client Reconnect & Fallback Guidance
1. **EventSource API:** The frontend should use the native browser `EventSource` API, which automatically attempts reconnections if the stream drops.
2. **Exponential Backoff:** If using a custom fetch-based SSE parser, implement exponential backoff on disconnects (e.g., retry after 1s, 2s, 4s, 8s).
3. **Fallback Polling:** If SSE fails entirely (e.g., corporate firewalls blocking streaming HTTP), the frontend should fall back to standard HTTP polling (e.g., every 15-30 seconds using SWR or React Query).

## Real-Time vs Scheduled Refresh
Not all UI components need live SSE updates:

**Where Real-Time is Required:**
- **Source Health Dashboard:** Sync status indicators (`started`, `failed`) need instant feedback to avoid confusing users actively managing integrations.
- **Critical Issues / Alerts:** Net-new supply chain disruptions (`issue_created`) must pop up immediately to minimize response latency.
- **Long-Running Job Status:** Risk recomputations.

**Where Scheduled/Manual Refresh is Enough:**
- **Master Data Grids:** Viewing lists of products, vendors, or historic sales orders. Standard caching and periodic polling (e.g., 5 minutes) or manual refresh is acceptable.
- **Reporting Analytics:** Aggregated metrics (e.g., weekly performance) do not require millisecond-level SSE.
