import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertOctagon, AlertTriangle, Info } from 'lucide-react';

const STYLES = {
  danger:  { bg: '#fee2e2', border: '#fca5a5', text: '#991b1b', icon: AlertOctagon  },
  warning: { bg: '#fef3c7', border: '#fcd34d', text: '#92400e', icon: AlertTriangle },
  info:    { bg: '#dbeafe', border: '#93c5fd', text: '#1e40af', icon: Info          },
};

export const AlertBanner = ({ alert }) => {
  if (!alert) return null;
  const s = STYLES[alert.severity] || STYLES.warning;
  const Icon = s.icon;

  return (
    <AnimatePresence>
      <motion.div
        key={alert.timestamp}
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        transition={{ duration: 0.25 }}
        className="w-full rounded-2xl p-4 flex items-center justify-between mb-2"
        style={{ background: s.bg, border: `1.5px solid ${s.border}` }}
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center"
               style={{ background: '#fff', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Icon className="w-5 h-5 animate-pulse" style={{ color: s.text }} />
          </div>
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wide" style={{ color: s.text }}>
              Driver Warning
            </div>
            <div className="text-sm font-semibold" style={{ color: s.text }}>{alert.message}</div>
          </div>
        </div>
        <div className="text-xs font-mono px-3 py-1 rounded-lg"
             style={{ background: 'rgba(0,0,0,0.06)', color: s.text }}>
          {new Date(alert.timestamp).toLocaleTimeString()}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
