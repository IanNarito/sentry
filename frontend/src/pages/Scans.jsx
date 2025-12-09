import React, { useState, useEffect } from 'react';
import { Play, Clock, CheckCircle, XCircle, Terminal } from 'lucide-react';
import api from '../utils/api';

const Scans = () => {
  const [scans, setScans] = useState([]);
  const [targets, setTargets] = useState([]);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [loading, setLoading] = useState(true);
  
  // NEW: State for the scan type (DNS or NMAP)
  const [scanType, setScanType] = useState('DNS');

  // Fetch Data
  const fetchData = async () => {
    try {
      const [scansRes, targetsRes] = await Promise.all([
        api.get('/scans/'),
        api.get('/targets/')
      ]);
      setScans(scansRes.data);
      setTargets(targetsRes.data);
      
      // Select the first target by default if none selected
      if (targetsRes.data.length > 0 && !selectedTarget) {
        setSelectedTarget(targetsRes.data[0].id);
      }
    } catch (error) {
      console.error("Error loading scan data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 5 seconds
    const interval = setInterval(() => {
        api.get('/scans/').then(res => setScans(res.data));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Handle Start Scan
  const handleStartScan = async () => {
    if (!selectedTarget) return;
    try {
      await api.post('/scans/', {
        target_id: selectedTarget,
        scan_type: scanType // <-- Use the selected type (DNS or NMAP)
      });
      fetchData(); // Refresh immediately
    } catch (error) {
      alert("Failed to start scan");
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-white">Scan Operations</h2>
        <p className="text-gray-400 mt-1">Execute reconnaissance modules and review logs</p>
      </div>

      {/* LAUNCH PAD */}
      <div className="bg-surface border border-gray-800 p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Terminal size={20} className="text-primary"/> New Mission
        </h3>
        <div className="flex gap-4 items-end">
            <div className="flex-1">
                <label className="block text-sm text-gray-400 mb-2">Select Target</label>
                <select 
                    className="w-full bg-background border border-gray-700 rounded p-3 text-white focus:border-primary focus:outline-none"
                    value={selectedTarget}
                    onChange={(e) => setSelectedTarget(e.target.value)}
                >
                    {targets.map(t => (
                        <option key={t.id} value={t.id}>{t.name} ({t.target_type})</option>
                    ))}
                </select>
            </div>
            
            <div className="flex-1">
                <label className="block text-sm text-gray-400 mb-2">Scan Module</label>
                <select 
                    className="w-full bg-background border border-gray-700 rounded p-3 text-white focus:border-primary focus:outline-none"
                    value={scanType}
                    onChange={(e) => setScanType(e.target.value)}
                >
                    <option value="DNS">DNS Enumeration (Basic)</option>
                    <option value="FUZZ">Directory Fuzzing (Active)</option>
                    <option value="NMAP">Nmap Port Scan (Top 100 Ports)</option>
                    <option value="SUBDOMAIN">Subdomain Discovery (Passive)</option>
                    <option value="WEB">Web Recon & Headers</option>
                    <option value="WHOIS">Whois Lookup (Registration)</option>
                    <option value="WAF">WAF Detection (Firewall)</option>
                    <option value="SSL">SSL/TLS Security Audit</option>
                    <option value="API">API Discovery (Swagger/Docs)</option>
                    <option value="CVE">CVE Vulnerability Mapping</option>
                    <option value="HONEYPOT">Honeypot Detection (Trap Check)</option>
                </select>
            </div>

            <button 
                onClick={handleStartScan}
                className="bg-primary hover:bg-secondary text-black font-bold py-3 px-8 rounded flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(0,255,65,0.2)]"
            >
                <Play size={18} fill="black" /> Launch Scan
            </button>
        </div>
      </div>

      {/* HISTORY TABLE */}
      <div className="bg-surface border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-800 bg-white/5">
            <h3 className="font-semibold text-white">Mission History</h3>
        </div>
        <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/20 text-xs uppercase font-mono">
                <tr>
                    <th className="px-6 py-3">ID</th>
                    <th className="px-6 py-3">Timestamp</th>
                    <th className="px-6 py-3">Module</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3">Output Data</th>
                </tr>
            </thead>
            <tbody className="divide-y divide-gray-800 font-mono">
                {scans.map((scan) => (
                    <tr key={scan.id} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4">#{scan.id}</td>
                        <td className="px-6 py-4">{new Date(scan.created_at).toLocaleString()}</td>
                        <td className="px-6 py-4 text-purple-400">{scan.scan_type}</td>
                        <td className="px-6 py-4">
                            {scan.status === 'completed' && <span className="flex items-center gap-2 text-primary"><CheckCircle size={14}/> DONE</span>}
                            {scan.status === 'running' && <span className="flex items-center gap-2 text-blue-400 animate-pulse"><Clock size={14}/> RUNNING</span>}
                            {scan.status === 'failed' && <span className="flex items-center gap-2 text-danger"><XCircle size={14}/> FAILED</span>}
                            {scan.status === 'pending' && <span className="flex items-center gap-2 text-gray-500"><Clock size={14}/> QUEUED</span>}
                        </td>
                        <td className="px-6 py-4">
                            <div className="max-w-md overflow-x-auto whitespace-pre bg-black/30 p-2 rounded border border-gray-800 text-xs font-mono">
                                {scan.result ? JSON.stringify(scan.result, null, 2) : '...'}
                            </div>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
      </div>
    </div>
  );
};

export default Scans;