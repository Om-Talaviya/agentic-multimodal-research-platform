import React, { useState } from 'react';
import { Network, ShieldCheck, Zap, Layers, Compass, GitMerge } from 'lucide-react';

export const ChromatinLoopStudioPage: React.FC = () => {
  const [cellLine, setCellLine] = useState('K562 Chronic Myelogenous Leukemia');
  const [chromosome, setChromosome] = useState('chr8');
  const [resBp, setResBp] = useState(5000);
  const [mapping, setMapping] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleMap = async () => {
    setMapping(true);
    try {
      const res = await fetch('/api/v1/chromatin-loop/map', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cell_line_name: cellLine,
          chromosome: chromosome,
          resolution_bp: resBp,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setMapping(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
            <GitMerge className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              High-Resolution Hi-C Chromatin Loop & Enhancer-Promoter Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 152: 3D Genome Architecture, CTCF Insulation Metrics & Cohesin Extrusion Contact Topology
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-indigo-400" />
              <span>Conformation Capture Parameters</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Cell Line / Biosample</label>
                <input
                  type="text"
                  value={cellLine}
                  onChange={(e) => setCellLine(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Chromosome</label>
                <input
                  type="text"
                  value={chromosome}
                  onChange={(e) => setChromosome(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Matrix Resolution (bp)</label>
                <input
                  type="number"
                  value={resBp}
                  onChange={(e) => setResBp(parseInt(e.target.value) || 5000)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                onClick={handleMap}
                disabled={mapping}
                className="w-full py-3 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-indigo-500/20 disabled:opacity-50"
              >
                {mapping ? 'Extracting Loops & TADs...' : 'Map Chromatin Conformation'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-indigo-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-indigo-400">Loop Topology & TAD Insulation Summary</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Total Loops</p>
                      <p className="text-lg font-bold text-white mt-1">{result.total_loops_detected}</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">TAD Boundaries</p>
                      <p className="text-lg font-bold text-indigo-400 mt-1">{result.tad_count}</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Mean Insulation</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{result.mean_insulation_score}</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Mean Span</p>
                      <p className="text-lg font-bold text-cyan-400 mt-1">{result.mean_loop_span_kb} kb</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">High-Confidence Enhancer-Promoter Edges</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Enhancer Locus</th>
                          <th className="px-4 py-3">Target Gene</th>
                          <th className="px-4 py-3">Frequency</th>
                          <th className="px-4 py-3">Span (kb)</th>
                          <th className="px-4 py-3">Log2FC</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.contact_edges.map((e: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-mono text-xs text-indigo-300">{e.enhancer_locus}</td>
                            <td className="px-4 py-3.5 font-bold text-white">{e.target_gene}</td>
                            <td className="px-4 py-3.5 text-slate-200">{e.contact_frequency}</td>
                            <td className="px-4 py-3.5 text-slate-400">{(e.loop_span_bp / 1000).toFixed(0)} kb</td>
                            <td className="px-4 py-3.5 text-emerald-400 font-bold">+{e.activation_log2fc}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Select chromosome and resolution to compute Hi-C contact matrix loop interactions.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChromatinLoopStudioPage;
