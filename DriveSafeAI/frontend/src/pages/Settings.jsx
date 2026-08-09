import React, { useEffect, useState } from 'react';
import { settingService } from '../services/settingService';
import { Settings as SettingsIcon, Volume2, Camera, Sliders, Check, Save } from 'lucide-react';

/* ── Reusable section card ── */
const SectionCard = ({ icon: Icon, iconBg, iconColor, title, desc, children }) => (
  <div className="card rounded-2xl p-6 space-y-4">
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
           style={{ background: iconBg }}>
        <Icon className="w-5 h-5" style={{ color: iconColor }} />
      </div>
      <div>
        <h4 className="text-sm font-bold" style={{ color: '#1a2747' }}>{title}</h4>
        <p className="text-[11px]" style={{ color: '#9ba8c4' }}>{desc}</p>
      </div>
    </div>
    {children}
  </div>
);

export const Settings = () => {
  const [settings, setSettings] = useState({
    voice_alerts_enabled: true,
    sensitivity: 'medium',
    camera_index: 0,
  });
  const [saving,      setSaving]      = useState(false);
  const [savedSuccess,setSavedSuccess]= useState(false);

  useEffect(() => {
    settingService.getSettings()
      .then(d => { if (d) setSettings(d); })
      .catch(console.error);
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);
    try {
      await settingService.updateSettings({
        voice_alerts_enabled: settings.voice_alerts_enabled,
        sensitivity:  settings.sensitivity,
        camera_index: Number(settings.camera_index),
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch { alert('Failed to save settings.'); }
    finally { setSaving(false); }
  };

  return (
    <div className="max-w-2xl space-y-5">
      {/* Header */}
      <div className="flex items-center gap-2">
        <SettingsIcon className="w-5 h-5" style={{ color: '#2563eb' }} />
        <div>
          <h2 className="text-xl font-black" style={{ color: '#1a2747' }}>System Settings</h2>
          <p className="text-[11px]" style={{ color: '#9ba8c4' }}>
            Configure AI detection sensitivity, voice feedback, and camera input
          </p>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-4">

        {/* ── Voice alerts ── */}
        <SectionCard icon={Volume2} iconBg="#ede9fe" iconColor="#5b21b6"
          title="Offline Voice Alerts" desc="Spoken text-to-speech warnings when drowsiness or distraction is detected">
          <div className="flex items-center justify-between p-3 rounded-xl" style={{ background: '#f8faff', border: '1px solid #e2e8f4' }}>
            <div>
              <div className="text-xs font-semibold" style={{ color: '#1a2747' }}>Voice Alerts</div>
              <div className="text-[11px]" style={{ color: '#9ba8c4' }}>
                {settings.voice_alerts_enabled ? 'Enabled — alerts will be spoken aloud' : 'Disabled'}
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" checked={settings.voice_alerts_enabled}
                onChange={e => setSettings({ ...settings, voice_alerts_enabled: e.target.checked })}
                className="sr-only peer" />
              <div className="w-11 h-6 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"
                   style={{ background: settings.voice_alerts_enabled ? '#4f46e5' : '#d1d5db' }} />
            </label>
          </div>
        </SectionCard>

        {/* ── Detection Sensitivity ── */}
        <SectionCard icon={Sliders} iconBg="#dbeafe" iconColor="#1d4ed8"
          title="Detection Sensitivity" desc="Adjust trigger thresholds for eye closure, head pose, and yawn detection">
          <div className="grid grid-cols-3 gap-3">
            {['low','medium','high'].map(level => (
              <button type="button" key={level}
                onClick={() => setSettings({ ...settings, sensitivity: level })}
                className="py-3 rounded-xl text-xs font-bold capitalize transition-all"
                style={{
                  background: settings.sensitivity === level ? '#1d4ed8' : '#f1f5ff',
                  color:      settings.sensitivity === level ? '#fff'     : '#6b7a99',
                  border: `1.5px solid ${settings.sensitivity === level ? '#1d4ed8' : '#e2e8f4'}`,
                  boxShadow:  settings.sensitivity === level ? '0 4px 12px rgba(29,78,216,0.2)' : 'none',
                }}>
                {level}
              </button>
            ))}
          </div>
        </SectionCard>

        {/* ── Camera ── */}
        <SectionCard icon={Camera} iconBg="#d1fae5" iconColor="#047857"
          title="Webcam Input Device" desc="Select the camera index to use for driver face detection">
          <select value={settings.camera_index}
            onChange={e => setSettings({ ...settings, camera_index: Number(e.target.value) })}
            className="w-full px-4 py-2.5 rounded-xl text-sm font-medium outline-none"
            style={{ background: '#f8faff', border: '1.5px solid #e2e8f4', color: '#1a2747' }}
            onFocus={e  => e.target.style.borderColor = '#2563eb'}
            onBlur={e   => e.target.style.borderColor = '#e2e8f4'}>
            <option value={0}>Camera 0 — Default / Integrated Webcam</option>
            <option value={1}>Camera 1 — Secondary / USB Camera</option>
            <option value={2}>Camera 2 — External Input</option>
          </select>
        </SectionCard>



        {/* Save */}
        <div className="flex items-center gap-4 pt-1">
          <button type="submit" disabled={saving}
            className="px-6 py-2.5 rounded-xl font-bold text-sm flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
            style={{ background: '#1d4ed8', color: '#fff', boxShadow: '0 4px 14px rgba(29,78,216,0.25)' }}>
            <Save className="w-4 h-4" />
            {saving ? 'Saving…' : 'Save Settings'}
          </button>
          {savedSuccess && (
            <span className="text-xs font-bold flex items-center gap-1" style={{ color: '#047857' }}>
              <Check className="w-4 h-4" /> Settings saved!
            </span>
          )}
        </div>
      </form>
    </div>
  );
};
