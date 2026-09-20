import React, { useState, useEffect } from 'react';
import { Compass, Box, Share2, Activity, Zap, Plus, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface AllostericPocket {
  pocket_name: string;
  center_x: number;
  center_y: number;
  center_z: number;
  apo_volume_a3: number;
  holo_volume_a3: number;
  volume_expansion_ratio: number;
  druggability_index: number;
  hydrophobicity_score: number;
  enclosing_residues?: string;
}

interface CoupledNetwork {
  source_residue: string;
  target_residue: string;
  allosteric_correlation: number;
  pathway_shortest_distance_a: number;
}

interface CrypticAnalysis {
  id: string;
  target_protein: string;
  pdb_id?: string;
  trajectory_frames_sampled: number;
  detected_cryptic_pockets: number;
  max_druggability_score: number;
  allosteric_coupling_score: number;
  status: string;
  pockets?: AllostericPocket[];
  coupled_networks?: CoupledNetwork[];
}

export const CrypticPocketsStudioPage: React.FC = () => {
  const [analyses, setAnalyses] = useState<CrypticAnalysis[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<CrypticAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [targetProtein, setTargetProtein] = useState('KRAS-G12D-Switch-II');

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/v1/cryptic-pockets/analyses');
      setAnalyses(res.data);
      if (res.data.length > 0) {
        fetchAnalysisDetail(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load cryptic pocket analyses', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalysisDetail = async (id: string) => {
    try {
      const res = await axios.get(`/api/v1/cryptic-pockets/analyses/${id}`);
      setSelectedAnalysis(res.data);
    } catch (err) {
      console.error('Failed to fetch cryptic analysis details', err);
    }
  };

  const handleRunDiscovery = async () => {
    setIsDiscovering(true);
    try {
      const payload = {
        target_protein: targetProtein,
        pdb_id: '7T47',
        trajectory_frames_sampled: 250,
        candidate_pockets: [
          {
            pocket_name: 'Cryptic-Switch-II-Pocket',
            center_x: 18.2, center_y: -12.4, center_z: 34.5,
            apo_volume_a3: 95.0, holo_volume_a3: 580.0,
            hydrophobicity_score: 0.84,
            enclosing_residues: 'GLY12, TYR64, MET72, GLN99, HIS95'
          },
          {
            pocket_name: 'Allosteric-Effector-Loop-Site',
            center_x: -8.5, center_y: 24.1, center_z: 19.8,
            apo_volume_a3: 110.0, holo_volume_a3: 490.0,
            hydrophobicity_score: 0.78,
            enclosing_residues: 'VAL29, ASP33, ILE36, GLU37'
          }
        ]
      };
      const res = await axios.post('/api/v1/cryptic-pockets/discover', payload);
      setAnalyses([res.data, ...analyses]);
      setSelectedAnalysis(res.data);
    } catch (err) {
      console.error('Failed to discover cryptic pockets', err);
    } finally {
      setIsDiscovering(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400">
              <Compass className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Autonomous Allosteric & Cryptic Pocket Studio</h1>
              <p className="text-sm text-slate-400">
                Phase 107 • MD Ensemble Cavity Expansion, Druggability Index Scoring & Allosteric Coupling Pathways
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRunDiscovery}
            disabled={isDiscovering}
            className="flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-medium rounded-lg transition disabled:opacity-50"
          >
            {isDiscovering ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Discover Cryptic Cavities
          </button>
        </div>
      </div>

      {/* KPI Stats */}
      {selectedAnalysis && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Cryptic Pockets Found</div>
            <div className="text-2xl font-bold text-white mt-1">{selectedAnalysis.detected_cryptic_pockets}</div>
            <div className="text-xs text-slate-500 mt-1">{selectedAnalysis.trajectory_frames_sampled} Conformation Frames</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Max Druggability (D)</div>
            <div className="text-2xl font-bold text-rose-400 mt-1">{selectedAnalysis.max_druggability_score}</div>
            <div className="text-xs text-slate-500 mt-1">D_score $\ge 0.70$ (Highly Druggable)</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Allosteric Coupling</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{selectedAnalysis.allosteric_coupling_score}</div>
            <div className="text-xs text-slate-500 mt-1">DCCM Dynamic Correlation</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Target PDB Structure</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{selectedAnalysis.pdb_id || 'AlphaFold'}</div>
            <div className="text-xs text-slate-500 mt-1">{selectedAnalysis.target_protein}</div>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Targets List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Box className="w-5 h-5 text-rose-400" />
            Analyzed Proteins
          </h2>
          {loading ? (
            <div className="text-center py-8 text-slate-400">Loading analyses...</div>
          ) : analyses.length === 0 ? (
            <div className="text-center py-8 text-slate-500">No analyses found. Run discovery above.</div>
          ) : (
            <div className="space-y-3">
              {analyses.map((a) => (
                <div
                  key={a.id}
                  onClick={() => fetchAnalysisDetail(a.id)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition ${
                    selectedAnalysis?.id === a.id
                      ? 'bg-rose-950/40 border-rose-500/60'
                      : 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-800'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div className="font-semibold text-white text-sm truncate">{a.target_protein}</div>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-rose-300 font-mono">
                      {a.pdb_id || 'AF3'}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-400 mt-2">
                    <span>{a.detected_cryptic_pockets} pockets</span>
                    <span>Max Drug: {a.max_druggability_score}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Pockets & Coupled Networks */}
        <div className="lg:col-span-2 space-y-6">
          {selectedAnalysis ? (
            <>
              {/* Pocket Profiles Cards */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-rose-400" />
                  Identified Cryptic & Allosteric Pocket Profiles
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedAnalysis.pockets && selectedAnalysis.pockets.length > 0 ? (
                    selectedAnalysis.pockets.map((p, idx) => (
                      <div key={idx} className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-xl space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="font-semibold text-rose-300 text-sm">{p.pocket_name}</span>
                          <span className="text-xs px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                            Drug: {p.druggability_index}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                          <div>
                            <span className="text-slate-500">Apo Volume:</span> {p.apo_volume_a3} Å³
                          </div>
                          <div>
                            <span className="text-slate-500">Holo Volume:</span> {p.holo_volume_a3} Å³
                          </div>
                          <div>
                            <span className="text-slate-500">Expansion:</span> {p.volume_expansion_ratio}x
                          </div>
                          <div>
                            <span className="text-slate-500">Hydrophobicity:</span> {p.hydrophobicity_score}
                          </div>
                        </div>
                        {p.enclosing_residues && (
                          <div className="text-[11px] text-slate-400 font-mono bg-slate-900/60 p-2 rounded border border-slate-800">
                            {p.enclosing_residues}
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-slate-500 col-span-2 text-center py-4">No pockets discovered.</div>
                  )}
                </div>
              </div>

              {/* Coupled Allosteric Residue Network */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Share2 className="w-5 h-5 text-rose-400" />
                  Allosteric Communication Pathways (DCCM Coupling)
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-800/80 text-xs uppercase text-slate-400 font-semibold">
                      <tr>
                        <th className="py-2.5 px-3">Allosteric Source Residue</th>
                        <th className="py-2.5 px-3">Catalytic Target Residue</th>
                        <th className="py-2.5 px-3">Coupling Correlation (r)</th>
                        <th className="py-2.5 px-3">Spatial Distance (Å)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {selectedAnalysis.coupled_networks && selectedAnalysis.coupled_networks.length > 0 ? (
                        selectedAnalysis.coupled_networks.map((net, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/40">
                            <td className="py-2.5 px-3 font-mono text-rose-300 font-semibold">{net.source_residue}</td>
                            <td className="py-2.5 px-3 font-mono text-indigo-300 font-semibold">{net.target_residue}</td>
                            <td className="py-2.5 px-3 font-mono text-emerald-400 font-bold">{net.allosteric_correlation}</td>
                            <td className="py-2.5 px-3 font-mono">{net.pathway_shortest_distance_a} Å</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="py-4 text-center text-slate-500">
                            No coupled residue networks calculated.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400">
              Select or discover cryptic pockets to explore allosteric binding cavities.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
