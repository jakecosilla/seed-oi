import React from 'react';

export const PageContainer: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <main className="flex flex-col flex-1 h-full w-full overflow-hidden">
    {children}
  </main>
);
