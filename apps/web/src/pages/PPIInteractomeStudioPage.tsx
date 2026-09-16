import React, { useState, useEffect } from 'react';
import { Network, Activity, Sparkles, Share2, Layers, Cpu, ShieldAlert, Target } from 'lucide-react';

interface Node {
  id: string;
  gene_symbol: string;
  uniprot_id: string;
  degree_centrality: number;
  betweenness_centrality: number;
  is_hub_target: boolean;
}

interface Edge {
  id: string;
  source_protein: string;
  target_protein: string;
  interaction_type: string;
  binding_affinity_kd_nm: number;
  confidence_score: number;
  druggability_index: number;
  interface_surface_area_a2: number;
}

interface NetworkGraph {
  id: string;
  network_name: string;
  disease_context: string;
  total_nodes: number;
  total_edges: number;
  created_at: string;
  nodes?: Node[];
  edges?: Edge[];
}

export const PPIInteractomeStudioPage: React.FC = () => {
  const [networks, setNetworks] = useState<NetworkGraph[]>([]);
  const [selectedNet, setSelectedNet] = useState<NetworkGraph | null>(null);
  const [networkName, setNetworkName] = useState('KRAS Oncogenic Signalosome');
  const [seedGene, setSeedGene] = useState('KRAS');
  const [diseaseContext, setDiseaseContext] = useState('Pancreatic Ductal Adenocarcinoma');
  const [loading, setLoading] = useState(false);

  const fetchNetworks = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/ppi-interactome/networks');
      if (res.ok) {
        const data = await res.json();
        setNetworks(data);
        if (data.length > 0 && !selectedNet) {
          fetchDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/ppi-interactome/networks/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedNet(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchNetworks();
  }, []);

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/ppi-interactome/networks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          network_name: networkName,
          seed_gene: seedGene,
          disease_context: diseaseContext,
        }),
      });
      if (res.ok) {
        await fetchNetworks();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-indigo-950/60 border border-indigo-500/40 rounded-xl text-indigo-400">
            <Network className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 to-pink-300 bg-clip-text text-transparent">
              Protein-Protein Interactome (PPI) Studio
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 58 • Graph neural network complex interactome cartography, betweenness hub ranking & druggable interface scoring
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-indigo-300">
            <Share2 className="w-5 h-5" /> Build Interactome Graph
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Network Name</label>
              <input
                type="text"
                value={networkName}
                onChange={(e) => setNetworkName(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Seed Protein / Gene</label>
              <input
                type="text"
                value={seedGene}
                onChange={(e) => setSeedGene(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Disease Context</label>
              <input
                type="text"
                value={diseaseContext}
                onChange={(e) => setDiseaseContext(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Constructing Graph...' : 'Generate PPI Network'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">Interactome Networks</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {networks.map((net) => (
                <div
                  key={net.id}
                  onClick={() => fetchDetail(net.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedNet?.id === net.id
                      ? 'bg-indigo-950/40 border-indigo-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{net.network_name}</span>
                    <span className="text-indigo-400 font-mono">{net.total_nodes} Nodes</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{net.disease_context}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Nodes & Interaction Edges */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-indigo-300">
              <Activity className="w-5 h-5" /> PPI Interaction Edges & Druggable Interfaces
            </h2>
            {selectedNet && (
              <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded border border-slate-700">
                Edges: {selectedNet.total_edges} | Nodes: {selectedNet.total_nodes}
              </span>
            )}
          </div>

          {selectedNet?.edges && selectedNet.edges.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Interaction Pair</th>
                    <th className="p-3">Mechanism</th>
                    <th className="p-3">Kd (nM)</th>
                    <th className="p-3">Confidence</th>
                    <th className="p-3">Druggability</th>
                    <th className="p-3">Surface (Å²)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedNet.edges.map((e) => (
                    <tr key={e.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-semibold text-indigo-300">
                        {e.source_protein} <span className="text-slate-500">↔</span> {e.target_protein}
                      </td>
                      <td className="p-3 text-slate-400">{e.interaction_type}</td>
                      <td className="p-3 font-mono text-pink-300">{e.binding_affinity_kd_nm} nM</td>
                      <td className="p-3 font-mono text-emerald-400">{(e.confidence_score * 100).toFixed(0)}%</td>
                      <td className="p-3 font-mono font-bold text-indigo-400">
                        {e.druggability_index >= 0.85 ? (
                          <span className="bg-emerald-950/60 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/40 text-[10px]">
                            High ({e.druggability_index})
                          </span>
                        ) : (
                          <span className="text-slate-400 text-[10px]">{e.druggability_index}</span>
                        )}
                      </td>
                      <td className="p-3 font-mono text-slate-400">{e.interface_surface_area_a2} Å²</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No edges loaded. Build or select a network above.</div>
          )}

          {/* Node Hub Centrality List */}
          {selectedNet?.nodes && selectedNet.nodes.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-2">
                <Target className="w-4 h-4 text-pink-400" /> Critical Interactome Hubs
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {selectedNet.nodes.map((n) => (
                  <div key={n.id} className={`p-3 rounded-lg border ${n.is_hub_target ? 'bg-indigo-950/40 border-indigo-500/40' : 'bg-slate-950/60 border-slate-800'}`}>
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-slate-200">{n.gene_symbol}</span>
                      <span className="font-mono text-[10px] text-slate-400">{n.uniprot_id}</span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
                      <span>Centrality: {n.degree_centrality}</span>
                      {n.is_hub_target && <span className="text-pink-400 font-semibold">Hub Target</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
