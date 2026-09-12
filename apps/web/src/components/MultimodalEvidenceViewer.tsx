import React, { useState } from 'react'
import { Evidence, Citation, CitationCoordinates } from '../types/research'
import { Volume2, Video, BarChart3, FileText, Clock, User, CheckCircle, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'

interface MultimodalEvidenceViewerProps {
  evidence: Evidence[]
  title?: string
}

export const MultimodalEvidenceViewer: React.FC<MultimodalEvidenceViewerProps> = ({
  evidence,
  title = "Multimodal Evidence & Media Citations"
}) => {
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [filterType, setFilterType] = useState<string>("all")

  if (!evidence || evidence.length === 0) {
    return (
      <div className="empty-state" style={{ padding: '24px', textAlign: 'center', background: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>No multimodal evidence records attached to this research job.</p>
      </div>
    )
  }

  const formatTimestamp = (seconds?: number | null) => {
    if (seconds === undefined || seconds === null) return null
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getMediaBadge = (coords?: CitationCoordinates | null) => {
    if (!coords) return <span className="badge badge-secondary"><FileText size={12} style={{ marginRight: '4px' }} /> Document</span>
    if (coords.timestamp_start !== undefined && coords.timestamp_start !== null) {
      return (
        <span className="badge" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
          {coords.media_type === 'video' ? <Video size={12} style={{ marginRight: '4px' }} /> : <Volume2 size={12} style={{ marginRight: '4px' }} />}
          {coords.media_type === 'video' ? 'Video Frame' : 'Audio Track'}
        </span>
      )
    }
    if (coords.chart_data || coords.media_type === 'chart') {
      return (
        <span className="badge" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', border: '1px solid rgba(168, 85, 247, 0.3)' }}>
          <BarChart3 size={12} style={{ marginRight: '4px' }} /> Scientific Chart
        </span>
      )
    }
    if (coords.page_number) {
      return (
        <span className="badge badge-info">
          <FileText size={12} style={{ marginRight: '4px' }} /> Page {coords.page_number}
        </span>
      )
    }
    return <span className="badge badge-secondary"><FileText size={12} style={{ marginRight: '4px' }} /> Text Excerpt</span>
  }

  const filteredEvidence = evidence.filter(ev => {
    if (filterType === 'all') return true
    const coords = ev.citation_coordinates || (ev.citations && ev.citations[0]?.coordinates)
    if (filterType === 'audio_video') return coords?.timestamp_start !== undefined && coords?.timestamp_start !== null
    if (filterType === 'chart') return !!coords?.chart_data || coords?.media_type === 'chart'
    if (filterType === 'doc') return !coords?.timestamp_start && !coords?.chart_data
    return true
  })

  return (
    <div className="card" style={{ marginBottom: '24px', background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>{title}</span>
            <span className="badge badge-primary">{filteredEvidence.length} items</span>
          </h3>
          <p style={{ margin: '4px 0 0 0', fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>
            Cross-referenced multi-modal claims with timestamp anchors and structured chart data.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            onClick={() => setFilterType('all')}
            className={`btn btn-sm ${filterType === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.78rem', padding: '4px 10px' }}
          >
            All Modalities
          </button>
          <button
            onClick={() => setFilterType('audio_video')}
            className={`btn btn-sm ${filterType === 'audio_video' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.78rem', padding: '4px 10px' }}
          >
            Audio & Video
          </button>
          <button
            onClick={() => setFilterType('chart')}
            className={`btn btn-sm ${filterType === 'chart' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.78rem', padding: '4px 10px' }}
          >
            Charts & Graphs
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filteredEvidence.map((ev, idx) => {
          const coords = ev.citation_coordinates || (ev.citations && ev.citations[0]?.coordinates)
          const isExpanded = expandedId === (ev.id || `ev-${idx}`)
          const startTs = formatTimestamp(coords?.timestamp_start)
          const endTs = formatTimestamp(coords?.timestamp_end)

          return (
            <div
              key={ev.id || idx}
              style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                padding: '14px 16px',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', flexWrap: 'wrap' }}>
                    {getMediaBadge(coords)}
                    {startTs && endTs && (
                      <span className="badge" style={{ background: 'rgba(245, 158, 11, 0.12)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={11} /> {startTs} - {endTs}
                      </span>
                    )}
                    {coords?.speaker && (
                      <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.12)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <User size={11} /> {coords.speaker}
                      </span>
                    )}
                    <span className="badge badge-success" style={{ fontSize: '0.72rem' }}>
                      <CheckCircle size={10} style={{ marginRight: '3px' }} /> {(ev.confidence * 100).toFixed(0)}% Confidence
                    </span>
                  </div>

                  <h4 style={{ margin: '0 0 6px 0', fontSize: '0.95rem', fontWeight: 600, color: 'var(--color-text-bright)' }}>
                    {ev.claim}
                  </h4>

                  <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                    "{ev.supporting_text}"
                  </p>
                </div>

                <button
                  onClick={() => setExpandedId(isExpanded ? null : (ev.id || `ev-${idx}`))}
                  className="btn btn-icon btn-secondary"
                  style={{ padding: '6px', minWidth: '32px', height: '32px' }}
                  title="Toggle detail breakdown"
                >
                  {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
              </div>

              {isExpanded && (
                <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.06)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {coords?.chart_data && (
                    <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '12px', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                      <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#c084fc', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <BarChart3 size={14} /> Structured Chart Series Data
                      </div>
                      <pre style={{ margin: 0, fontSize: '0.75rem', color: '#e2e8f0', overflowX: 'auto', maxHeight: '180px' }}>
                        {JSON.stringify(coords.chart_data, null, 2)}
                      </pre>
                    </div>
                  )}

                  {ev.citations && ev.citations.length > 0 && (
                    <div>
                      <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '6px' }}>
                        Exact Anchored Quotes ({ev.citations.length}):
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {ev.citations.map((c, cIdx) => (
                          <div key={c.id || cIdx} style={{ fontSize: '0.8rem', padding: '8px 10px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '4px', borderLeft: '2px solid var(--color-primary)' }}>
                            <div style={{ fontStyle: 'italic', color: 'var(--color-text)' }}>"{c.quote || c.citation_text}"</div>
                            <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                              Claim: {c.claim}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {ev.verification_notes && (
                    <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
                      <strong>Verification Note:</strong> {ev.verification_notes}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
