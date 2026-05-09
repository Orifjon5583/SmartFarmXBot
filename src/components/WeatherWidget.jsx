import { CloudSun, Droplets, Wind } from 'lucide-react';

export default function WeatherWidget({ weather }) {
  return (
    <section className="glass rounded-2xl p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-400">Tashqi ob-havo</p>
          <h2 className="mt-1 font-display text-xl font-bold text-white">{weather.condition}</h2>
        </div>
        <CloudSun className="h-9 w-9 text-cyber-blue" />
      </div>
      <div className="mt-6 grid grid-cols-3 gap-3">
        <div className="rounded-xl bg-white/[0.055] p-3 text-center">
          <p className="text-2xl font-bold text-white">{weather.outsideTemp}</p>
          <p className="text-xs text-slate-400">°C</p>
        </div>
        <div className="rounded-xl bg-white/[0.055] p-3 text-center">
          <Wind className="mx-auto mb-1 h-5 w-5 text-cyber-green" />
          <p className="text-sm font-semibold text-white">{weather.wind} km/h</p>
        </div>
        <div className="rounded-xl bg-white/[0.055] p-3 text-center">
          <Droplets className="mx-auto mb-1 h-5 w-5 text-cyber-blue" />
          <p className="text-sm font-semibold text-white">UV {weather.uv}</p>
        </div>
      </div>
    </section>
  );
}
