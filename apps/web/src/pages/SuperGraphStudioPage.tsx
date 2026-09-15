import React, { useState } from 'react';
import { 
  GitFork, 
  Network, 
  Sparkles, 
  Lightbulb, 
  Compass, 
  CheckCircle2, 
  ArrowRight,
  TrendingUp,
  Activity,
  Layers,
  Database
} from 'lucide-react';

interface SuperNode {
  id: string;
  canonical: string;
  label: string;
  type: 'Gene' | 'Disease' | 'Chemical' | 'Pathway' | 'CellType';
  color: string;
  x: number;
  y: number;
  degree: number;
}

interface SuperEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
  confidence: number;
  predicted: boolean;
}

interface Hypothesis {
  id: string;
  title: string;
  premise: string;
  chain: string[];
  novelty: number;
  plausibility: number;
  experiment: string;
}

export const SuperGraphStudioPage: React.FC = () => {
  const [selectedEntity, setSelectedEntity] = useState('PCSK9');
  const [selectedNode, setSelectedNode] = useState<SuperNode | null>(null);

  const nodes: SuperNode[] = [
    { id: 'n1', canonical: 'HGNC:PCSK9', label: 'PCSK9', type: 'Gene', color: '#ef4444', x: 280, y: 180, degree: 0.38 },
    { id: 'n2', canonical: 'HGNC:LDLR', label: 'LDLR', type: 'Gene', color: '#ef4444', x: 160, y: 110, degree: 0.42 },
    { id: 'n3', canonical: 'MESH:D006528', label: 'Hepatocellular Carcinoma', type: 'Disease', color: '#f97316', x: 420, y: 220, degree: 0.65 },
    { id: 'n4', canonical: 'CHEBI:1234', label: 'Evolocumab', type: 'Chemical', color: '#a855f7', x: 380, y: 80, degree: 0.25 },
    { id: 'n5', canonical: 'KEGG:hsa04151', label: 'PI3K-Akt Pathway', type: 'Pathway', color: '#3b82f6', x: 220, y: 320, degree: 0.58 },
    { id: 'n6', canonical: 'CL:0000182', label: 'Hepatocyte', type: 'CellType', color: '#10b981', x: 120, y: 240, degree: 0.49 },
    { id: 'n7', canonical: 'HGNC:VEGFA', label: 'VEGFA', type: 'Gene', color: '#ef4444', x: 480, y: 340, degree: 0.52 },
  ];

  const edges: SuperEdge[] = [
    { id: 'e1', source: 'n4', target: 'n1', relation: 'INHIBITS', confidence: 0.99, predicted: false },
    { id: 'e2', source: 'n1', target: 'n2', relation: 'DEGRADES', confidence: 0.98, predicted: false },
    { id: 'e3', source: 'n1', target: 'n6', relation: 'EXPRESSED_IN', confidence: 0.95, predicted: false },
    { id: 'e4', source: 'n7', target: 'n3', relation: 'PROMOTES_ANGIOGENESIS', confidence: 0.92, predicted: false },
    { id: 'e5', source: 'n1', target: 'n5', relation: 'CROSS_REGULATES', confidence: 0.86, predicted: true },
  ];

  const hypotheses: Hypothesis[] = [
    {
      id: 'h1',
      title: 'Synergistic PCSK9/PI3K-Akt Co-Targeting in Hypoxic HCC',
      premise: 'Targeting PCSK9 downregulates lysosomal LDLR turnover, simultaneously attenuating lipid raft-associated PI3K/Akt survival cascade in hypoxic hepatocytes.',
      chain: [
        'PCSK9 mAb Inhibition',
        'Membrane LDLR Surface Retention',
        'Lipid Raft Cholesterol Depletion',
        'Downregulation of Phospho-Akt (Ser473)',
        'Sensitization to Kinase Inhibitors (Sorafenib)'
      ],
      novelty: 0.912,
      plausibility: 0.935,
      experiment: 'LNP-CRISPR knockout of PCSK9 in patient-derived HCC organoids under hypoxia with Western blot for p-Akt.',
    },
    {
      id: 'h2',
      title: 'Paracrine VEGF-A/TGF-β Axis Drives Glioblastoma Vasculogenic Mimicry',
      premise: 'Co-localized secretion of VEGF-A from hypoxic core cells and astrocytic TGF-β induces endothelial transdifferentiation of stem cells.',
      chain: [
        'Hypoxia-Induced VEGFA Overexpression',
        'Astrocytic Paracrine TGF-β1 Activation',
        'SNAI1 / TWIST1 Nuclear Translocation',
        'Tubular Vasculogenic Mimicry Formation'
      ],
      novelty: 0.875,
      plausibility: 0.940,
      experiment: 'Spatial transcriptomic Visium co-immunofluorescence for CD133 and VEGFR2 across biopsy slices.',
    }
  ];

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-amber-500/20 to-orange-500/20 border border-amber-500/30 text-amber-400">
              <Network className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Scientific Super-Graph & Hypothesis Discovery Studio
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  Generation 17 • Phase 44
                </span>
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                Cross-domain fusion of omics, chemical structures, and literature with GNN link prediction and autonomous causal hypothesis synthesis.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="text"
            value={selectedEntity}
            onChange={(e) => setSelectedEntity(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber-500 w-44"
            placeholder="Focus Entity (e.g. PCSK9)"
          />
          <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-amber-500/20">
            <Sparkles className="w-4 h-4" />
            Synthesize Hypotheses
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: 2D Interactive Super-Graph Canvas */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-amber-400" />
                <h3 className="text-lg font-semibold text-white">Biomedical Knowledge Super-Graph</h3>
              </div>
              <div className="flex items-center gap-3 text-xs">
                <span className="flex items-center gap-1 text-slate-400">
                  <span className="w-2.5 h-0.5 bg-slate-500" /> Grounded Edge
                </span>
                <span className="flex items-center gap-1 text-amber-400">
                  <span className="w-2.5 h-0.5 bg-amber-400 stroke-dasharray" /> GNN Predicted Link
                </span>
              </div>
            </div>

            {/* SVG Interactive Canvas */}
            <div className="relative bg-slate-950/80 rounded-xl border border-slate-800/80 p-4 flex items-center justify-center overflow-hidden">
              <svg viewBox="0 0 600 420" className="w-full h-[380px] select-none">
                {/* Edges */}
                {edges.map((e) => {
                  const src = nodes.find((n) => n.id === e.source);
                  const tgt = nodes.find((n) => n.id === e.target);
                  if (!src || !tgt) return null;

                  return (
                    <g key={e.id}>
                      <line
                        x1={src.x}
                        y1={src.y}
                        x2={tgt.x}
                        y2={tgt.y}
                        stroke={e.predicted ? '#f59e0b' : '#475569'}
                        strokeWidth={e.predicted ? 2 : 1.5}
                        strokeDasharray={e.predicted ? '4 4' : 'none'}
                        opacity={0.85}
                      />
                      <text
                        x={(src.x + tgt.x) / 2}
                        y={(src.y + tgt.y) / 2 - 4}
                        fill="#94a3b8"
                        fontSize="9"
                        textAnchor="middle"
                        className="font-mono select-none"
                      >
                        {e.relation}
                      </text>
                    </g>
                  );
                })}

                {/* Nodes */}
                {nodes.map((n) => {
                  const isSelected = selectedNode?.id === n.id;

                  return (
                    <g 
                      key={n.id} 
                      className="cursor-pointer transition-transform"
                      onClick={() => setSelectedNode(n)}
                    >
                      <circle
                        cx={n.x}
                        cy={n.y}
                        r={isSelected ? 18 : 14}
                        fill={n.color}
                        stroke={isSelected ? '#ffffff' : '#0f172a'}
                        strokeWidth={isSelected ? 3 : 2}
                        className="transition-all"
                      />
                      <text
                        x={n.x}
                        y={n.y + 24}
                        fill="#ffffff"
                        fontSize="11"
                        fontWeight="600"
                        textAnchor="middle"
                        className="select-none"
                      >
                        {n.label}
                      </text>
                    </g>
                  );
                })}
              </svg>

              {/* Node Inspector Drawer */}
              {selectedNode && (
                <div className="absolute top-4 right-4 bg-slate-900/90 border border-slate-700 rounded-xl p-4 shadow-2xl backdrop-blur-md w-64 text-xs space-y-2">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="font-semibold text-white">Entity Telemetry</span>
                    <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono">{selectedNode.type}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-1 text-slate-300">
                    <div>Canonical ID:</div>
                    <div className="font-mono text-white text-right truncate">{selectedNode.canonical}</div>
                    <div>Degree Centrality:</div>
                    <div className="font-mono text-amber-400 text-right">{selectedNode.degree}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Autonomous Causal Hypotheses */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-400" />
              Autonomous Causal Scientific Hypotheses
            </h2>

            <div className="space-y-4">
              {hypotheses.map((h) => (
                <div key={h.id} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                    <h3 className="text-base font-semibold text-white">{h.title}</h3>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/50 text-amber-300 text-xs font-mono font-semibold">
                        Novelty {(h.novelty * 100).toFixed(1)}%
                      </span>
                      <span className="px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/50 text-emerald-300 text-xs font-mono font-semibold">
                        Plausibility {(h.plausibility * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">{h.premise}</p>

                  {/* Mechanistic Chain Steps */}
                  <div className="space-y-1.5">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      Transitive Mechanistic Chain:
                    </div>
                    <div className="flex flex-wrap items-center gap-2 text-xs">
                      {h.chain.map((step, i) => (
                        <React.Fragment key={i}>
                          <span className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 font-mono text-cyan-300 text-xs">
                            {step}
                          </span>
                          {i < h.chain.length - 1 && <ArrowRight className="w-3.5 h-3.5 text-slate-600" />}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-400 flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="font-semibold text-slate-200">Recommended Validation Experiment: </span>
                      {h.experiment}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Entity & Graph Metrics */}
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Database className="w-4 h-4 text-amber-400" />
              Super-Graph Graph Analytics
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">Total Unified Nodes:</span>
                <span className="font-mono text-white font-semibold">14,280</span>
              </div>
              <div className="flex justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">Total Verified Triples:</span>
                <span className="font-mono text-white font-semibold">89,450</span>
              </div>
              <div className="flex justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">GNN Predicted Novel Links:</span>
                <span className="font-mono text-amber-400 font-semibold">1,420 Links</span>
              </div>
              <div className="flex justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">Average Transitive Path Length:</span>
                <span className="font-mono text-emerald-400 font-semibold">3.4 Hops</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SuperGraphStudioPage;
