import React, { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle, Search, Download, FileText } from 'lucide-react';
import api from '../utils/api';

const Findings = () => {
  const [findings, setFindings] = useState([]);
  const [targets, setTargets] = useState([]);
  const [selectedExportTarget, setSelectedExportTarget] = useState(''); // Track selection
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [findingsRes, targetsRes] = await Promise.all([
          api.get('/findings/'),
          api.get('/targets/')
        ]);
        setFindings(findingsRes.data);
        setTargets(targetsRes.data);
        
        // Default to the first target if available
        if (targetsRes.data.length > 0) {
            setSelectedExportTarget(targetsRes.data[0].id);
        }
      } catch (error) {
        console.error("Error loading data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleExport = (type) => {
    if (!selectedExportTarget) {
        alert("Please select a target to export.");
        return;
    }
    const url = `http://localhost:8000/api/v1/reports/${selectedExportTarget}?format=${type}`;
    window.open(url, '_blank');
  };

  const getSeverityColor = (severity) => {
    switch(severity.toLowerCase()) {
      case 'critical': return 'text-purple-500 border-purple-500 bg-purple-500/10';
      case 'high': return 'text-red-500 border-red-500 bg-red-500/10';
      case 'medium': return 'text-orange-500 border-orange-500 bg-orange-500/10';
      case 'low': return 'text-yellow-500 border-yellow-500 bg-yellow-500/10';
      default: return 'text-blue-500 border-blue-500 bg-blue-500/10';
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Security Findings</h2>
          <p className="text-gray-400 mt-1">Vulnerabilities detected during reconnaissance</p>
        </div>

        {/* EXPORT CONTROLS */}
        <div className="flex items-center gap-3 bg-surface border border-gray-800 p-2 rounded-lg">
            <span className="text-xs text-gray-500 font-bold uppercase px-2">Export Report:</span>
            
            <select 
                className="bg-black/50 border border-gray-700 rounded p-2 text-sm text-white focus:border-primary focus:outline-none"
                value={selectedExportTarget}
                onChange={(e) => setSelectedExportTarget(e.target.value)}
            >
                {targets.map(t => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                ))}
            </select>

            <div className="h-6 w-px bg-gray-700 mx-1"></div>

            <button 
                onClick={() => handleExport('html')}
                className="hover:bg-white/10 text-gray-300 p-2 rounded transition-colors"
                title="View HTML"
            >
                <FileText size={18} />
            </button>
            <button 
                onClick={() => handleExport('pdf')}
                className="bg-primary hover:bg-secondary text-black p-2 rounded transition-colors shadow-lg shadow-primary/20"
                title="Download PDF"
            >
                <Download size={18} />
            </button>
        </div>
      </div>

      {/* STATS BAR */}
      <div className="bg-surface border border-gray-800 p-4 rounded-xl mb-6 flex gap-4 overflow-x-auto">
        <div className="flex-1 relative min-w-[200px]">
            <Search className="absolute left-3 top-3 text-gray-500" size={20}/>
            <input 
                type="text" 
                placeholder="Search vulnerabilities..." 
                className="w-full bg-background border border-gray-700 rounded pl-10 p-2 text-white focus:border-primary focus:outline-none"
            />
        </div>
        <div className="flex gap-2">
            <div className="px-4 py-2 bg-red-500/10 border border-red-500 text-red-500 rounded font-bold text-sm flex items-center gap-2 whitespace-nowrap">
                High: {findings.filter(f => f.severity === 'High').length}
            </div>
            <div className="px-4 py-2 bg-orange-500/10 border border-orange-500 text-orange-500 rounded font-bold text-sm flex items-center gap-2 whitespace-nowrap">
                Medium: {findings.filter(f => f.severity === 'Medium').length}
            </div>
        </div>
      </div>

      {/* FINDINGS LIST */}
      <div className="space-y-4">
        {loading ? <p className="text-gray-500">Loading intelligence...</p> : 
         findings.length === 0 ? (
            <div className="text-center py-12 border border-dashed border-gray-800 rounded-lg">
                <ShieldAlert size={48} className="mx-auto text-gray-600 mb-4"/>
                <p className="text-gray-500">No vulnerabilities detected yet.</p>
                <p className="text-sm text-gray-600">Run an Nmap or SSL scan to populate this list.</p>
            </div>
         ) : (
            findings.map((finding) => (
                <div key={finding.id} className="bg-surface border border-gray-800 p-6 rounded-xl hover:border-gray-600 transition-all group">
                    <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-3">
                            <span className={`px-3 py-1 rounded text-xs font-bold uppercase border ${getSeverityColor(finding.severity)}`}>
                                {finding.severity}
                            </span>
                            <h3 className="text-lg font-bold text-white font-mono">{finding.title}</h3>
                        </div>
                        <span className="text-xs text-gray-500 font-mono">
                            {new Date(finding.created_at).toLocaleDateString()}
                        </span>
                    </div>
                    
                    <p className="text-gray-400 text-sm mb-4">{finding.description}</p>
                    
                    {/* Remediation Box */}
                    <div className="bg-black/30 p-3 rounded border border-gray-800">
                        <p className="text-xs text-primary font-mono flex items-center gap-2">
                            <CheckCircle size={12}/> REMEDIATION:
                        </p>
                        <p className="text-xs text-gray-500 mt-1 pl-5">
                            {finding.remediation || "Restrict access via firewall or disable service if not needed."}
                        </p>
                    </div>
                </div>
            ))
         )}
      </div>
    </div>
  );
};

export default Findings;