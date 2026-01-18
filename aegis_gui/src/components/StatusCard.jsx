import React from 'react';

export default function StatusCard({ title, value, trend, trendUp, color = 'indigo', chartData = [] }) {
  // Map color names to Tailwind classes
  const colors = {
    indigo: { text: 'text-indigo-400', bg: 'bg-indigo-500', shadow: 'shadow-indigo-500/20' },
    cyan: { text: 'text-cyan-400', bg: 'bg-cyan-500', shadow: 'shadow-cyan-500/20' },
    emerald: { text: 'text-emerald-400', bg: 'bg-emerald-500', shadow: 'shadow-emerald-500/20' },
  };

  const theme = colors[color] || colors.indigo;

  return (
    <div className={`glass-panel p-6 rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all duration-300 hover:transform hover:-translate-y-1 ${theme.shadow} hover:shadow-2xl`}>
      {/* Background Decor */}
      <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full ${theme.bg} opacity-10 blur-2xl group-hover:opacity-20 transition-opacity duration-500`}></div>

      <div className="relative z-10">
        <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">{title}</h3>
        <div className="flex items-baseline gap-3">
          <span className="text-3xl font-bold text-white tracking-tight">{value}</span>
          {trend && (
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              trendUp === true ? 'bg-red-500/20 text-red-400' : 
              trendUp === false ? 'bg-emerald-500/20 text-emerald-400' : 
              'bg-slate-700 text-slate-300'
            }`}>
              {trend}
            </span>
          )}
        </div>
      </div>

      {/* Micro Chart Visualization (CSS Bars) */}
      <div className="flex items-end gap-1 h-8 mt-6 opacity-50 group-hover:opacity-100 transition-opacity">
        {chartData.map((height, i) => (
          <div 
            key={i} 
            style={{ height: `${height}%` }} 
            className={`flex-1 rounded-t-sm ${theme.bg} transition-all duration-500`}
          ></div>
        ))}
      </div>
    </div>
  );
}
