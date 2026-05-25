import { motion } from 'framer-motion';

export default function DeviceSwitch({ label, description, enabled, onChange, icon: Icon, disabled }) {
  return (
    <div className="glass-soft flex items-center justify-between gap-3 rounded-2xl p-4">
      <div className="flex min-w-0 flex-1 items-center gap-3">
        <div className={`shrink-0 rounded-xl border border-white/10 p-2.5 sm:p-3 ${enabled ? 'bg-cyber-green/15 text-cyber-green' : 'bg-white/5 text-slate-500'}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-white sm:text-base">{label}</p>
          <p className="hidden text-sm text-slate-400 sm:block">{description}</p>
        </div>
      </div>
      <button
        type="button"
        disabled={disabled}
        onClick={() => onChange(!enabled)}
        className={`focus-ring relative h-7 w-14 shrink-0 overflow-hidden rounded-full border transition sm:h-8 sm:w-16 ${
          enabled ? 'border-cyber-green/60 bg-cyber-green/30' : 'border-white/10 bg-white/10'
        } disabled:cursor-not-allowed disabled:opacity-60`}
        aria-pressed={enabled}
      >
        <motion.span
          animate={{ x: enabled ? 28 : 3 }}
          transition={{ type: 'spring', stiffness: 420, damping: 28 }}
          className={`absolute left-0 top-0.5 h-5.5 w-5.5 rounded-full sm:top-1 sm:h-6 sm:w-6 ${enabled ? 'bg-cyber-green shadow-neon' : 'bg-slate-400'}`}
          style={{ width: '22px', height: '22px' }}
        />
      </button>
    </div>
  );
}
