import React, { useEffect, useState } from 'react';
import { useMonitoring } from '../context/MonitoringContext';
import { WebcamFeed }       from '../components/WebcamFeed';
import { StatusCard }       from '../components/StatusCard';
import { SafetyScoreGauge } from '../components/SafetyScoreGauge';
import { AttentionChart }   from '../components/AttentionChart';
import { SessionTimer }     from '../components/SessionTimer';
import { AlertBanner }      from '../components/AlertBanner';
import { AlertHistory }     from '../components/AlertHistory';
import { sessionService }   from '../services/sessionService';
import { Eye, Smile, Smartphone, AlertTriangle, ShieldCheck, Activity, LayoutDashboard } from 'lucide-react';

/* ── Category summary tile (reference top-row style) ── */
const StatTile = ({ icon: Icon, label, count, gradient }) => (
  <div className="rounded-2xl p-4 flex flex-col gap-2 text-white" style={{ background: gradient }}>
    <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.2)' }}>
      <Icon className="w-5 h-5 text-white" />
    </div>
    <div className="text-2xl font-black leading-none">{count}</div>
    <div className="text-[11px] font-medium" style={{ color: 'rgba(255,255,255,0.75)' }}>{label}</div>
  </div>
);

export const Dashboard = () => {
  const {
    eyeStatus, headPose, phoneStatus, yawnStatus,
    safetyScore, attentionScore, currentAlert, chartData,
    activeSessionId, isMonitoring,
  } = useMonitoring();

  const [sessionAlerts, setSessionAlerts] = useState([]);

  useEffect(() => {
    if (activeSessionId) {
      sessionService.getAlerts(1, 20, activeSessionId)
        .then(d => setSessionAlerts(d.alerts || []))
        .catch(console.error);
    } else {
      setSessionAlerts([]);
    }
  }, [activeSessionId, currentAlert]);

  /* quick stats from session alerts */
  const eyeEvents   = sessionAlerts.filter(a => a.alert_type === 'drowsiness' || a.alert_type === 'eye_closed').length;
  const phoneEvents = sessionAlerts.filter(a => a.alert_type === 'phone_detected').length;
  const yawnEvents  = sessionAlerts.filter(a => a.alert_type === 'yawn_detected').length;

  return (
    <div className="space-y-5">
      {/* Page title */}
      <div className="flex items-center gap-2">
        <LayoutDashboard className="w-5 h-5" style={{ color: '#2563eb' }} />
        <h2 className="text-xl font-black" style={{ color: '#1a2747' }}>Dashboard</h2>
      </div>

      {/* Alert banner */}
      <AlertBanner alert={currentAlert} />

      {/* Session timer */}
      <SessionTimer />

      {/* ── Category tiles (reference top-row) ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatTile icon={ShieldCheck}    label="Safety Score"    count={`${Math.round(safetyScore)}%`}  gradient="linear-gradient(135deg,#1d4ed8,#3b82f6)" />
        <StatTile icon={Activity}       label="Attention Score" count={`${Math.round(attentionScore)}%`} gradient="linear-gradient(135deg,#7c3aed,#a78bfa)" />
        <StatTile icon={Eye}            label="Eye Events"      count={eyeEvents}                       gradient="linear-gradient(135deg,#e11d48,#f87171)" />
        <StatTile icon={Smartphone}     label="Phone Events"    count={phoneEvents}                     gradient="linear-gradient(135deg,#0d9488,#34d399)" />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Webcam + Chart */}
        <div className="lg:col-span-7 space-y-5">
          <WebcamFeed />
          <AttentionChart chartData={chartData} />
        </div>

        {/* Right: Gauges + Telemetry */}
        <div className="lg:col-span-5 space-y-5">
          {/* Score gauges */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <SafetyScoreGauge score={safetyScore}    title="Safety Score"    subtitle="Real-time" />
            <SafetyScoreGauge score={attentionScore} title="Attention Score" subtitle="Focus Level" />
          </div>

          {/* Telemetry cards — 2 × 2 */}
          <div className="grid grid-cols-2 gap-4">
            <StatusCard
              title="Eye Status"
              value={eyeStatus.eye_status === 'Open_Eyes' ? 'Open' : eyeStatus.eye_status === 'Closed_Eyes' ? 'CLOSED' : 'No Face'}
              subtext={`Conf: ${(eyeStatus.confidence * 100).toFixed(0)}%`}
              status={eyeStatus.eye_status === 'Closed_Eyes' ? 'Drowsy Warning' : 'Normal'}
              icon={Eye}
              color={eyeStatus.eye_status === 'Closed_Eyes' ? 'rose' : 'emerald'}
            />
            <StatusCard
              title="Head Pose"
              value={headPose.direction ? headPose.direction.replace('_', ' ') : 'Forward'}
              subtext={`Yaw: ${headPose.yaw}° Pitch: ${headPose.pitch}°`}
              status={headPose.direction !== 'Looking_Forward' ? 'Looking Away' : 'Centered'}
              icon={Smile}
              color={headPose.direction !== 'Looking_Forward' ? 'amber' : 'indigo'}
            />
            <StatusCard
              title="Phone Detection"
              value={phoneStatus.phone_detected ? 'DETECTED' : 'Clear'}
              subtext={phoneStatus.phone_detected ? `Count: ${phoneStatus.phone_count}` : 'Hands Free'}
              status={phoneStatus.phone_detected ? 'Violation' : 'Clear'}
              icon={Smartphone}
              color={phoneStatus.phone_detected ? 'rose' : 'emerald'}
            />
            <StatusCard
              title="Yawn Detection"
              value={yawnStatus.is_yawning ? 'YAWNING' : 'Normal'}
              subtext={`Total: ${yawnStatus.total_yawns}`}
              status={yawnStatus.is_yawning ? 'Fatigue Alert' : 'Alert'}
              icon={AlertTriangle}
              color={yawnStatus.is_yawning ? 'amber' : 'indigo'}
            />
          </div>

          {/* Alert log */}
          {!isMonitoring && <AlertHistory alerts={sessionAlerts} />}
        </div>
      </div>
    </div>
  );
};
