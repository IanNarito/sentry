import React, { useEffect, useState } from 'react';
import { Activity, Server, AlertTriangle, ShieldCheck, Clock, CheckCircle, XCircle, Loader } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../utils/api';

// --- COMPONENTS ---

const StatCard = ({ title, value, icon, color }) => (
  <div className="bg-surface border border-gray-800 p-6 rounded-xl hover:border-gray-700 transition-colors">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-gray-400 text-sm font-medium mb-1">{title}</p>
        <h3 className="text-2xl font-bold text-white font-mono">{value}</h3>
      </div>
      <div className={`p-2 rounded-lg bg-opacity-10 ${color.bg} ${color.text}`}>
        {icon}
      </div>
    </div>
  </div>
);

const Dashboard = () => {
  const [stats, setStats] = useState({ targets: 0, activeScans: 0, vulnCount: 0, score: '-' });
  const [recentScans, setRecentScans] = useState([]);
  const [severityData, setSeverityData] = useState([]);
  const [scanTypeData, setScanTypeData] = useState([]);
  const [loading, setLoading] = useState(true);

  // COLORS for Charts
  const COLORS = { Critical: '#ff3333', High: '#ffaa00', Medium: '#ffcc00', Low: '#33cc33', Info: '#3b82f6' };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [targetsRes, scansRes, findingsRes] = await Promise.all([
          api.get('/targets/'),
          api.get('/scans/'),
          api.get('/findings/')
        ]);

        const findings = findingsRes.data;
        const scans = scansRes.data;

        // 1. Calculate Severity Distribution (for Pie Chart)
        const severityCounts = { Critical: 0, High: 0, Medium: 0, Low: 0, Info: 0 };
        findings.forEach(f => {
            const sev = f.severity || 'Info';
            if (severityCounts[sev] !== undefined) severityCounts[sev]++;
        });

        const pieData = Object.keys(severityCounts)
            .filter(key => severityCounts[key] > 0)
            .map(key => ({ name: key, value: severityCounts[key] }));

        // 2. Calculate Scan Types (for Bar Chart)
        const typeCounts = {};
        scans.forEach(s => {
            typeCounts[s.scan_type] = (typeCounts[s.scan_type] || 0) + 1;
        });
        const barData = Object.keys(typeCounts).map(key => ({ name: key, count: typeCounts[key] }));

        // 3. Calculate Security Score
        let score = 'A';
        if (severityCounts.Critical > 0) score = 'F';
        else if (severityCounts.High > 0) score = 'C';
        else if (severityCounts.Medium > 0) score = 'B';

        // 4. Update State
        setStats({
          targets: targetsRes.data.length,
          activeScans: scans.filter(s => s.status === 'running' || s.status === 'pending').length,
          vulnCount: findings.length,
          score: score
        });
        
        setSeverityData(pieData);
        setScanTypeData(barData);
        setRecentScans(scans.slice(0, 5));

      } catch (error) {
        console.error("Dashboard error:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch(status) {
      case 'completed': return <CheckCircle size={16} className="text-primary"/>;
      case 'failed': return <XCircle size={16} className="text-danger"/>;
      case 'running': return <Loader size={16} className="text-blue-400 animate-spin"/>;
      default: return <Clock size={16} className="text-gray-500"/>;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Command Center</h2>
          <p className="text-gray-400 mt-1">System Overview & Intelligence</p>
        </div>
      </div>

      {/* STAT CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Active Targets" value={stats.targets} icon={<Server size={24} />} color={{ bg: 'bg-blue-500', text: 'text-blue-400' }} />
        <StatCard title="Scans in Progress" value={stats.activeScans} icon={<Activity size={24} />} color={{ bg: 'bg-primary', text: 'text-primary' }} />
        <StatCard title="Total Findings" value={stats.vulnCount} icon={<AlertTriangle size={24} />} color={{ bg: 'bg-warning', text: 'text-warning' }} />
        <StatCard 
            title="Security Grade" 
            value={stats.score} 
            icon={<ShieldCheck size={24} />} 
            color={{ 
                bg: stats.score === 'F' ? 'bg-red-500' : stats.score === 'A' ? 'bg-green-500' : 'bg-yellow-500', 
                text: stats.score === 'F' ? 'text-red-500' : stats.score === 'A' ? 'text-green-500' : 'text-yellow-500' 
            }} 
        />
      </div>

      {/* CHARTS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        
        {/* CHART 1: VULNERABILITY DISTRIBUTION */}
        <div className="bg-surface border border-gray-800 p-6 rounded-xl">
            <h3 className="text-white font-bold mb-4">Vulnerability Severity</h3>
            <div className="h-64 w-full">
                {severityData.length === 0 ? (
                    <div className="h-full flex items-center justify-center text-gray-500 text-sm">No vulnerabilities detected</div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie data={severityData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                                {severityData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#8884d8'} />
                                ))}
                            </Pie>
                            <Tooltip contentStyle={{ backgroundColor: '#111', borderColor: '#333' }} itemStyle={{ color: '#fff' }} />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                )}
            </div>
        </div>

        {/* CHART 2: SCAN ACTIVITY */}
        <div className="bg-surface border border-gray-800 p-6 rounded-xl">
            <h3 className="text-white font-bold mb-4">Scan Module Usage</h3>
            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={scanTypeData}>
                        <XAxis dataKey="name" stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                        <Tooltip cursor={{fill: '#333'}} contentStyle={{ backgroundColor: '#111', borderColor: '#333' }} itemStyle={{ color: '#fff' }} />
                        <Bar dataKey="count" fill="#00ff41" radius={[4, 4, 0, 0]} barSize={40} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
      </div>

      {/* RECENT ACTIVITY TABLE */}
      <div className="bg-surface border border-gray-800 rounded-xl overflow-hidden mt-6">
        <div className="p-4 border-b border-gray-800 bg-white/5">
          <h3 className="font-semibold text-white">Recent Activity Log</h3>
        </div>
        <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/20 text-xs uppercase font-mono">
              <tr>
                <th className="px-6 py-3">Timestamp</th>
                <th className="px-6 py-3">Module</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Result Preview</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800 font-mono">
              {recentScans.map((scan) => (
                  <tr key={scan.id} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4">{new Date(scan.created_at).toLocaleString()}</td>
                    <td className="px-6 py-4 text-purple-400">{scan.scan_type}</td>
                    <td className="px-6 py-4 flex items-center gap-2 uppercase text-xs font-bold">
                      {getStatusIcon(scan.status)}
                      <span className={scan.status === 'completed' ? 'text-primary' : scan.status === 'failed' ? 'text-danger' : 'text-blue-400'}>
                        {scan.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-500 truncate max-w-xs">
                      {scan.result ? (scan.result.url || scan.result.raw_output || "Data captured") : "..."}
                    </td>
                  </tr>
                ))}
            </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;