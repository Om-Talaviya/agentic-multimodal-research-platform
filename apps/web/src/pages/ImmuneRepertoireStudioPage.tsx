import React, { useState, useEffect } from 'react';
import { Shield, Activity, Dna, PieChart, BarChart2, Plus, CheckCircle, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface Clonotype {
  id: string;
  cdr3_aa: string;
  v_gene: string;
  j_gene: string;
  frequency: number;
  count: number;
  antigen_specificity?: string;
}

interface VDJPairing {
  v_family: string;
  j_family: string;
  pairing_frequency: number;
  cdr3_length: number;
}

interface Repertoire {
  id: string;
  sample_name: string;
  organism: string;
  chain_type: string;
  clonotype_count: number;
  total_cells: number;
  shannon_entropy: number;
  gini_simpson_index: number;
  clonality_score: number;
  status: string;
  clonotypes?: Clonotype[];
  vdj_pairings?: VDJPairing[];
}

export const ImmuneRepertoireStudioPage: React.FC = () => {
  const [repertoires, setRepertoires] = useState<Repertoire[]>([]);
  const [selectedRepertoire, setSelectedRepertoire] = useState<Repertoire | null>(null);
  const [loading, setLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [sampleName, setSampleName] = useState('PBMC-Post-Vaccination-TCRb');
  const [chainType, setChainType] = useState('TCR_ALPHA_BETA');

  useEffect(() => {
    fetchRepertoires();
  }, []);

  const fetchRepertoires = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/v1/immune-repertoire/repertoires');
      setRepertoires(res.data);
      if (res.data.length > 0) {
        fetchRepertoireDetail(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load immune repertoires', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRepertoireDetail = async (id: string) => {
    try {
      const res = await axios.get(`/api/v1/immune-repertoire/repertoires/${id}`);
      setSelectedRepertoire(res.data);
    } catch (err) {
      console.error('Failed to fetch repertoire details', err);
    }
  };

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const payload = {
        sample_name: sampleName,
        organism: 'Homo sapiens',
        chain_type: chainType,
        clonotypes: [
          { cdr3_aa: 'CASSLAPGATNEKLFF', v_gene: 'TRBV7-2*01', j_gene: 'TRBJ1-4*01', count: 450, is_productive: true },
          { cdr3_aa: 'CASSLIGVSSYNEQFF', v_gene: 'TRBV19*01', j_gene: 'TRBJ2-1*01', count: 320, is_productive: true },
          { cdr3_aa: 'CASSPGQGAYEQYF', v_gene: 'TRBV4-1*01', j_gene: 'TRBJ2-7*01', count: 180, is_productive: true },
          { cdr3_aa: 'CASSSRSSYEQYF', v_gene: 'TRBV12-3*01', j_gene: 'TRBJ2-7*01', count: 110, is_productive: true },
          { cdr3_aa: 'CASSLTGTEAFF', v_gene: 'TRBV28*01', j_gene: 'TRBJ1-1*01', count: 95, is_productive: true },
          { cdr3_aa: 'CASSRGTEYEQYF', v_gene: 'TRBV6-5*01', j_gene: 'TRBJ2-7*01', count: 70, is_productive: true }
        ]
      };
      const res = await axios.post('/api/v1/immune-repertoire/analyze', payload);
      setRepertoires([res.data, ...repertoires]);
      setSelectedRepertoire(res.data);
    } catch (err) {
      console.error('Failed to run repertoire analysis', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Autonomous Immune Repertoire & TCR/BCR Clonotype Studio</h1>
              <p className="text-sm text-slate-400">
                Phase 104 • V(D)J Gene Profiling, Shannon/Simpson Clonal Diversity & Antigen Specificity Matching
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRunAnalysis}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg transition disabled:opacity-50"
          >
            {isAnalyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Analyze New Repertoire
          </button>
        </div>
      </div>

      {/* KPI Header */}
      {selectedRepertoire && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Clonotype Count</div>
            <div className="text-2xl font-bold text-white mt-1">{selectedRepertoire.clonotype_count}</div>
            <div className="text-xs text-slate-500 mt-1">{selectedRepertoire.total_cells.toLocaleString()} Cells Profiled</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Shannon Entropy (H)</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{selectedRepertoire.shannon_entropy}</div>
            <div className="text-xs text-slate-500 mt-1">Repertoire Diversity Index</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Gini-Simpson Index</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{selectedRepertoire.gini_simpson_index}</div>
            <div className="text-xs text-slate-500 mt-1">1 - sum(p^2) Probability</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Clonality Score</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{(selectedRepertoire.clonality_score * 100).toFixed(1)}%</div>
            <div className="text-xs text-slate-500 mt-1">Clonal Expansion Level</div>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Repertoires Catalog */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Dna className="w-5 h-5 text-indigo-400" />
            Immune Repertoire Samples
          </h2>
          {loading ? (
            <div className="text-center py-8 text-slate-400">Loading samples...</div>
          ) : repertoires.length === 0 ? (
            <div className="text-center py-8 text-slate-500">No immune repertoires found. Run an analysis above.</div>
          ) : (
            <div className="space-y-3">
              {repertoires.map((rep) => (
                <div
                  key={rep.id}
                  onClick={() => fetchRepertoireDetail(rep.id)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition ${
                    selectedRepertoire?.id === rep.id
                      ? 'bg-indigo-950/40 border-indigo-500/50'
                      : 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-800'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div className="font-semibold text-white text-sm truncate">{rep.sample_name}</div>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-indigo-300 font-mono">
                      {rep.chain_type}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-400 mt-2">
                    <span>{rep.clonotype_count} clonotypes</span>
                    <span>Clonality: {(rep.clonality_score * 100).toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Clonotypes & V(D)J Recombination */}
        <div className="lg:col-span-2 space-y-6">
          {selectedRepertoire ? (
            <>
              {/* Top Clonotypes Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-indigo-400" />
                  Dominant Clonal Lineages (CDR3 & V-J Assignment)
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-800/80 text-xs uppercase text-slate-400 font-semibold">
                      <tr>
                        <th className="py-2.5 px-3">CDR3 Amino Acid</th>
                        <th className="py-2.5 px-3">V Gene</th>
                        <th className="py-2.5 px-3">J Gene</th>
                        <th className="py-2.5 px-3">Count</th>
                        <th className="py-2.5 px-3">Frequency</th>
                        <th className="py-2.5 px-3">Antigen Specificity</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {selectedRepertoire.clonotypes && selectedRepertoire.clonotypes.length > 0 ? (
                        selectedRepertoire.clonotypes.map((c) => (
                          <tr key={c.id} className="hover:bg-slate-800/40">
                            <td className="py-2.5 px-3 font-mono text-indigo-300 font-semibold">{c.cdr3_aa}</td>
                            <td className="py-2.5 px-3 text-xs font-mono">{c.v_gene}</td>
                            <td className="py-2.5 px-3 text-xs font-mono">{c.j_gene}</td>
                            <td className="py-2.5 px-3 font-mono">{c.count}</td>
                            <td className="py-2.5 px-3 font-mono">{(c.frequency * 100).toFixed(2)}%</td>
                            <td className="py-2.5 px-3">
                              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
                                <CheckCircle className="w-3 h-3 text-emerald-400" />
                                {c.antigen_specificity || 'Uncharacterized'}
                              </span>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={6} className="py-4 text-center text-slate-500">
                            No clonotypes loaded for this sample.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* V-J Pairing Frequencies */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <BarChart2 className="w-5 h-5 text-indigo-400" />
                  V(D)J Recombination Pairing Matrix
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {selectedRepertoire.vdj_pairings && selectedRepertoire.vdj_pairings.length > 0 ? (
                    selectedRepertoire.vdj_pairings.map((p, idx) => (
                      <div key={idx} className="p-3 bg-slate-800/50 border border-slate-700/60 rounded-lg">
                        <div className="flex justify-between text-xs font-mono font-semibold text-indigo-300">
                          <span>{p.v_family}</span>
                          <span>{p.j_family}</span>
                        </div>
                        <div className="flex justify-between text-xs text-slate-400 mt-2">
                          <span>Pairing Freq</span>
                          <span className="font-bold text-white">{(p.pairing_frequency * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-slate-700 h-1.5 rounded-full mt-2 overflow-hidden">
                          <div
                            className="bg-indigo-500 h-full rounded-full"
                            style={{ width: `${Math.min(100, p.pairing_frequency * 100 * 2)}%` }}
                          />
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-slate-500 col-span-3 text-center py-4">
                      No V-J recombination pairs found.
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400">
              Select or analyze an immune repertoire sample to view detailed CDR3 clonotypes and V(D)J pairing frequencies.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
