import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { MonitoringProvider, useMonitoring } from './context/MonitoringContext';

import { Sidebar } from './components/Sidebar';
import { MobileBottomNav } from './components/MobileBottomNav';
import { IntroSplash } from './components/IntroSplash';

import { Login }     from './pages/Login';
import { Register }  from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Reports }   from './pages/Reports';
import { Settings }  from './pages/Settings';
import { Profile }   from './pages/Profile';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const { isMonitoring } = useMonitoring();
  const location = useLocation();
  const navigate  = useNavigate();

  const [showSplash, setShowSplash] = useState(() => {
    return !sessionStorage.getItem('drivesafe_splash_seen');
  });

  const handleSplashComplete = () => {
    sessionStorage.setItem('drivesafe_splash_seen', 'true');
    setShowSplash(false);
  };

  useEffect(() => {
    if (!loading && isAuthenticated && isMonitoring && location.pathname !== '/dashboard') {
      navigate('/dashboard', { replace: true });
    }
  }, [loading, isAuthenticated, isMonitoring, location.pathname, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#dff3f8' }}>
        <div className="text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl mx-auto flex items-center justify-center" style={{ background: '#1a2747' }}>
            <svg className="w-6 h-6 text-white animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
          </div>
          <p className="text-sm font-semibold" style={{ color: '#1a2747' }}>Loading DriveSafe AI…</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return (
    <>
      {showSplash && <IntroSplash onComplete={handleSplashComplete} />}
      {/* Outer: light aqua bg */}
      <div className="min-h-screen flex" style={{ background: '#dff3f8' }}>
        <Sidebar />
        {/* Inner white rounded panel */}
        <div className="flex-1 m-3 rounded-2xl bg-white overflow-hidden flex flex-col"
             style={{ boxShadow: '0 4px 24px rgba(26,39,71,0.08)' }}>
          {/* Monitoring banner */}
          {isMonitoring && (
            <div className="px-5 py-2 text-xs font-semibold text-center"
                 style={{ background: '#fef3c7', color: '#92400e', borderBottom: '1px solid #fde68a' }}>
              🚗 Driving session active — end the session to access other pages.
            </div>
          )}
          <main className="flex-1 p-6 overflow-y-auto">
            {children}
          </main>
        </div>
        <MobileBottomNav />
      </div>
    </>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <MonitoringProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login"    element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/reports"   element={<ProtectedRoute><Reports /></ProtectedRoute>} />
              <Route path="/settings"  element={<ProtectedRoute><Settings /></ProtectedRoute>} />
              <Route path="/profile"   element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </BrowserRouter>
        </MonitoringProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
