import type { Metadata } from 'next';
import './globals.css';
import { TopNav } from '@/components/layout/TopNav';
import { PageContainer } from '@/components/layout/PageContainer';
import { QueryProvider } from '@/providers/QueryProvider';
import { RealtimeProvider } from '@/providers/RealtimeProvider';

export const metadata: Metadata = {
  title: 'Seed OI - Operations Intelligence',
  description: 'Visual operations intelligence platform for manufacturers.',
};

import { AuthProvider } from '@/providers/AuthProvider';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex flex-col h-full">
        <QueryProvider>
          <AuthProvider>
            <RealtimeProvider>
              <TopNav />
              <PageContainer>
                {children}
              </PageContainer>
            </RealtimeProvider>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
