import React from 'react';
import StatusCard from './StatusCard';

export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* METRICS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatusCard 
          title="CPU Load" 
          value="12%" 
          trend="+2%" 
          trendUp={true}
          color="indigo"
          chartData={[20, 45, 28, 80, 50, 43, 12]} 
        />
        <StatusCard 
          title="Memory Usage" 
          value="4.2 GB" 
          trend="-0.5%" 
          trendUp={false}
          color="cyan"
          chartData={[60, 55, 58, 52, 48, 50, 55]} 
        />
        <StatusCard 
          title="Threat Level" 
          value="LOW" 
          trend="Secure" 
          color="emerald"
          chartData={[10, 10, 5, 20, 5, 5, 0]} 
        />
      </div>

      {/* CONSOLE AREA */}
      <div className="glass-panel rounded-2xl p-1 shadow-2xl">
        <div className="bg-void-950/80 rounded-xl p-6 font-mono text-sm h-64 overflow-hidden border border-white/5">
          <div className="flex items-center gap-2 mb-4 text-slate-500 text-xs uppercase tracking-wider">
            <span className="w-2 h-2 bg-slate-500 rounded-full animate-pulse"></span>
            System Log Stream
          </div>
          <div className="space-y-2">
            <LogLine time="10:42:01" level="INFO" msg="Aegis Daemon initialized successfully." />
            <LogLine time="10:42:02" level="INFO" msg="Connected to local threat database (v4.2.0)." />
            <LogLine time="10:42:05" level="WARN" msg="Port 8080 is open to external traffic." />
            <LogLine time="10:42:05" level="SUCCESS" msg="Firewall rules updated. Traffic secured." color="text-green-400" />
            <div className="flex items-center gap-2 mt-2 text-cyan-400 animate-pulse">
              <span>_</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const LogLine = ({ time, level, msg, color = 'text-slate-300' }) => (
  <div className="flex items-start gap-4">
    <span className="text-slate-600 shrink-0">{time}</span>
    <span className={`shrink-0 w-16 ${
      level === 'INFO' ? 'text-blue-400' : 
      level === 'WARN' ? 'text-yellow-400' : 
      'text-green-400'
    }`}>{level}</span>
    <span className={color}>{msg}</span>
  </div>
);
