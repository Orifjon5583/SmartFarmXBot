import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { motion } from 'framer-motion';
import RealtimeChart from '../components/RealtimeChart.jsx';
import { useGreenhouse } from '../context/GreenhouseContext.jsx';

export default function Analytics() {
  const { history, activityLogs } = useGreenhouse();

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-2">
        <RealtimeChart data={history} dataKey="temperature" color="#38f2a1" label="Harorat tarixi" />
        <RealtimeChart data={history} dataKey="humidity" color="#35c7ff" label="Namlik trendi" />
        <RealtimeChart data={history} dataKey="soil" color="#b8ff5b" label="Tuproq namligi grafigi" />
        <section className="glass rounded-2xl p-5">
          <h2 className="mb-4 font-display text-xl font-bold text-white">Energiya sarfi</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={history}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: 'rgba(6,16,20,.92)', border: '1px solid rgba(255,255,255,.12)', borderRadius: 12 }} />
                <Bar dataKey="energy" radius={[8, 8, 0, 0]} fill="#35c7ff" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      <section className="grid gap-6 xl:grid-cols-[1.25fr_.75fr]">
        <div className="glass rounded-2xl p-5">
          <h2 className="mb-4 font-display text-xl font-bold text-white">Sensorlar o‘zaro bog‘lanishi</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: 'rgba(6,16,20,.92)', border: '1px solid rgba(255,255,255,.12)', borderRadius: 12 }} />
                <Legend />
                <Line dot={false} strokeWidth={3} dataKey="temperature" stroke="#38f2a1" />
                <Line dot={false} strokeWidth={3} dataKey="humidity" stroke="#35c7ff" />
                <Line dot={false} strokeWidth={3} dataKey="soil" stroke="#b8ff5b" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass rounded-2xl p-5">
          <h2 className="mb-4 font-display text-xl font-bold text-white">Qurilmalar jurnali</h2>
          <div className="space-y-3">
            {activityLogs.map((log) => (
              <div key={`${log.time}-${log.device}`} className="rounded-xl border border-white/10 bg-white/[0.055] p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-white">{log.device}</p>
                  <span className="text-xs text-slate-500">{log.time}</span>
                </div>
                <p className="mt-1 text-sm text-slate-300">{log.event}</p>
                <p className="mt-2 text-xs text-cyber-green">{log.value}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </motion.div>
  );
}
