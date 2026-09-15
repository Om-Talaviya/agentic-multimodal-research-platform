import React, { useState } from 'react';
import { 
  Layers, 
  Share2, 
  MapPin, 
  Sparkles, 
  Download, 
  Activity, 
  Info,
  Maximize2,
  RefreshCw,
  Eye,
  Crosshair
} from 'lucide-react';

interface SpatialSpot {
  id: string;
  barcode: string;
  x: number;
  y: number;
  cluster: string;
  color: string;
  proximity: number;
  genes: number;
}

interface SpatialDomain {
  id: string;
  name: string;
  type: string;
  color: string;
  spots: number;
  percentage: number;
  markers: string[];
}

interface CommPair {
  pathway: string;
  ligand: string;
  receptor: string;
  source: string;
  target: string;
  score: number;
  distance: number;
}

export const SpatialTranscriptomicsPage: React.FC = () => {
  const [selectedTissue, setSelectedTissue] = useState('Glioblastoma Multiforme (GBM)');
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [activeSpot, setActiveSpot] = useState<SpatialSpot | null>(null);

  const domains: SpatialDomain[] = [
    { id: 'dom_1', name: 'Tumor Core', type: 'tumor', color: '#ef4444', spots: 68, percentage: 34.0, markers: ['MKI67', 'EPCAM', 'EGFR', 'MYC'] },
    { id: 'dom_2', name: 'Invasive Margin', type: 'invasive_front', color: '#f97316', spots: 54, percentage: 27.0, markers: ['MMP9', 'VIM', 'SNAI1', 'TWIST1'] },
    { id: 'dom_3', name: 'Cancer-Associated Stroma', type: 'stroma', color: '#8b5cf6', spots: 48, percentage: 24.0, markers: ['ACTA2', 'COL1A1', 'FAP', 'POSTN'] },
    { id: 'dom_4', name: 'Tertiary Lymphoid Structure', type: 'immune_infiltrate', color: '#10b981', spots: 30, percentage: 15.0, markers: ['CD3E', 'CD8A', 'MS4A1', 'CXCL13'] },
  ];

  const comms: CommPair[] = [
    { pathway: 'VEGF', ligand: 'VEGFA', receptor: 'FLT1', source: 'Tumor Core', target: 'Invasive Margin', score: 0.941, distance: 60 },
    { pathway: 'TGFb', ligand: 'TGFB1', receptor: 'TGFBR2', source: 'Stroma', target: 'Invasive Margin', score: 0.892, distance: 85 },
    { pathway: 'WNT', ligand: 'WNT5A', receptor: 'FZD5', source: 'Invasive Margin', target: 'Tumor Core', score: 0.812, distance: 70 },
    { pathway: 'CXCL', ligand: 'CXCL12', receptor: 'CXCR4', source: 'Stroma', target: 'Tertiary Lymphoid Structure', score: 0.784, distance: 110 },
    { pathway: 'NOTCH', ligand: 'JAG1', receptor: 'NOTCH1', source: 'Tumor Core', target: 'Stroma', score: 0.725, distance: 95 },
  ];

  // Generate sample spots for the 2D histological canvas
  const spots: SpatialSpot[] = Array.from({ length: 200 }).map((_, i) => {
    const row = Math.floor(i / 15);
    const col = i % 15;
    const x = 50 + col * 36 + (Math.sin(i * 99) * 4);
    const y = 50 + row * 36 + (Math.cos(i * 77) * 4);
    
    // Proximity to center (300, 300)
    const dist = Math.sqrt((x - 300) ** 2 + (y - 300) ** 2);
    let dom = domains[2];
    if (dist < 100) dom = domains[0];
    else if (dist < 170) dom = domains[1];
    else if (x < 180 && y > 380) dom = domains[3];

    return {
      id: `spot_${i}`,
      barcode: `AAACAAC-${row.toString().padStart(2, '0')}-${col.toString().padStart(2, '0')}-1`,
      x,
      y,
      cluster: dom.name,
      color: dom.color,
      proximity: Math.max(0, Math.min(1, 1 - dist / 300)),
      genes: 1200 + Math.floor(Math.sin(i) * 300),
    };
  });

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 text-cyan-400">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Spatial Transcriptomics & Tissue Microenvironment Studio
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  Generation 16 • Phase 42
                </span>
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                10x Visium / MERFISH coordinate mapping, histological tissue domains, and cell-cell ligand-receptor signaling networks.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <select 
            value={selectedTissue} 
            onChange={(e) => setSelectedTissue(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            <option>Glioblastoma Multiforme (GBM)</option>
            <option>Hepatocellular Carcinoma (HCC)</option>
            <option>Triple-Negative Breast Cancer (TNBC)</option>
            <option>Colorectal Adenocarcinoma (CRC)</option>
          </select>
          <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-cyan-500/20">
            <RefreshCw className="w-4 h-4" />
            Recompute Signaling
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: 2D Spatial Histological Slide Canvas */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <MapPin className="w-5 h-5 text-cyan-400" />
                <h3 className="text-lg font-semibold text-white">Histological Spatial Spot Canvas</h3>
                <span className="text-xs text-slate-400 ml-2">200 Coordinated Spots • 55µm Resolution</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Crosshair className="w-4 h-4 text-slate-400" />
                Click spot to inspect coordinates
              </div>
            </div>

            {/* SVG Spatial Canvas */}
            <div className="relative bg-slate-950/80 rounded-xl border border-slate-800/80 p-4 flex items-center justify-center overflow-hidden">
              <svg viewBox="0 0 600 550" className="w-full h-[460px] select-none">
                {/* Simulated Tissue Background Gradient */}
                <circle cx="300" cy="275" r="240" fill="#0f172a" stroke="#1e293b" strokeWidth="2" strokeDasharray="6 6" />
                <circle cx="300" cy="275" r="140" fill="#1e1b4b" opacity="0.3" />
                <circle cx="300" cy="275" r="70" fill="#450a0a" opacity="0.4" />

                {/* Spatial Spots */}
                {spots.map((s) => {
                  const isHovered = activeSpot?.id === s.id;
                  const isDimmed = selectedDomain && s.cluster !== selectedDomain;

                  return (
                    <circle
                      key={s.id}
                      cx={s.x}
                      cy={s.y}
                      r={isHovered ? 8 : 5}
                      fill={s.color}
                      opacity={isDimmed ? 0.2 : (isHovered ? 1 : 0.85)}
                      stroke={isHovered ? '#ffffff' : '#0f172a'}
                      strokeWidth={isHovered ? 2 : 1}
                      className="cursor-pointer transition-all duration-150"
                      onClick={() => setActiveSpot(s)}
                    />
                  );
                })}
              </svg>

              {/* Spot Inspector Popup */}
              {activeSpot && (
                <div className="absolute top-4 right-4 bg-slate-900/90 border border-slate-700 rounded-xl p-4 shadow-2xl backdrop-blur-md w-64 text-xs space-y-2">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="font-semibold text-white">Spot Inspector</span>
                    <span className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300">{activeSpot.barcode}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-1 text-slate-300">
                    <div>Coordinates:</div>
                    <div className="font-mono text-white text-right">({activeSpot.x.toFixed(1)}, {activeSpot.y.toFixed(1)})</div>
                    <div>Domain:</div>
                    <div className="text-right text-cyan-400">{activeSpot.cluster}</div>
                    <div>Detected Genes:</div>
                    <div className="font-mono text-white text-right">{activeSpot.genes}</div>
                    <div>Tumor Proximity:</div>
                    <div className="font-mono text-emerald-400 text-right">{(activeSpot.proximity * 100).toFixed(1)}%</div>
                  </div>
                </div>
              )}
            </div>

            {/* Spatial Domains Legend */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
              {domains.map((dom) => (
                <button
                  key={dom.id}
                  onClick={() => setSelectedDomain(selectedDomain === dom.name ? null : dom.name)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    selectedDomain === dom.name 
                      ? 'bg-slate-800 border-cyan-500/50 shadow-md ring-1 ring-cyan-500/30' 
                      : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: dom.color }} />
                    <span className="text-xs font-semibold text-white truncate">{dom.name}</span>
                  </div>
                  <div className="flex items-center justify-between mt-1 text-[11px] text-slate-400">
                    <span>{dom.spots} spots</span>
                    <span className="font-mono text-slate-300">{dom.percentage}%</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Marker Genes Table */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <h3 className="text-base font-semibold text-white mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              Spatial Domain Top Marker Genes
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {domains.map((d) => (
                <div key={d.id} className="p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-white flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: d.color }} />
                      {d.name}
                    </span>
                    <span className="text-slate-400 uppercase tracking-wider text-[10px]">{d.type}</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {d.markers.map((m) => (
                      <span key={m} className="px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700/60 text-xs font-mono text-cyan-300">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Ligand-Receptor Cell-Cell Communications */}
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-emerald-400" />
                <h3 className="text-lg font-semibold text-white">Ligand-Receptor Crosstalk</h3>
              </div>
              <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                CellChat / CellPhoneDB
              </span>
            </div>

            <div className="space-y-3">
              {comms.map((c, i) => (
                <div key={i} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-cyan-500/40 transition space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-white flex items-center gap-1">
                      <span className="text-cyan-400 font-mono">{c.ligand}</span>
                      <span className="text-slate-500">→</span>
                      <span className="text-emerald-400 font-mono">{c.receptor}</span>
                    </span>
                    <span className="font-mono text-cyan-300 text-xs bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-800/50">
                      Score {(c.score).toFixed(3)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span className="truncate max-w-[120px]">{c.source}</span>
                    <span className="text-slate-600">to</span>
                    <span className="truncate max-w-[120px] text-right">{c.target}</span>
                  </div>

                  {/* Progress Score Bar */}
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-cyan-500 to-emerald-500 h-full rounded-full" 
                      style={{ width: `${c.score * 100}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                    <span>Pathway: {c.pathway}</span>
                    <span>Distance: {c.distance} µm</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tumor Infiltration & Gradients Card */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Info className="w-4 h-4 text-cyan-400" />
              Microenvironment Metrics
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">Invasive Front Thickness:</span>
                <span className="font-mono text-white font-semibold">145 µm</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">TLS Immune Infiltration Score:</span>
                <span className="font-mono text-emerald-400 font-semibold">0.862 (High)</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">Hypoxic Core Volume:</span>
                <span className="font-mono text-red-400 font-semibold">34.2%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpatialTranscriptomicsPage;
