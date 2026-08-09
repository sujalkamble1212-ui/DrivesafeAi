import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { useWebcam } from '../hooks/useWebcam';
import { monitoringService } from '../services/monitoringService';

const MonitoringContext = createContext(null);

export const MonitoringProvider = ({ children }) => {
  const {
    videoRef,
    isWebcamActive,
    cameraError,
    startWebcam,
    stopWebcam,
    captureFrameBase64,
  } = useWebcam();

  const [isMonitoring, setIsMonitoring] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState(null);

  // Live AI telemetry state
  const [eyeStatus, setEyeStatus] = useState({ eye_status: 'No_Face', confidence: 0, closed_duration: 0 });
  const [headPose, setHeadPose] = useState({ direction: 'Forward', yaw: 0, pitch: 0, distraction_duration: 0 });
  const [phoneStatus, setPhoneStatus] = useState({ phone_detected: false, phone_count: 0 });
  const [yawnStatus, setYawnStatus] = useState({ mar: 0, is_yawning: false, total_yawns: 0 });
  const [faceBbox, setFaceBbox] = useState(null);

  // Real-time Scores — reset to 100 on each new session
  const [safetyScore, setSafetyScore] = useState(100);
  const [attentionScore, setAttentionScore] = useState(100);

  // Alert State
  const [currentAlert, setCurrentAlert] = useState(null);
  const alertTimeoutRef = useRef(null);

  // Session Statistics
  const [sessionDuration, setSessionDuration] = useState(0);
  const [alertCounters, setAlertCounters] = useState({
    total: 0,
    drowsiness: 0,
    distraction: 0,
    phone: 0,
    yawn: 0,
  });

  // Chart data ring buffer (max 30 data points)
  const [chartData, setChartData] = useState([]);

  // Session timer ticker
  useEffect(() => {
    let interval = null;
    if (isMonitoring) {
      interval = setInterval(() => {
        setSessionDuration((prev) => prev + 1);
      }, 1000);
    } else {
      setSessionDuration(0);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isMonitoring]);

  const startMonitoringSession = async (frameBase64 = null) => {
    try {
      // Start webcam first so camera is on for the session
      await startWebcam();
      const res = await monitoringService.startSession(frameBase64);
      setActiveSessionId(res.session_id);
      setIsMonitoring(true);
      setSessionDuration(0);
      // Reset ALL scores and counters to initial state for each new trip
      setSafetyScore(100);
      setAttentionScore(100);
      setAlertCounters({ total: 0, drowsiness: 0, distraction: 0, phone: 0, yawn: 0 });
      setChartData([]);
      setCurrentAlert(null);
      return res.session_id;
    } catch (err) {
      console.error('Failed to start monitoring session:', err);
      throw err;
    }
  };

  const stopMonitoringSession = async () => {
    if (activeSessionId) {
      try {
        await monitoringService.endSession(activeSessionId);
      } catch (err) {
        console.error('Error ending session on backend:', err);
      }
    }
    setIsMonitoring(false);
    // Stop webcam when session ends — camera off after trip
    stopWebcam();
    const lastSessionId = activeSessionId;
    setActiveSessionId(null);
    return lastSessionId;
  };

  const updateFrameResults = useCallback((data) => {
    if (!data) return;

    if (data.eye || data.eye_status) setEyeStatus(data.eye || data.eye_status);
    if (data.head || data.head_pose) setHeadPose(data.head || data.head_pose);
    if (data.phone || data.phone_status) setPhoneStatus(data.phone || data.phone_status);
    if (data.yawn || data.yawn_status) setYawnStatus(data.yawn || data.yawn_status);
    setFaceBbox(data.face_bbox || null);

    if (data.safety_score !== undefined) setSafetyScore(data.safety_score);
    if (data.attention_score !== undefined) setAttentionScore(data.attention_score);

    // Update real-time chart history
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    setChartData((prev) => {
      const next = [...prev, { time: now, safety: data.safety_score, attention: data.attention_score }];
      return next.length > 25 ? next.slice(next.length - 25) : next;
    });

    // Check if new alerts were fired
    if (data.alerts_fired && data.alerts_fired.length > 0) {
      data.alerts_fired.forEach((alertObj) => {
        const alertType = typeof alertObj === 'string' ? alertObj : alertObj?.alert_type;
        if (!alertType) return;

        setAlertCounters((prev) => ({
          ...prev,
          total: prev.total + 1,
          drowsiness: alertType === 'drowsiness' ? prev.drowsiness + 1 : prev.drowsiness,
          distraction: alertType === 'distraction' ? prev.distraction + 1 : prev.distraction,
          phone: alertType === 'phone_detected' ? prev.phone + 1 : prev.phone,
          yawn: alertType === 'yawn_detected' ? prev.yawn + 1 : prev.yawn,
        }));

        let msg = 'Alert Detected!';
        let sev = 'warning';
        let speechText = '';

        if (alertType === 'drowsiness') {
          msg = '⚠️ Drowsiness Detected! Please open your eyes!';
          speechText = 'Driver appears drowsy. Please open your eyes.';
          sev = 'danger';
        } else if (alertType === 'distraction') {
          msg = '👀 Distraction Detected! Focus on the road!';
          speechText = 'Please focus on the road.';
          sev = 'warning';
        } else if (alertType === 'phone_detected') {
          msg = '📱 Mobile Phone Detected! Keep your hands on the wheel!';
          speechText = 'Mobile phone detected. Please put it down.';
          sev = 'danger';
        } else if (alertType === 'yawn_detected') {
          msg = '🥱 Yawning Detected! Consider taking a rest break.';
          speechText = 'Yawning detected. Consider taking a rest.';
          sev = 'info';
        }

        setCurrentAlert({ type: alertType, message: msg, severity: sev, timestamp: new Date() });

        if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
        alertTimeoutRef.current = setTimeout(() => {
          setCurrentAlert(null);
        }, 1200);
      });
    } else {
      // Clear alert banner promptly when driver is focused again (no alerts fired)
      if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
      alertTimeoutRef.current = setTimeout(() => {
        setCurrentAlert(null);
      }, 1200);
    }
  }, []);

  return (
    <MonitoringContext.Provider
      value={{
        isMonitoring,
        activeSessionId,
        eyeStatus,
        headPose,
        phoneStatus,
        yawnStatus,
        faceBbox,
        safetyScore,
        attentionScore,
        currentAlert,
        sessionDuration,
        alertCounters,
        chartData,
        videoRef,
        isWebcamActive,
        cameraError,
        startWebcam,
        stopWebcam,
        captureFrameBase64,
        startMonitoringSession,
        stopMonitoringSession,
        updateFrameResults,
      }}
    >
      {children}
    </MonitoringContext.Provider>
  );
};

export const useMonitoring = () => {
  const context = useContext(MonitoringContext);
  if (!context) {
    throw new Error('useMonitoring must be used within a MonitoringProvider');
  }
  return context;
};
