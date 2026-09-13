import React, { useState, useMemo } from 'react'
import {
  Search,
  Share2,
  Plus,
  Trash2,
  Layers,
  Compass,
  ArrowRight,
  Sparkles,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  Eye,
  Loader2,
} from 'lucide-react'
import type {
  KnowledgeEntity,
  KnowledgeRelation,
  EntityType,
  GraphStats,
  CreateEntityPayload,
  CreateRelationPayload,
  GraphPathResult,
} from '../types/graph'

interface KnowledgeGraphViewerProps {
  entities: KnowledgeEntity[]
  relations: KnowledgeRelation[]
  stats?: GraphStats | null
  isLoading?: boolean
  onSearch?: (query: string, entityType?: string) => Promise<void>
  onExpandNode?: (nodeId: string, hops: number) => Promise<void>
  onCreateEntity?: (payload: CreateEntityPayload) => Promise<void>
  onCreateRelation?: (payload: CreateRelationPayload) => Promise<void>
  onDeleteEntity?: (entityId: string) => Promise<void>
  onDeleteRelation?: (relationId: string) => Promise<void>
  onFindPath?: (source: string, target: string) => Promise<GraphPathResult | null>
  onExtractTriplets?: (text: string) => Promise<void>
}

const TYPE_COLORS: Record<string, { bg: string; text: string; border: string; glow: string }> = {
  CONCEPT: { bg: 'rgba(6, 182, 212, 0.15)', text: '#06b6d4', border: '#0891b2', glow: 'rgba(6, 182, 212, 0.4)' },
  TECHNOLOGY: { bg: 'rgba(168, 85, 247, 0.15)', text: '#a855f7', border: '#9333ea', glow: 'rgba(168, 85, 247, 0.4)' },
  MATERIAL: { bg: 'rgba(245, 158, 11, 0.15)', text: '#f59e0b', border: '#d97706', glow: 'rgba(245, 158, 11, 0.4)' },
  PERSON: { bg: 'rgba(16, 185, 129, 0.15)', text: '#10b981', border: '#059669', glow: 'rgba(16, 185, 129, 0.4)' },
  ORGANIZATION: { bg: 'rgba(59, 130, 246, 0.15)', text: '#3b82f6', border: '#2563eb', glow: 'rgba(59, 130, 246, 0.4)' },
  METRIC: { bg: 'rgba(244, 63, 94, 0.15)', text: '#f43f5e', border: '#e11d48', glow: 'rgba(244, 63, 94, 0.4)' },
  DATASET: { bg: 'rgba(16, 185, 129, 0.15)', text: '#34d399', border: '#10b981', glow: 'rgba(16, 185, 129, 0.4)' },
  PAPER: { bg: 'rgba(234, 88, 12, 0.15)', text: '#ea580c', border: '#c2410c', glow: 'rgba(234, 88, 12, 0.4)' },
  LOCATION: { bg: 'rgba(239, 68, 68, 0.15)', text: '#ef4444', border: '#dc2626', glow: 'rgba(239, 68, 68, 0.4)' },
  OTHER: { bg: 'rgba(148, 163, 184, 0.15)', text: '#94a3b8', border: '#64748b', glow: 'rgba(148, 163, 184, 0.4)' },
}

export function KnowledgeGraphViewer({
  entities,
  relations,
  stats,
  isLoading = false,
  onSearch,
  onExpandNode,
  onCreateEntity,
  onCreateRelation,
  onDeleteEntity,
  onDeleteRelation,
  onFindPath,
  onExtractTriplets,
}: KnowledgeGraphViewerProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState<string>('ALL')
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null)
  const [pathSource, setPathSource] = useState<string>('')
  const [pathTarget, setPathTarget] = useState<string>('')
  const [pathResult, setPathResult] = useState<GraphPathResult | null>(null)
  const [isPathSearching, setIsPathSearching] = useState(false)
  const [activeTab, setActiveTab] = useState<'graph' | 'entities' | 'relations' | 'pathfinder' | 'extract'>('graph')

  // Modals / forms
  const [showAddNodeModal, setShowAddNodeModal] = useState(false)
  const [showAddEdgeModal, setShowAddEdgeModal] = useState(false)
  const [extractText, setExtractText] = useState('')
  const [isExtracting, setIsExtracting] = useState(false)

  // Zoom & Pan state for interactive canvas
  const [zoomLevel, setZoomLevel] = useState(1.0)
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })

  // Form states
  const [newNodeName, setNewNodeName] = useState('')
  const [newNodeType, setNewNodeType] = useState<EntityType>('CONCEPT')
  const [newNodeDesc, setNewNodeDesc] = useState('')
  const [newNodeAliases, setNewNodeAliases] = useState('')

  const [newEdgeSource, setNewEdgeSource] = useState('')
  const [newEdgeTarget, setNewEdgeTarget] = useState('')
  const [newEdgeType, setNewEdgeType] = useState('RELATES_TO')
  const [newEdgeDesc, setNewEdgeDesc] = useState('')

  // Filtered entities
  const filteredEntities = useMemo(() => {
    return entities.filter((e) => {
      const matchesSearch =
        !searchQuery ||
        e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.canonical_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (e.description && e.description.toLowerCase().includes(searchQuery.toLowerCase()))
      const matchesType = selectedType === 'ALL' || e.entity_type.toUpperCase() === selectedType.toUpperCase()
      return matchesSearch && matchesType
    })
  }, [entities, searchQuery, selectedType])

  const filteredNodeIds = useMemo(() => new Set(filteredEntities.map((e) => e.id)), [filteredEntities])

  // Filtered relations
  const filteredRelations = useMemo(() => {
    return relations.filter((r) => filteredNodeIds.has(r.source_id) && filteredNodeIds.has(r.target_id))
  }, [relations, filteredNodeIds])

  // Selected Entity Node
  const selectedNode = useMemo(() => {
    if (!selectedNodeId) return null
    return entities.find((e) => e.id === selectedNodeId) || null
  }, [entities, selectedNodeId])

  // Incident relations for selected node
  const selectedNodeRelations = useMemo(() => {
    if (!selectedNodeId) return []
    return relations.filter((r) => r.source_id === selectedNodeId || r.target_id === selectedNodeId)
  }, [relations, selectedNodeId])

  // Map of node ID to computed canvas position (Force layout simulator approximation)
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {}
    const count = filteredEntities.length
    if (count === 0) return positions

    const radius = Math.min(320, 40 + count * 22)
    const centerX = 450
    const centerY = 300

    filteredEntities.forEach((entity, index) => {
      const angle = (index / count) * 2 * Math.PI
      positions[entity.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      }
    })

    return positions
  }, [filteredEntities])

  // Highlighted path node IDs
  const highlightedPathNodeIds = useMemo(() => {
    if (!pathResult || !pathResult.path_found) return new Set<string>()
    const ids = new Set<string>()
    pathResult.steps.forEach((s) => {
      ids.add(s.from_id)
      ids.add(s.to_id)
    })
    return ids
  }, [pathResult])

  const handlePathSearch = async () => {
    if (!pathSource.trim() || !pathTarget.trim() || !onFindPath) return
    try {
      setIsPathSearching(true)
      const res = await onFindPath(pathSource.trim(), pathTarget.trim())
      setPathResult(res)
    } finally {
      setIsPathSearching(false)
    }
  }

  const handleExtractSubmit = async () => {
    if (!extractText.trim() || !onExtractTriplets) return
    try {
      setIsExtracting(true)
      await onExtractTriplets(extractText)
      setExtractText('')
      setActiveTab('graph')
    } finally {
      setIsExtracting(false)
    }
  }

  const handleCreateNodeSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newNodeName.trim() || !onCreateEntity) return
    const aliases = newNodeAliases
      .split(',')
      .map((a) => a.trim())
      .filter(Boolean)
    await onCreateEntity({
      name: newNodeName.trim(),
      entity_type: newNodeType,
      description: newNodeDesc.trim() || undefined,
      aliases,
    })
    setNewNodeName('')
    setNewNodeDesc('')
    setNewNodeAliases('')
    setShowAddNodeModal(false)
  }

  const handleCreateEdgeSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newEdgeSource || !newEdgeTarget || !onCreateRelation) return
    await onCreateRelation({
      source_id: newEdgeSource,
      target_id: newEdgeTarget,
      relation_type: newEdgeType,
      description: newEdgeDesc.trim() || undefined,
    })
    setNewEdgeDesc('')
    setShowAddEdgeModal(false)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)' }}>
      {/* Header with Stats & Actions */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 'var(--spacing-md)',
          background: 'var(--color-surface)',
          padding: 'var(--spacing-lg)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
            }}
          >
            <Share2 size={24} />
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 600 }}>Long-Term Knowledge Graph</h2>
            <p style={{ margin: '4px 0 0 0', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
              Multi-hop relational reasoning, cross-document entity networks & Graph-Augmented RAG
            </p>
          </div>
        </div>

        {/* Global Stats Badges */}
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap' }}>
          <div
            style={{
              padding: '6px 14px',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(6, 182, 212, 0.1)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              color: '#06b6d4',
              fontSize: '0.85rem',
              fontWeight: 500,
            }}
          >
            <strong>{stats?.total_entities ?? entities.length}</strong> Entities
          </div>
          <div
            style={{
              padding: '6px 14px',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(168, 85, 247, 0.1)',
              border: '1px solid rgba(168, 85, 247, 0.3)',
              color: '#a855f7',
              fontSize: '0.85rem',
              fontWeight: 500,
            }}
          >
            <strong>{stats?.total_relations ?? relations.length}</strong> Relations
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: 'var(--spacing-xs)', borderBottom: '1px solid var(--color-border)' }}>
        {[
          { id: 'graph', label: 'Network Studio', icon: Share2 },
          { id: 'entities', label: `Entities (${filteredEntities.length})`, icon: Layers },
          { id: 'relations', label: `Relations (${filteredRelations.length})`, icon: ArrowRight },
          { id: 'pathfinder', label: 'Multi-Hop Pathfinder', icon: Compass },
          { id: 'extract', label: 'Extract Triplets', icon: Sparkles },
        ].map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                border: 'none',
                background: 'transparent',
                borderBottom: isActive ? '2px solid var(--color-primary)' : '2px solid transparent',
                color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.9rem',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Tab 1: Interactive Network Studio */}
      {activeTab === 'graph' && (
        <div style={{ display: 'grid', gridTemplateColumns: selectedNode ? '1fr 340px' : '1fr', gap: 'var(--spacing-lg)' }}>
          <div
            style={{
              background: 'var(--color-surface)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            {/* Toolbar */}
            <div
              style={{
                padding: 'var(--spacing-md)',
                borderBottom: '1px solid var(--color-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: 'var(--spacing-sm)',
              }}
            >
              {/* Search & Category filter */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', flex: 1 }}>
                <div style={{ position: 'relative', minWidth: '220px' }}>
                  <Search
                    size={16}
                    style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-secondary)' }}
                  />
                  <input
                    type="text"
                    placeholder="Search entities or concepts..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value)
                      if (onSearch) onSearch(e.target.value, selectedType)
                    }}
                    style={{
                      width: '100%',
                      padding: '7px 10px 7px 32px',
                      background: 'var(--color-background)',
                      border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--color-text)',
                      fontSize: '0.85rem',
                    }}
                  />
                </div>

                <select
                  value={selectedType}
                  onChange={(e) => {
                    setSelectedType(e.target.value)
                    if (onSearch) onSearch(searchQuery, e.target.value)
                  }}
                  style={{
                    padding: '7px 12px',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                    fontSize: '0.85rem',
                  }}
                >
                  <option value="ALL">All Types</option>
                  {Object.keys(TYPE_COLORS).map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>

                {isLoading && <Loader2 size={16} className="loading-spinner" style={{ color: 'var(--color-primary)' }} />}
              </div>

              {/* Action buttons & Zoom controls */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <button
                  onClick={() => setZoomLevel((z) => Math.min(2.0, z + 0.15))}
                  title="Zoom In"
                  style={{
                    padding: '6px 10px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                    cursor: 'pointer',
                  }}
                >
                  <ZoomIn size={16} />
                </button>
                <button
                  onClick={() => setZoomLevel((z) => Math.max(0.4, z - 0.15))}
                  title="Zoom Out"
                  style={{
                    padding: '6px 10px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                    cursor: 'pointer',
                  }}
                >
                  <ZoomOut size={16} />
                </button>
                <button
                  onClick={() => {
                    setZoomLevel(1.0)
                    setPanOffset({ x: 0, y: 0 })
                  }}
                  title="Reset View"
                  style={{
                    padding: '6px 10px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                    cursor: 'pointer',
                  }}
                >
                  <RefreshCw size={16} />
                </button>
                {onCreateEntity && (
                  <button
                    onClick={() => setShowAddNodeModal(true)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '7px 12px',
                      borderRadius: 'var(--radius-md)',
                      background: 'var(--color-primary)',
                      border: 'none',
                      color: '#fff',
                      fontSize: '0.85rem',
                      fontWeight: 500,
                      cursor: 'pointer',
                    }}
                  >
                    <Plus size={15} /> Add Entity
                  </button>
                )}
                {onCreateRelation && entities.length >= 2 && (
                  <button
                    onClick={() => setShowAddEdgeModal(true)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '7px 12px',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(168, 85, 247, 0.15)',
                      border: '1px solid rgba(168, 85, 247, 0.4)',
                      color: '#a855f7',
                      fontSize: '0.85rem',
                      fontWeight: 500,
                      cursor: 'pointer',
                    }}
                  >
                    <Plus size={15} /> Add Relation
                  </button>
                )}
              </div>
            </div>

            {/* SVG Interactive Canvas */}
            <div
              style={{
                height: '560px',
                background: '#0d1117',
                position: 'relative',
                overflow: 'hidden',
                cursor: isDragging ? 'grabbing' : 'grab',
              }}
              onMouseDown={(e) => {
                setIsDragging(true)
                setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y })
              }}
              onMouseMove={(e) => {
                if (!isDragging) return
                setPanOffset({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y })
              }}
              onMouseUp={() => setIsDragging(false)}
              onMouseLeave={() => setIsDragging(false)}
            >
              <svg
                width="100%"
                height="100%"
                style={{
                  transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
                  transformOrigin: 'center center',
                  transition: isDragging ? 'none' : 'transform 0.1s ease-out',
                }}
              >
                {/* Arrow markers */}
                <defs>
                  <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
                  </marker>
                  <marker id="arrow-highlight" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#06b6d4" />
                  </marker>
                </defs>

                {/* Edges / Relations */}
                {filteredRelations.map((relation) => {
                  const srcPos = nodePositions[relation.source_id]
                  const tgtPos = nodePositions[relation.target_id]
                  if (!srcPos || !tgtPos) return null

                  const isEdgeSelected = selectedEdgeId === relation.id
                  const isHighlighted =
                    highlightedPathNodeIds.has(relation.source_id) && highlightedPathNodeIds.has(relation.target_id)

                  const midX = (srcPos.x + tgtPos.x) / 2
                  const midY = (srcPos.y + tgtPos.y) / 2

                  return (
                    <g
                      key={relation.id}
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedEdgeId(relation.id)
                      }}
                      style={{ cursor: 'pointer' }}
                    >
                      <line
                        x1={srcPos.x}
                        y1={srcPos.y}
                        x2={tgtPos.x}
                        y2={tgtPos.y}
                        stroke={isHighlighted ? '#06b6d4' : isEdgeSelected ? '#a855f7' : '#334155'}
                        strokeWidth={isHighlighted ? 3 : isEdgeSelected ? 2.5 : 1.5}
                        strokeDasharray={relation.confidence < 0.7 ? '4,4' : 'none'}
                        markerEnd={isHighlighted ? 'url(#arrow-highlight)' : 'url(#arrow)'}
                      />
                      {/* Relation type pill */}
                      <rect
                        x={midX - 35}
                        y={midY - 10}
                        width="70"
                        height="18"
                        rx="4"
                        fill="#1e293b"
                        stroke={isHighlighted ? '#06b6d4' : '#475569'}
                        strokeWidth="1"
                      />
                      <text
                        x={midX}
                        y={midY + 3}
                        fill={isHighlighted ? '#06b6d4' : '#94a3b8'}
                        fontSize="9"
                        textAnchor="middle"
                        fontFamily="monospace"
                      >
                        {relation.relation_type.length > 11 ? relation.relation_type.slice(0, 10) + '…' : relation.relation_type}
                      </text>
                    </g>
                  )
                })}

                {/* Nodes / Entities */}
                {filteredEntities.map((entity) => {
                  const pos = nodePositions[entity.id]
                  if (!pos) return null

                  const style = TYPE_COLORS[entity.entity_type.toUpperCase()] || TYPE_COLORS.OTHER
                  const isNodeSelected = selectedNodeId === entity.id
                  const isHighlighted = highlightedPathNodeIds.has(entity.id)

                  return (
                    <g
                      key={entity.id}
                      transform={`translate(${pos.x}, ${pos.y})`}
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedNodeId(entity.id)
                      }}
                      style={{ cursor: 'pointer' }}
                    >
                      {/* Outer pulse circle for selected/highlighted */}
                      {(isNodeSelected || isHighlighted) && (
                        <circle r="30" fill="none" stroke={style.glow} strokeWidth="3" opacity="0.8" />
                      )}

                      {/* Main node circle */}
                      <circle
                        r="20"
                        fill={style.bg}
                        stroke={isNodeSelected ? '#ffffff' : style.border}
                        strokeWidth={isNodeSelected ? 2.5 : 1.5}
                      />

                      {/* Node label */}
                      <text
                        y="4"
                        fill="#ffffff"
                        fontSize="10"
                        fontWeight="600"
                        textAnchor="middle"
                        pointerEvents="none"
                      >
                        {entity.name.slice(0, 3).toUpperCase()}
                      </text>

                      {/* Name label beneath node */}
                      <text
                        y="34"
                        fill={isNodeSelected ? '#38bdf8' : '#e2e8f0'}
                        fontSize="11"
                        fontWeight={isNodeSelected ? '600' : '400'}
                        textAnchor="middle"
                        pointerEvents="none"
                      >
                        {entity.name.length > 16 ? entity.name.slice(0, 15) + '…' : entity.name}
                      </text>
                    </g>
                  )
                })}
              </svg>

              {filteredEntities.length === 0 && (
                <div
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    textAlign: 'center',
                    color: 'var(--color-text-secondary)',
                  }}
                >
                  <Share2 size={40} style={{ opacity: 0.3, marginBottom: '8px' }} />
                  <p>No knowledge entities matching filter.</p>
                </div>
              )}
            </div>
          </div>

          {/* Node Inspector Drawer */}
          {selectedNode && (
            <div
              style={{
                background: 'var(--color-surface)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--color-border)',
                padding: 'var(--spacing-lg)',
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--spacing-md)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span
                    style={{
                      padding: '3px 8px',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      background: TYPE_COLORS[selectedNode.entity_type.toUpperCase()]?.bg || 'var(--color-background)',
                      color: TYPE_COLORS[selectedNode.entity_type.toUpperCase()]?.text || 'var(--color-text)',
                    }}
                  >
                    {selectedNode.entity_type}
                  </span>
                  <h3 style={{ margin: '8px 0 0 0', fontSize: '1.2rem', fontWeight: 600 }}>{selectedNode.name}</h3>
                </div>
                <button
                  onClick={() => setSelectedNodeId(null)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--color-text-secondary)',
                    cursor: 'pointer',
                    fontSize: '1rem',
                  }}
                >
                  ✕
                </button>
              </div>

              {selectedNode.description && (
                <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
                  {selectedNode.description}
                </p>
              )}

              {selectedNode.aliases && selectedNode.aliases.length > 0 && (
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>ALIASES</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                    {selectedNode.aliases.map((alias, i) => (
                      <span
                        key={i}
                        style={{
                          padding: '2px 8px',
                          background: 'var(--color-background)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.75rem',
                          border: '1px solid var(--color-border)',
                        }}
                      >
                        {alias}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Connected Relations */}
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                  RELATIONS ({selectedNodeRelations.length})
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px', maxHeight: '180px', overflowY: 'auto' }}>
                  {selectedNodeRelations.map((rel) => {
                    const isOutgoing = rel.source_id === selectedNode.id
                    const otherEntityId = isOutgoing ? rel.target_id : rel.source_id
                    const otherEntity = entities.find((e) => e.id === otherEntityId)

                    return (
                      <div
                        key={rel.id}
                        onClick={() => setSelectedNodeId(otherEntityId)}
                        style={{
                          padding: '8px',
                          background: 'var(--color-background)',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--color-border)',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                        }}
                      >
                        <div>
                          <span style={{ color: '#a855f7', fontWeight: 600, fontSize: '0.75rem' }}>
                            {isOutgoing ? '➔ ' : '⬅ '}
                            {rel.relation_type}
                          </span>
                          <div style={{ fontWeight: 500, marginTop: '2px' }}>{otherEntity ? otherEntity.name : 'Unknown Node'}</div>
                        </div>
                        {onDeleteRelation && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              onDeleteRelation(rel.id)
                            }}
                            title="Delete relation"
                            style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}
                          >
                            <Trash2 size={13} />
                          </button>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
                {onExpandNode && (
                  <button
                    onClick={() => onExpandNode(selectedNode.id, 2)}
                    style={{
                      flex: 1,
                      padding: '8px',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(6, 182, 212, 0.15)',
                      border: '1px solid rgba(6, 182, 212, 0.3)',
                      color: '#06b6d4',
                      fontSize: '0.85rem',
                      fontWeight: 500,
                      cursor: 'pointer',
                    }}
                  >
                    Expand 2-Hops
                  </button>
                )}
                {onDeleteEntity && (
                  <button
                    onClick={() => {
                      onDeleteEntity(selectedNode.id)
                      setSelectedNodeId(null)
                    }}
                    style={{
                      padding: '8px 12px',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      color: '#ef4444',
                      fontSize: '0.85rem',
                      cursor: 'pointer',
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Entities Table */}
      {activeTab === 'entities' && (
        <div
          style={{
            background: 'var(--color-surface)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border)',
            overflow: 'hidden',
          }}
        >
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ background: 'var(--color-background)', borderBottom: '1px solid var(--color-border)' }}>
                <th style={{ padding: '12px 16px' }}>Name</th>
                <th style={{ padding: '12px 16px' }}>Type</th>
                <th style={{ padding: '12px 16px' }}>Aliases</th>
                <th style={{ padding: '12px 16px' }}>Confidence</th>
                <th style={{ padding: '12px 16px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredEntities.map((e) => (
                <tr key={e.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td style={{ padding: '12px 16px', fontWeight: 600 }}>{e.name}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span
                      style={{
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        background: TYPE_COLORS[e.entity_type.toUpperCase()]?.bg || 'var(--color-background)',
                        color: TYPE_COLORS[e.entity_type.toUpperCase()]?.text || 'var(--color-text)',
                      }}
                    >
                      {e.entity_type}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', color: 'var(--color-text-secondary)' }}>
                    {e.aliases && e.aliases.length > 0 ? e.aliases.join(', ') : '—'}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{ color: e.confidence >= 0.8 ? '#10b981' : '#f59e0b', fontWeight: 500 }}>
                      {Math.round(e.confidence * 100)}%
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                    <button
                      onClick={() => {
                        setSelectedNodeId(e.id)
                        setActiveTab('graph')
                      }}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--color-primary)',
                        cursor: 'pointer',
                        marginRight: '8px',
                      }}
                    >
                      <Eye size={16} />
                    </button>
                    {onDeleteEntity && (
                      <button
                        onClick={() => onDeleteEntity(e.id)}
                        style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 3: Relations Table */}
      {activeTab === 'relations' && (
        <div
          style={{
            background: 'var(--color-surface)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border)',
            overflow: 'hidden',
          }}
        >
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ background: 'var(--color-background)', borderBottom: '1px solid var(--color-border)' }}>
                <th style={{ padding: '12px 16px' }}>Source Entity</th>
                <th style={{ padding: '12px 16px' }}>Predicate / Relation</th>
                <th style={{ padding: '12px 16px' }}>Target Entity</th>
                <th style={{ padding: '12px 16px' }}>Weight</th>
                <th style={{ padding: '12px 16px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRelations.map((r) => {
                const src = entities.find((e) => e.id === r.source_id)
                const tgt = entities.find((e) => e.id === r.target_id)
                return (
                  <tr key={r.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 600 }}>{src ? src.name : r.source_id}</td>
                    <td style={{ padding: '12px 16px' }}>
                      <span
                        style={{
                          padding: '3px 8px',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.75rem',
                          fontFamily: 'monospace',
                          background: 'rgba(168, 85, 247, 0.15)',
                          color: '#a855f7',
                        }}
                      >
                        {r.relation_type}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', fontWeight: 600 }}>{tgt ? tgt.name : r.target_id}</td>
                    <td style={{ padding: '12px 16px' }}>{r.weight.toFixed(1)}</td>
                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                      {onDeleteRelation && (
                        <button
                          onClick={() => onDeleteRelation(r.id)}
                          style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 4: Multi-Hop Pathfinder */}
      {activeTab === 'pathfinder' && (
        <div
          style={{
            background: 'var(--color-surface)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border)',
            padding: 'var(--spacing-xl)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--spacing-lg)',
          }}
        >
          <div>
            <h3 style={{ margin: '0 0 6px 0', fontSize: '1.2rem', fontWeight: 600 }}>Multi-Hop Relational Pathfinder</h3>
            <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
              Find shortest causal, conceptual, or methodology paths connecting two distant entities in your knowledge graph.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 'var(--spacing-md)', alignItems: 'flex-end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '6px' }}>SOURCE ENTITY</label>
              <input
                type="text"
                placeholder="e.g. Transformer"
                value={pathSource}
                onChange={(e) => setPathSource(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  background: 'var(--color-background)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--color-text)',
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '6px' }}>TARGET ENTITY</label>
              <input
                type="text"
                placeholder="e.g. GPT-4"
                value={pathTarget}
                onChange={(e) => setPathTarget(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  background: 'var(--color-background)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--color-text)',
                }}
              />
            </div>
            <button
              onClick={handlePathSearch}
              disabled={isPathSearching || !pathSource || !pathTarget}
              style={{
                padding: '10px 20px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--color-primary)',
                border: 'none',
                color: '#fff',
                fontWeight: 600,
                cursor: 'pointer',
                opacity: isPathSearching || !pathSource || !pathTarget ? 0.6 : 1,
              }}
            >
              {isPathSearching ? 'Traversing...' : 'Find Path'}
            </button>
          </div>

          {pathResult && (
            <div
              style={{
                marginTop: 'var(--spacing-md)',
                padding: 'var(--spacing-lg)',
                background: 'var(--color-background)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)',
              }}
            >
              {pathResult.path_found ? (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981', fontWeight: 600, marginBottom: '12px' }}>
                    <Sparkles size={18} /> Path Found ({pathResult.hop_count} Hops)
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                    <span style={{ padding: '6px 12px', background: '#1e293b', borderRadius: 'var(--radius-sm)', fontWeight: 600 }}>
                      {pathResult.source_entity}
                    </span>
                    {pathResult.steps.map((step, idx) => (
                      <React.Fragment key={idx}>
                        <span style={{ color: '#a855f7', fontSize: '0.8rem', fontFamily: 'monospace' }}>
                          ──[{step.relation_type}]──▶
                        </span>
                        <span style={{ padding: '6px 12px', background: '#1e293b', borderRadius: 'var(--radius-sm)', fontWeight: 600 }}>
                          {entities.find((e) => e.id === step.to_id)?.name || step.to_id}
                        </span>
                      </React.Fragment>
                    ))}
                  </div>
                  {pathResult.summary && (
                    <p style={{ marginTop: '12px', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                      {pathResult.summary}
                    </p>
                  )}
                </div>
              ) : (
                <div style={{ color: '#ef4444', fontWeight: 500 }}>
                  No relational path found between "{pathSource}" and "{pathTarget}" within traversal depth.
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 5: Triplet Extraction */}
      {activeTab === 'extract' && (
        <div
          style={{
            background: 'var(--color-surface)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border)',
            padding: 'var(--spacing-xl)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--spacing-md)',
          }}
        >
          <div>
            <h3 style={{ margin: '0 0 6px 0', fontSize: '1.2rem', fontWeight: 600 }}>Automated Triplet Extraction</h3>
            <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
              Paste scientific literature, paper abstract, or synthesis finding to extract and catalog entities and relations.
            </p>
          </div>

          <textarea
            rows={6}
            placeholder="Paste text or research notes here (e.g. Graph Neural Networks (GNNs) operate on graph structures to perform node classification and link prediction on benchmark datasets like Cora and PubMed)..."
            value={extractText}
            onChange={(e) => setExtractText(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              background: 'var(--color-background)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-text)',
              fontSize: '0.9rem',
              lineHeight: 1.5,
            }}
          />

          <button
            onClick={handleExtractSubmit}
            disabled={isExtracting || !extractText.trim()}
            style={{
              alignSelf: 'flex-start',
              padding: '10px 24px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-primary)',
              border: 'none',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer',
              opacity: isExtracting || !extractText.trim() ? 0.6 : 1,
            }}
          >
            {isExtracting ? 'Extracting & Indexing...' : 'Extract & Persist to Graph'}
          </button>
        </div>
      )}

      {/* Modal: Add Entity */}
      {showAddNodeModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              background: 'var(--color-surface)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border)',
              padding: 'var(--spacing-xl)',
              width: '460px',
              maxWidth: '90vw',
            }}
          >
            <h3 style={{ margin: '0 0 var(--spacing-md) 0' }}>Add Knowledge Entity</h3>
            <form onSubmit={handleCreateNodeSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '4px' }}>NAME</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Qubit Superposition"
                  value={newNodeName}
                  onChange={(e) => setNewNodeName(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '4px' }}>TYPE</label>
                <select
                  value={newNodeType}
                  onChange={(e) => setNewNodeType(e.target.value as EntityType)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                  }}
                >
                  {Object.keys(TYPE_COLORS).map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '4px' }}>DESCRIPTION</label>
                <textarea
                  rows={3}
                  placeholder="Contextual description of this concept or entity..."
                  value={newNodeDesc}
                  onChange={(e) => setNewNodeDesc(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '4px' }}>ALIASES (comma separated)</label>
                <input
                  type="text"
                  placeholder="e.g. Quantum State, Superposition"
                  value={newNodeAliases}
                  onChange={(e) => setNewNodeAliases(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--spacing-sm)', marginTop: 'var(--spacing-sm)' }}>
                <button
                  type="button"
                  onClick={() => setShowAddNodeModal(false)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: 'var(--radius-md)',
                    background: 'none',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '8px 16px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-primary)',
                    border: 'none',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Create Entity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Add Relation */}
      {showAddEdgeModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              background: 'var(--color-surface)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border)',
              padding: 'var(--spacing-xl)',
              width: '460px',
              maxWidth: '90vw',
            }}
          >
            <h3 style={{ margin: '0 0 var(--spacing-md) 0' }}>Add Knowledge Relation</h3>
            <form onSubmit={handleCreateEdgeSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '4px' }}>SOURCE ENTITY</label>
                <select
                  required
                  value={newEdgeSource}
                  onChange={(e) => setNewEdgeSource(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                  }}
                >
                  <option value="">Select source entity...</option>
                  {entities.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.name} ({e.entity_type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '4px' }}>RELATION TYPE</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. DERIVED_FROM, RELATES_TO, ENHANCES"
                  value={newEdgeType}
                  onChange={(e) => setNewEdgeType(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '4px' }}>TARGET ENTITY</label>
                <select
                  required
                  value={newEdgeTarget}
                  onChange={(e) => setNewEdgeTarget(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                  }}
                >
                  <option value="">Select target entity...</option>
                  {entities.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.name} ({e.entity_type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '4px' }}>DESCRIPTION (optional)</label>
                <input
                  type="text"
                  placeholder="Contextual explanation of this relationship..."
                  value={newEdgeDesc}
                  onChange={(e) => setNewEdgeDesc(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--spacing-sm)', marginTop: 'var(--spacing-sm)' }}>
                <button
                  type="button"
                  onClick={() => setShowAddEdgeModal(false)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: 'var(--radius-md)',
                    background: 'none',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '8px 16px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-primary)',
                    border: 'none',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Create Relation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
