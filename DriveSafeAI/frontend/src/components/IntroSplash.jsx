import React, { useState, useEffect } from 'react';
import { ShieldCheck, Activity, Eye, Smartphone, CheckCircle2, Play } from 'lucide-react';

export const IntroSplash = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [stepIndex, setStepIndex] = useState(0);
  const [isFading, setIsFading] = useState(false);

  const steps = [
    { label: 'Safety Score Engine', icon: ShieldCheck, color: 'linear-gradient(135deg,#1d4ed8,#3b82f6)' },
    { label: 'Attention Focus Mesh', icon: Activity,    color: 'linear-gradient(135deg,#7c3aed,#a78bfa)' },
    { label: 'Eye Closure Classifier', icon: Eye,        color: 'linear-gradient(135deg,#e11d48,#f87171)' },
    { label: 'Phone & Yawn Detector', icon: Smartphone, color: 'linear-gradient(135deg,#0d9488,#34d399)' },
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          return 100;
        }
        const next = prev + 2;
        if (next > 75) setStepIndex(3);
        else if (next > 50) setStepIndex(2);
        else if (next > 25) setStepIndex(1);
        return next;
      });
    }, 35);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (progress === 100) {
      const fadeTimer = setTimeout(() => {
        setIsFading(true);
        const completeTimer = setTimeout(() => {
          if (onComplete) onComplete();
        }, 500);
        return () => clearTimeout(completeTimer);
      }, 400);
      return () => clearTimeout(fadeTimer);
    }
  }, [progress, onComplete]);

  const handleSkip = () => {
    setIsFading(true);
    setTimeout(() => {
      if (onComplete) onComplete();
    }, 300);
  };

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center p-4 transition-all duration-500 ease-out ${
        isFading ? 'opacity-0 scale-95 pointer-events-none' : 'opacity-100 scale-100'
      }`}
      style={{ background: '#dff3f8' }}
    >
      {/* ── Outer Card matching Dashboard UI ── */}
      <div
        className="w-full max-w-xl bg-white rounded-3xl p-8 space-y-6 flex flex-col items-center text-center relative overflow-hidden"
        style={{
          boxShadow: '0 20px 60px rgba(26, 39, 71, 0.12)',
          border: '1px solid #e2e8f4',
        }}
      >
        {/* Top Navy Branding Badge */}
        <div className="flex items-center gap-3 px-5 py-2.5 rounded-2xl" style={{ background: '#1a2747' }}>
          <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.15)' }}>
            <ShieldCheck className="w-4 h-4 text-white" />
          </div>
          <div className="text-left">
            <div className="text-white font-extrabold text-xs leading-tight">DriveSafe AI</div>
            <div className="text-[9px] font-medium" style={{ color: '#8fa3c8' }}>Driver Safety System</div>
          </div>
        </div>

        {/* Title */}
        <div className="space-y-1">
          <h2 className="text-2xl font-black" style={{ color: '#1a2747' }}>
            Initializing AI System
          </h2>
          <p className="text-xs font-medium max-w-sm" style={{ color: '#6b7a99' }}>
            Preparing computer vision, eye monitoring, and attention analytics
          </p>
        </div>

        {/* ── 4 Mini Dashboard Tiles Preview ── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full">
          {steps.map((step, idx) => {
            const isLoaded = progress >= (idx + 1) * 25;
            const Icon = step.icon;
            return (
              <div
                key={idx}
                className={`rounded-2xl p-3.5 text-white text-left transition-all duration-300 flex flex-col justify-between ${
                  isLoaded ? 'scale-100 opacity-100 shadow-md' : 'scale-95 opacity-40'
                }`}
                style={{
                  background: isLoaded ? step.color : '#cbd5e1',
                  minHeight: '90px',
                }}
              >
                <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.25)' }}>
                  <Icon className="w-4 h-4 text-white" />
                </div>
                <div>
                  <div className="text-lg font-black leading-none mt-2">
                    {isLoaded ? '100%' : '...'}
                  </div>
                  <div className="text-[10px] font-semibold opacity-90 truncate mt-1">{step.label}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Progress Bar & Status Text ── */}
        <div className="w-full space-y-2 pt-1">
          <div className="flex justify-between items-center text-xs font-bold font-mono" style={{ color: '#1a2747' }}>
            <span className="flex items-center gap-1.5" style={{ color: '#2563eb' }}>
              <CheckCircle2 className="w-3.5 h-3.5" />
              {steps[stepIndex]?.label}
            </span>
            <span>{progress}%</span>
          </div>

          <div className="w-full h-3 rounded-full overflow-hidden p-0.5" style={{ background: '#f1f5f9', border: '1px solid #e2e8f4' }}>
            <div
              className="h-full rounded-full transition-all duration-150 ease-out"
              style={{
                width: `${progress}%`,
                background: 'linear-gradient(90deg, #1d4ed8, #10b981)',
              }}
            />
          </div>
        </div>

        {/* ── Skip / Enter Button matching 'Start Driving Session' button ── */}
        <button
          onClick={handleSkip}
          className="w-full sm:w-auto px-8 py-3 rounded-xl font-bold text-sm text-white flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg"
          style={{
            background: 'linear-gradient(135deg,#047857,#10b981)',
            boxShadow: '0 4px 14px rgba(16,185,129,0.35)',
          }}
        >
          <Play className="w-4 h-4 fill-white" />
          {progress === 100 ? 'Access Dashboard' : 'Skip & Enter System'}
        </button>
      </div>
    </div>
  );
};
