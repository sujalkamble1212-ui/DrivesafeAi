import React, { useEffect, useState } from 'react';
import { sessionService } from '../services/sessionService';
import { reportService } from '../services/reportService';
import { ConfirmDeleteModal } from '../components/ConfirmDeleteModal';
import { History as HistoryIcon, Calendar, Clock, Download, Trash2, ShieldCheck, Eye, Smartphone, AlertTriangle, Loader2, CheckCircle2 } from 'lucide-react';

export const History = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [deletingId, setDeletingId] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const fetchSessions = async (p = 1) => {
    try {
      setLoading(true);
      const data = await sessionService.getSessions(p, 10);
      setSessions(data.sessions || []);
      setTotalPages(data.pages || 1);
      setPage(data.page || 1);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions(page);
  }, [page]);

  const confirmDeleteSession = async () => {
    if (!deletingId) return;
    try {
      setIsDeleting(true);
      await sessionService.deleteSession(deletingId);
      setToastMessage(`Session #${deletingId} deleted successfully!`);
      setTimeout(() => setToastMessage(null), 4000);
      fetchSessions(page);
    } catch (err) {
      console.error(err);
    } finally {
      setIsDeleting(false);
      setDeletingId(null);
    }
  };

  const handleDownload = async (id) => {
    try {
      await reportService.downloadReport(id);
    } catch (err) {
      alert('Failed to download PDF report.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Toast Banner */}
      {toastMessage && (
        <div className="flex items-center gap-2 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm font-semibold shadow-lg animate-fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            <HistoryIcon className="w-6 h-6 text-indigo-400" /> Driving Session History
          </h2>
          <p className="text-xs text-slate-400">Review past driving analytics, safety scores, and download PDF reports</p>
        </div>
      </div>

      {loading ? (
        <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-indigo-400 animate-spin mx-auto" />
          <p className="text-sm text-slate-400 font-medium">Loading session history...</p>
        </div>
      ) : sessions.length === 0 ? (
        <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center space-y-3">
          <HistoryIcon className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-lg font-bold text-slate-300">No Driving Sessions Found</h3>
          <p className="text-sm text-slate-400 max-w-sm mx-auto">
            Start a new session from the Dashboard to record safety scores and alert events.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition-all shadow-xl"
              >
                <div className="flex items-start md:items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-slate-100 text-base">Session #{session.id}</h4>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                          session.safety_score >= 80
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : session.safety_score >= 60
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                            : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                        }`}
                      >
                        Safety Score: {session.safety_score?.toFixed(0)}/100
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        {new Date(session.start_time).toLocaleDateString()}
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        {session.duration_formatted || '00:00:00'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Event Counters */}
                <div className="flex items-center gap-6 bg-slate-900/60 px-4 py-2 rounded-xl border border-slate-800 text-xs">
                  <div className="text-center">
                    <span className="text-slate-500 block text-[10px] uppercase font-bold">Eyes Closed</span>
                    <span className="font-bold text-rose-400">{session.eye_closure_count}</span>
                  </div>
                  <div className="text-center">
                    <span className="text-slate-500 block text-[10px] uppercase font-bold">Yawns</span>
                    <span className="font-bold text-amber-400">{session.yawn_count}</span>
                  </div>
                  <div className="text-center">
                    <span className="text-slate-500 block text-[10px] uppercase font-bold">Phones</span>
                    <span className="font-bold text-indigo-400">{session.phone_usage_count}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 justify-end">
                  <button
                    onClick={() => handleDownload(session.id)}
                    className="px-3 py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 font-semibold text-xs border border-indigo-500/30 flex items-center gap-1.5 transition-colors"
                  >
                    <Download className="w-3.5 h-3.5" /> Report PDF
                  </button>
                  <button
                    onClick={() => setDeletingId(session.id)}
                    className="p-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-colors"
                    title="Delete Session"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2 pt-4">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-xs text-slate-400 font-mono">
                Page {page} of {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmDeleteModal
        isOpen={Boolean(deletingId)}
        onClose={() => setDeletingId(null)}
        onConfirm={confirmDeleteSession}
        loading={isDeleting}
        title={`Delete Driving Session #${deletingId}`}
        message="Are you sure you want to delete this session and all associated driving telemetry metrics? This action cannot be undone."
      />
    </div>
  );
};
