import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export default function RealtimeChart({ data, dataKey = 'temperature', color = '#38f2a1', label = 'Harorat' }) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">Real vaqt telemetriyasi</p>
          <h2 className="font-display text-xl font-bold text-white">{label}</h2>
        </div>
        <span className="rounded-full border border-cyber-green/20 bg-cyber-green/10 px-3 py-1 text-xs font-semibold text-cyber-green">
          Jonli
        </span>
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.45} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} width={36} />
            <Tooltip
              contentStyle={{
                background: 'rgba(6,16,20,0.92)',
                border: '1px solid rgba(255,255,255,0.12)',
                borderRadius: 12,
                color: '#e8fbf4',
              }}
            />
            <Area type="monotone" dataKey={dataKey} stroke={color} strokeWidth={3} fill={`url(#gradient-${dataKey})`} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
