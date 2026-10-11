import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = (status || '').toUpperCase();

  let bg = 'bg-slate-800 text-slate-300 border-slate-700';
  let Icon = HelpCircle;

  if (norm === 'PASS') {
    bg = 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40 shadow-sm shadow-emerald-950';
    Icon = CheckCircle2;
  } else if (norm === 'FAIL') {
    bg = 'bg-rose-950/80 text-rose-400 border-rose-500/40 shadow-sm shadow-rose-950';
    Icon = XCircle;
  } else if (norm === 'REVIEW') {
    bg = 'bg-amber-950/80 text-amber-300 border-amber-500/40 shadow-sm shadow-amber-950';
    Icon = AlertTriangle;
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 space-x-1',
    md: 'text-xs px-2.5 py-1 space-x-1.5',
    lg: 'text-sm px-3.5 py-1.5 space-x-2 font-semibold',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  };

  return (
    <span
      className={`inline-flex items-center font-mono font-medium rounded-full border tracking-wide uppercase ${bg} ${sizeClasses[size]}`}
    >
      <Icon className={iconSizes[size]} />
      <span>{norm}</span>
    </span>
  );
};

export const ModeBadge: React.FC<{ mode: string }> = ({ mode }) => {
  const colors: Record<string, string> = {
    dimensional: 'bg-blue-950 text-blue-300 border-blue-800',
    defect: 'bg-purple-950 text-purple-300 border-purple-800',
    reference: 'bg-amber-950 text-amber-300 border-amber-800',
    combined: 'bg-cyan-950 text-cyan-300 border-cyan-700',
  };

  const labels: Record<string, string> = {
    dimensional: 'Dimensional Metrology',
    defect: 'Defect Analysis',
    reference: 'Golden Reference',
    combined: 'Combined System',
  };

  const m = (mode || 'combined').toLowerCase();

  return (
    <span className={`inline-flex items-center text-[11px] px-2 py-0.5 rounded border font-mono ${colors[m] || 'bg-slate-800 text-slate-300 border-slate-700'}`}>
      {labels[m] || m}
    </span>
  );
};
