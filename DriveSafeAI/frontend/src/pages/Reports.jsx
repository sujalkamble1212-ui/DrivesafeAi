import React, { useEffect, useState } from 'react';
import { sessionService }    from '../services/sessionService';
import { reportService }     from '../services/reportService';
import { ConfirmDeleteModal } from '../components/ConfirmDeleteModal';
import {
  ShieldCheck, AlertTriangle, Clock, TrendingUp, Download,
  Trash2, Loader2, CheckCircle2, FileText, BarChart2, Activity
} from 'lucide-react';

/* ── helpers ── */
const grade = sc => sc >= 80 ? 'safe' : sc >= 60 ? 'fair' : 'risk';
const GRADE = {
  safe: { label: 'Safe',    bg: '#d1fae5', color: '#065f46', dot: '#10b981', bar: '#10b981' },
  fair: { label: 'Fair',    bg: '#fef3c7', color: '#92400e', dot: '#f59e0b', bar: '#f59e0b' },
  risk: { label: 'At Risk', bg: '#fee2e2', color: '#9f1239', dot: '#ef4444', bar: '#ef4444' },
};
const TILES = [
  { key: 'all',  label: 'All Sessions',  icon: FileText,      grad: 'linear-gradient(135deg,#1d4ed8,#3b82f6)' },
  { key: 'safe', label: 'Safe Drives',   icon: ShieldCheck,   grad: 'linear-gradient(135deg,#047857,#10b981)' },
  { key: 'fair', label: 'Fair Drives',   icon: AlertTriangle, grad: 'linear-gradient(135deg,#b45309,#f59e0b)' },
  { key: 'risk', label: 'At Risk',       icon: Activity,      grad: 'linear-gradient(135deg,#be123c,#f43f5e)' },
];

/* ── Category tile ── */
const Tile = ({ icon: Icon, label, count, gradient, active, onClick }) => (
  <button onClick={onClick}
    className="rounded-2xl p-4 flex flex-col gap-2 text-left transition-all"
    style={{ background: gradient, opacity: active ? 1 : 0.72,
             transform: active ? 'scale(1.02)' : 'scale(1)',
             boxShadow: active ? '0 8px 24px rgba(0,0,0,0.15)' : 'none' }}>
    <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.2)' }}>
      <Icon className="w-5 h-5 text-white" />
    </div>
    <div className="text-2xl font-black text-white leading-none">{count}</div>
    <div className="text-[11px] font-medium" style={{ color: 'rgba(255,255,255,0.75)' }}>{label}</div>
  </button>
);

/* ── Session row (reference "recent files" style) ── */
const Row = ({ session, onDownload, onDelete, downloading }) => {
  const sc = session.safety_score ?? 0;
  const g  = GRADE[grade(sc)];
  const dt = session.start_time
    ? new Date(session.start_time).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
    : '—';

  return (
    <div className="flex items-center gap-3 px-5 py-3 hover:bg-slate-50 transition-colors group"
         style={{ borderBottom: '1px solid #e2e8f4' }}>
      {/* Icon pill */}
      <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
           style={{ background: g.bg }}>
        <FileText className="w-4 h-4" style={{ color: g.color }} />
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold" style={{ color: '#1a2747' }}>Session #{session.id}</span>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full"
                style={{ background: g.bg, color: g.color }}>{g.label}</span>
        </div>
        <div className="text-[11px]" style={{ color: '#9ba8c4' }}>{dt}</div>
      </div>

      {/* Score bar */}
      <div className="hidden sm:flex items-center gap-2 shrink-0 w-24">
        <div className="flex-1 h-1.5 rounded-full" style={{ background: '#e2e8f4' }}>
          <div className="h-full rounded-full transition-all" style={{ width: `${sc}%`, background: g.bar }} />
        </div>
        <span className="text-[11px] font-mono font-bold w-6 text-right" style={{ color: g.color }}>{Math.round(sc)}</span>
      </div>

      {/* Duration */}
      <span className="hidden md:block text-[11px] font-mono shrink-0 w-14 text-right" style={{ color: '#9ba8c4' }}>
        {session.duration_formatted || '—'}
      </span>

      {/* Alerts */}
      <span className="text-[11px] font-bold px-2 py-0.5 rounded-full shrink-0"
            style={{ background: '#fef3c7', color: '#92400e' }}>
        {session.total_alerts ?? 0} alerts
      </span>

      {/* Actions (hover-reveal) */}
      <div className="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
        <button onClick={() => onDownload(session.id)} disabled={downloading === session.id}
                className="p-1.5 rounded-lg transition-colors disabled:opacity-50"
                style={{ background: '#dbeafe', color: '#1d4ed8' }}>
          {downloading === session.id
            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
            : <Download className="w-3.5 h-3.5" />}
        </button>
        <button onClick={() => onDelete(session.id)}
                className="p-1.5 rounded-lg transition-colors"
                style={{ background: '#fee2e2', color: '#9f1239' }}>
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};

/* ── Right panel stat ── */
const RightStat = ({ icon: Icon, label, value, bg, color }) => (
  <div className="flex items-center gap-3">
    <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0" style={{ background: bg }}>
      <Icon className="w-4 h-4" style={{ color }} />
    </div>
    <div>
      <div className="text-[11px]" style={{ color: '#9ba8c4' }}>{label}</div>
      <div className="text-sm font-bold" style={{ color: '#1a2747' }}>{value}</div>
    </div>
  </div>
);

/* ── Main page ── */
export const Reports = () => {
  const [sessions,    setSessions]   = useState([]);
  const [loading,     setLoading]    = useState(true);
  const [filter,      setFilter]     = useState('all');
  const [deletingId,  setDeletingId] = useState(null);
  const [isDeleting,  setIsDeleting] = useState(false);
  const [downloading, setDownloading]= useState(null);
  const [toast,       setToast]      = useState(null);

  const fetchReports = () => {
    setLoading(true);
    sessionService.getSessions(1, 50)
      .then(d => setSessions(d.sessions || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };
  useEffect(() => { fetchReports(); }, []);

  const handleDownload = async (id) => {
    try { setDownloading(id); await reportService.downloadReport(id); }
    catch { alert('Download failed.'); }
    finally { setDownloading(null); }
  };

  const confirmDelete = async () => {
    if (!deletingId) return;
    try {
      setIsDeleting(true);
      await sessionService.deleteSession(deletingId);
      setSessions(prev => prev.filter(s => s.id !== deletingId));
      setToast(`Report #${deletingId} deleted.`);
      setTimeout(() => setToast(null), 4000);
    } catch { console.error('Delete failed'); }
    finally { setIsDeleting(false); setDeletingId(null); }
  };

  const counts = {
    all:  sessions.length,
    safe: sessions.filter(s => (s.safety_score ?? 0) >= 80).length,
    fair: sessions.filter(s => { const sc = s.safety_score ?? 0; return sc >= 60 && sc < 80; }).length,
    risk: sessions.filter(s => (s.safety_score ?? 0) < 60).length,
  };
  const avgSafety  = sessions.length ? Math.round(sessions.reduce((a, s) => a + (s.safety_score ?? 0), 0) / sessions.length) : 0;
  const totalAlerts= sessions.reduce((a, s) => a + (s.total_alerts ?? 0), 0);
  const totalMins  = Math.round(sessions.reduce((a, s) => a + (s.duration_seconds ?? 0), 0) / 60);

  const displayed = sessions
    .filter(s => {
      if (filter === 'all') return true;
      if (filter === 'safe') return (s.safety_score ?? 0) >= 80;
      if (filter === 'fair') { const sc = s.safety_score ?? 0; return sc >= 60 && sc < 80; }
      return (s.safety_score ?? 0) < 60;
    })
    .sort((a, b) => new Date(b.start_time || 0) - new Date(a.start_time || 0));

  return (
    <div className="space-y-5">
      {/* Toast */}
      {toast && (
        <div className="flex items-center gap-2 p-3 rounded-xl text-sm font-semibold"
             style={{ background: '#d1fae5', color: '#065f46', border: '1px solid #6ee7b7' }}>
          <CheckCircle2 className="w-4 h-4" /> {toast}
        </div>
      )}

      {/* Title */}
      <div className="flex items-center gap-2">
        <FileText className="w-5 h-5" style={{ color: '#2563eb' }} />
        <h2 className="text-xl font-black" style={{ color: '#1a2747' }}>PDF Reports</h2>
      </div>

      {/* ── Category tiles ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {TILES.map(t => (
          <Tile key={t.key} icon={t.icon} label={t.label} count={counts[t.key]}
                gradient={t.grad} active={filter === t.key} onClick={() => setFilter(t.key)} />
        ))}
      </div>

      {/* ── Content + right panel ── */}
      <div className="flex gap-5 items-start">

        {/* Session list — like reference "recent files" */}
        <div className="flex-1 min-w-0 card rounded-2xl overflow-hidden">
          {/* List header */}
          <div className="px-5 py-3.5 flex items-center justify-between"
               style={{ borderBottom: '1px solid #e2e8f4' }}>
            <h3 className="text-sm font-bold flex items-center gap-2" style={{ color: '#1a2747' }}>
              <BarChart2 className="w-4 h-4" style={{ color: '#2563eb' }} />
              Recent Sessions
            </h3>
            <span className="text-[11px]" style={{ color: '#9ba8c4' }}>
              {displayed.length} result{displayed.length !== 1 ? 's' : ''}
            </span>
          </div>

          {loading ? (
            <div className="p-12 text-center space-y-3">
              <Loader2 className="w-6 h-6 mx-auto animate-spin" style={{ color: '#2563eb' }} />
              <p className="text-sm" style={{ color: '#9ba8c4' }}>Loading sessions…</p>
            </div>
          ) : displayed.length === 0 ? (
            <div className="p-12 text-center space-y-3">
              <FileText className="w-10 h-10 mx-auto" style={{ color: '#c8d2e8' }} />
              <p className="text-sm" style={{ color: '#9ba8c4' }}>
                {sessions.length === 0
                  ? 'No sessions yet. Complete a monitoring session to generate a report.'
                  : 'No sessions match this filter.'}
              </p>
            </div>
          ) : (
            <div>
              {displayed.map(s => (
                <Row key={s.id} session={s}
                     onDownload={handleDownload} onDelete={setDeletingId}
                     downloading={downloading} />
              ))}
            </div>
          )}
        </div>

        {/* ── Right panel (reference right sidebar style) ── */}
        {sessions.length > 0 && (
          <div className="hidden lg:flex flex-col gap-4 w-60 shrink-0">

            {/* Overall score */}
            <div className="card rounded-2xl p-5 space-y-3">
              <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: '#9ba8c4' }}>
                Overall Safety
              </div>
              <div className="text-4xl font-black" style={{ color: GRADE[grade(avgSafety)].color }}>
                {avgSafety}<span className="text-sm font-normal ml-1" style={{ color: '#9ba8c4' }}>/100</span>
              </div>
              <div className="h-2 rounded-full" style={{ background: '#e2e8f4' }}>
                <div className="h-full rounded-full transition-all"
                     style={{ width: `${avgSafety}%`, background: GRADE[grade(avgSafety)].bar }} />
              </div>
              <p className="text-[11px]" style={{ color: '#9ba8c4' }}>
                Avg across {sessions.length} session{sessions.length !== 1 ? 's' : ''}
              </p>
            </div>

            {/* Quick stats */}
            <div className="card rounded-2xl p-5 space-y-4">
              <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: '#9ba8c4' }}>Your Stats</div>
              <RightStat icon={ShieldCheck}   label="Safe Sessions" value={`${counts.safe} / ${counts.all}`} bg="#d1fae5" color="#065f46" />
              <RightStat icon={AlertTriangle} label="Total Alerts"  value={totalAlerts}                       bg="#fef3c7" color="#92400e" />
              <RightStat icon={Clock}         label="Total Time"    value={`${totalMins} min`}                bg="#dbeafe" color="#1d4ed8" />
            </div>

            {/* Grade breakdown */}
            <div className="card rounded-2xl p-5 space-y-3">
              <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: '#9ba8c4' }}>Grade Breakdown</div>
              {(['safe','fair','risk']).map(k => {
                const pct = sessions.length ? Math.round((counts[k] / sessions.length) * 100) : 0;
                const g   = GRADE[k];
                return (
                  <div key={k}>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="flex items-center gap-1.5" style={{ color: '#6b7a99' }}>
                        <span className="w-2 h-2 rounded-full" style={{ background: g.dot }} />
                        {g.label}
                      </span>
                      <span className="font-semibold" style={{ color: '#1a2747' }}>{counts[k]} ({pct}%)</span>
                    </div>
                    <div className="h-1.5 rounded-full" style={{ background: '#e2e8f4' }}>
                      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: g.bar }} />
                    </div>
                  </div>
                );
              })}
            </div>

          </div>
        )}
      </div>

      <ConfirmDeleteModal
        isOpen={Boolean(deletingId)} onClose={() => setDeletingId(null)}
        onConfirm={confirmDelete} loading={isDeleting}
        title={`Delete Report #${deletingId}`}
        message="This will permanently delete this report and all associated data. This cannot be undone."
      />
    </div>
  );
};
