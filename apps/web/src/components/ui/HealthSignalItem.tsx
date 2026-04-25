import React from 'react';
import { Heart, TrendingUp, Zap, Lightbulb, LucideIcon } from 'lucide-react';

export type HealthCategory = 'Healthy' | 'Improved' | 'Capacity' | 'Opportunity';

export interface HealthSignalProps {
  category: HealthCategory;
  title: string;
  description: string;
  metricValue?: string;
  metricTrend?: 'up' | 'down' | 'stable';
  impactArea: string;
  className?: string;
}

const categoryConfig: Record<HealthCategory, { icon: LucideIcon; colorClass: string; bgColorClass: string }> = {
  Healthy: { icon: Heart, colorClass: 'text-emerald-600', bgColorClass: 'bg-emerald-50' },
  Improved: { icon: TrendingUp, colorClass: 'text-blue-600', bgColorClass: 'bg-blue-50' },
  Capacity: { icon: Zap, colorClass: 'text-amber-600', bgColorClass: 'bg-amber-50' },
  Opportunity: { icon: Lightbulb, colorClass: 'text-purple-600', bgColorClass: 'bg-purple-50' },
};

export const HealthSignalItem: React.FC<HealthSignalProps> = ({
  category,
  title,
  description,
  metricValue,
  metricTrend,
  impactArea,
  className = '',
}) => {
  const { icon: Icon, colorClass, bgColorClass } = categoryConfig[category];

  return (
    <div className={`p-4 hover:bg-slate-50 transition-colors flex items-start gap-4 ${className}`}>
      <div className={`p-2 rounded-lg shrink-0 ${bgColorClass} ${colorClass}`}>
        <Icon size={18} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-0.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            {category} • {impactArea}
          </span>
          {metricValue && (
            <span className={`text-xs font-bold ${
              metricTrend === 'up' ? 'text-emerald-600' :
              metricTrend === 'down' ? 'text-blue-600' :
              'text-slate-600'
            }`}>
              {metricValue}
              {metricTrend === 'up' && ' ↑'}
              {metricTrend === 'down' && ' ↓'}
            </span>
          )}
        </div>
        <h4 className="font-bold text-slate-900">{title}</h4>
        <p className="text-xs text-slate-500 mt-1">{description}</p>
      </div>
    </div>
  );
};
