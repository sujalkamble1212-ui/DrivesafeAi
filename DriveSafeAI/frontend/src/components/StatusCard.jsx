import React from 'react';

const COLOR = {
  indigo:  { bg: '#ede9fe', text: '#5b21b6', border: '#c4b5fd', badge: '#ede9fe', badgeText: '#5b21b6' },
  emerald: { bg: '#d1fae5', text: '#065f46', border: '#6ee7b7', badge: '#d1fae5', badgeText: '#065f46' },
  rose:    { bg: '#ffe4e6', text: '#9f1239', border: '#fda4af', badge: '#ffe4e6', badgeText: '#9f1239' },
  amber:   { bg: '#fef3c7', text: '#92400e', border: '#fcd34d', badge: '#fef3c7', badgeText: '#92400e' },
};

export const StatusCard = ({ title, value, status, icon: Icon, color = 'indigo', subtext }) => {
  const t = COLOR[color] || COLOR.indigo;

  return (
    <div
      className="card card-hover p-4 flex flex-col gap-3 rounded-2xl"
      style={{ borderColor: t.border }}
    >
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-bold uppercase tracking-wider" style={{ color: '#9ba8c4' }}>
          {title}
        </span>
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: t.bg, color: t.text }}
        >
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div>
        <div className="text-lg font-black" style={{ color: '#1a2747' }}>{value}</div>
        {subtext && <div className="text-[11px] mt-0.5" style={{ color: '#9ba8c4' }}>{subtext}</div>}
      </div>

      {status && (
        <span
          className="text-[10px] font-bold px-2 py-0.5 rounded-full self-start"
          style={{ background: t.badge, color: t.badgeText }}
        >
          {status}
        </span>
      )}
    </div>
  );
};
