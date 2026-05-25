import { Bell, Download, LogOut, Menu, RefreshCw, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext.jsx';
import { useGreenhouse } from '../../context/GreenhouseContext.jsx';
import { usePwaInstall } from '../../hooks/usePwaInstall.js';

export default function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const { refresh, status } = useGreenhouse();
  const { canInstall, install, isInstalled } = usePwaInstall();

  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-night/72 px-4 py-4 backdrop-blur-2xl sm:px-6 lg:px-8">
      <div className="flex items-center justify-between gap-4">
        <button onClick={onMenuClick} className="flex items-center gap-3 lg:hidden">
          <Menu className="h-5 w-5 text-cyber-green" />
          <span className="font-display font-bold">Issiqxona Nexus</span>
        </button>
        <div className="hidden min-w-0 lg:block">
          <p className="text-xs uppercase tracking-[0.3em] text-cyber-blue">Sanoat issiqxonasi boshqaruvi</p>
          <h1 className="truncate font-display text-2xl font-bold text-white">Aqlli Issiqxona Boshqaruv Markazi</h1>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={refresh}
            className="focus-ring rounded-xl border border-white/10 bg-white/5 p-3 text-slate-200 transition hover:border-cyber-blue/40 hover:text-cyber-blue"
            title="Sensorlarni yangilash"
          >
            <RefreshCw className="h-5 w-5" />
          </motion.button>
          <div className="hidden items-center gap-2 rounded-xl border border-cyber-green/20 bg-cyber-green/10 px-3 py-2 text-sm text-cyber-green sm:flex">
            <ShieldCheck className="h-4 w-4" />
            {status.raspberryPi || 'onlayn'}
          </div>
          <motion.button
            whileHover={{ scale: isInstalled ? 1 : 1.04 }}
            whileTap={{ scale: isInstalled ? 1 : 0.96 }}
            onClick={install}
            disabled={isInstalled}
            className={`focus-ring flex items-center gap-2 rounded-xl border px-3 py-3 text-sm font-bold transition ${
              canInstall
                ? 'border-cyber-blue/40 bg-cyber-blue/10 text-cyber-blue hover:border-cyber-green/50 hover:text-cyber-green'
                : 'border-white/10 bg-white/5 text-slate-300 hover:border-cyber-blue/40 hover:text-cyber-blue'
            } disabled:cursor-default disabled:opacity-60`}
            title={isInstalled ? 'App allaqachon o‘rnatilgan' : 'PWA appni o‘rnatish'}
          >
            <Download className="h-5 w-5" />
            <span className="hidden xl:inline">{isInstalled ? 'O‘rnatilgan' : 'Yuklab olish'}</span>
          </motion.button>
          <button className="focus-ring rounded-xl border border-white/10 bg-white/5 p-3 text-slate-200 transition hover:border-cyber-green/40 hover:text-cyber-green" title="Ogohlantirishlar">
            <Bell className="h-5 w-5" />
          </button>
          <div className="hidden text-right md:block">
            <p className="text-sm font-semibold text-white">{user?.name}</p>
            <p className="text-xs text-slate-400">{user?.role}</p>
          </div>
          <button onClick={logout} className="focus-ring rounded-xl border border-white/10 bg-white/5 p-3 text-slate-300 transition hover:border-cyber-red/40 hover:text-cyber-red" title="Chiqish">
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
