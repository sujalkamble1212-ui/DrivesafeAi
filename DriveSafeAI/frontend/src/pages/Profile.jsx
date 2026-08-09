import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { User as UserIcon, Mail, Lock, Check, AlertCircle, Save } from 'lucide-react';

const Field = ({ label, icon: Icon, ...props }) => (
  <div className="space-y-1">
    <label className="text-[11px] font-bold uppercase tracking-wider" style={{ color: '#9ba8c4' }}>{label}</label>
    <div className="relative">
      {Icon && <Icon className="w-4 h-4 absolute left-3.5 top-3" style={{ color: '#9ba8c4' }} />}
      <input
        {...props}
        className={`w-full ${Icon ? 'pl-10' : 'pl-4'} pr-4 py-2.5 rounded-xl text-sm outline-none transition-colors`}
        style={{
          background: props.disabled ? '#f1f5ff' : '#f8faff',
          border: '1.5px solid #e2e8f4',
          color: props.disabled ? '#9ba8c4' : '#1a2747',
          cursor: props.disabled ? 'not-allowed' : 'text',
        }}
        onFocus={e => { if (!props.disabled) e.target.style.borderColor = '#2563eb'; }}
        onBlur={e  => { e.target.style.borderColor = '#e2e8f4'; }}
      />
    </div>
  </div>
);

export const Profile = () => {
  const { user, updateProfile } = useAuth();

  const [fullName,       setFullName]       = useState(user?.full_name || '');
  const [email,          setEmail]          = useState(user?.email || '');
  const [currentPassword,setCurrentPassword]= useState('');
  const [newPassword,    setNewPassword]    = useState('');
  const [saving,         setSaving]         = useState(false);
  const [message,        setMessage]        = useState('');
  const [error,          setError]          = useState('');

  const initials    = user ? (user.full_name || user.username || 'U').charAt(0).toUpperCase() : 'U';
  const displayName = user?.full_name || user?.username || 'Driver';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true); setMessage(''); setError('');
    try {
      const payload = { full_name: fullName, email };
      if (newPassword) { payload.current_password = currentPassword; payload.new_password = newPassword; }
      await updateProfile(payload);
      setMessage('Profile updated successfully!');
      setCurrentPassword(''); setNewPassword('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile.');
    } finally { setSaving(false); }
  };

  return (
    <div className="max-w-2xl space-y-5">
      {/* Header */}
      <div className="flex items-center gap-2">
        <UserIcon className="w-5 h-5" style={{ color: '#2563eb' }} />
        <div>
          <h2 className="text-xl font-black" style={{ color: '#1a2747' }}>Driver Profile</h2>
          <p className="text-[11px]" style={{ color: '#9ba8c4' }}>Manage account information and security credentials</p>
        </div>
      </div>

      <div className="card rounded-2xl p-6 space-y-6">
        {/* Avatar + user info — like reference profile row */}
        <div className="flex items-center gap-4 pb-5" style={{ borderBottom: '1px solid #e2e8f4' }}>
          <div className="w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-black shrink-0"
               style={{ background: 'linear-gradient(135deg,#4f46e5,#10b981)' }}>
            {initials}
          </div>
          <div>
            <h3 className="text-base font-bold" style={{ color: '#1a2747' }}>{displayName}</h3>
            <p className="text-xs" style={{ color: '#9ba8c4' }}>{user?.email}</p>
            <span className="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full mt-1"
                  style={{ background: '#dbeafe', color: '#1e40af' }}>Registered Driver</span>
          </div>
        </div>

        {/* Messages */}
        {message && (
          <div className="p-3 rounded-xl text-xs flex items-center gap-2 font-semibold"
               style={{ background: '#d1fae5', border: '1px solid #6ee7b7', color: '#065f46' }}>
            <Check className="w-4 h-4" /> {message}
          </div>
        )}
        {error && (
          <div className="p-3 rounded-xl text-xs flex items-center gap-2 font-semibold"
               style={{ background: '#fee2e2', border: '1px solid #fca5a5', color: '#9f1239' }}>
            <AlertCircle className="w-4 h-4" /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Username"  icon={UserIcon} type="text"  disabled value={user?.username || ''} />
          <Field label="Full Name" icon={UserIcon} type="text"  value={fullName} onChange={e => setFullName(e.target.value)} />
          <Field label="Email"     icon={Mail}     type="email" value={email}    onChange={e => setEmail(e.target.value)} />

          {/* Password section */}
          <div className="pt-4 space-y-4" style={{ borderTop: '1px solid #e2e8f4' }}>
            <h4 className="text-[11px] font-bold uppercase tracking-wider" style={{ color: '#9ba8c4' }}>
              Change Password (optional)
            </h4>
            <Field label="Current Password" icon={Lock} type="password" placeholder="••••••••"
              value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} />
            <Field label="New Password"     icon={Lock} type="password" placeholder="••••••••"
              value={newPassword}     onChange={e => setNewPassword(e.target.value)} />
          </div>

          <button type="submit" disabled={saving}
            className="w-full py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50 mt-2"
            style={{ background: '#1d4ed8', color: '#fff', boxShadow: '0 4px 14px rgba(29,78,216,0.25)' }}>
            <Save className="w-4 h-4" />
            {saving ? 'Saving…' : 'Update Profile'}
          </button>
        </form>
      </div>
    </div>
  );
};
