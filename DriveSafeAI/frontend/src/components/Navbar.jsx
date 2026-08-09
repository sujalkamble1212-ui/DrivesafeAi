import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useMonitoring } from '../context/MonitoringContext';
import { ShieldCheck, LogOut } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const { isMonitoring } = useMonitoring();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="glass-panel sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between border-b border-slate-200/70 dark:border-slate-800">
      {/* Brand Logo */}
      <Link to="/dashboard" className="flex items-center gap-3 group">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 p-0.5 shadow-lg glow-indigo group-hover:scale-105 transition-transform">
          <div className="w-full h-full bg-slate-50 dark:bg-slate-950 rounded-[10px] flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
          </div>
        </div>
        <div>
          <h1 className="text-xl font-extrabold bg-gradient-to-r from-slate-900 via-slate-700 to-indigo-600 dark:from-white dark:via-slate-100 dark:to-indigo-300 bg-clip-text text-transparent tracking-tight">
            DriveSafe <span className="text-indigo-400">AI</span>
          </h1>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium tracking-wider uppercase">Driver Monitoring System</p>
        </div>
      </Link>

      {/* System Status Indicator & Controls */}
      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          AI Engines Active
        </div>

        {/* User Profile dropdown or avatar */}
        {user && (
          <div className="flex items-center gap-3 pl-3 border-l border-slate-200/70 dark:border-slate-800">
            <Link
              to="/profile"
              onClick={(event) => {
                if (isMonitoring) {
                  event.preventDefault();
                }
              }}
              className="flex items-center gap-2.5 hover:opacity-80 transition-opacity"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-emerald-500 flex items-center justify-center text-white font-bold text-xs shadow-md">
                {user.full_name ? user.full_name.charAt(0).toUpperCase() : user.username.charAt(0).toUpperCase()}
              </div>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200 hidden md:inline">
                {user.full_name || user.username}
              </span>
            </Link>

            <button
              onClick={handleLogout}
              className="p-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};
