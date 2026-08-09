import React from 'react';

export const SafetyScoreGauge = ({ score = 100, title = 'Safety Score', subtitle = 'Overall' }) => {
  const s = Math.max(0, Math.min(100, score));
  const radius = 42;
  const circ   = 2 * Math.PI * radius;
  const offset = circ - (s / 100) * circ;

  const color  = s >= 80 ? '#10b981' : s >= 60 ? '#f59e0b' : '#ef4444';
  const trackC = s >= 80 ? '#d1fae5' : s >= 60 ? '#fef3c7' : '#fee2e2';
  const label  = s >= 80 ? 'Optimal' : s >= 60 ? 'Moderate' : 'Critical';
  const labelBg= s >= 80 ? '#d1fae5' : s >= 60 ? '#fef3c7' : '#fee2e2';
  const labelC = s >= 80 ? '#065f46' : s >= 60 ? '#92400e' : '#991b1b';

  return (
    <div className="card p-5 rounded-2xl flex items-center justify-between gap-4">
      <div className="space-y-1.5">
        <div className="text-[11px] font-bold uppercase tracking-wider" style={{ color: '#9ba8c4' }}>{title}</div>
        <div className="text-3xl font-black" style={{ color: '#1a2747' }}>
          {s.toFixed(0)}<span className="text-sm font-normal ml-1" style={{ color: '#9ba8c4' }}>/100</span>
        </div>
        <span
          className="text-[10px] font-bold px-2.5 py-1 rounded-full inline-block"
          style={{ background: labelBg, color: labelC }}
        >{label}</span>
      </div>

      <div className="relative w-20 h-20 shrink-0">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r={radius} fill="transparent"
                  stroke={trackC} strokeWidth="9" />
          <circle cx="50" cy="50" r={radius} fill="transparent"
                  stroke={color} strokeWidth="9"
                  strokeDasharray={circ}
                  strokeDashoffset={offset}
                  strokeLinecap="round"
                  style={{ transition: 'stroke-dashoffset 0.5s ease' }} />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-xs font-bold"
              style={{ color: '#1a2747' }}>
          {s.toFixed(0)}%
        </span>
      </div>
    </div>
  );
};
