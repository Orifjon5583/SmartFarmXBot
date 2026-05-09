import { AlertTriangle, CheckCircle2, Info } from 'lucide-react';

const iconMap = {
  warning: AlertTriangle,
  success: CheckCircle2,
  info: Info,
};

export default function AlertPanel({ alerts }) {
  return (
    <section className="glass rounded-2xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl font-bold text-white">Ogohlantirishlar</h2>
        <span className="rounded-full bg-white/8 px-3 py-1 text-xs text-slate-300">{alerts.length} ta faol</span>
      </div>
      <div className="space-y-3">
        {alerts.map((alert) => {
          const Icon = iconMap[alert.type] || Info;
          return (
            <div key={alert.id} className="rounded-xl border border-white/10 bg-white/[0.045] p-3">
              <div className="flex gap-3">
                <Icon className="mt-0.5 h-5 w-5 text-cyber-amber" />
                <div>
                  <p className="text-sm font-semibold text-white">{alert.title}</p>
                  <p className="mt-1 text-sm text-slate-400">{alert.detail}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
