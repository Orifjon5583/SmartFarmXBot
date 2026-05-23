import { CalendarClock, Download, ScanSearch } from 'lucide-react';
import { motion } from 'framer-motion';
import CameraFeed from '../components/CameraFeed.jsx';

export default function CameraMonitoring() {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <CameraFeed />
      <section className="grid gap-6 lg:grid-cols-3">
        {[
          { title: 'Rasm olish', value: '--', detail: 'Hozircha faol emas', icon: Download },
          { title: 'Vaqt oralig‘i video', value: '--', detail: 'Hozircha faol emas', icon: CalendarClock },
          { title: 'AI o‘simlik salomatligi', value: '--', detail: 'Kamera kerak', icon: ScanSearch },
        ].map(({ title, value, detail, icon: Icon }) => (
          <div key={title} className="glass rounded-2xl p-5">
            <Icon className="mb-5 h-7 w-7 text-cyber-green" />
            <p className="text-sm text-slate-400">{title}</p>
            <p className="mt-2 font-display text-3xl font-bold text-white">{value}</p>
            <p className="mt-2 text-sm text-slate-400">{detail}</p>
          </div>
        ))}
      </section>
    </motion.div>
  );
}
