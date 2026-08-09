import React from 'react';
import { Trash2, X, Loader2 } from 'lucide-react';

export const ConfirmDeleteModal = ({ isOpen, onClose, onConfirm, title, message, loading }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
         style={{ background: 'rgba(26,39,71,0.35)', backdropFilter: 'blur(4px)' }}>
      <div className="card w-full max-w-md rounded-2xl p-6 space-y-5 relative"
           style={{ boxShadow: '0 20px 60px rgba(26,39,71,0.18)' }}>
        {/* Close */}
        <button onClick={onClose} disabled={loading}
                className="absolute top-4 right-4 p-1.5 rounded-xl transition-colors"
                style={{ color: '#9ba8c4' }}
                onMouseEnter={e => e.currentTarget.style.background = '#f1f5ff'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl flex items-center justify-center"
               style={{ background: '#fee2e2' }}>
            <Trash2 className="w-5 h-5" style={{ color: '#9f1239' }} />
          </div>
          <div>
            <h3 className="text-base font-bold" style={{ color: '#1a2747' }}>{title || 'Delete Report'}</h3>
            <p className="text-[11px]" style={{ color: '#e11d48' }}>Permanent Action</p>
          </div>
        </div>

        {/* Body */}
        <p className="text-xs leading-relaxed rounded-xl p-3.5"
           style={{ background: '#f8faff', border: '1px solid #e2e8f4', color: '#6b7a99' }}>
          {message || 'Are you sure you want to delete this session and all recorded data? This cannot be undone.'}
        </p>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-1">
          <button onClick={onClose} disabled={loading}
                  className="px-4 py-2 rounded-xl text-xs font-semibold transition-all"
                  style={{ background: '#f1f5ff', color: '#1a2747', border: '1px solid #e2e8f4' }}>
            Cancel
          </button>
          <button onClick={onConfirm} disabled={loading}
                  className="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all disabled:opacity-50"
                  style={{ background: '#dc2626', color: '#fff', boxShadow: '0 4px 12px rgba(220,38,38,0.25)' }}>
            {loading
              ? <><Loader2 className="w-4 h-4 animate-spin" /> Deleting…</>
              : <><Trash2  className="w-4 h-4" /> Delete</>}
          </button>
        </div>
      </div>
    </div>
  );
};
