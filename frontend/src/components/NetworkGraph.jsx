import React, { useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import api from '../utils/api';

const NetworkGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  // Removed 'ready' state and 'ref' for now to isolate the crash

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [targetsRes, scansRes] = await Promise.all([
          api.get('/targets/'),
          api.get('/scans/')
        ]);

        const nodes = [];
        const links = [];
        const addedNodes = new Set();

        const addNode = (id, group, val) => {
            if (!addedNodes.has(id)) {
                nodes.push({ id, group, val });
                addedNodes.add(id);
            }
        };

        // 1. Add Main Targets
        targetsRes.data.forEach(t => addNode(t.name, 'target', 20));

        // 2. Process Scans
        scansRes.data.forEach(scan => {
            const targetName = scan.target ? scan.target.name : null;
            if (!targetName) return;

            addNode(targetName, 'target', 20);

            if (scan.scan_type === 'SUBDOMAIN' && scan.result && scan.result.subdomains) {
                scan.result.subdomains.forEach(sub => {
                    addNode(sub, 'subdomain', 10);
                    links.push({ source: targetName, target: sub });
                });
            }

            if (scan.result && scan.result.ip) {
                const ip = scan.result.ip;
                addNode(ip, 'ip', 10);
                links.push({ source: targetName, target: ip });
            }
        });

        setGraphData({ nodes, links });

      } catch (error) {
        console.error("Graph Error:", error);
      }
    };

    fetchData();
  }, []);

  // Use a fixed height container
  return (
    <div style={{ height: '500px', border: '1px solid #333', borderRadius: '8px', overflow: 'hidden', backgroundColor: '#000' }}>
        {graphData.nodes.length > 0 ? (
            <ForceGraph2D
                graphData={graphData}
                nodeLabel="id"
                nodeColor={node => {
                    if (node.group === 'target') return '#00ff41';
                    if (node.group === 'subdomain') return '#008F11';
                    return '#3b82f6';
                }}
                linkColor={() => '#333'}
                backgroundColor="#0a0a0a"
                nodeRelSize={6}
                linkWidth={2}
            />
        ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
                Loading Graph Data...
            </div>
        )}
    </div>
  );
};

export default NetworkGraph;