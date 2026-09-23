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
  Dna
} from 'lucide-react';

interface AntibodyTag {
  tag_barcode: string;
  marker_name: string;
  clone_id: string;
  snr: number;
}

interface ProteinExpression {
  cell_cluster: string;
  marker: string;
  dsb_expression: number;
  rna_tpm: number;
  rho: number;
}

export const CITEseqStudioPage: React.FC = () => {
  const [sampleName, setSampleName] = useState('Melanoma_TIL_CITEseq_54P');
  const [tissueOrigin, setTissueOrigin] = useState('Melanoma Tumor Infiltrating Lymphocytes');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'expressions' | 'antibodies' | 'wnn'>('expressions');

  const [totalCells, setTotalCells] = useState(14500);
  const [panelSize, setPanelSize] = useState(54);
  const [proteinWeight, setProteinWeight] = useState(0.58);

  const [antibodies, setAntibodies] = useState<AntibodyTag[]>([
    {
      tag_barcode: 'TotalSeq-C-CD8a',
      marker_name: 'CD8a',
      clone_id: 'RPA-T8',
      snr: 18.4,
    },
    {
      tag_barcode: 'TotalSeq-C-CD4',
      marker_name: 'CD4',
      clone_id: 'SK3',
      snr: 16.5,
    },
    {
      tag_barcode: 'TotalSeq-C-CD3e',
      marker_name: 'CD3e',
      clone_id: 'UCHT1',
      snr: 15.8,
    },
    {
      tag_barcode: 'TotalSeq-C-PD1',
      marker_name: 'PD-1',
      clone_id: 'EH12.2H7',
      snr: 14.1,
    },
  ]);

  const [expressions, setExpressions] = useState<ProteinExpression[]>([
    {
      cell_cluster: 'Cytotoxic_CD8_T_Cells',
      marker: 'CD8a',
      dsb_expression: 5.42,
      rna_tpm: 245.0,
      rho: 0.84,
    },
    {
      cell_cluster: 'Helper_CD4_T_Cells',
      marker: 'CD4',
      dsb_expression: 4.85,
      rna_tpm: 180.0,
      rho: 0.79,
    },
    {
      cell_cluster: 'Exhausted_T_Cells',
      marker: 'PD-1',
      dsb_expression: 4.12,
      rna_tpm: 45.0,
      rho: 0.68,
    },
    {
      cell_cluster: 'Treg_Subpopulation',
      marker: 'CTLA-4',
      dsb_expression: 3.95,
      rna_tpm: 32.0,
      rho: 0.72,
    },
  ]);

  const handleRunPipeline = () => {
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
              Phase 128
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Single-Cell CITE-seq Multi-Modal
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-2 flex items-center gap-2">
            <Layers className="w-7 h-7 text-emerald-400" />
            Autonomous Single-Cell CITE-seq Surface Protein & mRNA Co-Mapping Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            DSB background-ambient antibody normalization, weighted nearest-neighbor (wNN) multimodal graph fusion, and protein-RNA concordance modeling.
          </p>
        </div>

        <button
          onClick={handleRunPipeline}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-5 py-2.5 rounded-lg font-medium transition shadow-lg shadow-emerald-900/30 disabled:opacity-50"
        >
          {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          {loading ? 'Fusing CITE-seq Modalities...' : 'Run CITE-seq Analysis'}
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <Target className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Total Cells Profiled</div>
            <div className="text-xl font-bold text-white">{totalCells.toLocaleString()}</div>
            <div className="text-[11px] text-emerald-400 mt-0.5">Dual-Assayed Cells</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">ADT Panel Size</div>
            <div className="text-xl font-bold text-white">{panelSize} Surface Markers</div>
            <div className="text-[11px] text-blue-400 mt-0.5">TotalSeq-C Oligo Conjugates</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-purple-500/10 text-purple-400 rounded-lg">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">wNN Modality Balance</div>
            <div className="text-xl font-bold text-white">{(proteinWeight * 100).toFixed(0)}% Protein / {((1 - proteinWeight) * 100).toFixed(0)}% RNA</div>
            <div className="text-[11px] text-purple-400 mt-0.5">Signal-Optimized wNN Graph</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">DSB Signal-to-Noise</div>
            <div className="text-xl font-bold text-white">16.2x Mean SNR</div>
            <div className="text-[11px] text-amber-400 mt-0.5">Background Ambient Denoised</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-800 mb-6">
        <button
          onClick={() => setActiveTab('expressions')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'expressions'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Protein vs RNA Concordance ({expressions.length})
        </button>
        <button
          onClick={() => setActiveTab('antibodies')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'antibodies'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          TotalSeq-C Antibody Tags ({antibodies.length})
        </button>
        <button
          onClick={() => setActiveTab('wnn')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'wnn'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          wNN Multi-Modal Joint Embedding
        </button>
      </div>

      {/* Content */}
      {activeTab === 'expressions' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">Surface Protein & RNA Correlation Matrix</h2>
            <span className="text-xs text-slate-400">DSB normalized expression vs transcriptomic TPM</span>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3">Cell Cluster</th>
                <th className="px-4 py-3">Marker</th>
                <th className="px-4 py-3">DSB Surface Level</th>
                <th className="px-4 py-3">RNA TPM</th>
                <th className="px-4 py-3">Spearman ρ</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {expressions.map((e, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 text-white font-bold font-sans">{e.cell_cluster}</td>
                  <td className="px-4 py-3 text-emerald-400 font-bold">{e.marker}</td>
                  <td className="px-4 py-3 text-cyan-400">{e.dsb_expression}</td>
                  <td className="px-4 py-3 text-slate-300">{e.rna_tpm} TPM</td>
                  <td className="px-4 py-3 text-amber-400 font-bold">+{e.rho}</td>
                  <td className="px-4 py-3 font-sans">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      Concordant
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'antibodies' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">Antibody-Derived Tag (ADT) Quality Control</h2>
            <span className="text-xs text-slate-400">TotalSeq-C oligonucleotide barcodes</span>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3">Tag Barcode</th>
                <th className="px-4 py-3">Marker Target</th>
                <th className="px-4 py-3">Clone ID</th>
                <th className="px-4 py-3">Signal-to-Noise Ratio</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {antibodies.map((a, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 text-emerald-400">{a.tag_barcode}</td>
                  <td className="px-4 py-3 text-white font-bold font-sans">{a.marker_name}</td>
                  <td className="px-4 py-3 text-slate-300">{a.clone_id}</td>
                  <td className="px-4 py-3 text-amber-400 font-bold">{a.snr}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'wnn' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center">
          <div className="max-w-md mx-auto py-8">
            <Layers className="w-12 h-12 text-emerald-400 mx-auto mb-3 opacity-80" />
            <h3 className="text-base font-semibold text-white">wNN Multi-Modal Joint Embedding</h3>
            <p className="text-slate-400 text-xs mt-1">
              Constructs weighted nearest-neighbor graphs fusing RNA transcriptional variance and surface ADT protein markers into a single low-dimensional manifold.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default CITEseqStudioPage;
