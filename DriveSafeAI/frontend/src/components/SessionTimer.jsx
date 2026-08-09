import React from 'react';
import { useMonitoring } from '../context/MonitoringContext';
import { Play, Square, Clock } from 'lucide-react';

export const SessionTimer = () => {
  const {
    isMonitoring,
    sessionDuration,
    startMonitoringSession,
    stopMonitoringSession,
  } = useMonitoring();

  const handleStartSession = async () => {
    // startMonitoringSession will start the webcam before beginning the session
    await startMonitoringSession();
  };

  const fmt = (t) => {
    const h = Math.floor(t / 3600).toString().padStart(2, '0');
    const m = Math.floor((t % 3600) / 60).toString().padStart(2, '0');
    const s = (t % 60).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
  };

  return (
    <div className="card rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      {/* Timer */}
      <div className="flex items-center gap-3">
        <div className="w-11 h-11 rounded-xl flex items-center justify-center"
             style={{ background: '#ede9fe' }}>
          <Clock className="w-5 h-5" style={{ color: '#5b21b6' }} />
        </div>
        <div>
          <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: '#9ba8c4' }}>
            Session Timer
          </div>
          <div className="text-2xl font-black font-mono tracking-wider" style={{ color: '#1a2747' }}>
            {fmt(sessionDuration)}
          </div>
        </div>
      </div>

      {/* Control */}
      <div className="w-full sm:w-auto flex gap-3">
        {!isMonitoring ? (
          <button
            onClick={handleStartSession}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all active:scale-95"
            style={{ background: 'linear-gradient(135deg,#047857,#10b981)', color: '#fff',
                     boxShadow: '0 4px 14px rgba(16,185,129,0.3)' }}
          >
            <Play className="w-4 h-4 fill-white" /> Start Driving Session
          </button>
        ) : (
          <button
            onClick={stopMonitoringSession}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all active:scale-95 animate-pulse-soft"
            style={{ background: 'linear-gradient(135deg,#dc2626,#ef4444)', color: '#fff',
                     boxShadow: '0 4px 14px rgba(239,68,68,0.3)' }}
          >
            <Square className="w-4 h-4 fill-white" /> End Session & Report
          </button>
        )}
      </div>
    </div>
  );
};
