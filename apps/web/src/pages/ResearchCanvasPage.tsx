import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Network,
  Plus,
  Sparkles,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Share2,
  CheckCircle2,
  Layers,
} from 'lucide-react';
import { CanvasBoard, CanvasNode, CanvasEdge, CanvasMetrics } from '../types/canvas';

const SAMPLE_CANVAS: CanvasBoard = {
  id: 'board-1',
  title: 'Quantum Advantage in Combinatorial Graph Optimization',
  description: 'Visual ideation DAG linking Hamiltonian variational ansatz to empirical benchmark data.',
  viewport_state: { zoom: 0.9, pan_x: 40.0, pan_y: 40.0 },
  background_grid: 'dots',
  status: 'active',
  created_at: new Date().toISOString(),
  nodes: [
    {
      id: 'node-1',
      node_type: 'hypothesis',
      title: 'Central Hypothesis: QAOA Speedup',
      content: 'Multi-angle QAOA yields super-polynomial sampling advantage over classical simulated annealing on Max-Cut graphs.',
      confidence_score: 0.92,
      status: 'verified',
      position_x: 80,
      position_y: 180,
      width: 280,
      height: 150,
      color_accent: '#3b82f6',
    },
    {
      id: 'node-2',
      node_type: 'agent_thought',
      title: 'Finding: Depth-4 Ansatz Convergence',
      content: 'Empirical parameter optimization converged within 12 iterations across 64-vertex 3-regular graphs.',
      confidence_score: 0.88,
      status: 'verified',
      position_x: 440,
      position_y: 100,
      width: 270,
      height: 140,
      color_accent: '#f59e0b',
    },
    {
      id: 'node-3',
      node_type: 'evidence',
      title: 'Evidence: 128-Qubit Hardware Run',
      content: 'Fidelity reached 98.4% on trapped-ion processor with zero-noise extrapolation.',
      confidence_score: 0.95,
      status: 'verified',
      position_x: 800,
      position_y: 100,
      width: 270,
      height: 140,
      color_accent: '#10b981',
    },
    {
      id: 'node-4',
      node_type: 'counter_claim',
      title: 'Counter-Claim: Barren Plateaus',
      content: 'Random initialization in p > 8 ansatz introduces exponential gradient vanishing unless pre-trained with tensor networks.',
      confidence_score: 0.78,
      status: 'disputed',
      position_x: 440,
      position_y: 300,
      width: 270,
      height: 140,
      color_accent: '#ef4444',
    },
    {
      id: 'node-5',
      node_type: 'conclusion',
      title: 'Synthesis: Hybrid Warm-Start',
      content: 'Hybrid tensor-network warm-starting mitigates barren plateaus while preserving quantum sampling advantage.',
      confidence_score: 0.91,
      status: 'verified',
      position_x: 1140,
      position_y: 190,
      width: 290,
      height: 150,
      color_accent: '#ec4899',
    },
  ],
  edges: [
    {
      id: 'edge-1',
      source_node_id: 'node-1',
      target_node_id: 'node-2',
      relation_type: 'branches_to',
      label: 'empirically tests',
      weight: 1.0,
    },
    {
      id: 'edge-2',
      source_node_id: 'node-2',
      target_node_id: 'node-3',
      relation_type: 'supports',
      label: 'supported by',
      weight: 1.0,
    },
    {
      id: 'edge-3',
      source_node_id: 'node-1',
      target_node_id: 'node-4',
      relation_type: 'refutes',
      label: 'challenged by',
      weight: 0.8,
    },
    {
      id: 'edge-4',
      source_node_id: 'node-3',
      target_node_id: 'node-5',
      relation_type: 'derives_from',
      label: 'synthesizes',
      weight: 1.0,
    },
    {
      id: 'edge-5',
      source_node_id: 'node-4',
      target_node_id: 'node-5',
      relation_type: 'derives_from',
      label: 'resolves',
      weight: 1.0,
    },
  ],
};

export const ResearchCanvasPage: React.FC = () => {
  const [boards, setBoards] = useState<CanvasBoard[]>([SAMPLE_CANVAS]);
  const [selectedBoardId, setSelectedBoardId] = useState<string>(SAMPLE_CANVAS.id);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>('node-1');
  const [zoom, setZoom] = useState<number>(0.9);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isBrainstorming, setIsBrainstorming] = useState<boolean>(false);

  // Dragging state
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const canvasRef = useRef<HTMLDivElement>(null);

  // Modals
  const [showNewBoardModal, setShowNewBoardModal] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newDesc, setNewDesc] = useState<string>('');
  const [newGrid, setNewGrid] = useState<'dots' | 'lines' | 'crosses' | 'clean'>('dots');

  // Load from API
  const fetchBoards = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/canvas/boards');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          const detailRes = await fetch(`/api/v1/canvas/boards/${data[0].id}`);
          if (detailRes.ok) {
            const detailData = await detailRes.json();
            setBoards([detailData, ...data.slice(1)]);
            setSelectedBoardId(detailData.id);
          } else {
            setBoards(data);
            setSelectedBoardId(data[0].id);
          }
        }
      }
    } catch {
      // fallback
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBoards();
  }, []);

  const currentBoard = useMemo(() => {
    return boards.find((b) => b.id === selectedBoardId) || boards[0];
  }, [boards, selectedBoardId]);

  const selectedNode = useMemo(() => {
    return currentBoard?.nodes?.find((n) => n.id === selectedNodeId) || null;
  }, [currentBoard, selectedNodeId]);

  const metrics: CanvasMetrics = useMemo(() => {
    const totalBoards = boards.length;
    const totalNodes = boards.reduce((acc, b) => acc + (b.nodes?.length || 0), 0);
    const totalEdges = boards.reduce((acc, b) => acc + (b.edges?.length || 0), 0);
    const typeDist: Record<string, number> = {};
    boards.forEach((b) => {
      b.nodes?.forEach((n) => {
        typeDist[n.node_type] = (typeDist[n.node_type] || 0) + 1;
      });
    });
    return {
      total_canvas_boards: totalBoards,
      total_canvas_nodes: totalNodes,
      total_canvas_edges: totalEdges,
      node_type_distribution: typeDist,
      average_nodes_per_board: totalBoards > 0 ? Number((totalNodes / totalBoards).toFixed(1)) : 0,
    };
  }, [boards]);

  // AI Brainstorming
  const handleBrainstorm = async () => {
    if (!currentBoard) return;
    setIsBrainstorming(true);
    try {
      const res = await fetch(`/api/v1/canvas/boards/${currentBoard.id}/brainstorm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: currentBoard.title }),
      });
      if (res.ok) {
        const detailRes = await fetch(`/api/v1/canvas/boards/${currentBoard.id}`);
        if (detailRes.ok) {
          const updated = await detailRes.json();
          setBoards((prev) => prev.map((b) => (b.id === updated.id ? updated : b)));
        }
      }
    } catch {
      // Local fallback simulation
      const newCounter: CanvasNode = {
        id: `node-${Date.now()}-1`,
        node_type: 'counter_claim',
        title: 'Counter-Claim: Gradient Variance',
        content: 'Unbounded variance in gradient estimators reduces sampling efficiency under high noise rates.',
        confidence_score: 0.74,
        status: 'disputed',
        position_x: 440,
        position_y: 480,
        width: 270,
        height: 140,
        color_accent: '#ef4444',
      };
      const newEdge: CanvasEdge = {
        id: `edge-${Date.now()}`,
        source_node_id: newCounter.id,
        target_node_id: currentBoard.nodes?.[0]?.id || 'node-1',
        relation_type: 'refutes',
        label: 'challenges',
        weight: 0.85,
      };
      setBoards((prev) =>
        prev.map((b) =>
          b.id === currentBoard.id
            ? {
                ...b,
                nodes: [...(b.nodes || []), newCounter],
                edges: [...(b.edges || []), newEdge],
              }
            : b
        )
      );
    } finally {
      setIsBrainstorming(false);
    }
  };

  // Node Dragging handlers
  const handleMouseDown = (nodeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDraggingNodeId(nodeId);
    const node = currentBoard?.nodes?.find((n) => n.id === nodeId);
    if (node) {
      setDragOffset({
        x: e.clientX - node.position_x * zoom,
        y: e.clientY - node.position_y * zoom,
      });
    }
    setSelectedNodeId(nodeId);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!draggingNodeId || !currentBoard) return;
    const newX = Math.max(20, (e.clientX - dragOffset.x) / zoom);
    const newY = Math.max(20, (e.clientY - dragOffset.y) / zoom);

    setBoards((prev) =>
      prev.map((b) =>
        b.id === currentBoard.id
          ? {
              ...b,
              nodes: b.nodes?.map((n) => (n.id === draggingNodeId ? { ...n, position_x: newX, position_y: newY } : n)),
            }
          : b
      )
    );
  };

  const handleMouseUp = () => {
    setDraggingNodeId(null);
  };

  // Create new board
  const handleCreateBoard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/canvas/boards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          description: newDesc,
          background_grid: newGrid,
        }),
      });
      if (res.ok) {
        const created = await res.json();
        setBoards([created, ...boards]);
        setSelectedBoardId(created.id);
        setShowNewBoardModal(false);
      }
    } catch {
      const localBoard: CanvasBoard = {
        id: `board-${Date.now()}`,
        title: newTitle,
        description: newDesc,
        background_grid: newGrid,
        viewport_state: { zoom: 1.0, pan_x: 0, pan_y: 0 },
        status: 'active',
        created_at: new Date().toISOString(),
        nodes: [],
        edges: [],
      };
      setBoards([localBoard, ...boards]);
      setSelectedBoardId(localBoard.id);
      setShowNewBoardModal(false);
    } finally {
      setIsLoading(false);
      setNewTitle('');
      setNewDesc('');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-primary/10 border border-primary/20 text-primary">
              <Network className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Multi-Agent Research Canvas & Visual Ideation Studio</h1>
              <p className="text-sm text-text-secondary">
                2D infinite node-graph ideation, evidence DAG mapping, and autonomous agent brainstorming
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={fetchBoards} disabled={isLoading} className="btn btn-secondary text-sm">
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button onClick={handleBrainstorm} disabled={isBrainstorming} className="btn btn-primary text-sm">
            <Sparkles className={`w-4 h-4 mr-2 ${isBrainstorming ? 'animate-spin' : ''}`} />
            AI Brainstorm
          </button>
          <button onClick={() => setShowNewBoardModal(true)} className="btn btn-secondary text-sm">
            <Plus className="w-4 h-4 mr-2" />
            New Canvas
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-text-secondary uppercase tracking-wider">Canvas Boards</div>
            <div className="text-2xl font-bold mt-1">{metrics.total_canvas_boards}</div>
          </div>
          <Layers className="w-8 h-8 text-primary/40" />
        </div>
        <div className="card p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-text-secondary uppercase tracking-wider">Visual Nodes</div>
            <div className="text-2xl font-bold mt-1 text-info">{metrics.total_canvas_nodes}</div>
          </div>
          <Network className="w-8 h-8 text-info/40" />
        </div>
        <div className="card p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-text-secondary uppercase tracking-wider">Relational Links</div>
            <div className="text-2xl font-bold mt-1 text-success">{metrics.total_canvas_edges}</div>
          </div>
          <Share2 className="w-8 h-8 text-success/40" />
        </div>
        <div className="card p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-text-secondary uppercase tracking-wider">Avg Node Density</div>
            <div className="text-2xl font-bold mt-1 text-warning">{metrics.average_nodes_per_board} / board</div>
          </div>
          <CheckCircle2 className="w-8 h-8 text-warning/40" />
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Canvas Board Selector */}
        <div className="lg:col-span-3 space-y-4">
          <div className="card p-4 space-y-3">
            <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">Canvas Archive</h2>
            <div className="space-y-2 max-h-[560px] overflow-y-auto pr-1">
              {boards.map((b) => {
                const isSelected = b.id === currentBoard?.id;
                return (
                  <div
                    key={b.id}
                    onClick={() => setSelectedBoardId(b.id)}
                    className={`p-3 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-primary/5 border-primary/40 shadow-sm'
                        : 'bg-surface border-border hover:border-border-hover'
                    }`}
                  >
                    <div className="font-medium text-sm line-clamp-2">{b.title}</div>
                    <div className="flex items-center gap-2 mt-2 text-xs text-text-secondary">
                      <span>{b.nodes?.length || 0} nodes</span>
                      <span>•</span>
                      <span>{b.edges?.length || 0} links</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Center & Right Column: Interactive 2D Node Canvas */}
        <div className="lg:col-span-9 space-y-4">
          {currentBoard && (
            <div className="card p-4 space-y-4">
              {/* Canvas Controls Toolbar */}
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div className="flex items-center gap-3">
                  <h2 className="text-base font-bold">{currentBoard.title}</h2>
                  <span className="badge badge-neutral text-xs">{currentBoard.nodes?.length || 0} Nodes</span>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => setZoom((z) => Math.max(0.5, z - 0.1))} className="btn btn-secondary text-xs px-2.5 py-1">
                    <ZoomOut className="w-3.5 h-3.5" />
                  </button>
                  <span className="text-xs font-mono text-text-secondary px-1">{Math.round(zoom * 100)}%</span>
                  <button onClick={() => setZoom((z) => Math.min(1.5, z + 0.1))} className="btn btn-secondary text-xs px-2.5 py-1">
                    <ZoomIn className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => setZoom(0.9)} className="btn btn-secondary text-xs px-2.5 py-1">
                    <Maximize2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Infinite 2D SVG Canvas Stage */}
              <div
                ref={canvasRef}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                className="relative w-full h-[540px] bg-surface-alt rounded-xl border border-border overflow-hidden select-none cursor-crosshair"
                style={{
                  backgroundImage:
                    currentBoard.background_grid === 'dots'
                      ? 'radial-gradient(circle, rgba(255,255,255,0.08) 1px, transparent 1px)'
                      : 'none',
                  backgroundSize: '24px 24px',
                }}
              >
                {/* SVG Edges Layer */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ transform: `scale(${zoom})`, transformOrigin: '0 0' }}>
                  <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.4)" />
                    </marker>
                  </defs>
                  {currentBoard.edges?.map((e) => {
                    const sourceNode = currentBoard.nodes?.find((n) => n.id === e.source_node_id);
                    const targetNode = currentBoard.nodes?.find((n) => n.id === e.target_node_id);
                    if (!sourceNode || !targetNode) return null;

                    const sx = sourceNode.position_x + (sourceNode.width || 280);
                    const sy = sourceNode.position_y + (sourceNode.height || 140) / 2;
                    const tx = targetNode.position_x;
                    const ty = targetNode.position_y + (targetNode.height || 140) / 2;
                    const midX = (sx + tx) / 2;

                    return (
                      <g key={e.id}>
                        <path
                          d={`M ${sx} ${sy} C ${midX} ${sy}, ${midX} ${ty}, ${tx} ${ty}`}
                          fill="none"
                          stroke={e.relation_type === 'refutes' ? '#ef4444' : 'rgba(255,255,255,0.3)'}
                          strokeWidth="2"
                          strokeDasharray={e.relation_type === 'refutes' ? '4 4' : 'none'}
                          markerEnd="url(#arrow)"
                        />
                        {e.label && (
                          <text x={midX} y={(sy + ty) / 2 - 8} fill="rgba(255,255,255,0.6)" fontSize="11" textAnchor="middle" className="font-mono">
                            {e.label}
                          </text>
                        )}
                      </g>
                    );
                  })}
                </svg>

                {/* Interactive Node Cards */}
                {currentBoard.nodes?.map((n) => {
                  const isSelected = n.id === selectedNodeId;
                  return (
                    <div
                      key={n.id}
                      onMouseDown={(e) => handleMouseDown(n.id, e)}
                      style={{
                        transform: `translate(${n.position_x * zoom}px, ${n.position_y * zoom}px) scale(${zoom})`,
                        transformOrigin: '0 0',
                        width: `${n.width || 280}px`,
                      }}
                      className={`absolute p-3.5 rounded-xl border cursor-move transition-shadow ${
                        isSelected
                          ? 'bg-surface border-primary shadow-xl ring-2 ring-primary/40 z-20'
                          : 'bg-surface/95 border-border hover:border-border-hover shadow-md z-10'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 border-b border-border/60 pb-2 mb-2">
                        <span
                          className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded font-mono"
                          style={{
                            backgroundColor: `${n.color_accent || '#3b82f6'}20`,
                            color: n.color_accent || '#3b82f6',
                          }}
                        >
                          {n.node_type.replace('_', ' ')}
                        </span>
                        <span className="text-[11px] font-mono text-text-secondary">
                          {Math.round(n.confidence_score * 100)}%
                        </span>
                      </div>
                      <div className="font-bold text-xs line-clamp-2 text-text">{n.title}</div>
                      <p className="text-[11px] text-text-secondary line-clamp-3 mt-1 leading-relaxed">
                        {n.content}
                      </p>
                    </div>
                  );
                })}
              </div>

              {/* Selected Node Inspector Drawer */}
              {selectedNode && (
                <div className="p-4 rounded-xl border border-border bg-surface-alt space-y-3">
                  <div className="flex items-center justify-between border-b border-border/60 pb-2">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: selectedNode.color_accent || '#3b82f6' }}
                      />
                      <h3 className="font-bold text-sm">Node Inspector: {selectedNode.title}</h3>
                    </div>
                    <span className="badge badge-neutral text-xs uppercase">{selectedNode.node_type}</span>
                  </div>
                  <p className="text-xs text-text leading-relaxed bg-surface p-3 rounded-lg border border-border">
                    {selectedNode.content || 'No additional content.'}
                  </p>
                  <div className="flex items-center gap-4 text-xs text-text-secondary font-mono">
                    <span>Position: X={Math.round(selectedNode.position_x)}, Y={Math.round(selectedNode.position_y)}</span>
                    <span>•</span>
                    <span>Status: {selectedNode.status}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* New Canvas Modal */}
      {showNewBoardModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="card max-w-md w-full p-6 space-y-4 shadow-2xl border border-border animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="font-bold text-base">Create Research Canvas</h3>
              <button onClick={() => setShowNewBoardModal(false)} className="text-text-secondary hover:text-text">
                ✕
              </button>
            </div>
            <form onSubmit={handleCreateBoard} className="space-y-3 text-sm">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Canvas Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Asymmetric Representation Learning DAG"
                  className="input w-full text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Description</label>
                <textarea
                  rows={3}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Summary of research exploration scope..."
                  className="input w-full text-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Background Grid Style</label>
                <select
                  value={newGrid}
                  onChange={(e) => setNewGrid(e.target.value as any)}
                  className="input w-full text-xs"
                >
                  <option value="dots">Dotted Matrix Grid</option>
                  <option value="lines">Crossline Grid</option>
                  <option value="clean">Clean Surface</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-border">
                <button type="button" onClick={() => setShowNewBoardModal(false)} className="btn btn-secondary text-xs">
                  Cancel
                </button>
                <button type="submit" disabled={isLoading} className="btn btn-primary text-xs">
                  Create Board
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
