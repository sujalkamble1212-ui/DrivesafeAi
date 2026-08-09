import React, { useEffect, useRef } from 'react';
import { useMonitoring } from '../context/MonitoringContext';
import { monitoringService } from '../services/monitoringService';
import { Camera, CameraOff, AlertTriangle, Eye, Smartphone, Smile } from 'lucide-react';

export const WebcamFeed = () => {
  const {
    videoRef,
    isWebcamActive,
    cameraError,
    startWebcam,
    stopWebcam,
    captureFrameBase64,
    isMonitoring,
    activeSessionId,
    updateFrameResults,
    eyeStatus,
    headPose,
    phoneStatus,
    faceBbox,
  } = useMonitoring();
  const processingRef = useRef(false);

  // Do NOT auto-start webcam on mount.
  // Camera turns on only when the user explicitly starts a session (via MonitoringContext).
  // We still stop the stream on component unmount to release hardware.
  useEffect(() => {
    return () => stopWebcam();
  }, [stopWebcam]);

  // ── Preview loop: face detection BEFORE a session starts ──────────────
  // Runs at 300ms to show live face box + eye/head status without any alerts.
  useEffect(() => {
    let interval = null;

    if (isWebcamActive && !isMonitoring) {
      interval = setInterval(async () => {
        if (processingRef.current) return;
        const frameBase64 = captureFrameBase64();
        if (!frameBase64) return;

        processingRef.current = true;
        try {
          const results = await monitoringService.previewFrame(frameBase64);
          updateFrameResults(results);
        } catch {
          // Silent — preview is best-effort
        } finally {
          processingRef.current = false;
        }
      }, 300);
    }

    return () => { if (interval) clearInterval(interval); };
  }, [isMonitoring, isWebcamActive, captureFrameBase64, updateFrameResults]);

  // ── Session loop: full detection + alerts during an active session ──────
  useEffect(() => {
    let interval = null;

    if (isWebcamActive && isMonitoring && activeSessionId) {
      interval = setInterval(async () => {
        if (processingRef.current) return;

        const frameBase64 = captureFrameBase64();
        if (!frameBase64) return;

        processingRef.current = true;
        try {
          const results = await monitoringService.processFrame(frameBase64, activeSessionId);
          updateFrameResults(results);
        } catch (err) {
          console.error('Frame processing error:', err);
        } finally {
          processingRef.current = false;
        }
      }, 150); // ~7 FPS
    }

    return () => { if (interval) clearInterval(interval); };
  }, [isMonitoring, isWebcamActive, activeSessionId, captureFrameBase64, updateFrameResults]);

  return (
    <div className="relative card rounded-2xl overflow-hidden flex flex-col justify-center items-center aspect-video max-h-[420px] w-full" style={{ background: '#0f172a' }}>
      {/* Video Feed */}
      <video
        ref={videoRef}
        playsInline
        muted
        className={`w-full h-full object-cover transform -scale-x-100 ${!isWebcamActive ? 'hidden' : ''}`}
      />

      {/* Fallback Camera Off Overlay */}
      {!isWebcamActive && (
        <div className="flex flex-col items-center justify-center p-8 text-center space-y-4">
          <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.08)', color: '#8fa3c8' }}>
            <CameraOff className="w-8 h-8" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Camera Feed Offline</h3>
            <p className="text-sm max-w-xs mt-1" style={{ color: '#8fa3c8' }}>
              {cameraError || 'Please allow webcam permissions to start real-time driver monitoring.'}
            </p>
          </div>
          <button
            onClick={() => startWebcam()}
            className="px-4 py-2 rounded-xl text-white font-medium text-sm transition-colors flex items-center gap-2"
            style={{ background: '#1d4ed8', boxShadow: '0 4px 12px rgba(29,78,216,0.3)' }}
          >
            <Camera className="w-4 h-4" /> Enable Camera
          </button>
        </div>
      )}

      {/* Live AI HUD Overlay */}
      {isWebcamActive && (
        <>
          {/* Top Left Telemetry Badges */}
          <div className="absolute top-4 left-4 flex flex-col gap-2 z-10">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950/70 backdrop-blur-md border border-slate-800/80 text-xs font-semibold text-slate-200">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  eyeStatus.eye_status === 'Open_Eyes'
                    ? 'bg-emerald-400 animate-pulse'
                    : eyeStatus.eye_status === 'Closed_Eyes'
                    ? 'bg-rose-500 animate-ping'
                    : 'bg-amber-400'
                }`}
              />
              <Eye className="w-3.5 h-3.5 text-indigo-400" />
              <span>
                {eyeStatus.eye_status === 'Open_Eyes'
                  ? `Open (${(eyeStatus.confidence * 100).toFixed(0)}%)`
                  : eyeStatus.eye_status === 'Closed_Eyes'
                  ? `CLOSED (${eyeStatus.closed_duration.toFixed(1)}s)`
                  : 'Searching Face...'}
              </span>
            </div>

            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950/70 backdrop-blur-md border border-slate-800/80 text-xs font-semibold text-slate-200">
              <Smile className="w-3.5 h-3.5 text-emerald-400" />
              <span>Head: {headPose.direction ? headPose.direction.replace('_', ' ') : 'Forward'}</span>
            </div>
          </div>

          {/* Top Right Live Recording Indicator */}
          <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950/80 backdrop-blur-md border border-slate-800/80 text-xs font-bold z-10">
            {isMonitoring ? (
              <span className="flex items-center gap-2 text-rose-400">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
                LIVE MONITORING
              </span>
            ) : (
              <span className="text-slate-400">STANDBY</span>
            )}
          </div>

          {/* Real-time AI Face Bounding Box Reticle */}
          {faceBbox && (
            <div
              className={`absolute transition-all duration-150 ease-out border-2 pointer-events-none rounded-xl z-20 shadow-[0_0_15px_rgba(16,185,129,0.3)] ${
                eyeStatus.eye_status === 'Closed_Eyes'
                  ? 'border-rose-500 bg-rose-500/10 shadow-rose-500/40 text-rose-400'
                  : eyeStatus.eye_status === 'Open_Eyes'
                  ? 'border-emerald-400 bg-emerald-400/5 shadow-emerald-400/30 text-emerald-400'
                  : 'border-cyan-400 bg-cyan-400/5 text-cyan-400'
              }`}
              style={{
                left: `${(1 - faceBbox.x - faceBbox.width) * 100}%`,
                top: `${faceBbox.y * 100}%`,
                width: `${faceBbox.width * 100}%`,
                height: `${faceBbox.height * 100}%`,
              }}
            >
              {/* Corner Tech Accents */}
              <div className="absolute -top-1 -left-1 w-3 h-3 border-t-2 border-l-2 border-current" />
              <div className="absolute -top-1 -right-1 w-3 h-3 border-t-2 border-r-2 border-current" />
              <div className="absolute -bottom-1 -left-1 w-3 h-3 border-b-2 border-l-2 border-current" />
              <div className="absolute -bottom-1 -right-1 w-3 h-3 border-b-2 border-r-2 border-current" />

              {/* Driver AI HUD Target Tag */}
              <div className="absolute -top-7 left-1/2 transform -translate-x-1/2 px-2 py-0.5 rounded-md bg-slate-950/90 border border-slate-700 text-[10px] font-mono font-bold whitespace-nowrap shadow-md flex items-center gap-1.5 text-slate-200">
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    eyeStatus.eye_status === 'Closed_Eyes' ? 'bg-rose-500 animate-ping' : 'bg-emerald-400 animate-pulse'
                  }`}
                />
                <span>
                  {eyeStatus.eye_status === 'Closed_Eyes' ? 'DROWSY DETECTED' : 'FACE LOCKED'}
                </span>
              </div>
            </div>
          )}

          {/* Phone Warning Overlay directly on camera video */}
          {phoneStatus.phone_detected && (
            <div className="absolute inset-x-0 bottom-4 mx-auto w-max px-4 py-2 rounded-xl bg-rose-600/90 text-white font-bold text-sm shadow-2xl flex items-center gap-2 animate-bounce backdrop-blur-md z-20 border border-rose-400">
              <Smartphone className="w-5 h-5 animate-pulse" />
              MOBILE PHONE DETECTED
            </div>
          )}
        </>
      )}
    </div>
  );
};
