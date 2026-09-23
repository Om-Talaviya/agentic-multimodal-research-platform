import React, { useState } from 'react';
import {
  ShieldCheck,
  Activity,
  Layers,
  Sparkles,
  Search,
  Sliders,
  CheckCircle2,
  BarChart3,
  Flame,
  Award,
  Share2,
  Cpu,
  Target
} from 'lucide-react';

interface MaturationVariant {
  variant_id: string;
  cdr_region: string;
  mutations: string;
  ddg: number;
  kd_nm: number;
  developability: boolean;
}

interface ParatopeContact {
  antibody_residue: string;
  antigen_residue: string;
  interaction_type: string;
  distance: number;
  energy_kcal: number;
}

export const AntibodyMaturationStudioPage: React.FC = () => {
  const [candidateName, setCandidateName] = useState('mAb-EGFRvIII-Lead-01');
  const [targetAntigen, setTargetAntigen] = useState('EGFRvIII Deletion Mutant');
  const [parentalKd, setParentalKd] = useState(18.5);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'variants' | 'contacts' | 'developability'>('variants');

  const [maturedKd, setMaturedKd] = useState(0.12);
  const [foldGain, setFoldGain] = useState(154.2);
  const [oasisScore, setOasisScore] = useState(0.92);

  const [variants, setVariants] = useState<MaturationVariant[]>([
    {
      variant_id: 'VAR_CDR-H3_Y102W',
      cdr_region: 'CDR-H3',
      mutations: 'Y102W, T104R',
      ddg: -3.12,
      kd_nm: 0.12,
      developability: true,
    },
    {
      variant_id: 'VAR_CDR-H2_S54Y',
      cdr_region: 'CDR-H2',
      mutations: 'S54Y',
      ddg: -2.45,
      kd_nm: 0.28,
      developability: true,
    },
    {
      variant_id: 'VAR_CDR-L3_A91F',
      cdr_region: 'CDR-L3',
      mutations: 'A91F',
      ddg: -2.15,
      kd_nm: 0.35,
      developability: true,
    },
  ]);

  const [contacts, setContacts] = useState<ParatopeContact[]>([
    {
      antibody_residue: 'Trp102H',
      antigen_residue: 'Leu314Antigen',
      interaction_type: 'PiStacking',
      distance: 3.15,
      energy_kcal: -2.25,
    },
    {
      antibody_residue: 'Arg104H',
      antigen_residue: 'Glu318Antigen',
      interaction_type: 'SaltBridge',
      distance: 2.74,
      energy_kcal: -3.15,
    },
    {
      antibody_residue: 'Tyr54H',
      antigen_residue: 'Lys322Antigen',
      interaction_type: 'HydrogenBond',
      distance: 2.89,
      energy_kcal: -1.75,
    },
  ]);

  const handleRunMaturation = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Phase 127
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Biotherapeutics & Directed Evolution
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-2 flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-emerald-400" />
            Autonomous In-Silico Antibody Affinity Maturation Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            AID-targeted somatic hypermutation simulation, $\Delta\Delta G$ free energy scoring, and Oasis humanness developability filtering.
          </p>
        </div>

        <button
          onClick={handleRunMaturation}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-5 py-2.5 rounded-lg font-medium transition shadow-lg shadow-emerald-900/30 disabled:opacity-50"
        >
          {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          {loading ? 'Evolving CDR Loops...' : 'Run Affinity Maturation'}
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <Target className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Matured Binding Kd</div>
            <div className="text-xl font-bold text-white">{maturedKd} nM</div>
            <div className="text-[11px] text-emerald-400 mt-0.5">Parental: {parentalKd} nM ({foldGain}x gain)</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Oasis Humanness</div>
            <div className="text-xl font-bold text-white">{(oasisScore * 100).toFixed(0)}%</div>
            <div className="text-[11px] text-blue-400 mt-0.5">Zero Immunogenicity Flags</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-purple-500/10 text-purple-400 rounded-lg">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Paratope Contacts</div>
            <div className="text-xl font-bold text-white">{contacts.length} Strong Interacting</div>
            <div className="text-[11px] text-purple-400 mt-0.5">Salt bridges & Pi-stacking</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Thermostability Tm</div>
            <div className="text-xl font-bold text-white">76.8 °C</div>
            <div className="text-[11px] text-amber-400 mt-0.5">Optimal Bioprocess Stability</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-800 mb-6">
        <button
          onClick={() => setActiveTab('variants')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'variants'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Evolved CDR Variants ({variants.length})
        </button>
        <button
          onClick={() => setActiveTab('contacts')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'contacts'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Paratope-Epitope Interfaces ({contacts.length})
        </button>
        <button
          onClick={() => setActiveTab('developability')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'developability'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Developability & Viscosity Matrix
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'variants' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">Top In-Silico Evolved Candidates</h2>
            <span className="text-xs text-slate-400">Ranked by predicted binding affinity</span>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3">Variant ID</th>
                <th className="px-4 py-3">CDR Loop</th>
                <th className="px-4 py-3">Mutations</th>
                <th className="px-4 py-3">Binding ΔΔG</th>
                <th className="px-4 py-3">Predicted Kd</th>
                <th className="px-4 py-3">Developability</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {variants.map((v, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 text-emerald-400 font-medium">{v.variant_id}</td>
                  <td className="px-4 py-3 text-white font-bold font-sans">{v.cdr_region}</td>
                  <td className="px-4 py-3 text-slate-300">{v.mutations}</td>
                  <td className="px-4 py-3 text-cyan-400 font-bold">{v.ddg} kcal/mol</td>
                  <td className="px-4 py-3 text-amber-400 font-bold">{v.kd_nm} nM</td>
                  <td className="px-4 py-3 font-sans">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      Passed Screen
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'contacts' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">Residue-Level Contact Energetics</h2>
            <span className="text-xs text-slate-400">Structural binding pocket interface</span>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3">Antibody Residue</th>
                <th className="px-4 py-3">Antigen Residue</th>
                <th className="px-4 py-3">Interaction Type</th>
                <th className="px-4 py-3">Distance (Å)</th>
                <th className="px-4 py-3">Energy Contribution</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {contacts.map((c, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 text-emerald-400 font-medium">{c.antibody_residue}</td>
                  <td className="px-4 py-3 text-white font-bold">{c.antigen_residue}</td>
                  <td className="px-4 py-3 font-sans">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      {c.interaction_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-300">{c.distance} Å</td>
                  <td className="px-4 py-3 text-amber-400 font-bold">{c.energy_kcal} kcal/mol</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'developability' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center">
          <div className="max-w-md mx-auto py-8">
            <ShieldCheck className="w-12 h-12 text-emerald-400 mx-auto mb-3 opacity-80" />
            <h3 className="text-base font-semibold text-white">Biophysical Liability Assessment</h3>
            <p className="text-slate-400 text-xs mt-1">
              Evaluates post-translational modification (PTM) motifs, deamidation (NG), isomerization (DG), and hydrophobic patches.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AntibodyMaturationStudioPage;
