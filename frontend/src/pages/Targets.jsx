import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Globe, Server, Search } from 'lucide-react';
import api from '../utils/api';
import NetworkGraph from '../components/NetworkGraph';

const Targets = () => {
  const [targets, setTargets] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Form State
  const [newTarget, setNewTarget] = useState({
    name: '',
    target_type: 'domain',
    description: ''
  });

  // 1. Fetch Targets
  const fetchTargets = async () => {
    try {
      const response = await api.get('/targets/');
      setTargets(response.data);
    } catch (error) {
      console.error("Error fetching targets:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTargets();
  }, []);

  // 2. Add Target
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/targets/', newTarget);
      setNewTarget({ name: '', target_type: 'domain', description: '' }); // Reset form
      fetchTargets(); // Refresh list
    } catch (error) {
      alert("Error adding target. It might already exist.");
    }
  };

  // 3. Delete Target
  const handleDelete = async (id) => {
    if(!window.confirm("Are you sure you want to delete this target?")) return;
    try {
      await api.delete(`/targets/${id}`);
      fetchTargets();
    } catch (error) {
      console.error("Error deleting target:", error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Target Management</h2>
          <p className="text-gray-400 mt-1">Manage scope and assets for reconnaissance</p>
        </div>
      </div>
      
      <div className="mb-8">
        <h3 className="text-white font-bold mb-4 flex items-center gap-2">Asset Topology Map</h3>
          <NetworkGraph />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT COLUMN: Add New Target Form */}
        <div className="bg-surface border border-gray-800 p-6 rounded-xl h-fit">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Plus size={20} className="text-primary"/> Add New Asset
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Target Name (IP or Domain)</label>
              <input 
                type="text" 
                required
                placeholder="e.g. google.com"
                className="w-full bg-background border border-gray-700 rounded p-2 text-white focus:border-primary focus:outline-none"
                value={newTarget.name}
                onChange={(e) => setNewTarget({...newTarget, name: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Asset Type</label>
              <select 
                className="w-full bg-background border border-gray-700 rounded p-2 text-white focus:border-primary focus:outline-none"
                value={newTarget.target_type}
                onChange={(e) => setNewTarget({...newTarget, target_type: e.target.value})}
              >
                <option value="domain">Domain</option>
                <option value="ip">IP Address</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Description (Optional)</label>
              <textarea 
                rows="3"
                placeholder="Notes about this asset..."
                className="w-full bg-background border border-gray-700 rounded p-2 text-white focus:border-primary focus:outline-none"
                value={newTarget.description}
                onChange={(e) => setNewTarget({...newTarget, description: e.target.value})}
              />
            </div>

            <button type="submit" className="w-full bg-primary hover:bg-secondary text-black font-bold py-2 rounded transition-colors">
              Add Target
            </button>
          </form>
        </div>

        {/* RIGHT COLUMN: Target List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center gap-2 bg-surface border border-gray-800 p-2 rounded-lg mb-4">
            <Search className="text-gray-500 ml-2" size={20} />
            <input 
              type="text" 
              placeholder="Search targets..." 
              className="bg-transparent border-none focus:outline-none text-white w-full"
            />
          </div>

          {loading ? (
            <p className="text-gray-500">Loading assets...</p>
          ) : (
            <div className="grid gap-3">
              {targets.map((target) => (
                <div key={target.id} className="bg-surface border border-gray-800 p-4 rounded-lg flex justify-between items-center group hover:border-gray-600 transition-all">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-black/40 rounded border border-gray-800">
                      {target.target_type === 'domain' ? <Globe className="text-blue-400" size={20}/> : <Server className="text-purple-400" size={20}/>}
                    </div>
                    <div>
                      <h4 className="text-white font-mono font-medium">{target.name}</h4>
                      <p className="text-sm text-gray-500">{target.description || "No description provided"}</p>
                      <span className="text-xs text-gray-600 mt-1 block">Added: {new Date(target.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  <button 
                    onClick={() => handleDelete(target.id)}
                    className="p-2 text-gray-600 hover:text-danger hover:bg-white/5 rounded transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
              
              {targets.length === 0 && (
                <div className="text-center py-12 border border-dashed border-gray-800 rounded-lg">
                  <p className="text-gray-500">No targets found. Add one to get started.</p>
                </div>
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default Targets;