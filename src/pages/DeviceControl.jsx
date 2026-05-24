import { CloudRain, Droplets, Fan, Lightbulb, Power, RadioTower } from 'lucide-react';
import { motion } from 'framer-motion';
import DeviceSwitch from '../components/DeviceSwitch.jsx';
import { useGreenhouse } from '../context/GreenhouseContext.jsx';

export default function DeviceControl() {
  const { devices, setDevice, autoMode, setAutoMode, gpioPins } = useGreenhouse();

  const controls = [
    { key: 'drip_pump', label: "Tomchilatib nasos", description: "Tuproq namligi past bo'lsa ishlaydigan nasos", icon: Droplets },
    { key: 'rain_pump', label: "Yomg'irlatib nasos", description: "Kuchli sug'orish uchun alohida nasos", icon: CloudRain },
    { key: 'photo_led', label: 'Fotosintez LED', description: "Fotorezistor qorong'ilikni aniqlasa yonadi", icon: Lightbulb },
    { key: 'insect_led', label: 'Matrix LED', description: "WS2812B LED lenta - qorong'ilikda avtomatik yonadi", icon: Lightbulb },
    { key: 'cooler_1', label: 'Kuler 1', description: 'Harorat yuqori bo‘lsa ventilyatsiya', icon: Fan },
    { key: 'cooler_2', label: 'Kuler 2', description: 'Qo‘shimcha ventilyatsiya', icon: Fan },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="grid gap-6 xl:grid-cols-[1.2fr_.8fr]">
      <section className="glass rounded-2xl p-5">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.26em] text-cyber-blue">Rele paneli</p>
            <h2 className="font-display text-2xl font-bold text-white">Qurilmalarni boshqarish</h2>
          </div>
          <button
            onClick={() => setAutoMode(!autoMode)}
            className={`focus-ring flex items-center gap-2 rounded-2xl border px-4 py-3 text-sm font-bold transition ${
              autoMode ? 'border-cyber-green/40 bg-cyber-green/15 text-cyber-green' : 'border-white/10 bg-white/8 text-slate-300'
            }`}
          >
            <Power className="h-5 w-5" />
            {autoMode ? 'Avto rejim' : "Qo'l rejimi"}
          </button>
        </div>
        <div className="space-y-4">
          {controls.map((control) => (
            <DeviceSwitch
              key={control.key}
              label={control.label}
              description={control.description}
              icon={control.icon}
              enabled={devices[control.key]}
              disabled={false}
              onChange={(enabled) => setDevice(control.key, enabled)}
            />
          ))}
        </div>
      </section>

      <section className="glass rounded-2xl p-5">
        <div className="mb-5 flex items-center gap-2">
          <RadioTower className="h-5 w-5 text-cyber-green" />
          <h2 className="font-display text-xl font-bold text-white">GPIO holati</h2>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 xl:grid-cols-2">
          {gpioPins.map((pin) => (
            <div key={pin.pin} className="rounded-2xl border border-white/10 bg-white/[0.055] p-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">GPIO {pin.pin}</span>
                <span className={`h-2.5 w-2.5 rounded-full ${pin.active ? 'bg-cyber-green shadow-neon' : 'bg-slate-600'}`} />
              </div>
              <p className="mt-3 text-sm font-semibold text-white">{pin.label}</p>
              <p className="mt-1 text-xs text-slate-500">{pin.active ? 'Rele yoqilgan' : "Rele o'chirilgan"}</p>
            </div>
          ))}
        </div>
      </section>
    </motion.div>
  );
}
