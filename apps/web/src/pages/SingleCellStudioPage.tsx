import React, { useState, useEffect, useRef } from 'react';
import {
  Microscope,
  AlertCircle,
  Plus,
  RefreshCw,
  Sparkles,
  TrendingUp,
  BarChart3,
  Flame,
  Clock,
  Compass,
} from 'lucide-react';
import { api } from '../services/api';

interface CellCluster {
  id: string;
  cluster_index: number;
  cell_type_annotation: string;
  cell_count: number;
  percentage_of_total: number;
  top_markers: string[];
}

interface CellCoordinate {
  cell_barcode: string;
  cluster_index: number;
  umap_x: number;
  umap_y: number;
  tsne_x: number;
  tsne_y: number;
  pseudotime: number;
  cell_type: string;
}

interface DifferentialGene {
  id: string;
  cluster_index: number;
  gene_symbol: string;
  log2_fold_change: number;
  p_value: number;
  p_val_adj: number;
  pct_in_cluster: number;
  pct_out_of_cluster: number;
  is_significant: boolean;
}

interface PathwayEnrichment {
  id: string;
  cluster_index: number;
  pathway_name: string;
  database_source: string;
  normalized_enrichment_score: number;
  p_val_adj: number;
  leading_edge_genes: string[];
}

interface SingleCellDataset {
  id: string;
  dataset_title: string;
  organism: string;
  tissue: string;
  sequencing_platform: string;
  total_cells: number;
  total_genes: number;
  clustering_resolution: number;
  clusters_count?: number;
  metadata_json?: Record<string, any>;
  clusters?: CellCluster[];
  differential_genes?: DifferentialGene[];
  pathway_enrichments?: PathwayEnrichment[];
  created_at?: string;
}

const CLUSTER_COLORS = [
  '#38bdf8', // Sky Blue
  '#10b981', // Emerald Green
  '#f59e0b', // Amber
  '#ec4899', // Pink
  '#a855f7', // Purple
  '#ef4444', // Red
  '#06b6d4', // Cyan
  '#84cc16', // Lime
];

const PRESET_DATASETS = [
  {
    title: 'Human Liver Hepatocytes & LNP Uptake Atlas',
    tissue: 'Liver',
    organism: 'Homo sapiens',
    platform: "10x Chromium Next GEM 3' v3.1",
    resolution: 0.5,
    cells: 600,
    desc: 'Targeted PCSK9 silencing and lipid nanoparticle biodistribution in primary hepatocytes and sinusoidal niche.',
  },
  {
    title: 'Human PBMC Immune Subsets Profiling',
    tissue: 'PBMC',
    organism: 'Homo sapiens',
    platform: '10x Chromium 5’ Immune Profiling',
    resolution: 0.6,
    cells: 500,
    desc: 'Deep single-cell immunophenotyping of T cells, B cells, Monocytes, and NK cells.',
  },
];

export const SingleCellStudioPage: React.FC = () => {
  const [datasets, setDatasets] = useState<SingleCellDataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<SingleCellDataset | null>(null);
  const [coordinates, setCoordinates] = useState<CellCoordinate[]>([]);
  const [activeTab, setActiveTab] = useState<'umap' | 'volcano' | 'markers' | 'pseudotime' | 'pathways'>('umap');
  const [projectionMode, setProjectionMode] = useState<'umap' | 'tsne'>('umap');
  const [colorMode, setColorMode] = useState<'cluster' | 'pseudotime'>('cluster');
  const [selectedClusterFilter, setSelectedClusterFilter] = useState<number | 'all'>('all');
  const [hoveredCell, setHoveredCell] = useState<CellCoordinate | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showAnalyzeModal, setShowAnalyzeModal] = useState<boolean>(false);

  // Form State
  const [formTitle, setFormTitle] = useState(PRESET_DATASETS[0].title);
  const [formTissue, setFormTissue] = useState(PRESET_DATASETS[0].tissue);
  const [formOrganism, setFormOrganism] = useState(PRESET_DATASETS[0].organism);
  const [formPlatform, setFormPlatform] = useState(PRESET_DATASETS[0].platform);
  const [formResolution, setFormResolution] = useState(0.5);
  const [formCells, setFormCells] = useState(600);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('/single-cell/datasets');
      const items: SingleCellDataset[] = res.data.items || [];
      setDatasets(items);
      if (items.length > 0 && (!selectedDataset || !items.find(d => d.id === selectedDataset.id))) {
        await loadDatasetDetails(items[0].id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch single-cell datasets');
    } finally {
      setLoading(false);
    }
  };

  const loadDatasetDetails = async (id: string) => {
    try {
      const [resDetails, resCoords] = await Promise.all([
        api.get(`/single-cell/datasets/${id}`),
        api.get(`/single-cell/datasets/${id}/coordinates?limit=2000`),
      ]);
      setSelectedDataset(resDetails.data);
      setCoordinates(resCoords.data.coordinates || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load single-cell dataset details');
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleCreateAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setAnalyzing(true);
      setError(null);
      const payload = {
        dataset_title: formTitle.trim(),
        tissue: formTissue.trim(),
        organism: formOrganism.trim(),
        sequencing_platform: formPlatform.trim(),
        clustering_resolution: formResolution,
        total_cells: formCells,
      };
      const res = await api.post('/single-cell/analyze', payload);
      setShowAnalyzeModal(false);
      await fetchDatasets();
      if (res.data.dataset_id) {
        await loadDatasetDetails(res.data.dataset_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'scRNA-seq analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  // Render 2D Scatter Canvas for UMAP / t-SNE
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || coordinates.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    // Background Grid
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Determine Coordinate Bounds
    const isUmap = projectionMode === 'umap';
    const xs = coordinates.map(c => isUmap ? c.umap_x : c.tsne_x);
    const ys = coordinates.map(c => isUmap ? c.umap_y : c.tsne_y);

    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    const pad = 35;
    const scaleX = (width - pad * 2) / (maxX - minX || 1);
    const scaleY = (height - pad * 2) / (maxY - minY || 1);

    // Render Each Single Cell
    coordinates.forEach(cell => {
      const xVal = isUmap ? cell.umap_x : cell.tsne_x;
      const yVal = isUmap ? cell.umap_y : cell.tsne_y;

      const px = pad + (xVal - minX) * scaleX;
      const py = height - (pad + (yVal - minY) * scaleY);

      const isFiltered = selectedClusterFilter !== 'all' && cell.cluster_index !== selectedClusterFilter;

      let color = CLUSTER_COLORS[cell.cluster_index % CLUSTER_COLORS.length];
      if (colorMode === 'pseudotime') {
        // Gradient from Dark Purple (0.0) -> Cyan -> Yellow (1.0)
        const t = cell.pseudotime;
        const r = Math.round(56 + t * 190);
        const g = Math.round(189 - t * 40);
        const b = Math.round(248 - t * 180);
        color = `rgb(${r},${g},${b})`;
      }

      ctx.beginPath();
      ctx.arc(px, py, isFiltered ? 2 : 4, 0, 2 * Math.PI);
      ctx.fillStyle = isFiltered ? 'rgba(100, 116, 139, 0.2)' : color;
      ctx.fill();

      if (!isFiltered) {
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }
    });
  }, [coordinates, projectionMode, colorMode, selectedClusterFilter]);

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || coordinates.length === 0) return;

    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const width = canvas.width;
    const height = canvas.height;
    const isUmap = projectionMode === 'umap';

    const xs = coordinates.map(c => isUmap ? c.umap_x : c.tsne_x);
    const ys = coordinates.map(c => isUmap ? c.umap_y : c.tsne_y);

    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    const pad = 35;
    const scaleX = (width - pad * 2) / (maxX - minX || 1);
    const scaleY = (height - pad * 2) / (maxY - minY || 1);

    // Find closest cell
    let closest: CellCoordinate | null = null;
    let minDist = 14; // pixel radius threshold

    coordinates.forEach(cell => {
      const xVal = isUmap ? cell.umap_x : cell.tsne_x;
      const yVal = isUmap ? cell.umap_y : cell.tsne_y;

      const px = pad + (xVal - minX) * scaleX;
      const py = height - (pad + (yVal - minY) * scaleY);

      const d = Math.hypot(mx - px, my - py);
      if (d < minDist) {
        minDist = d;
        closest = cell;
      }
    });

    setHoveredCell(closest);
  };

  const handlePresetSelect = (p: typeof PRESET_DATASETS[0]) => {
    setFormTitle(p.title);
    setFormTissue(p.tissue);
    setFormOrganism(p.organism);
    setFormPlatform(p.platform);
    setFormResolution(p.resolution);
    setFormCells(p.cells);
  };

  const filteredMarkers = selectedDataset?.differential_genes?.filter(
    g => selectedClusterFilter === 'all' || g.cluster_index === selectedClusterFilter
  ) || [];

  const filteredPathways = selectedDataset?.pathway_enrichments?.filter(
    p => selectedClusterFilter === 'all' || p.cluster_index === selectedClusterFilter
  ) || [];

  return (
    <div style={{ padding: '24px', maxWidth: '1440px', margin: '0 auto' }}>
      {/* Header Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ padding: '10px', borderRadius: '12px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
              <Microscope size={28} />
            </div>
            <div>
              <h1 style={{ fontSize: '26px', fontWeight: 700, margin: 0 }}>Multi-Omics & Single-Cell Transcriptomics Studio</h1>
              <p style={{ margin: '4px 0 0', color: 'var(--text-secondary, #94a3b8)', fontSize: '14px' }}>
                Graph-based Leiden cell clustering, 2D UMAP / t-SNE dimensionality reduction, Wilcoxon marker discovery, pseudotime differentiation trajectories, and GSEA pathways.
              </p>
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => setShowAnalyzeModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: '#38bdf8',
              color: '#0f172a',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 18px',
              fontWeight: 700,
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(56, 189, 248, 0.3)',
            }}
          >
            <Plus size={18} /> New scRNA-seq Analysis
          </button>
          <button
            onClick={fetchDatasets}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'var(--card-bg, #1e293b)',
              color: 'var(--text-primary, #f8fafc)',
              border: '1px solid var(--border-color, #334155)',
              borderRadius: '8px',
              padding: '10px 14px',
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={16} /> Refresh
          </button>
        </div>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#fca5a5', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Grid: Datasets Selector + Workspace */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '20px' }}>
        {/* Left Sidebar: Dataset List */}
        <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '820px', overflowY: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color, #334155)', paddingBottom: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary, #94a3b8)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              scRNA-seq Datasets ({datasets.length})
            </span>
          </div>

          {loading && datasets.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>Loading single-cell atlases...</div>
          ) : datasets.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8', fontSize: '13px' }}>
              No single-cell datasets analyzed yet. Launch a pipeline to profile cellular heterogeneity.
            </div>
          ) : (
            datasets.map(d => {
              const isSelected = selectedDataset?.id === d.id;
              return (
                <div
                  key={d.id}
                  onClick={() => loadDatasetDetails(d.id)}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    backgroundColor: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                    border: isSelected ? '1px solid #38bdf8' : '1px solid var(--border-color, #334155)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ fontWeight: 700, fontSize: '14px', color: '#f8fafc', marginBottom: '4px', lineHeight: '18px' }}>{d.dataset_title}</div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>{d.tissue} &bull; {d.organism}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#cbd5e1' }}>
                    <span>{d.total_cells.toLocaleString()} Cells</span>
                    <span style={{ color: '#38bdf8', fontWeight: 600 }}>{d.clusters_count ?? (d.clusters ? d.clusters.length : 6)} Clusters</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Workspace */}
        {selectedDataset ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Overview & Metadata Card */}
            <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <h2 style={{ fontSize: '22px', fontWeight: 700, margin: 0 }}>{selectedDataset.dataset_title}</h2>
                    <span style={{ padding: '3px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 600, backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#10b981', border: '1px solid #10b981' }}>
                      {selectedDataset.tissue} ({selectedDataset.organism})
                    </span>
                  </div>
                  <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '4px' }}>
                    Platform: <strong>{selectedDataset.sequencing_platform}</strong> &bull; Total Cells: <strong>{selectedDataset.total_cells.toLocaleString()}</strong> &bull; Genes Detected: <strong>{selectedDataset.total_genes.toLocaleString()}</strong> &bull; Res: <strong>{selectedDataset.clustering_resolution}</strong>
                  </div>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-color, #334155)', paddingBottom: '8px', flexWrap: 'wrap' }}>
                {[
                  { key: 'umap', label: '2D Embedding Canvas (UMAP/t-SNE)', icon: Compass },
                  { key: 'volcano', label: 'Differential Volcano Plot', icon: Flame },
                  { key: 'markers', label: `Marker Genes (${filteredMarkers.length})`, icon: BarChart3 },
                  { key: 'pseudotime', label: 'Pseudotime Trajectory', icon: Clock },
                  { key: 'pathways', label: `GSEA Pathways (${filteredPathways.length})`, icon: TrendingUp },
                ].map(tab => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.key;
                  return (
                    <button
                      key={tab.key}
                      onClick={() => setActiveTab(tab.key as any)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        border: 'none',
                        backgroundColor: isActive ? '#38bdf8' : 'transparent',
                        color: isActive ? '#0f172a' : '#94a3b8',
                        fontWeight: isActive ? 700 : 500,
                        fontSize: '13px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <Icon size={16} />
                      {tab.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* TAB 1: 2D UMAP / t-SNE Canvas */}
            {activeTab === 'umap' && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                {/* Control Bar */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <span style={{ fontSize: '13px', color: '#94a3b8', fontWeight: 600 }}>Embedding:</span>
                    <div style={{ display: 'flex', backgroundColor: '#0f172a', borderRadius: '6px', padding: '2px', border: '1px solid #334155' }}>
                      <button
                        onClick={() => setProjectionMode('umap')}
                        style={{ padding: '4px 12px', fontSize: '12px', border: 'none', borderRadius: '4px', backgroundColor: projectionMode === 'umap' ? '#38bdf8' : 'transparent', color: projectionMode === 'umap' ? '#0f172a' : '#94a3b8', fontWeight: 600, cursor: 'pointer' }}
                      >
                        UMAP
                      </button>
                      <button
                        onClick={() => setProjectionMode('tsne')}
                        style={{ padding: '4px 12px', fontSize: '12px', border: 'none', borderRadius: '4px', backgroundColor: projectionMode === 'tsne' ? '#38bdf8' : 'transparent', color: projectionMode === 'tsne' ? '#0f172a' : '#94a3b8', fontWeight: 600, cursor: 'pointer' }}
                      >
                        t-SNE
                      </button>
                    </div>

                    <span style={{ fontSize: '13px', color: '#94a3b8', fontWeight: 600, marginLeft: '12px' }}>Color By:</span>
                    <div style={{ display: 'flex', backgroundColor: '#0f172a', borderRadius: '6px', padding: '2px', border: '1px solid #334155' }}>
                      <button
                        onClick={() => setColorMode('cluster')}
                        style={{ padding: '4px 12px', fontSize: '12px', border: 'none', borderRadius: '4px', backgroundColor: colorMode === 'cluster' ? '#38bdf8' : 'transparent', color: colorMode === 'cluster' ? '#0f172a' : '#94a3b8', fontWeight: 600, cursor: 'pointer' }}
                      >
                        Cell Cluster
                      </button>
                      <button
                        onClick={() => setColorMode('pseudotime')}
                        style={{ padding: '4px 12px', fontSize: '12px', border: 'none', borderRadius: '4px', backgroundColor: colorMode === 'pseudotime' ? '#38bdf8' : 'transparent', color: colorMode === 'pseudotime' ? '#0f172a' : '#94a3b8', fontWeight: 600, cursor: 'pointer' }}
                      >
                        Pseudotime ($0 \rightarrow 1$)
                      </button>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <span style={{ fontSize: '13px', color: '#94a3b8' }}>Filter Cluster:</span>
                    <select
                      value={selectedClusterFilter}
                      onChange={e => setSelectedClusterFilter(e.target.value === 'all' ? 'all' : parseInt(e.target.value))}
                      style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '12px' }}
                    >
                      <option value="all">All Cell Clusters</option>
                      {selectedDataset.clusters?.map(c => (
                        <option key={c.cluster_index} value={c.cluster_index}>
                          C{c.cluster_index}: {c.cell_type_annotation} ({c.cell_count} cells)
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Canvas Area with Floating Tooltip */}
                <div style={{ position: 'relative', width: '100%', height: '520px', backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #334155', overflow: 'hidden' }}>
                  <canvas
                    ref={canvasRef}
                    width={880}
                    height={520}
                    onMouseMove={handleCanvasMouseMove}
                    onMouseLeave={() => setHoveredCell(null)}
                    style={{ width: '100%', height: '100%', cursor: 'crosshair' }}
                  />

                  {hoveredCell && (
                    <div
                      style={{
                        position: 'absolute',
                        top: '16px',
                        right: '16px',
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        border: '1px solid #38bdf8',
                        borderRadius: '8px',
                        padding: '12px 16px',
                        fontSize: '12px',
                        color: '#f8fafc',
                        boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
                        pointerEvents: 'none',
                        maxWidth: '280px',
                      }}
                    >
                      <div style={{ fontWeight: 700, color: '#38bdf8', marginBottom: '4px' }}>{hoveredCell.cell_type}</div>
                      <div style={{ color: '#94a3b8', marginBottom: '2px' }}>Barcode: <span style={{ fontFamily: 'monospace', color: '#cbd5e1' }}>{hoveredCell.cell_barcode}</span></div>
                      <div style={{ color: '#94a3b8', marginBottom: '2px' }}>Cluster: <span style={{ fontWeight: 600, color: '#f8fafc' }}>#{hoveredCell.cluster_index}</span></div>
                      <div style={{ color: '#94a3b8', marginBottom: '2px' }}>Pseudotime: <span style={{ fontWeight: 600, color: '#10b981' }}>{hoveredCell.pseudotime}</span></div>
                      <div style={{ color: '#94a3b8' }}>
                        Coords: <span style={{ fontFamily: 'monospace' }}>({projectionMode === 'umap' ? `${hoveredCell.umap_x}, ${hoveredCell.umap_y}` : `${hoveredCell.tsne_x}, ${hoveredCell.tsne_y}`})</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Cluster Legend Chips */}
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '16px' }}>
                  {selectedDataset.clusters?.map(c => {
                    const color = CLUSTER_COLORS[c.cluster_index % CLUSTER_COLORS.length];
                    const isSelected = selectedClusterFilter === c.cluster_index;
                    return (
                      <div
                        key={c.cluster_index}
                        onClick={() => setSelectedClusterFilter(selectedClusterFilter === c.cluster_index ? 'all' : c.cluster_index)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '6px 12px',
                          borderRadius: '8px',
                          backgroundColor: isSelected ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                          border: isSelected ? '1px solid #38bdf8' : '1px solid #334155',
                          cursor: 'pointer',
                          fontSize: '12px',
                        }}
                      >
                        <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: color }} />
                        <span style={{ fontWeight: 600, color: '#f8fafc' }}>{c.cell_type_annotation}</span>
                        <span style={{ color: '#94a3b8' }}>({c.percentage_of_total}%)</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 2: Differential Expression & Volcano Plot */}
            {activeTab === 'volcano' && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Flame size={18} color="#ef4444" /> Differential Expression Volcano Plot (Log2FC vs -Log10 Adj-P)
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '16px' }}>
                  Identifies statistically significant marker genes defining cell identities. Significance threshold: |Log2FC| &ge; 1.0, adjusted p-value &lt; 0.05.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '14px' }}>
                  {filteredMarkers.slice(0, 12).map(g => (
                    <div
                      key={g.id}
                      style={{
                        backgroundColor: 'rgba(255, 255, 255, 0.02)',
                        border: g.is_significant ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid #334155',
                        borderRadius: '8px',
                        padding: '14px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontWeight: 700, fontSize: '15px', color: '#38bdf8' }}>{g.gene_symbol}</span>
                        <span style={{ fontSize: '11px', padding: '2px 6px', borderRadius: '4px', backgroundColor: g.log2_fold_change > 0 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)', color: g.log2_fold_change > 0 ? '#10b981' : '#fca5a5' }}>
                          {g.log2_fold_change > 0 ? '▲ Upregulated' : '▼ Downregulated'}
                        </span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#cbd5e1', display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span>Log2 Fold Change:</span>
                        <strong style={{ color: g.log2_fold_change > 0 ? '#10b981' : '#ef4444' }}>{g.log2_fold_change > 0 ? `+${g.log2_fold_change.toFixed(2)}` : g.log2_fold_change.toFixed(2)}</strong>
                      </div>
                      <div style={{ fontSize: '12px', color: '#cbd5e1', display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span>Adjusted p-val:</span>
                        <span style={{ fontFamily: 'monospace' }}>{g.p_val_adj.toExponential(2)}</span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                        <span>In-Cluster %:</span>
                        <span>{(g.pct_in_cluster * 100).toFixed(0)}% (vs {(g.pct_out_of_cluster * 100).toFixed(0)}% bg)</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 3: Marker Genes Table */}
            {activeTab === 'markers' && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart3 size={18} color="#38bdf8" /> Cluster-Specific Differential Expression Markers
                </h3>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textAlign: 'left' }}>
                        <th style={{ padding: '10px 8px' }}>Cluster</th>
                        <th style={{ padding: '10px 8px' }}>Gene Symbol</th>
                        <th style={{ padding: '10px 8px' }}>Log2 FC</th>
                        <th style={{ padding: '10px 8px' }}>p-value</th>
                        <th style={{ padding: '10px 8px' }}>Adj p-val (FDR)</th>
                        <th style={{ padding: '10px 8px' }}>Pct In Cluster</th>
                        <th style={{ padding: '10px 8px' }}>Pct Out of Cluster</th>
                        <th style={{ padding: '10px 8px' }}>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredMarkers.map(g => (
                        <tr key={g.id} style={{ borderBottom: '1px solid #334155' }}>
                          <td style={{ padding: '10px 8px', fontWeight: 600, color: '#f8fafc' }}>
                            Cluster {g.cluster_index}
                          </td>
                          <td style={{ padding: '10px 8px', fontFamily: 'monospace', fontWeight: 700, color: '#38bdf8' }}>{g.gene_symbol}</td>
                          <td style={{ padding: '10px 8px', fontWeight: 700, color: g.log2_fold_change > 0 ? '#10b981' : '#ef4444' }}>
                            {g.log2_fold_change > 0 ? `+${g.log2_fold_change.toFixed(2)}` : g.log2_fold_change.toFixed(2)}
                          </td>
                          <td style={{ padding: '10px 8px', fontFamily: 'monospace', color: '#94a3b8' }}>{g.p_value.toExponential(2)}</td>
                          <td style={{ padding: '10px 8px', fontFamily: 'monospace', color: '#cbd5e1' }}>{g.p_val_adj.toExponential(2)}</td>
                          <td style={{ padding: '10px 8px', color: '#10b981' }}>{(g.pct_in_cluster * 100).toFixed(1)}%</td>
                          <td style={{ padding: '10px 8px', color: '#94a3b8' }}>{(g.pct_out_of_cluster * 100).toFixed(1)}%</td>
                          <td style={{ padding: '10px 8px' }}>
                            <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700, backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#10b981' }}>
                              SIGNIFICANT
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* TAB 4: Pseudotime Trajectory */}
            {activeTab === 'pseudotime' && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Clock size={18} color="#10b981" /> Cellular Differentiation Pseudotime Trajectory
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '20px' }}>
                  Diffusion pseudotime orders individual cells along developmental and pharmacological response axes ($0.0 \rightarrow 1.0$), capturing stem/quiescent state transitions to mature or LNP-transfected states.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {selectedDataset.clusters?.map(c => {
                    const cCoords = coordinates.filter(coord => coord.cluster_index === c.cluster_index);
                    const avgTime = cCoords.length > 0 ? cCoords.reduce((acc, curr) => acc + curr.pseudotime, 0) / cCoords.length : 0;
                    return (
                      <div key={c.cluster_index} style={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '14px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                          <span style={{ fontWeight: 700, fontSize: '14px', color: '#f8fafc' }}>
                            Cluster {c.cluster_index}: {c.cell_type_annotation}
                          </span>
                          <span style={{ fontSize: '12px', color: '#38bdf8', fontWeight: 600 }}>Mean Pseudotime: {avgTime.toFixed(3)}</span>
                        </div>
                        <div style={{ width: '100%', height: '8px', backgroundColor: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${Math.min(100, Math.max(5, avgTime * 100))}%`, height: '100%', backgroundColor: '#10b981', borderRadius: '4px' }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 5: GSEA Pathways */}
            {activeTab === 'pathways' && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TrendingUp size={18} color="#a855f7" /> Gene Set Enrichment Analysis (GSEA) Pathway Waterfall
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '16px' }}>
                  Normalized Enrichment Scores (NES) across canonical MSigDB, KEGG, and Reactome biological pathways.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {filteredPathways.map((p, idx) => (
                    <div key={p.id || idx} style={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '14px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <span style={{ fontWeight: 700, fontSize: '14px', color: '#f8fafc' }}>{p.pathway_name}</span>
                        <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', backgroundColor: '#334155', color: '#a855f7', fontWeight: 600 }}>{p.database_source}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#cbd5e1', marginBottom: '8px' }}>
                        <span>NES: <strong style={{ color: '#10b981' }}>+{p.normalized_enrichment_score.toFixed(2)}</strong></span>
                        <span>Adj p-val: <strong style={{ fontFamily: 'monospace' }}>{p.p_val_adj.toExponential(2)}</strong></span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                        Leading Edge Genes: <span style={{ color: '#38bdf8', fontFamily: 'monospace' }}>{p.leading_edge_genes.join(', ')}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
            Select or launch a single-cell dataset to explore cellular embeddings and marker genes.
          </div>
        )}
      </div>

      {/* Modal: New scRNA-seq Analysis */}
      {showAnalyzeModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '14px', width: '100%', maxWidth: '680px', maxHeight: '90vh', overflowY: 'auto', padding: '24px', boxShadow: '0 20px 40px rgba(0,0,0,0.5)' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Microscope size={22} color="#38bdf8" /> Launch Single-Cell Multi-Omics Pipeline
            </h2>

            {/* Preloaded Presets */}
            <div style={{ marginBottom: '16px' }}>
              <span style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Load Pre-configured Single-Cell Atlas:</span>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {PRESET_DATASETS.map((p, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handlePresetSelect(p)}
                    style={{
                      padding: '6px 12px',
                      fontSize: '12px',
                      borderRadius: '6px',
                      backgroundColor: formTitle === p.title ? '#38bdf8' : '#334155',
                      color: formTitle === p.title ? '#0f172a' : '#ffffff',
                      border: 'none',
                      cursor: 'pointer',
                      fontWeight: 700,
                    }}
                  >
                    {p.tissue} ({p.organism})
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleCreateAnalysis} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Dataset Title</label>
                <input
                  type="text"
                  required
                  value={formTitle}
                  onChange={e => setFormTitle(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Tissue / Origin</label>
                  <input
                    type="text"
                    required
                    value={formTissue}
                    onChange={e => setFormTissue(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Host Organism</label>
                  <input
                    type="text"
                    required
                    value={formOrganism}
                    onChange={e => setFormOrganism(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Sequencing Chemistry & Platform</label>
                <input
                  type="text"
                  value={formPlatform}
                  onChange={e => setFormPlatform(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Clustering Resolution ({formResolution})</label>
                  <input
                    type="range"
                    min="0.2"
                    max="1.5"
                    step="0.1"
                    value={formResolution}
                    onChange={e => setFormResolution(parseFloat(e.target.value))}
                    style={{ width: '100%' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Total Single Cells</label>
                  <input
                    type="number"
                    min={100}
                    max={2500}
                    value={formCells}
                    onChange={e => setFormCells(parseInt(e.target.value) || 600)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowAnalyzeModal(false)}
                  style={{ padding: '8px 16px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: 'transparent', color: '#94a3b8', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={analyzing}
                  style={{
                    padding: '8px 20px',
                    borderRadius: '6px',
                    border: 'none',
                    backgroundColor: '#38bdf8',
                    color: '#0f172a',
                    fontWeight: 700,
                    cursor: analyzing ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  {analyzing ? <RefreshCw className="animate-spin" size={16} /> : <Sparkles size={16} />}
                  {analyzing ? 'Processing Cells...' : 'Run Pipeline'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
