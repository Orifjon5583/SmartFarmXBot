import { motion } from 'framer-motion';

export default function DeviceSwitch({ label, description, enabled, onChange, icon: Icon, disabled }) {
  return (
    <div className="glass-soft flex items-center justify-between gap-4 rounded-2xl p-4">
      <div className="flex min-w-0 items-center gap-3">
        <div className={`rounded-xl border border-white/10 p-3 ${enabled ? 'bg-cyber-green/15 text-cyber-green' : 'bg-white/5 text-slate-500'}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="font-semibold text-white">{label}</p>
          <p className="truncate text-sm text-slate-400">{description}</p>
        </div>
      </div>
      <button
        type="button"
        disabled={disabled}
        onClick={() => onChange(!enabled)}
        className={`focus-ring relative h-8 w-16 shrink-0 overflow-hidden rounded-full border transition ${
          enabled ? 'border-cyber-green/60 bg-cyber-green/30' : 'border-white/10 bg-white/10'
        } disabled:cursor-not-allowed disabled:opacity-60`}
        aria-pressed={enabled}
      >
        <motion.span
          animate={{ x: enabled ? 32 : 4 }}
          transition={{ type: 'spring', stiffness: 420, damping: 28 }}
          className={`absolute left-0 top-1 h-6 w-6 rounded-full ${enabled ? 'bg-cyber-green shadow-neon' : 'bg-slate-400'}`}
        />
      </button>
    </div>
  );
}
