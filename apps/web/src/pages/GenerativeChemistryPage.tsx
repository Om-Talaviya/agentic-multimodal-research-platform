import React, { useState } from 'react';
import { 
  Dna, 
  FlaskConical, 
  ShieldCheck, 
  Sparkles, 
  Zap, 
  Download, 
  CheckCircle2, 
  ChevronRight,
  TrendingDown,
  Activity,
  Sliders,
  Layers
} from 'lucide-react';

interface Molecule {
  id: string;
  name: string;
  target: string;
  smiles: string;
  mw: number;
  logp: number;
  qed: number;
  sa: number;
  affinity: number;
  violations: number;
  admet: {
    hia: number;
    bbb: number;
    cyp3a4: boolean;
    herg: boolean;
    ppb: number;
  };
}

interface Antibody {
  id: string;
  variant: string;
  antigen: string;
  cdr_h3: string;
  kd: number;
  tm: number;
  humanness: number;
}

export const GenerativeChemistryPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'small_molecules' | 'antibodies'>('small_molecules');
  const [targetProtein, setTargetProtein] = useState('PCSK9');
  const [selectedMol, setSelectedMol] = useState<Molecule | null>(null);

  const molecules: Molecule[] = [
    {
      id: 'mol_1',
      name: 'PCSK9-GEN-001 (Quinazoline-Sulfonamide)',
      target: 'PCSK9',
      smiles: 'CC1=CC(=C(C=C1)S(=O)(=O)NC2=CC=C(C=C2)F)NC3=NC=NC4=CC(=C(C=C34)OC)OC',
      mw: 442.5,
      logp: 2.85,
      qed: 0.892,
      sa: 2.4,
      affinity: -9.85,
      violations: 0,
      admet: { hia: 94.2, bbb: 0.35, cyp3a4: false, herg: false, ppb: 86.5 }
    },
    {
      id: 'mol_2',
      name: 'PCSK9-GEN-002 (Pyrazolopyrimidine-Amine)',
      target: 'PCSK9',
      smiles: 'CC(C)NC1=NC=NC2=C1C(=NN2C3=CC=C(C=C3)Cl)C4=CC=CC=C4F',
      mw: 418.9,
      logp: 3.12,
      qed: 0.865,
      sa: 2.7,
      affinity: -10.15,
      violations: 0,
      admet: { hia: 91.8, bbb: 0.48, cyp3a4: false, herg: false, ppb: 89.0 }
    },
    {
      id: 'mol_3',
      name: 'PCSK9-GEN-003 (Imidazopyridine-Carboxamide)',
      target: 'PCSK9',
      smiles: 'CNC(=O)C1=CC=C(C=C1)N2C=NC3=CC(=CC=C32)C4=CC=C(C=C4)S(=O)(=O)C',
      mw: 405.4,
      logp: 2.45,
      qed: 0.915,
      sa: 2.2,
      affinity: -9.35,
      violations: 0,
      admet: { hia: 96.0, bbb: 0.22, cyp3a4: false, herg: false, ppb: 83.2 }
    }
  ];

  const antibodies: Antibody[] = [
    { id: 'ab_1', variant: 'mAb-PDL1-v1', antigen: 'PD-L1', cdr_h3: 'CARDLLGWYYGMDVW', kd: 0.185, tm: 76.2, humanness: 0.94 },
    { id: 'ab_2', variant: 'mAb-PDL1-v2', antigen: 'PD-L1', cdr_h3: 'CARDLLGYYYYMDVW', kd: 0.240, tm: 74.8, humanness: 0.95 },
    { id: 'ab_3', variant: 'mAb-PDL1-v3', antigen: 'PD-L1', cdr_h3: 'CARDLLGFAYGMDVW', kd: 0.315, tm: 75.5, humanness: 0.93 },
  ];

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-purple-500/20 to-pink-500/20 border border-purple-500/30 text-purple-400">
              <FlaskConical className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Generative De Novo Molecule & Antibody Design Studio
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  Generation 16 • Phase 43
                </span>
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                AI diffusion small molecule synthesis, Lipinski & QED filters, ADMET profiles, and CDR-H3 antibody affinity maturation.
              </p>
            </div>
          </div>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center bg-slate-900 border border-slate-800 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('small_molecules')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
              activeTab === 'small_molecules' 
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Small Molecules
          </button>
          <button
            onClick={() => setActiveTab('antibodies')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
              activeTab === 'antibodies' 
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Antibody Therapeutics
          </button>
        </div>
      </div>

      {activeTab === 'small_molecules' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left 2 Cols: Generated Candidate Cards */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                De Novo Generated Small Molecules for {targetProtein}
              </h2>
              <span className="text-xs text-slate-400">Target Binding Filter: ΔG ≤ -9.0 kcal/mol</span>
            </div>

            <div className="space-y-4">
              {molecules.map((m) => {
                const isSelected = selectedMol?.id === m.id;

                return (
                  <div
                    key={m.id}
                    onClick={() => setSelectedMol(m)}
                    className={`p-5 rounded-2xl border transition-all cursor-pointer ${
                      isSelected 
                        ? 'bg-slate-900 border-purple-500/50 shadow-xl ring-1 ring-purple-500/30' 
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                      <div>
                        <h3 className="text-sm font-semibold text-white">{m.name}</h3>
                        <p className="text-xs text-slate-400 font-mono mt-0.5">{m.smiles}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-1 rounded bg-purple-950/60 border border-purple-800/50 text-purple-300 font-mono text-xs font-semibold">
                          ΔG {m.affinity} kcal/mol
                        </span>
                        <span className="px-2 py-1 rounded bg-emerald-950/60 border border-emerald-800/50 text-emerald-300 font-mono text-xs font-semibold">
                          QED {m.qed}
                        </span>
                      </div>
                    </div>

                    {/* Metric Grids */}
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-3 text-xs">
                      <div className="p-2 rounded bg-slate-950/60 border border-slate-800/80">
                        <div className="text-slate-500 text-[10px]">Mol Weight</div>
                        <div className="font-mono text-white mt-0.5">{m.mw} g/mol</div>
                      </div>
                      <div className="p-2 rounded bg-slate-950/60 border border-slate-800/80">
                        <div className="text-slate-500 text-[10px]">LogP</div>
                        <div className="font-mono text-white mt-0.5">{m.logp}</div>
                      </div>
                      <div className="p-2 rounded bg-slate-950/60 border border-slate-800/80">
                        <div className="text-slate-500 text-[10px]">Synth Access (SA)</div>
                        <div className="font-mono text-emerald-400 mt-0.5">{m.sa} (Easy)</div>
                      </div>
                      <div className="p-2 rounded bg-slate-950/60 border border-slate-800/80">
                        <div className="text-slate-500 text-[10px]">Lipinski Ro5</div>
                        <div className="font-mono text-emerald-400 mt-0.5">0 Violations</div>
                      </div>
                      <div className="p-2 rounded bg-slate-950/60 border border-slate-800/80">
                        <div className="text-slate-500 text-[10px]">Intest. Absorpt.</div>
                        <div className="font-mono text-cyan-400 mt-0.5">{m.admet.hia}%</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Col: ADMET Pharmacokinetic Profile */}
          <div className="space-y-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-semibold text-white">ADMET Safety Scorecard</h3>
              </div>

              <div className="space-y-3 text-xs">
                <div className="flex justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-slate-400">Human Intestinal Absorption (HIA):</span>
                  <span className="font-mono text-emerald-400 font-semibold">94.2% (High)</span>
                </div>
                <div className="flex justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-slate-400">Blood-Brain Barrier (BBB):</span>
                  <span className="font-mono text-white font-semibold">0.35 logBB</span>
                </div>
                <div className="flex justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-slate-400">hERG Cardiotoxicity:</span>
                  <span className="font-mono text-emerald-400 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Clean (Low Risk)
                  </span>
                </div>
                <div className="flex justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-slate-400">CYP3A4 / CYP2D6 Inhibition:</span>
                  <span className="font-mono text-emerald-400 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Non-Inhibitor
                  </span>
                </div>
                <div className="flex justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-slate-400">Plasma Protein Binding:</span>
                  <span className="font-mono text-cyan-400 font-semibold">86.5%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Antibody Engineering View */
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Dna className="w-5 h-5 text-pink-400" />
              Engineered Antibody CDR-H3 Affinity Maturation
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {antibodies.map((ab) => (
                <div key={ab.id} className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 hover:border-pink-500/40 transition space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white text-sm">{ab.variant}</span>
                    <span className="px-2 py-0.5 rounded bg-pink-500/20 text-pink-300 text-xs font-mono">
                      Kd = {ab.kd} nM
                    </span>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                    <div className="text-slate-500 text-[10px]">Engineered CDR-H3 Loop:</div>
                    <div className="font-mono text-cyan-300 font-semibold">{ab.cdr_h3}</div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                    <div>Thermal Stability Tm:</div>
                    <div className="font-mono text-emerald-400 text-right">{ab.tm} °C</div>
                    <div>Humanness Score:</div>
                    <div className="font-mono text-white text-right">{(ab.humanness * 100).toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerativeChemistryPage;
