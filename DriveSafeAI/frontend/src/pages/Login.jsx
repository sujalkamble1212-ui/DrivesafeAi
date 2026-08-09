import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, User, ArrowRight, AlertCircle } from 'lucide-react';

const Field = ({ label, icon: Icon, ...props }) => (
  <div className="space-y-1.5">
    <label className="text-xs font-semibold" style={{ color: '#6b7a99' }}>{label}</label>
    <div className="relative">
      <Icon className="w-4 h-4 absolute left-3.5 top-3" style={{ color: '#9ba8c4' }} />
      <input
        {...props}
        className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm outline-none transition-colors"
        style={{ background: '#f1f5ff', border: '1.5px solid #e2e8f4', color: '#1a2747' }}
        onFocus={e => e.target.style.borderColor = '#2563eb'}
        onBlur={e  => e.target.style.borderColor = '#e2e8f4'}
      />
    </div>
  </div>
);

export const Login = () => {
  const { login } = useAuth();
  const navigate  = useNavigate();

  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password,        setPassword]        = useState('');
  const [error,           setError]           = useState('');
  const [loading,         setLoading]         = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try { await login(usernameOrEmail, password); navigate('/dashboard'); }
    catch (err) { setError(err.response?.data?.error || 'Invalid credentials. Please try again.'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: '#dff3f8' }}>
      {/* Card */}
      <div className="w-full max-w-md rounded-3xl overflow-hidden"
           style={{ boxShadow: '0 20px 60px rgba(26,39,71,0.14)' }}>

        {/* Navy top band — matches sidebar */}
        <div className="px-8 py-7 flex flex-col items-center gap-3"
             style={{ background: '#1a2747' }}>
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center"
               style={{ background: 'rgba(255,255,255,0.12)' }}>
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div className="text-center">
            <h1 className="text-xl font-black text-white">DriveSafe AI</h1>
            <p className="text-[11px] mt-0.5" style={{ color: '#8fa3c8' }}>Driver Monitoring System</p>
          </div>
        </div>

        {/* White form panel */}
        <div className="bg-white px-8 py-7 space-y-5">
          <div>
            <h2 className="text-lg font-black" style={{ color: '#1a2747' }}>Welcome Back</h2>
            <p className="text-xs" style={{ color: '#9ba8c4' }}>Sign in to access your dashboard</p>
          </div>

          {error && (
            <div className="p-3 rounded-xl text-xs flex items-center gap-2 font-semibold"
                 style={{ background: '#fee2e2', border: '1px solid #fca5a5', color: '#9f1239' }}>
              <AlertCircle className="w-4 h-4 shrink-0" /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Field label="Username or Email" icon={User} type="text" required
              placeholder="driver@drivesafe.ai"
              value={usernameOrEmail} onChange={e => setUsernameOrEmail(e.target.value)} />
            <Field label="Password" icon={Lock} type="password" required
              placeholder="••••••••"
              value={password} onChange={e => setPassword(e.target.value)} />

            <button type="submit" disabled={loading}
              className="w-full py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50 mt-1"
              style={{ background: '#1d4ed8', color: '#fff', boxShadow: '0 4px 14px rgba(29,78,216,0.25)' }}>
              {loading ? 'Signing in…' : 'Sign In'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="text-center text-xs pt-3" style={{ borderTop: '1px solid #e2e8f4', color: '#9ba8c4' }}>
            Don't have an account?{' '}
            <Link to="/register" className="font-bold" style={{ color: '#1d4ed8' }}>Create Account</Link>
          </div>
        </div>
      </div>
    </div>
  );
};
