import { Camera, ScanLine, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export default function CameraFeed({ compact = false }) {
  return (
    <section className="glass overflow-hidden rounded-2xl">
      <div className="relative aspect-video bg-[linear-gradient(135deg,rgba(56,242,161,.16),rgba(53,199,255,.1)),url('https://images.unsplash.com/photo-1511690656952-34342bb7c2f2?auto=format&fit=crop&w=1400&q=80')] bg-cover bg-center">
        <div className="absolute inset-0 bg-night/35" />
        <motion.div
          animate={{ y: ['0%', '88%', '0%'] }}
          transition={{ duration: 4.8, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute left-0 right-0 top-0 h-1 bg-cyber-green/80 shadow-neon"
        />
        <div className="absolute left-4 top-4 flex items-center gap-2 rounded-full border border-cyber-green/30 bg-night/70 px-3 py-1 text-xs font-semibold text-cyber-green backdrop-blur-xl">
          <span className="h-2 w-2 rounded-full bg-cyber-green" />
          Jonli kamera
        </div>
        <div className="absolute bottom-4 left-4 right-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="font-display text-2xl font-bold text-white">A zona kuzatuvi</p>
            <p className="text-sm text-slate-200">AI tahlil: barg qoplami 94% sog‘lom</p>
          </div>
          <div className="flex gap-2">
            <button className="focus-ring rounded-xl bg-white/12 p-3 text-white backdrop-blur-xl" title="Rasm olish">
              <Camera className="h-5 w-5" />
            </button>
            <button className="focus-ring rounded-xl bg-white/12 p-3 text-white backdrop-blur-xl" title="O‘simlikni tekshirish">
              <ScanLine className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
      {!compact && (
        <div className="grid gap-3 p-4 sm:grid-cols-3">
          {['Rasm olish tayyor', 'Vaqt oralig‘i video har 15 daqiqada', 'AI kasallik tekshiruvi tayyor'].map((text) => (
            <div key={text} className="flex items-center gap-2 rounded-xl bg-white/[0.055] p-3 text-sm text-slate-300">
              <Sparkles className="h-4 w-4 text-cyber-green" />
              {text}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
