import { useState } from 'react';
import { Bell, Bot, Router, Thermometer, Users, Waves } from 'lucide-react';
import { motion } from 'framer-motion';
import { useGreenhouse } from '../context/GreenhouseContext.jsx';
import { greenhouseApi } from '../services/api.js';

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
  const [telegram, setTelegram] = useState(() => {
    const saved = localStorage.getItem('greenhouse_telegram');
    return saved ? JSON.parse(saved) : { token: '', chatId: '' };
  });
  const [telegramStatus, setTelegramStatus] = useState('');
  const [isCheckingTelegram, setIsCheckingTelegram] = useState(false);
  const [isSavingTelegram, setIsSavingTelegram] = useState(false);
  const [isSendingTelegram, setIsSendingTelegram] = useState(false);
  const [connection, setConnection] = useState(() => {
    const saved = localStorage.getItem('greenhouse_connection');
    return saved
      ? JSON.parse(saved)
      : { host: '192.168.1.42', gpioProfile: 'BCM', apiUrl: 'http://raspberrypi.local:5000' };
  });
  const [connectionStatus, setConnectionStatus] = useState('');

  const updateTelegram = (field, value) => {
    setTelegram((current) => ({ ...current, [field]: value }));
    setTelegramStatus('');
  };

  const saveTelegram = async () => {
    if (!telegram.token.trim() || !telegram.chatId.trim()) {
      setTelegramStatus('Bot tokeni va Chat ID ni kiriting.');
      return;
    }

    setIsSavingTelegram(true);
    setTelegramStatus('Telegram sozlamalari saqlanmoqda...');
    try {
      const result = await greenhouseApi.saveTelegramSettings({ ...telegram, enabled: true });
      localStorage.setItem('greenhouse_telegram', JSON.stringify(telegram));
      setTelegramStatus(result.message || 'Telegram sozlamalari saqlandi.');
    } catch (error) {
      setTelegramStatus(`Saqlashda xato: ${error.message}`);
    } finally {
      setIsSavingTelegram(false);
    }
  };

  const verifyTelegram = async () => {
    if (!telegram.token.trim() || !telegram.chatId.trim()) {
      setTelegramStatus('Bot tokeni va Chat ID ni kiriting.');
      return;
    }

    setIsCheckingTelegram(true);
    setTelegramStatus('Telegram ulanishi tekshirilmoqda...');
    try {
      const result = await greenhouseApi.verifyTelegram(telegram);
      localStorage.setItem('greenhouse_telegram', JSON.stringify(telegram));
      setTelegramStatus(result.message || 'Telegram ulanishi muvaffaqiyatli tekshirildi.');
    } catch (error) {
      setTelegramStatus(`Telegram tekshiruvida xato: ${error.message}`);
    } finally {
      setIsCheckingTelegram(false);
    }
  };

  const sendDemoTelegramAlert = async () => {
    setIsSendingTelegram(true);
    setTelegramStatus('Test bildirishnoma yuborilmoqda...');
    try {
      const result = await greenhouseApi.sendTelegramNotification(
        'Issiqxona Nexus: bu test bildirishnoma. Sensorlar va qurilmalar monitoringi faol.',
      );
      setTelegramStatus(result.message || 'Test bildirishnoma yuborildi.');
    } catch (error) {
      setTelegramStatus(`Bildirishnoma xatosi: ${error.message}`);
    } finally {
      setIsSendingTelegram(false);
    }
  };

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
            <span className="text-slate-300">Ventilyator ishga tushishi</span>
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

      <SettingCard title="Telegram bot sozlamasi" icon={Bot}>
        <div className="space-y-3">
          <input
            className="focus-ring w-full rounded-xl border border-white/10 bg-white/8 px-4 py-3 text-white"
            placeholder="Bot tokeni"
            type="password"
            value={telegram.token}
            onChange={(event) => updateTelegram('token', event.target.value)}
          />
          <input
            className="focus-ring w-full rounded-xl border border-white/10 bg-white/8 px-4 py-3 text-white"
            placeholder="Chat ID"
            value={telegram.chatId}
            onChange={(event) => updateTelegram('chatId', event.target.value)}
          />
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={verifyTelegram}
              disabled={isCheckingTelegram}
              className="focus-ring rounded-xl bg-cyber-green px-4 py-3 font-bold text-night disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isCheckingTelegram ? 'Tekshirilmoqda...' : 'Telegram ulanishini tekshirish'}
            </button>
            <button
              type="button"
              onClick={saveTelegram}
              disabled={isSavingTelegram}
              className="focus-ring rounded-xl border border-white/10 bg-white/8 px-4 py-3 font-bold text-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSavingTelegram ? 'Saqlanmoqda...' : 'Saqlash'}
            </button>
            <button
              type="button"
              onClick={sendDemoTelegramAlert}
              disabled={isSendingTelegram}
              className="focus-ring rounded-xl border border-cyber-blue/30 bg-cyber-blue/10 px-4 py-3 font-bold text-cyber-blue disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSendingTelegram ? 'Yuborilmoqda...' : 'Test xabar'}
            </button>
          </div>
          {telegramStatus && (
            <p className="rounded-xl border border-cyber-green/20 bg-cyber-green/10 px-4 py-3 text-sm text-cyber-green">
              {telegramStatus}
            </p>
          )}
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
