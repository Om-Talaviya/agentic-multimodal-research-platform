import { useState } from 'react'
import {
  Brain,
  Search,
  Tag,
  Clock,
  Sparkles,
  BookOpen,
  Lightbulb,
  CheckCircle2,
  Trash2,
  Plus,
  ExternalLink,
  Filter,
  Eye,
  Zap,
} from 'lucide-react'
import type { MemoryItem, MemoryType, CreateMemoryPayload } from '../types/memory'

interface ResearchMemoryViewerProps {
  memories: MemoryItem[]
  onSearch?: (query: string, type?: string, tag?: string) => Promise<void>
  onCreateMemory?: (payload: CreateMemoryPayload) => Promise<void>
  onDeleteMemory?: (memoryId: string) => Promise<void>
  isLoading?: boolean
  selectedJobId?: string
}

export function ResearchMemoryViewer({
  memories = [],
  onSearch,
  onCreateMemory,
  onDeleteMemory,
  isLoading = false,
  selectedJobId,
}: ResearchMemoryViewerProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedTag, setSelectedTag] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [expandedMemoryId, setExpandedMemoryId] = useState<string | null>(null)

  // Form State for new memory
  const [newTitle, setNewTitle] = useState('')
  const [newContent, setNewContent] = useState('')
  const [newType, setNewType] = useState<MemoryType>('finding')
  const [newTagsStr, setNewTagsStr] = useState('')
  const [newConfidence, setNewConfidence] = useState(1.0)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Extract unique tags
  const allTags = Array.from(
    new Set(memories.flatMap((m) => m.tags || []))
  ).sort()

  const memoryTypeConfig: Record<string, { label: string; color: string; bg: string; icon: typeof Lightbulb }> = {
    finding: { label: 'Finding', color: '#38bdf8', bg: 'rgba(56, 189, 248, 0.12)', icon: CheckCircle2 },
    insight: { label: 'Insight', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.12)', icon: Lightbulb },
    methodology: { label: 'Methodology', color: '#10b981', bg: 'rgba(16, 185, 129, 0.12)', icon: BookOpen },
    concept: { label: 'Concept', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.12)', icon: Sparkles },
    summary: { label: 'Summary', color: '#6366f1', bg: 'rgba(99, 102, 241, 0.12)', icon: Brain },
    hypothesis: { label: 'Hypothesis', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.12)', icon: Zap },
  }

  // Filter memories locally
  const filteredMemories = memories.filter((m) => {
    const matchesType = selectedType === 'all' || m.memory_type === selectedType
    const matchesTag = selectedTag === 'all' || (m.tags && m.tags.includes(selectedTag))
    const matchesQuery =
      !searchQuery ||
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (m.tags && m.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase())))
    return matchesType && matchesTag && matchesQuery
  })

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (onSearch) {
      onSearch(
        searchQuery,
        selectedType === 'all' ? undefined : selectedType,
        selectedTag === 'all' ? undefined : selectedTag
      )
    }
  }

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim() || !newContent.trim() || !onCreateMemory) return

    setIsSubmitting(true)
    try {
      const tags = newTagsStr
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)

      await onCreateMemory({
        title: newTitle.trim(),
        content: newContent.trim(),
        memory_type: newType,
        job_id: selectedJobId,
        tags,
        confidence: newConfidence,
      })

      // Reset form
      setNewTitle('')
      setNewContent('')
      setNewTagsStr('')
      setNewConfidence(1.0)
      setShowCreateModal(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--spacing-lg)',
        background: 'var(--color-surface)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-border)',
        padding: 'var(--spacing-xl)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 'var(--spacing-md)',
          borderBottom: '1px solid var(--color-border)',
          paddingBottom: 'var(--spacing-lg)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-primary)',
            }}
          >
            <Brain size={24} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>Research Memory</h3>
              <span
                style={{
                  fontSize: '0.75rem',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  background: 'rgba(99, 102, 241, 0.15)',
                  color: 'var(--color-primary)',
                  fontWeight: 600,
                }}
              >
                Generation 3
              </span>
            </div>
            <p style={{ margin: '4px 0 0 0', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
              Autonomous cross-session project memory, conceptual indexing, and historical recall.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
          {onCreateMemory && (
            <button
              type="button"
              onClick={() => setShowCreateModal(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-xs)',
                padding: 'var(--spacing-sm) var(--spacing-md)',
                background: 'var(--color-primary)',
                color: '#fff',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontWeight: 600,
                cursor: 'pointer',
                fontSize: '0.85rem',
              }}
            >
              <Plus size={16} />
              Store Memory
            </button>
          )}
        </div>
      </div>

      {/* Search & Filters */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
          <div
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-sm)',
              background: 'var(--color-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: '0 var(--spacing-md)',
            }}
          >
            <Search size={18} style={{ color: 'var(--color-text-secondary)' }} />
            <input
              type="text"
              placeholder="Search concepts, findings, or methodology notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                flex: 1,
                padding: 'var(--spacing-sm) 0',
                background: 'transparent',
                border: 'none',
                color: 'var(--color-text)',
                outline: 'none',
                fontSize: '0.9rem',
              }}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            style={{
              padding: 'var(--spacing-sm) var(--spacing-lg)',
              background: 'var(--color-surface-hover)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-text)',
              cursor: 'pointer',
              fontWeight: 500,
              fontSize: '0.85rem',
            }}
          >
            {isLoading ? 'Recalling...' : 'Recall'}
          </button>
        </form>

        {/* Type Filter Pills */}
        <div style={{ display: 'flex', gap: 'var(--spacing-xs)', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginRight: '4px' }}>
            <Filter size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }} />
            Type:
          </span>
          <button
            type="button"
            onClick={() => setSelectedType('all')}
            style={{
              padding: '4px 10px',
              borderRadius: '16px',
              border: '1px solid var(--color-border)',
              background: selectedType === 'all' ? 'var(--color-primary)' : 'transparent',
              color: selectedType === 'all' ? '#fff' : 'var(--color-text-secondary)',
              fontSize: '0.75rem',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            All ({memories.length})
          </button>
          {Object.entries(memoryTypeConfig).map(([key, config]) => {
            const count = memories.filter((m) => m.memory_type === key).length
            if (count === 0 && selectedType !== key) return null
            return (
              <button
                key={key}
                type="button"
                onClick={() => setSelectedType(key)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '16px',
                  border: `1px solid ${selectedType === key ? config.color : 'var(--color-border)'}`,
                  background: selectedType === key ? config.bg : 'transparent',
                  color: selectedType === key ? config.color : 'var(--color-text-secondary)',
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                }}
              >
                {config.label} ({count})
              </button>
            )
          })}
        </div>

        {/* Tag Filters */}
        {allTags.length > 0 && (
          <div style={{ display: 'flex', gap: 'var(--spacing-xs)', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginRight: '4px' }}>
              <Tag size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }} />
              Tags:
            </span>
            <button
              type="button"
              onClick={() => setSelectedTag('all')}
              style={{
                padding: '2px 8px',
                borderRadius: '12px',
                border: '1px solid var(--color-border)',
                background: selectedTag === 'all' ? 'var(--color-surface-hover)' : 'transparent',
                color: selectedTag === 'all' ? 'var(--color-text)' : 'var(--color-text-secondary)',
                fontSize: '0.7rem',
                cursor: 'pointer',
              }}
            >
              All Tags
            </button>
            {allTags.slice(0, 10).map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => setSelectedTag(tag)}
                style={{
                  padding: '2px 8px',
                  borderRadius: '12px',
                  border: `1px solid ${selectedTag === tag ? 'var(--color-primary)' : 'var(--color-border)'}`,
                  background: selectedTag === tag ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                  color: selectedTag === tag ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                  fontSize: '0.7rem',
                  cursor: 'pointer',
                }}
              >
                #{tag}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Memories List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
        {filteredMemories.length === 0 ? (
          <div
            style={{
              padding: 'var(--spacing-xl)',
              textAlign: 'center',
              border: '1px dashed var(--color-border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-text-secondary)',
            }}
          >
            <Brain size={36} style={{ margin: '0 auto var(--spacing-sm) auto', opacity: 0.4 }} />
            <p style={{ margin: 0, fontWeight: 500 }}>No research memories found</p>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem' }}>
              Research findings and conceptual definitions will automatically persist here across sessions.
            </p>
          </div>
        ) : (
          filteredMemories.map((memory) => {
            const config = memoryTypeConfig[memory.memory_type] || memoryTypeConfig.finding
            const Icon = config.icon
            const isExpanded = expandedMemoryId === memory.id

            return (
              <div
                key={memory.id}
                style={{
                  background: 'var(--color-bg)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--spacing-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 'var(--spacing-sm)',
                  transition: 'border-color 0.2s',
                }}
              >
                {/* Memory Card Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--spacing-md)' }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)', flex: 1 }}>
                    <div
                      style={{
                        padding: '6px',
                        borderRadius: 'var(--radius-sm)',
                        background: config.bg,
                        color: config.color,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginTop: '2px',
                      }}
                    >
                      <Icon size={16} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', flexWrap: 'wrap' }}>
                        <span
                          style={{
                            fontSize: '0.7rem',
                            fontWeight: 600,
                            padding: '2px 6px',
                            borderRadius: '8px',
                            background: config.bg,
                            color: config.color,
                            textTransform: 'uppercase',
                          }}
                        >
                          {config.label}
                        </span>
                        {memory.confidence < 1.0 && (
                          <span
                            style={{
                              fontSize: '0.7rem',
                              padding: '2px 6px',
                              borderRadius: '8px',
                              background: 'rgba(245, 158, 11, 0.1)',
                              color: '#f59e0b',
                            }}
                          >
                            {(memory.confidence * 100).toFixed(0)}% confidence
                          </span>
                        )}
                        {memory.source_type && (
                          <span style={{ fontSize: '0.7rem', color: 'var(--color-text-secondary)' }}>
                            via {memory.source_type}
                          </span>
                        )}
                      </div>
                      <h4
                        style={{
                          margin: '4px 0 0 0',
                          fontSize: '0.95rem',
                          fontWeight: 600,
                          color: 'var(--color-text)',
                        }}
                      >
                        {memory.title}
                      </h4>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                    {onDeleteMemory && (
                      <button
                        type="button"
                        onClick={() => onDeleteMemory(memory.id)}
                        title="Delete Memory"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: 'var(--color-text-secondary)',
                          cursor: 'pointer',
                          padding: '4px',
                          borderRadius: 'var(--radius-sm)',
                        }}
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </div>

                {/* Content */}
                <div
                  style={{
                    fontSize: '0.85rem',
                    color: 'var(--color-text-secondary)',
                    lineHeight: 1.5,
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {isExpanded ? memory.content : memory.content.slice(0, 240)}
                  {memory.content.length > 240 && (
                    <button
                      type="button"
                      onClick={() => setExpandedMemoryId(isExpanded ? null : memory.id)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--color-primary)',
                        cursor: 'pointer',
                        fontSize: '0.8rem',
                        fontWeight: 500,
                        padding: '0 4px',
                        marginLeft: '4px',
                      }}
                    >
                      {isExpanded ? 'Show less' : '...Read more'}
                    </button>
                  )}
                </div>

                {/* Tags & Meta Footer */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: 'var(--spacing-xs)',
                    fontSize: '0.75rem',
                    color: 'var(--color-text-secondary)',
                    borderTop: '1px solid var(--color-border)',
                    paddingTop: 'var(--spacing-xs)',
                    marginTop: 'var(--spacing-xs)',
                  }}
                >
                  <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                    {memory.tags?.map((t) => (
                      <span
                        key={t}
                        style={{
                          background: 'var(--color-surface-hover)',
                          padding: '2px 6px',
                          borderRadius: '6px',
                          fontSize: '0.7rem',
                        }}
                      >
                        #{t}
                      </span>
                    ))}
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                    {memory.access_count > 0 && (
                      <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                        <Eye size={12} /> {memory.access_count} recalls
                      </span>
                    )}
                    {memory.job_id && (
                      <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                        <ExternalLink size={12} /> Job {memory.job_id.slice(0, 8)}
                      </span>
                    )}
                    {memory.created_at && (
                      <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                        <Clock size={12} /> {new Date(memory.created_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Create Memory Modal */}
      {showCreateModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 'var(--spacing-md)',
          }}
        >
          <div
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              padding: 'var(--spacing-xl)',
              maxWidth: '560px',
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--spacing-md)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 600 }}>Store New Research Memory</h3>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--color-text-secondary)',
                  cursor: 'pointer',
                  fontSize: '1.2rem',
                }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 500, marginBottom: '4px' }}>
                  Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., QAOA Parameter Scaling in Quantum Optimization"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 'var(--spacing-sm)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 500, marginBottom: '4px' }}>
                    Memory Type
                  </label>
                  <select
                    value={newType}
                    onChange={(e) => setNewType(e.target.value as MemoryType)}
                    style={{
                      width: '100%',
                      padding: 'var(--spacing-sm)',
                      background: 'var(--color-bg)',
                      border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--color-text)',
                      boxSizing: 'border-box',
                    }}
                  >
                    <option value="finding">Finding</option>
                    <option value="insight">Insight</option>
                    <option value="methodology">Methodology</option>
                    <option value="concept">Concept</option>
                    <option value="summary">Summary</option>
                    <option value="hypothesis">Hypothesis</option>
                  </select>
                </div>

                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 500, marginBottom: '4px' }}>
                    Confidence ({Math.round(newConfidence * 100)}%)
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.05"
                    value={newConfidence}
                    onChange={(e) => setNewConfidence(parseFloat(e.target.value))}
                    style={{ width: '100%', marginTop: '8px' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 500, marginBottom: '4px' }}>
                  Tags (comma separated)
                </label>
                <input
                  type="text"
                  placeholder="quantum, qaoa, optimization, benchmarks"
                  value={newTagsStr}
                  onChange={(e) => setNewTagsStr(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 'var(--spacing-sm)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 500, marginBottom: '4px' }}>
                  Content / Findings *
                </label>
                <textarea
                  required
                  rows={4}
                  placeholder="Detailed finding, conceptual definition, or methodology guideline to persist..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 'var(--spacing-sm)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                    boxSizing: 'border-box',
                    fontFamily: 'inherit',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--spacing-sm)', marginTop: 'var(--spacing-sm)' }}>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  style={{
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    background: 'transparent',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  style={{
                    padding: 'var(--spacing-sm) var(--spacing-lg)',
                    background: 'var(--color-primary)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 'var(--radius-md)',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  {isSubmitting ? 'Storing...' : 'Save to Memory'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
