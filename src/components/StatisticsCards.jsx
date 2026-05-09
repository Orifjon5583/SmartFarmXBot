export default function StatisticsCards({ items }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="glass-soft rounded-2xl p-4">
          <p className="text-sm text-slate-400">{item.label}</p>
          <p className="mt-2 font-display text-2xl font-bold text-white">{item.value}</p>
          <p className="mt-1 text-sm text-cyber-green">{item.delta}</p>
        </div>
      ))}
    </div>
  );
}
