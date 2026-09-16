import React, { useState, useEffect } from 'react';
import { Shield, Dna, Activity, Plus, CheckCircle, Sparkles, Layers, ListFilter } from 'lucide-react';

interface Epitope {
  id: string;
  gene_symbol: string;
  mutation_variant: string;
  peptide_sequence: string;
  hla_allele: string;
  binding_ic50_nm: number;
  percentile_rank: number;
  tcr_immunogenicity_score: number;
  composite_priority_score: number;
  recommended_for_vaccine: boolean;
}

interface VaccineConstruct {
  id: string;
  construct_name: string;
  construct_type: string;
  ordered_epitopes: string[];
  full_polyepitope_sequence: string;
  predicted_expression_efficiency: number;
}

interface Screen {
  id: string;
  patient_id: string;
  tumor_type: string;
  hla_alleles: string[];
  top_candidates_count: number;
  status: string;
  created_at: string;
  epitopes?: Epitope[];
  vaccine_constructs?: VaccineConstruct[];
}

export const ImmunologyStudioPage: React.FC = () => {
  const [screens, setScreens] = useState<Screen[]>([]);
  const [selectedScreen, setSelectedScreen] = useState<Screen | null>(null);
  const [patientId, setPatientId] = useState('PT-MEL-2026-09');
  const [tumorType, setTumorType] = useState('Cutaneous Melanoma');
  const [loading, setLoading] = useState(false);

  const fetchScreens = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/immunology/screens');
      if (res.ok) {
        const data = await res.json();
        setScreens(data);
        if (data.length > 0 && !selectedScreen) {
          fetchScreenDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchScreenDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/immunology/screens/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedScreen(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchScreens();
  }, []);

  const handleCreateScreen = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/immunology/screens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: patientId,
          tumor_type: tumorType,
          hla_alleles: ['HLA-A*02:01', 'HLA-B*07:02', 'HLA-C*07:01'],
        }),
      });
      if (res.ok) {
        await fetchScreens();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDesignVaccine = async () => {
    if (!selectedScreen) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/immunology/screens/${selectedScreen.id}/design-vaccine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          construct_name: `mRNA-NeoVax-${selectedScreen.patient_id}`,
          construct_type: 'mRNA_LNP',
          linker: 'AAY',
        }),
      });
      if (res.ok) {
        await fetchScreenDetail(selectedScreen.id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-rose-950/60 border border-rose-500/40 rounded-xl text-rose-400">
            <Shield className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-rose-400 to-amber-300 bg-clip-text text-transparent">
              Computational Immunology & Neoantigen Studio
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 55 • Deep learning TCR-pMHC binding prediction, HLA presentation & poly-epitope vaccine construct synthesis
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-rose-300">
            <Dna className="w-5 h-5" /> Launch Neoantigen Screen
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Patient ID</label>
              <input
                type="text"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Tumor Type</label>
              <input
                type="text"
                value={tumorType}
                onChange={(e) => setTumorType(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleCreateScreen}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-rose-600 to-amber-600 hover:from-rose-500 hover:to-amber-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Running Screen...' : 'Run HLA-TCR Screen'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">Screening Campaigns</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {screens.map((s) => (
                <div
                  key={s.id}
                  onClick={() => fetchScreenDetail(s.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedScreen?.id === s.id
                      ? 'bg-rose-950/40 border-rose-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{s.patient_id}</span>
                    <span className="text-rose-400 font-mono">{s.top_candidates_count} Top Epitopes</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{s.tumor_type}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Epitopes Matrix */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-rose-300">
              <Activity className="w-5 h-5" /> Prioritized Neoantigen Epitopes
            </h2>
            {selectedScreen && (
              <button
                onClick={handleDesignVaccine}
                className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 rounded-lg text-xs font-semibold text-white flex items-center gap-1.5 shadow"
              >
                <Layers className="w-4 h-4" /> Synthesize Poly-Epitope Vaccine
              </button>
            )}
          </div>

          {selectedScreen?.epitopes && selectedScreen.epitopes.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Gene / Variant</th>
                    <th className="p-3">Peptide Sequence</th>
                    <th className="p-3">HLA Allele</th>
                    <th className="p-3">IC50 (nM)</th>
                    <th className="p-3">TCR Score</th>
                    <th className="p-3">Priority Score</th>
                    <th className="p-3">Vaccine Candidate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedScreen.epitopes.map((ep) => (
                    <tr key={ep.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-semibold text-rose-300">
                        {ep.gene_symbol} <span className="text-slate-400 font-normal">({ep.mutation_variant})</span>
                      </td>
                      <td className="p-3 font-mono text-amber-300">{ep.peptide_sequence}</td>
                      <td className="p-3 font-mono text-slate-400">{ep.hla_allele}</td>
                      <td className="p-3 font-mono">{ep.binding_ic50_nm} nM</td>
                      <td className="p-3 font-mono text-emerald-400">{ep.tcr_immunogenicity_score}</td>
                      <td className="p-3 font-mono font-bold text-rose-400">{ep.composite_priority_score}</td>
                      <td className="p-3">
                        {ep.recommended_for_vaccine ? (
                          <span className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-950/50 border border-emerald-500/40 px-2 py-0.5 rounded text-[10px]">
                            <CheckCircle className="w-3 h-3" /> Recommended
                          </span>
                        ) : (
                          <span className="text-slate-500 text-[10px]">Low rank</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No epitopes loaded. Run or select a screen above.</div>
          )}

          {/* Vaccine Constructs */}
          {selectedScreen?.vaccine_constructs && selectedScreen.vaccine_constructs.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                <Layers className="w-4 h-4" /> Synthesized Poly-Epitope Constructs
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {selectedScreen.vaccine_constructs.map((c) => (
                  <div key={c.id} className="p-4 bg-slate-950/80 border border-amber-500/30 rounded-xl space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-slate-200 text-sm">{c.construct_name}</span>
                      <span className="text-[10px] bg-amber-950 text-amber-400 px-2 py-0.5 rounded border border-amber-500/30">
                        {c.construct_type}
                      </span>
                    </div>
                    <div className="text-xs font-mono text-slate-300 break-all bg-slate-900 p-2 rounded border border-slate-800">
                      {c.full_polyepitope_sequence}
                    </div>
                    <div className="text-[11px] text-slate-400 flex justify-between">
                      <span>Expression Efficiency: {(c.predicted_expression_efficiency * 100).toFixed(1)}%</span>
                      <span>Epitopes: {c.ordered_epitopes.length}</span>
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
