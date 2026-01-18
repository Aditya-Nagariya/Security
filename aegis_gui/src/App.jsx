import React, { useState } from 'react';
import Dashboard from './components/Dashboard';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="flex h-screen w-full bg-void-950 text-slate-200 overflow-hidden font-sans selection:bg-cyan-500/30">
      
      {/* GLASS SIDEBAR */}
      <aside className="w-64 h-full flex flex-col glass-panel z-20 shadow-glass">
        <div className="p-8 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-indigo-600 shadow-neon shadow-cyan-500/50"></div>
          <h1 className="text-2xl font-bold tracking-tight text-white">AEGIS</h1>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          <SidebarItem 
            active={activeTab === 'dashboard'} 
            onClick={() => setActiveTab('dashboard')} 
            icon="📊" 
            label="Overview" 
          />
          <SidebarItem 
            active={activeTab === 'scan'} 
            onClick={() => setActiveTab('scan')} 
            icon="🛡️" 
            label="Security Scan" 
          />
          <SidebarItem 
            active={activeTab === 'network'} 
            onClick={() => setActiveTab('network')} 
            icon="🌐" 
            label="Network" 
          />
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-void-900/50 border border-white/5">
            <div className="w-2 h-2 rounded-full bg-green-500 shadow-neon shadow-green-500"></div>
            <span className="text-xs font-mono text-slate-400">System Active</span>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 h-full overflow-y-auto relative">
        {/* Background Ambient Glow */}
        <div className="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-indigo-900/20 to-transparent pointer-events-none"></div>
        
        <div className="p-10 relative z-10">
          <header className="mb-8 flex justify-between items-end">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Command Center</h2>
              <p className="text-slate-400">Real-time telemetry and threat suppression.</p>
            </div>
            <button className="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-void-950 font-bold transition-all duration-300 shadow-neon shadow-cyan-500/20 hover:shadow-cyan-500/40 transform hover:-translate-y-0.5">
              Initiate Scan
            </button>
          </header>

          {activeTab === 'dashboard' && <Dashboard />}
        </div>
      </main>
    </div>
  );
}

const SidebarItem = ({ active, onClick, icon, label }) => (
  <button 
    onClick={onClick}
    className={`w-full flex items-center gap-4 px-4 py-3.5 rounded-xl transition-all duration-200 group ${
      active 
        ? 'bg-gradient-to-r from-indigo-600/20 to-cyan-500/10 border border-indigo-500/30 text-white' 
        : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
    }`}
  >
    <span className={`text-xl filter ${active ? 'grayscale-0' : 'grayscale group-hover:grayscale-0'} transition-all`}>
      {icon}
    </span>
    <span className="font-medium">{label}</span>
    {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-neon shadow-cyan-400"></div>}
  </button>
);

export default App;
