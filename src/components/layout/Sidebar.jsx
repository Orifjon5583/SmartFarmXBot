import { Activity, BarChart3, Camera, LayoutDashboard, Leaf, Settings, SlidersHorizontal } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Bosh panel', icon: LayoutDashboard },
  { to: '/devices', label: 'Qurilmalar', icon: SlidersHorizontal },
  { to: '/analytics', label: 'Analitika', icon: BarChart3 },
  { to: '/camera', label: 'Kamera', icon: Camera },
  { to: '/settings', label: 'Sozlamalar', icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 border-r border-white/10 bg-night/80 px-4 py-5 backdrop-blur-2xl lg:block">
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyber-green/30 bg-cyber-green/10 shadow-neon">
          <Leaf className="h-6 w-6 text-cyber-green" />
        </div>
        <div>
          <p className="font-display text-lg font-bold tracking-wide text-white">Issiqxona Nexus</p>
          <p className="text-xs uppercase tracking-[0.22em] text-cyber-blue">Raspberry Pi IoT</p>
        </div>
      </div>

      <nav className="space-y-2">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `group flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold transition ${
                isActive
                  ? 'border border-cyber-green/30 bg-cyber-green/12 text-white shadow-neon'
                  : 'text-slate-400 hover:bg-white/8 hover:text-white'
              }`
            }
          >
            <Icon className="h-5 w-5 text-cyber-green transition group-hover:scale-110" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="absolute bottom-5 left-4 right-4 rounded-2xl border border-white/10 bg-white/[0.045] p-4">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
          <Activity className="h-4 w-4 text-cyber-blue" />
          Avtomatika yadrosi
        </div>
        <div className="h-2 rounded-full bg-white/10">
          <div className="h-2 w-[87%] rounded-full bg-gradient-to-r from-cyber-green to-cyber-blue shadow-blue" />
        </div>
        <p className="mt-3 text-xs text-slate-400">Qoidalar tizimi faol, rele kechikishi 32ms.</p>
      </div>
    </aside>
  );
}
