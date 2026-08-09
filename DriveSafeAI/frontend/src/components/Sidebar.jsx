import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, FileText, Settings, User, ShieldCheck, LogOut } from 'lucide-react';
import { useMonitoring } from '../context/MonitoringContext';
import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/reports',   label: 'Reports',   icon: FileText        },
  { path: '/settings',  label: 'Settings',  icon: Settings        },
  { path: '/profile',   label: 'Profile',   icon: User            },
];

export const Sidebar = () => {
  const { isMonitoring } = useMonitoring();
  const { user, logout }  = useAuth();
  const navigate           = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const initials = user
    ? (user.full_name || user.username || 'U').charAt(0).toUpperCase()
    : 'U';
  const displayName = user?.full_name || user?.username || 'Driver';

  return (
    <aside
      className="hidden md:flex flex-col min-h-screen"
      style={{ width: 220, minWidth: 220, background: '#1a2747' }}
    >
      {/* ── Logo / Brand ── */}
      <div className="px-5 pt-7 pb-6 flex items-center gap-3">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
          style={{ background: 'rgba(255,255,255,0.12)' }}
        >
          <ShieldCheck className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="text-white font-extrabold text-[15px] leading-tight">DriveSafe</div>
          <div className="text-[10px] font-medium" style={{ color: '#8fa3c8' }}>AI Monitor</div>
        </div>
      </div>

      {/* ── User avatar ── */}
      <div className="mx-4 mb-5 p-3 rounded-xl flex items-center gap-3"
           style={{ background: 'rgba(255,255,255,0.06)' }}>
        <div
          className="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm shrink-0"
          style={{ background: 'linear-gradient(135deg,#6366f1,#10b981)', color: '#fff' }}
        >
          {initials}
        </div>
        <div className="min-w-0">
          <div className="text-white font-semibold text-xs truncate">{displayName}</div>
          <div className="text-[10px]" style={{ color: '#8fa3c8' }}>Driver</div>
        </div>
      </div>

      {/* ── Nav label ── */}
      <div className="px-5 mb-2 text-[10px] font-bold uppercase tracking-widest"
           style={{ color: '#4e6299' }}>
        Menu
      </div>

      {/* ── Nav items ── */}
      <nav className="flex-1 px-3 space-y-0.5">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            onClick={(e) => {
              if (isMonitoring && path !== '/dashboard') e.preventDefault();
            }}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-white text-[#1a2747] shadow font-bold'
                  : 'text-[#8fa3c8] hover:bg-white/10 hover:text-white'
              }`
            }
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* ── Bottom: Settings + Logout ── */}
      <div className="p-3 space-y-0.5 border-t" style={{ borderColor: 'rgba(255,255,255,0.07)' }}>
        <div className="px-3 py-2 text-[10px]" style={{ color: '#4e6299' }}>
          EfficientNetB0 · MediaPipe · YOLOv8
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all"
          style={{ color: '#f87171' }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(248,113,113,0.1)'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
        >
          <LogOut className="w-4 h-4 shrink-0" />
          Log out
        </button>
      </div>
    </aside>
  );
};
