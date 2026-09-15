import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { ResearchMemoryViewer } from '../components/ResearchMemoryViewer'
import type { MemoryItem, CreateMemoryPayload } from '../types/memory'
import { Loader2 } from 'lucide-react'

export function MemoryPage() {
  const [memories, setMemories] = useState<MemoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMemories = async (type?: string, tag?: string) => {
    try {
      setLoading(true)
      const params: Record<string, any> = { limit: 100 }
      if (type && type !== 'all') params.memory_type = type
      if (tag && tag !== 'all') params.tag = tag

      const res = await api.get<MemoryItem[]>('/memory', { params })
      setMemories(res.data || [])
      setError(null)
    } catch (err) {
      console.error('Failed to load memories:', err)
      setError('Failed to load research memories')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (query: string, type?: string, tag?: string) => {
    if (!query.trim()) {
      await fetchMemories(type, tag)
      return
    }

    try {
      setLoading(true)
      const params: Record<string, any> = { query, top_k: 20 }
      if (type && type !== 'all') params.memory_type = type
      if (tag && tag !== 'all') params.tag = tag

      const res = await api.get<{ memories: MemoryItem[] }>('/memory/search', { params })
      setMemories(res.data?.memories || [])
      setError(null)
    } catch (err) {
      console.error('Failed to recall memories:', err)
      setError('Memory search recall failed')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateMemory = async (payload: CreateMemoryPayload) => {
    try {
      const res = await api.post<MemoryItem>('/memory', payload)
      setMemories((prev) => [res.data, ...prev])
    } catch (err) {
      console.error('Failed to store memory:', err)
      throw err
    }
  }

  const handleDeleteMemory = async (memoryId: string) => {
    if (!window.confirm('Are you sure you want to delete this memory?')) return

    try {
      await api.delete(`/memory/${memoryId}`)
      setMemories((prev) => prev.filter((m) => m.id !== memoryId))
    } catch (err) {
      console.error('Failed to delete memory:', err)
    }
  }

  useEffect(() => {
    fetchMemories()
  }, [])

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xl)' }}>
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

      {loading && memories.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
          <Loader2 className="loading-spinner" size={32} />
        </div>
      ) : (
        <ResearchMemoryViewer
          memories={memories}
          onSearch={handleSearch}
          onCreateMemory={handleCreateMemory}
          onDeleteMemory={handleDeleteMemory}
          isLoading={loading}
        />
      )}
    </div>
  )
}
