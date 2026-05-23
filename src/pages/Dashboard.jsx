import { Activity, Droplets, Gauge, Lightbulb, Thermometer, Waves } from 'lucide-react';
import { motion } from 'framer-motion';
import AlertPanel from '../components/AlertPanel.jsx';
import RealtimeChart from '../components/RealtimeChart.jsx';
import SensorCard from '../components/SensorCard.jsx';
import StatisticsCards from '../components/StatisticsCards.jsx';
import WeatherWidget from '../components/WeatherWidget.jsx';
import { useGreenhouse } from '../context/GreenhouseContext.jsx';
import { healthScore } from '../utils/automation.js';

export default function Dashboard() {
  const { sensors, history, alerts, devices, status } = useGreenhouse();
  const score = healthScore(sensors);

  const stats = [
    { label: 'Avtomatika holati', value: `${score}%`, delta: 'Bugun +3.8%' },
    { label: 'Pi ishlash vaqti', value: status.uptime || '18 kun 06 soat', delta: 'Uzilish yo‘q' },
    { label: 'Energiya sarfi', value: '2.7 kWh', delta: 'Kecha bilan -8%' },
    { label: 'Rele kechikishi', value: '32 ms', delta: 'GPIO barqaror' },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SensorCard title="Harorat" value={sensors.temperature} unit="°C" icon={Thermometer} color="text-cyber-red" trend="+1.2" detail="O‘rtacha ko‘rsatkich" />
        <SensorCard title="Namlik" value={sensors.humidity} unit="%" icon={Droplets} color="text-cyber-blue" trend="+4%" detail="Havo namligi" />
        <SensorCard title="Tuproq namligi" value={sensors.soilMoisture} unit="%" icon={Waves} color="text-cyber-green" trend="-2%" detail="Ildiz zonasi" />
        <SensorCard title="Yorug‘lik" value={sensors.light} unit="lux" icon={Lightbulb} color="text-cyber-amber" trend="+12%" detail="PAR taxmini" />
      </section>

      <StatisticsCards items={stats} />

      <section className="grid gap-6 xl:grid-cols-[1.7fr_1fr]">
        <RealtimeChart data={history} dataKey="temperature" color="#38f2a1" label="Harorat tarixi" />
        <div className="space-y-6">
          <WeatherWidget weather={sensors.weather} />
          <div className="glass rounded-2xl p-5">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-xl font-bold text-white">Qurilmalar holati</h2>
              <Gauge className="h-5 w-5 text-cyber-green" />
            </div>
            <div className="space-y-3">
              {Object.entries(devices).map(([device, enabled]) => (
                <div key={device} className="flex items-center justify-between rounded-xl bg-white/[0.055] px-4 py-3">
                  <span className="capitalize text-slate-300">
                    {{
                      drip: 'tomchilatib',
                      rain: "yomg'irlatib",
                      cooler: '2 ta kuler',
                      led: 'LED chiroq',
                    }[device] || device}
                  </span>
                  <span className={`flex items-center gap-2 text-sm font-semibold ${enabled ? 'text-cyber-green' : 'text-slate-500'}`}>
                    <span className={`h-2 w-2 rounded-full ${enabled ? 'bg-cyber-green shadow-neon' : 'bg-slate-600'}`} />
                    {enabled ? 'Ishlayapti' : 'Kutish'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <AlertPanel alerts={alerts} />
        <div className="glass rounded-2xl p-5">
          <div className="mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-cyber-blue" />
            <h2 className="font-display text-xl font-bold text-white">Tizim salomatligi</h2>
          </div>
          <div className="space-y-4">
            {['Flask API', 'Socket oqimi', 'SQLite tarixi', 'GPIO relelari'].map((item, index) => (
              <div key={item}>
                <div className="mb-2 flex justify-between text-sm">
                  <span className="text-slate-300">{item}</span>
                  <span className="text-cyber-green">{96 - index * 3}%</span>
                </div>
                <div className="h-2 rounded-full bg-white/10">
                  <div className="h-2 rounded-full bg-gradient-to-r from-cyber-green to-cyber-blue" style={{ width: `${96 - index * 3}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </motion.div>
  );
}
