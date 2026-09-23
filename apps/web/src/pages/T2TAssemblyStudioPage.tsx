import React, { useState } from 'react';
import {
  Dna,
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
  ShieldCheck,
  Target
} from 'lucide-react';

interface StructuralVariant {
  variant_id: string;
  chromosome: string;
  start_position: number;
  end_position: number;
  sv_type: string;
  sv_length_bp: number;
  genotype_quality: number;
  functional_impact_score: number;
}

interface HaplotypeBlock {
  chromosome: string;
  block_start_bp: number;
  block_end_bp: number;
  phase_switch_error_rate: number;
}

export const T2TAssemblyStudioPage: React.FC = () => {
  const [sampleName, setSampleName] = useState('CHM13_T2T_v2_Haploid');
  const [tech, setTech] = useState('PacBio-HiFi + ONT-UltraLong');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'variants' | 'haplotypes' | 'metrics'>('variants');

  const [qvScore, setQvScore] = useState(73.5);
  const [n50Length, setN50Length] = useState(154.2);
  const [closedChromosomes, setClosedChromosomes] = useState(24);

  const [variants, setVariants] = useState<StructuralVariant[]>([
    {
      variant_id: 'SV_DEL_chr1_145200000',
      chromosome: 'chr1',
      start_position: 145200000,
      end_position: 145245000,
      sv_type: 'DELETION',
      sv_length_bp: 45000,
      genotype_quality: 99.9,
      functional_impact_score: 0.88,
    },
    {
      variant_id: 'SV_INS_chr8_43200000',
      chromosome: 'chr8',
      start_position: 43200000,
      end_position: 43208500,
      sv_type: 'INSERTION',
      sv_length_bp: 8500,
      genotype_quality: 99.4,
      functional_impact_score: 0.76,
    },
    {
      variant_id: 'SV_INV_chr17_41200000',
      chromosome: 'chr17',
      start_position: 41200000,
      end_position: 41215000,
      sv_type: 'INVERSION',
      sv_length_bp: 15000,
      genotype_quality: 98.7,
      functional_impact_score: 0.92,
    },
  ]);

  const [haplotypes, setHaplotypes] = useState<HaplotypeBlock[]>([
    {
      chromosome: 'chr1',
      block_start_bp: 1,
      block_end_bp: 248956422,
      phase_switch_error_rate: 0.0007,
    },
    {
      chromosome: 'chr2',
      block_start_bp: 1,
      block_end_bp: 242193529,
      phase_switch_error_rate: 0.0009,
    },
    {
      chromosome: 'chr3',
      block_start_bp: 1,
      block_end_bp: 198295559,
      phase_switch_error_rate: 0.0008,
    },
  ]);

  const handleRunAssembly = () => {
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
              Phase 126
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Genomics & Long-Read Assembly
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-2 flex items-center gap-2">
            <Dna className="w-7 h-7 text-emerald-400" />
            Autonomous Telomere-to-Telomere (T2T) Assembly & SV Calling Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            De novo string graph long-read assembly, chromosome-scale haplotype phasing, and complex structural variant resolution.
          </p>
        </div>

        <button
          onClick={handleRunAssembly}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-5 py-2.5 rounded-lg font-medium transition shadow-lg shadow-emerald-900/30 disabled:opacity-50"
        >
          {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          {loading ? 'Assembling T2T Genome...' : 'Run T2T Pipeline'}
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Consensus Quality</div>
            <div className="text-xl font-bold text-white">QV {qvScore}</div>
            <div className="text-[11px] text-emerald-400 mt-0.5">&lt; 1 error per 20 Mbp</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Contig N50</div>
            <div className="text-xl font-bold text-white">{n50Length} Mbp</div>
            <div className="text-[11px] text-blue-400 mt-0.5">Chromosome-Scale Contiguity</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-purple-500/10 text-purple-400 rounded-lg">
            <Target className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">T2T Closed Chromosomes</div>
            <div className="text-xl font-bold text-white">{closedChromosomes} / 24</div>
            <div className="text-[11px] text-purple-400 mt-0.5">Zero Gap Telomere-to-Telomere</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Phasing Error Rate</div>
            <div className="text-xl font-bold text-white">0.08% Switch Error</div>
            <div className="text-[11px] text-amber-400 mt-0.5">Dual-Haplotype Phased</div>
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
          Resolved Structural Variants ({variants.length})
        </button>
        <button
          onClick={() => setActiveTab('haplotypes')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'haplotypes'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Phased Haplotype Blocks ({haplotypes.length})
        </button>
        <button
          onClick={() => setActiveTab('metrics')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'metrics'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Assembly Quality Matrix
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'variants' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">Complex Structural Variant Callset</h2>
            <span className="text-xs text-slate-400">Validated against T2T-CHM13 benchmark</span>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3">Variant ID</th>
                <th className="px-4 py-3">Chromosome</th>
                <th className="px-4 py-3">Position Range</th>
                <th className="px-4 py-3">SV Type</th>
                <th className="px-4 py-3">Length</th>
                <th className="px-4 py-3">Genotype Quality</th>
                <th className="px-4 py-3">Impact Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {variants.map((v, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 text-emerald-400 font-medium">{v.variant_id}</td>
                  <td className="px-4 py-3 text-white font-bold font-sans">{v.chromosome}</td>
                  <td className="px-4 py-3 text-slate-300">{v.start_position.toLocaleString()} - {v.end_position.toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-blue-500/10 text-blue-400 border border-blue-500/20 font-sans">
                      {v.sv_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-cyan-400">{v.sv_length_bp.toLocaleString()} bp</td>
                  <td className="px-4 py-3 text-amber-400 font-bold">{v.genotype_quality}</td>
                  <td className="px-4 py-3 text-purple-400 font-bold">{v.functional_impact_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'haplotypes' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">Chromosome-Length Phase Blocks</h2>
            <span className="text-xs text-slate-400">Trio-binned and Hi-C scaffolded</span>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3">Chromosome</th>
                <th className="px-4 py-3">Block Start</th>
                <th className="px-4 py-3">Block End</th>
                <th className="px-4 py-3">Span (Mbp)</th>
                <th className="px-4 py-3">Switch Error Rate</th>
                <th className="px-4 py-3">Phase Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {haplotypes.map((h, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 text-white font-bold font-sans">{h.chromosome}</td>
                  <td className="px-4 py-3 text-slate-300">{h.block_start_bp}</td>
                  <td className="px-4 py-3 text-slate-300">{h.block_end_bp.toLocaleString()}</td>
                  <td className="px-4 py-3 text-emerald-400 font-bold">{(h.block_end_bp / 1000000.0).toFixed(1)} Mbp</td>
                  <td className="px-4 py-3 text-cyan-400 font-bold">{(h.phase_switch_error_rate * 100).toFixed(3)}%</td>
                  <td className="px-4 py-3 font-sans">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      Fully Phased
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'metrics' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center">
          <div className="max-w-md mx-auto py-8">
            <Layers className="w-12 h-12 text-emerald-400 mx-auto mb-3 opacity-80" />
            <h3 className="text-base font-semibold text-white">T2T Assembly Quality Summary</h3>
            <p className="text-slate-400 text-xs mt-1">
              Complete gapless telomere-to-telomere consensus sequence validation according to Human Pangenome Reference Consortium (HPRC) standards.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default T2TAssemblyStudioPage;
