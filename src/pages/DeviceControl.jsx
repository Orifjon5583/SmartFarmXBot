import { Camera, Fan, Lightbulb, Power, RadioTower, Waves } from 'lucide-react';
import { motion } from 'framer-motion';
import DeviceSwitch from '../components/DeviceSwitch.jsx';
import { useGreenhouse } from '../context/GreenhouseContext.jsx';

export default function DeviceControl() {
  const { devices, setDevice, autoMode, setAutoMode, gpioPins } = useGreenhouse();

  const controls = [
    { key: 'fan', label: 'Ventilyator', description: 'Haroratni chiqarish uchun GPIO relesi', icon: Fan },
    { key: 'pump', label: 'Suv nasosi', description: 'Impulsli sug‘orish nasosi boshqaruvi', icon: Waves },
    { key: 'light', label: 'O‘stirish chirog‘i', description: 'LED spektrli yoritish tizimi', icon: Lightbulb },
    { key: 'camera', label: 'Kamera moduli', description: 'CSI/USB monitoring oqimi', icon: Camera },
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
            {autoMode ? 'Avto rejim' : 'Qo‘l rejimi'}
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
              disabled={autoMode && control.key !== 'camera'}
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
              <p className="mt-1 text-xs text-slate-500">{pin.active ? 'Signal yuqori' : 'Signal past'}</p>
            </div>
          ))}
        </div>
      </section>
    </motion.div>
  );
}
