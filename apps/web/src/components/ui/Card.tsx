import React from 'react';

export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; className?: string }> = ({ children, style, className }) => (
  <div 
    style={style}
    className={`bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden ${className || ''}`}
  >
    {children}
  </div>
);

export const CardHeader: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="px-5 py-4 border-b border-slate-100 font-semibold text-slate-900">
    {children}
  </div>
);

export const CardContent: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="px-5 py-5">
    {children}
  </div>
);
