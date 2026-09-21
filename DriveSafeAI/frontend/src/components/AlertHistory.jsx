import React from 'react';
import { AlertCircle, Eye, Smartphone, Smile, Image as ImageIcon } from 'lucide-react';

const ICON_MAP = {
  drowsiness:    <Eye       className="w-4 h-4" style={{ color: '#9f1239' }} />,
  phone_detected:<Smartphone className="w-4 h-4" style={{ color: '#9f1239' }} />,
  yawn_detected: <Smile     className="w-4 h-4" style={{ color: '#92400e' }} />,
};
const SEVERITY_STYLE = {
  danger:  { bg: '#fee2e2', color: '#9f1239' },
  warning: { bg: '#fef3c7', color: '#92400e' },
  info:    { bg: '#dbeafe', color: '#1e40af' },
};

export const AlertHistory = ({ alerts = [] }) => {
  if (!alerts?.length) {
    return (
      <div className="card rounded-2xl p-8 text-center space-y-2">
        <AlertCircle className="w-8 h-8 mx-auto" style={{ color: '#c8d2e8' }} />
        <p className="text-sm font-medium" style={{ color: '#9ba8c4' }}>No alerts recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="card rounded-2xl overflow-hidden">
      {/* Header — like reference "recent files" header */}
      <div className="px-5 py-3.5 flex items-center justify-between"
           style={{ borderBottom: '1px solid #e2e8f4' }}>
        <h3 className="text-sm font-bold" style={{ color: '#1a2747' }}>Alert Event Log</h3>
        <span className="text-xs font-bold px-2.5 py-1 rounded-full"
              style={{ background: '#f1f5ff', color: '#1a2747' }}>
          {alerts.length} Events
        </span>
      </div>

      {/* Rows — like reference "recent files" list */}
      <div className="divide-y overflow-y-auto max-h-[280px]" style={{ divideColor: '#e2e8f4' }}>
        {alerts.map((alert, idx) => {
          const sev = SEVERITY_STYLE[alert.severity] || SEVERITY_STYLE.warning;
          return (
            <div key={alert.id || idx}
                 className="flex items-center gap-3 px-5 py-3 hover:bg-slate-50 transition-colors">
              {/* Icon pill */}
              <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                   style={{ background: sev.bg }}>
                {ICON_MAP[alert.alert_type] || <AlertCircle className="w-4 h-4" style={{ color: sev.color }} />}
              </div>
              {/* Name + type */}
              <div className="flex-1 min-w-0">
                <div className="text-xs font-bold truncate" style={{ color: '#1a2747' }}>
                  {alert.alert_type ? alert.alert_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : 'Alert'}
                </div>
                <div className="text-[11px] truncate" style={{ color: '#9ba8c4' }}>{alert.message}</div>
              </div>
              {/* Severity badge */}
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0"
                    style={{ background: sev.bg, color: sev.color }}>
                {alert.severity || 'warning'}
              </span>
              {/* Time */}
              <span className="text-[11px] font-mono shrink-0" style={{ color: '#9ba8c4' }}>
                {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : 'N/A'}
              </span>
              {/* Screenshot */}
              {alert.screenshot_path ? (
                <a href={
                     alert.screenshot_path.startsWith('http')
                       ? alert.screenshot_path
                       : alert.screenshot_path.startsWith('screenshots/')
                         ? `/${alert.screenshot_path.replace(/\\/g, '/')}`
                         : `/api/screenshots/${alert.screenshot_path}`
                   }
                   target="_blank" rel="noreferrer"
                   className="flex items-center gap-1 text-xs font-semibold shrink-0"
                   style={{ color: '#2563eb' }}>
                  <ImageIcon className="w-3.5 h-3.5" /> View
                </a>
              ) : (
                <span className="w-10 shrink-0" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
