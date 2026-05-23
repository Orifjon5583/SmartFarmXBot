import { useState } from 'react';
import { Bell, Router, Thermometer, Users, Waves } from 'lucide-react';
import { motion } from 'framer-motion';
import { useGreenhouse } from '../context/GreenhouseContext.jsx';

function SettingCard({ title, icon: Icon, children }) {
  return (
    <section className="glass rounded-2xl p-5">
      <div className="mb-5 flex items-center gap-2">
        <Icon className="h-5 w-5 text-cyber-green" />
        <h2 className="font-display text-xl font-bold text-white">{title}</h2>
      </div>
      {children}
    </section>
  );
}

export default function Settings() {
  const { thresholds, setThresholds } = useGreenhouse();
  const [connection, setConnection] = useState(() => {
    const saved = localStorage.getItem('greenhouse_connection');
    return saved
      ? JSON.parse(saved)
      : { host: '192.168.1.42', gpioProfile: 'BCM', apiUrl: 'http://raspberrypi.local:5000' };
  });
  const [connectionStatus, setConnectionStatus] = useState('');

  const updateConnection = (field, value) => {
    setConnection((current) => ({ ...current, [field]: value }));
    setConnectionStatus('');
  };

  const saveConnection = () => {
    localStorage.setItem('greenhouse_connection', JSON.stringify(connection));
    setConnectionStatus('Raspberry Pi ulanish sozlamalari saqlandi.');
  };

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="grid gap-6 xl:grid-cols-2">
      <SettingCard title="Harorat chegarasi" icon={Thermometer}>
        <label className="block">
          <div className="mb-3 flex justify-between text-sm">
            <span className="text-slate-300">Kulerlar ishga tushishi</span>
            <span className="text-cyber-green">{thresholds.temperature} C</span>
          </div>
          <input
            type="range"
            min="18"
            max="42"
            value={thresholds.temperature}
            onChange={(event) => setThresholds((current) => ({ ...current, temperature: Number(event.target.value) }))}
            className="w-full accent-cyber-green"
          />
        </label>
      </SettingCard>

      <SettingCard title="Namlik chegarasi" icon={Waves}>
        <label className="block">
          <div className="mb-3 flex justify-between text-sm">
            <span className="text-slate-300">Nasos ishga tushishi</span>
            <span className="text-cyber-green">{thresholds.moisture}%</span>
          </div>
          <input
            type="range"
            min="15"
            max="75"
            value={thresholds.moisture}
            onChange={(event) => setThresholds((current) => ({ ...current, moisture: Number(event.target.value) }))}
            className="w-full accent-cyber-green"
          />
        </label>
      </SettingCard>

      <SettingCard title="Bildirishnoma sozlamalari" icon={Bell}>
        <div className="space-y-3">
          {['Muhim sensor ogohlantirishlari', 'Qurilma holati o‘zgarishlari', 'Kunlik agro hisobot'].map((label) => (
            <label key={label} className="flex items-center justify-between rounded-xl bg-white/[0.055] p-4">
              <span className="text-sm font-medium text-slate-200">{label}</span>
              <input type="checkbox" defaultChecked className="h-5 w-5 accent-cyber-green" />
            </label>
          ))}
        </div>
      </SettingCard>

      <SettingCard title="Raspberry Pi ulanishi" icon={Router}>
        <div className="grid gap-3 sm:grid-cols-2">
          <input
            className="focus-ring rounded-xl border border-white/10 bg-white/8 px-4 py-3 text-white"
            placeholder="192.168.1.42"
            value={connection.host}
            onChange={(event) => updateConnection('host', event.target.value)}
          />
          <input
            className="focus-ring rounded-xl border border-white/10 bg-white/8 px-4 py-3 text-white"
            placeholder="GPIO profili: BCM"
            value={connection.gpioProfile}
            onChange={(event) => updateConnection('gpioProfile', event.target.value)}
          />
          <input
            className="focus-ring rounded-xl border border-white/10 bg-white/8 px-4 py-3 text-white sm:col-span-2"
            placeholder="Flask API URL: http://raspberrypi.local:5000"
            value={connection.apiUrl}
            onChange={(event) => updateConnection('apiUrl', event.target.value)}
          />
          <button
            type="button"
            onClick={saveConnection}
            className="focus-ring rounded-xl bg-cyber-green px-4 py-3 font-bold text-night sm:col-span-2"
          >
            Ulanish sozlamalarini saqlash
          </button>
          {connectionStatus && (
            <p className="rounded-xl border border-cyber-green/20 bg-cyber-green/10 px-4 py-3 text-sm text-cyber-green sm:col-span-2">
              {connectionStatus}
            </p>
          )}
        </div>
      </SettingCard>

      <SettingCard title="Foydalanuvchilar" icon={Users}>
        <div className="space-y-3">
          {['Issiqxona administratori', 'Ferma operatori', 'Kuzatuvchi'].map((user, index) => (
            <div key={user} className="flex items-center justify-between rounded-xl bg-white/[0.055] p-4">
              <div>
                <p className="font-semibold text-white">{user}</p>
                <p className="text-xs text-slate-500">{index === 0 ? 'To‘liq ruxsat' : index === 1 ? 'Boshqaruv ruxsati' : 'Faqat ko‘rish'}</p>
              </div>
              <button className="focus-ring rounded-lg border border-white/10 px-3 py-2 text-sm text-slate-300">Tahrirlash</button>
            </div>
          ))}
        </div>
      </SettingCard>
    </motion.div>
  );
}
