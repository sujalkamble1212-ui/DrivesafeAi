import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileText, Settings, User } from 'lucide-react';
import { useMonitoring } from '../context/MonitoringContext';

const NAV = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/reports',   label: 'Reports',   icon: FileText        },
  { path: '/settings',  label: 'Settings',  icon: Settings        },
  { path: '/profile',   label: 'Profile',   icon: User            },
];

export const MobileBottomNav = () => {
  const { isMonitoring } = useMonitoring();

  return (
    <nav
      className="md:hidden fixed bottom-0 inset-x-0 z-40 flex items-center justify-around px-2 py-1.5"
      style={{
        background: '#1a2747',
        boxShadow: '0 -4px 20px rgba(26,39,71,0.15)',
      }}
    >
      {NAV.map(({ path, label, icon: Icon }) => (
        <NavLink
          key={path}
          to={path}
          onClick={e => { if (isMonitoring && path !== '/dashboard') e.preventDefault(); }}
          className={({ isActive }) =>
            `flex flex-col items-center gap-0.5 px-4 py-1.5 rounded-xl transition-all ${
              isActive ? 'scale-105' : ''
            }`
          }
        >
          {({ isActive }) => (
            <>
              <div
                className="w-8 h-8 rounded-xl flex items-center justify-center"
                style={{ background: isActive ? 'rgba(255,255,255,0.15)' : 'transparent' }}
              >
                <Icon className="w-4.5 h-4.5" style={{ color: isActive ? '#fff' : '#8fa3c8' }} />
              </div>
              <span className="text-[9px] font-semibold"
                    style={{ color: isActive ? '#fff' : '#8fa3c8' }}>
                {label}
              </span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
};
