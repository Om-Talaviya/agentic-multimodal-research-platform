import React, { useState, useEffect } from 'react';
import { Cpu, Activity, Sparkles, Layers, Dna, Code2, CheckCircle, Zap } from 'lucide-react';

interface Part {
  id: string;
  part_type: string;
  part_name: string;
  part_sequence: string;
  order_index: number;
  relative_strength_au: number;
}

interface TruthTableEntry {
  id: string;
  input_state_a: boolean;
  input_state_b: boolean;
  expected_output: boolean;
  simulated_fluorescence_rfu: number;
  response_delay_minutes: number;
}

interface Circuit {
  id: string;
  circuit_name: string;
  host_organism: string;
  logic_expression: string;
  gate_topology: string;
  total_parts: number;
  dynamic_range_on_off_ratio: number;
  created_at: string;
  parts?: Part[];
  truth_table?: TruthTableEntry[];
}

export const SyntheticBiologyStudioPage: React.FC = () => {
  const [circuits, setCircuits] = useState<Circuit[]>([]);
  const [selectedCircuit, setSelectedCircuit] = useState<Circuit | null>(null);
  const [circuitName, setCircuitName] = useState('Dual-Input Biosensor AND-Gate');
  const [logicExpr, setLogicExpr] = useState('A AND B');
  const [hostOrganism, setHostOrganism] = useState('E. coli K-12 (MG1655)');
  const [loading, setLoading] = useState(false);

  const fetchCircuits = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/synthetic-biology/circuits');
      if (res.ok) {
        const data = await res.json();
        setCircuits(data);
        if (data.length > 0 && !selectedCircuit) {
          fetchDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/synthetic-biology/circuits/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedCircuit(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchCircuits();
  }, []);

  const handleCompile = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/synthetic-biology/circuits', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          circuit_name: circuitName,
          logic_expression: logicExpr,
          host_organism: hostOrganism,
          gate_topology: 'Transcriptional Logic Gate',
        }),
      });
      if (res.ok) {
        await fetchCircuits();
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
          <div className="p-3 bg-emerald-950/60 border border-emerald-500/40 rounded-xl text-emerald-400">
            <Cpu className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-lime-300 bg-clip-text text-transparent">
              Synthetic Biology DNA Circuit Studio
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 65 • Cello-style genetic logic gate compiler, promoter-repressor transcription modeling & truth table simulation
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-emerald-300">
            <Code2 className="w-5 h-5" /> Compile Logic Gate
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Circuit Name</label>
              <input
                type="text"
                value={circuitName}
                onChange={(e) => setCircuitName(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Boolean Logic Expression</label>
              <input
                type="text"
                value={logicExpr}
                onChange={(e) => setLogicExpr(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200 font-mono"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Host Organism</label>
              <input
                type="text"
                value={hostOrganism}
                onChange={(e) => setHostOrganism(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleCompile}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-lime-600 hover:from-emerald-500 hover:to-lime-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Synthesizing Circuit...' : 'Compile DNA Circuit'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">Compiled DNA Circuits</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {circuits.map((c) => (
                <div
                  key={c.id}
                  onClick={() => fetchDetail(c.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedCircuit?.id === c.id
                      ? 'bg-emerald-950/40 border-emerald-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{c.circuit_name}</span>
                    <span className="text-emerald-400 font-mono">{c.dynamic_range_on_off_ratio}x ON/OFF</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1 font-mono">{c.logic_expression} • {c.host_organism}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Parts Diagram & Truth Table */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-emerald-300">
              <Activity className="w-5 h-5" /> Genetic Part Assembly & Truth Table
            </h2>
            {selectedCircuit && (
              <span className="text-xs bg-emerald-950 text-emerald-300 px-2.5 py-1 rounded border border-emerald-500/40 font-semibold">
                Dynamic Range: {selectedCircuit.dynamic_range_on_off_ratio}x
              </span>
            )}
          </div>

          {/* Genetic Parts Cassette */}
          {selectedCircuit?.parts && selectedCircuit.parts.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Dna className="w-4 h-4 text-emerald-400" /> Linear DNA Cassette Architecture
              </h3>
              <div className="flex flex-wrap gap-2 p-3 bg-slate-950 rounded-xl border border-slate-800">
                {selectedCircuit.parts.map((p) => (
                  <div key={p.id} className="p-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs space-y-1">
                    <div className="flex items-center gap-1.5 font-bold">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                        p.part_type === 'Promoter'
                          ? 'bg-amber-950 text-amber-300 border border-amber-500/30'
                          : p.part_type === 'RBS'
                          ? 'bg-blue-950 text-blue-300 border border-blue-500/30'
                          : p.part_type === 'CDS'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30'
                          : 'bg-rose-950 text-rose-300 border border-rose-500/30'
                      }`}>
                        {p.part_type}
                      </span>
                      <span className="text-slate-200">{p.part_name}</span>
                    </div>
                    <div className="text-[10px] font-mono text-slate-400 truncate max-w-[150px]">{p.part_sequence}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Truth Table */}
          {selectedCircuit?.truth_table && selectedCircuit.truth_table.length > 0 ? (
            <div className="overflow-x-auto pt-2">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Input A (Inducer 1)</th>
                    <th className="p-3">Input B (Inducer 2)</th>
                    <th className="p-3">Expected State</th>
                    <th className="p-3">Simulated Fluorescence (RFU)</th>
                    <th className="p-3">Kinetics</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedCircuit.truth_table.map((tt) => (
                    <tr key={tt.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-mono font-bold">
                        {tt.input_state_a ? (
                          <span className="text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">1 (HIGH)</span>
                        ) : (
                          <span className="text-slate-500">0 (LOW)</span>
                        )}
                      </td>
                      <td className="p-3 font-mono font-bold">
                        {tt.input_state_b ? (
                          <span className="text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">1 (HIGH)</span>
                        ) : (
                          <span className="text-slate-500">0 (LOW)</span>
                        )}
                      </td>
                      <td className="p-3 font-mono font-bold">
                        {tt.expected_output ? (
                          <span className="text-lime-300">TRUE (ON)</span>
                        ) : (
                          <span className="text-slate-400">FALSE (OFF)</span>
                        )}
                      </td>
                      <td className="p-3 font-mono font-bold text-emerald-400 text-sm">
                        {tt.simulated_fluorescence_rfu.toLocaleString()} RFU
                      </td>
                      <td className="p-3 font-mono text-slate-400">{tt.response_delay_minutes} min delay</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No circuits loaded. Compile a gate above.</div>
          )}
        </div>
      </div>
    </div>
  );
};
