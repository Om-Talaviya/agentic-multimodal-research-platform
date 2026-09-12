import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { KnowledgeGraphViewer } from '../components/KnowledgeGraphViewer'
import type {
  KnowledgeEntity,
  KnowledgeRelation,
  GraphStats,
  CreateEntityPayload,
  CreateRelationPayload,
  GraphPathResult,
} from '../types/graph'
import { Loader2 } from 'lucide-react'

export function KnowledgeGraphPage() {
  const [entities, setEntities] = useState<KnowledgeEntity[]>([])
  const [relations, setRelations] = useState<KnowledgeRelation[]>([])
  const [stats, setStats] = useState<GraphStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchGraphData = async (query?: string, entityType?: string) => {
    try {
      setLoading(true)
      const params: Record<string, any> = { limit: 150 }
      if (query && query.trim()) params.search = query.trim()
      if (entityType && entityType !== 'ALL') params.entity_type = entityType

      const [nodesRes, edgesRes, statsRes] = await Promise.all([
        api.get<KnowledgeEntity[]>('/graph/nodes', { params }),
        api.get<KnowledgeRelation[]>('/graph/edges', { params: { limit: 300 } }),
        api.get<GraphStats>('/graph/stats'),
      ])

      setEntities(nodesRes.data || [])
      setRelations(edgesRes.data || [])
      setStats(statsRes.data || null)
      setError(null)
    } catch (err) {
      console.error('Failed to load knowledge graph data:', err)
      setError('Failed to load knowledge graph data')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (query: string, entityType?: string) => {
    await fetchGraphData(query, entityType)
  }

  const handleExpandNode = async (nodeId: string, hops: number) => {
    try {
      const res = await api.get<{ nodes: KnowledgeEntity[]; edges: KnowledgeRelation[] }>('/graph/subgraph', {
        params: { center_entity_id: nodeId, k_hops: hops },
      })
      if (res.data) {
        // Merge nodes and edges
        setEntities((prev) => {
          const existingIds = new Set(prev.map((e) => e.id))
          const newNodes = (res.data.nodes || []).filter((n) => !existingIds.has(n.id))
          return [...prev, ...newNodes]
        })
        setRelations((prev) => {
          const existingIds = new Set(prev.map((r) => r.id))
          const newEdges = (res.data.edges || []).filter((r) => !existingIds.has(r.id))
          return [...prev, ...newEdges]
        })
      }
    } catch (err) {
      console.error('Failed to expand node subgraph:', err)
    }
  }

  const handleCreateEntity = async (payload: CreateEntityPayload) => {
    try {
      const res = await api.post<KnowledgeEntity>('/graph/nodes', payload)
      setEntities((prev) => [res.data, ...prev])
    } catch (err) {
      console.error('Failed to create entity:', err)
      throw err
    }
  }

  const handleCreateRelation = async (payload: CreateRelationPayload) => {
    try {
      const res = await api.post<KnowledgeRelation>('/graph/edges', payload)
      setRelations((prev) => [res.data, ...prev])
    } catch (err) {
      console.error('Failed to create relation:', err)
      throw err
    }
  }

  const handleDeleteEntity = async (entityId: string) => {
    if (!window.confirm('Delete this entity node and all attached relations?')) return
    try {
      await api.delete(`/graph/nodes/${entityId}`)
      setEntities((prev) => prev.filter((e) => e.id !== entityId))
      setRelations((prev) => prev.filter((r) => r.source_id !== entityId && r.target_id !== entityId))
    } catch (err) {
      console.error('Failed to delete entity:', err)
    }
  }

  const handleDeleteRelation = async (relationId: string) => {
    try {
      await api.delete(`/graph/edges/${relationId}`)
      setRelations((prev) => prev.filter((r) => r.id !== relationId))
    } catch (err) {
      console.error('Failed to delete relation:', err)
    }
  }

  const handleFindPath = async (source: string, target: string): Promise<GraphPathResult | null> => {
    try {
      const res = await api.get<GraphPathResult>('/graph/paths', {
        params: { source, target, max_depth: 4 },
      })
      return res.data
    } catch (err) {
      console.error('Failed to query path:', err)
      return null
    }
  }

  const handleExtractTriplets = async (text: string) => {
    try {
      await api.post('/graph/extract', { text, persist: true })
      await fetchGraphData()
    } catch (err) {
      console.error('Failed to extract triplets:', err)
    }
  }

  useEffect(() => {
    fetchGraphData()
  }, [])

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xl)' }}>
      {error && (
        <div
          style={{
            padding: 'var(--spacing-md)',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            color: '#ef4444',
            fontSize: '0.9rem',
          }}
        >
          {error}
        </div>
      )}

      {loading && entities.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
          <Loader2 className="loading-spinner" size={32} />
        </div>
      ) : (
        <KnowledgeGraphViewer
          entities={entities}
          relations={relations}
          stats={stats}
          isLoading={loading}
          onSearch={handleSearch}
          onExpandNode={handleExpandNode}
          onCreateEntity={handleCreateEntity}
          onCreateRelation={handleCreateRelation}
          onDeleteEntity={handleDeleteEntity}
          onDeleteRelation={handleDeleteRelation}
          onFindPath={handleFindPath}
          onExtractTriplets={handleExtractTriplets}
        />
      )}
    </div>
  )
}
