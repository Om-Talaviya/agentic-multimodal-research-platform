import React, { useState } from 'react';
import {
  Layers,
  Activity,
  Sparkles,
  Search,
  Sliders,
  CheckCircle2,
  BarChart3,
  Flame,
  Award,
  Share2,
  Cpu,
  Target,
  Dna,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle
} from 'lucide-react';

interface AlleleProfile {
  hla_gene: string;
  allele_name: string;
  baf_tumor: number;
  estimated_copy_number: number;
  loh_status: string;
}

export const HLALOHResistanceStudioPage: React.FC = () => {
  const [patientId, setPatientId] = useState('PT_MEL_401');
  const [tumorType, setTumorType] = useState('Cutaneous Melanoma');
  const [tumorPurity, setTumorPurity] = useState(0.68);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'alleles' | 'evasion' | 'rescue'>('alleles');

  const [alleles] = useState<AlleleProfile[]>([
    {
      hla_gene: 'HLA-A',
      allele_name: 'HLA-A*02:01',
      baf_tumor: 0.06,
      estimated_copy_number: 0.38,
      loh_status: 'DELETED',
    },
    {
      hla_gene: 'HLA-A',
      allele_name: 'HLA-A*24:02',
      baf_tumor: 0.94,
      estimated_copy_number: 1.54,
      loh_status: 'AMPLIFIED_HOMOZYGOUS',
    },
    {
      hla_gene: 'HLA-B',
      allele_name: 'HLA-B*07:02',
      baf_tumor: 0.48,
      estimated_copy_number: 1.0,
      loh_status: 'RETAINED',
    },
    {
      hla_gene: 'HLA-B',
      allele_name: 'HLA-B*44:02',
      baf_tumor: 0.52,
      estimated_copy_number: 1.0,
      loh_status: 'RETAINED',
    },
    {
      hla_gene: 'HLA-C',
      allele_name: 'HLA-C*07:01',
      baf_tumor: 0.08,
      estimated_copy_number: 0.39,
      loh_status: 'DELETED',
    },
    {
      hla_gene: 'HLA-C',
      allele_name: 'HLA-C*04:01',
      baf_tumor: 0.92,
      estimated_copy_number: 1.54,
      loh_status: 'AMPLIFIED_HOMOZYGOUS',
    },
  ]);

  const handleRunEvaluation = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 700);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-gradient-to-r from-slate-900 via-amber-950 to-slate-900 p-6 rounded-2xl border border-amber-800/40 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/20 rounded-lg border border-amber-400/30 text-amber-300">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              HLA Loss of Heterozygosity (LOH) Studio
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Phase 135: Allele-Specific Copy Number Calling & Neoantigen Immune Evasion / Checkpoint Resistance Engine
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRunEvaluation}
            disabled={loading}
            className="flex items-center gap-2 bg-amber-600 hover:bg-amber-500 text-white px-5 py-2.5 rounded-xl font-medium shadow-lg shadow-amber-600/20 transition-all cursor-pointer"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Evaluating Alleles...' : 'Run HLA LOH Call'}
          </button>
        </div>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Patient Sample ID</label>
          <input
            type="text"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Tumor Histology</label>
          <input
            type="text"
            value={tumorType}
            onChange={(e) => setTumorType(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Tumor Purity Estimate</label>
          <input
            type="number"
            step="0.01"
            value={tumorPurity}
            onChange={(e) => setTumorPurity(parseFloat(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
          />
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 p-4 rounded-xl border border-amber-900/40">
          <div className="text-xs text-slate-400 font-medium">Focal HLA LOH Status</div>
          <div className="text-2xl font-bold text-rose-400 mt-1">2 Alleles Deleted</div>
          <div className="text-xs text-rose-500 mt-1">HLA-A*02:01, HLA-C*07:01</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-amber-900/40">
          <div className="text-xs text-slate-400 font-medium">Immune Evasion Index</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">0.78 / 1.0</div>
          <div className="text-xs text-amber-500 mt-1">High Risk of Anti-PD1 Failure</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-amber-900/40">
          <div className="text-xs text-slate-400 font-medium">Neoantigen Loss</div>
          <div className="text-2xl font-bold text-white mt-1">33.3%</div>
          <div className="text-xs text-slate-400 mt-1">Class I Restricted Clones</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-amber-900/40">
          <div className="text-xs text-slate-400 font-medium">NK-Cell Susceptibility</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">65% Active</div>
          <div className="text-xs text-emerald-400 mt-1">KIR 'Missing-Self' Trigger</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-6">
        <button
          onClick={() => setActiveTab('alleles')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'alleles'
              ? 'border-b-2 border-amber-500 text-amber-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Allele Copy Number Calls ({alleles.length})
        </button>
        <button
          onClick={() => setActiveTab('evasion')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'evasion'
              ? 'border-b-2 border-amber-500 text-amber-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Evasion Mechanics & Checkpoint Risk
        </button>
      </div>

      {/* Content */}
      {activeTab === 'alleles' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-semibold">
              <tr>
                <th className="p-4">Gene</th>
                <th className="p-4">Allele Identifier</th>
                <th className="p-4">Tumor BAF</th>
                <th className="p-4">Estimated Copy Number</th>
                <th className="p-4">LOH Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {alleles.map((a) => (
                <tr key={a.allele_name} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-4 font-mono font-medium text-amber-400">{a.hla_gene}</td>
                  <td className="p-4 font-mono text-white">{a.allele_name}</td>
                  <td className="p-4 font-mono">{a.baf_tumor}</td>
                  <td className="p-4 font-mono">{a.estimated_copy_number}</td>
                  <td className="p-4">
                    <span
                      className={`text-xs px-2.5 py-1 rounded font-semibold ${
                        a.loh_status === 'DELETED'
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : a.loh_status === 'RETAINED'
                          ? 'bg-emerald-950 text-emerald-300'
                          : 'bg-indigo-950 text-indigo-300'
                      }`}
                    >
                      {a.loh_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'evasion' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-lg font-bold text-white">Immunotherapy Escape Mechanism</h3>
            <p className="text-sm text-slate-300 leading-relaxed">
              Deletion of <span className="font-mono text-rose-400">HLA-A*02:01</span> abolishes presentation of high-affinity driver neoepitopes, permitting clonal outgrowth under anti-PD1 selective pressure.
            </p>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="text-xs text-slate-400 font-semibold uppercase">Recommended Synthetic Rescue Strategy</div>
              <div className="text-sm font-medium text-emerald-400">
                1. Missing-self NK cell engagers (anti-KIR / anti-NKG2A BiKE)
              </div>
              <div className="text-sm font-medium text-indigo-400">
                2. Switch to MHC Class II-restricted CD4+ neoantigen vaccination
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
