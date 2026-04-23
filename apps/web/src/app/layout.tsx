import type { Metadata } from 'next';
import './globals.css';
import { TopNav } from '@/components/layout/TopNav';
import { PageContainer } from '@/components/layout/PageContainer';
import { QueryProvider } from '@/providers/QueryProvider';

export const metadata: Metadata = {
  title: 'Seed OI - Operations Intelligence',
  description: 'Visual operations intelligence platform for manufacturers.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex flex-col h-full">
        <QueryProvider>
          <TopNav />
          <PageContainer>
            {children}
          </PageContainer>
        </QueryProvider>
      </body>
    </html>
  );
}
