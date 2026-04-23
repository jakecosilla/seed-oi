import React from 'react';

interface SidePanelProps {
  children: React.ReactNode;
  side?: 'left' | 'right';
  width?: string;
}

export const SidePanel: React.FC<SidePanelProps> = ({ children, side = 'right', width = '320px' }) => {
  const borderClass = side === 'left' ? 'border-r' : 'border-l';
  return (
    <aside 
      style={{ width }}
      className={`h-full bg-white border-slate-200 flex flex-col shrink-0 min-h-0 ${borderClass}`}
    >
      {children}
    </aside>
  );
};
