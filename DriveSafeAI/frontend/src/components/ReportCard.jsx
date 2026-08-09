import React, { useState } from 'react';
import { reportService } from '../services/reportService';
import {
  FileText, Download, Calendar, Clock, AlertTriangle,
  ShieldCheck, Loader2, Trash2, Eye, Smartphone, Wind,
  TrendingUp, Timer, ChevronRight
} from 'lucide-react';

const ScoreRing = ({ score, size = 64, stroke = 6 }) => {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(Math.max(score || 0, 0), 100);
  const dash = (pct / 100) * circ;
  const color = pct >= 80 ? '#34d399' : pct >= 60 ? '#fbbf24' : '#f87171';

  return (
    <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#1e293b" strokeWidth={stroke} />
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none" stroke={color} strokeWidth={stroke}
        strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round"
        style={{ transition: 'stroke-dasharray 0.6s ease' }}
      />
      <text
        x="50%" y="50%"
        textAnchor="middle" dominantBaseline="middle"
        fill={color}
        fontSize={size * 0.22}
        fontWeight="bold"
        style={{ transform: 'rotate(90deg)', transformOrigin: '50% 50%' }}
      >
        {Math.round(pct)}
      </text>
    </svg>
  );
};

const StatPill = ({ icon: Icon, label, value, color }) => (
  <div className={`flex items-center gap-2 px-3 py-2 rounded-xl border ${color} bg-slate-900/60`}>
    <Icon className="w-3.5 h-3.5 shrink-0" />
    <div className="min-w-0">
      <div className="text-[10px] text-slate-500 leading-none">{label}</div>
      <div className="text-xs font-bold text-slate-200 mt-0.5">{value}</div>
    </div>
  </div>
);

export const ReportCard = ({ session, onDelete }) => {
  const [downloading, setDownloading] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const handleDownload = async () => {
    try {
      setDownloading(true);
      await reportService.downloadReport(session.id);
    } catch (err) {
      console.error('Failed to download report:', err);
      alert('Error downloading PDF report. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  const formattedDate = session.start_time
    ? new Date(session.start_time).toLocaleDateString(undefined, {
        weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
      })
    : 'N/A';

  const formattedTime = session.start_time
    ? new Date(session.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  const safety = session.safety_score ?? 0;
  const gradeLabel = safety >= 80 ? 'Safe' : safety >= 60 ? 'Fair' : 'At Risk';
  const gradeColor = safety >= 80
    ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10'
    : safety >= 60
    ? 'border-amber-500/30 text-amber-400 bg-amber-500/10'
    : 'border-rose-500/30 text-rose-400 bg-rose-500/10';

  return (
    <div
      className="glass-panel rounded-2xl border border-slate-800 overflow-hidden transition-all duration-300 hover:border-indigo-500/40 hover:shadow-2xl hover:shadow-indigo-500/5 group"
      style={{ background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(20,30,55,0.9) 100%)' }}
    >
      {/* Top accent bar */}
      <div
        className="h-1 w-full"
        style={{
          background: safety >= 80
            ? 'linear-gradient(90deg, #059669, #34d399)'
            : safety >= 60
            ? 'linear-gradient(90deg, #d97706, #fbbf24)'
            : 'linear-gradient(90deg, #dc2626, #f87171)'
        }}
      />

      <div className="p-5 space-y-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="relative shrink-0">
              <ScoreRing score={safety} size={58} stroke={5} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-black text-slate-100 text-base tracking-tight">
                  Session #{session.id}
                </h4>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${gradeColor}`}>
                  {gradeLabel}
                </span>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-slate-500 mt-1">
                <Calendar className="w-3 h-3" />
                <span>{formattedDate}</span>
                <span className="text-slate-700">·</span>
                <Clock className="w-3 h-3" />
                <span>{formattedTime}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-2">
          <StatPill
            icon={Timer}
            label="Duration"
            value={session.duration_formatted || '—'}
            color="border-indigo-500/20 text-indigo-400"
          />
          <StatPill
            icon={TrendingUp}
            label="Attention"
            value={`${session.attention_score?.toFixed(0) ?? '—'}%`}
            color="border-cyan-500/20 text-cyan-400"
          />
          <StatPill
            icon={Eye}
            label="Eye Closures"
            value={session.drowsy_events ?? session.total_alerts ?? 0}
            color="border-amber-500/20 text-amber-400"
          />
          <StatPill
            icon={AlertTriangle}
            label="Total Alerts"
            value={session.total_alerts ?? 0}
            color="border-rose-500/20 text-rose-400"
          />
        </div>

        {/* Dual score bar */}
        <div className="space-y-2 px-1">
          <div>
            <div className="flex justify-between text-[10px] text-slate-500 mb-1">
              <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> Safety Score</span>
              <span className="font-mono text-slate-300">{safety.toFixed(0)}/100</span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${safety}%`,
                  background: safety >= 80 ? 'linear-gradient(90deg,#059669,#34d399)' : safety >= 60 ? 'linear-gradient(90deg,#d97706,#fbbf24)' : 'linear-gradient(90deg,#dc2626,#f87171)'
                }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-[10px] text-slate-500 mb-1">
              <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> Attention Score</span>
              <span className="font-mono text-slate-300">{(session.attention_score ?? 0).toFixed(0)}/100</span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-indigo-600 to-cyan-400 transition-all duration-700"
                style={{ width: `${session.attention_score ?? 0}%` }}
              />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 pt-1">
          <button
            onClick={handleDownload}
            disabled={downloading}
            id={`download-report-${session.id}`}
            className="flex-1 py-2.5 rounded-xl font-semibold text-xs flex items-center justify-center gap-2 transition-all duration-200 disabled:opacity-50 border"
            style={{
              background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1))',
              borderColor: 'rgba(99,102,241,0.4)',
              color: '#a5b4fc',
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.2))'}
            onMouseLeave={e => e.currentTarget.style.background = 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1))'}
          >
            {downloading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Generating PDF…</>
            ) : (
              <><Download className="w-4 h-4" /> Download PDF Report</>
            )}
          </button>
          {onDelete && (
            <button
              onClick={() => onDelete(session.id)}
              id={`delete-report-${session.id}`}
              className="p-2.5 rounded-xl border border-rose-500/20 bg-rose-500/8 hover:bg-rose-500/20 text-rose-400 transition-colors"
              title="Delete Report"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
