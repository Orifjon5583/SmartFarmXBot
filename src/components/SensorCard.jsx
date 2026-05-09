import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';

export default function SensorCard({ title, value, unit, icon: Icon, color = 'text-cyber-green', trend, detail }) {
  return (
    <motion.article
      whileHover={{ y: -4, scale: 1.01 }}
      className="glass relative overflow-hidden rounded-2xl p-5"
    >
      <div className="absolute right-0 top-0 h-28 w-28 rounded-full bg-cyber-green/10 blur-3xl" />
      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <div className="mt-3 flex items-end gap-2">
            <span className="font-display text-4xl font-bold text-white">{value}</span>
            <span className="pb-1 text-sm font-semibold text-slate-400">{unit}</span>
          </div>
        </div>
        <div className={`rounded-2xl border border-white/10 bg-white/8 p-3 ${color}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      <div className="relative mt-5 flex items-center justify-between text-sm">
        <span className="text-slate-400">{detail}</span>
        <span className="flex items-center gap-1 text-cyber-green">
          <TrendingUp className="h-4 w-4" />
          {trend}
        </span>
      </div>
    </motion.article>
  );
}
