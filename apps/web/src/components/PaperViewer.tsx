import React, { useState } from 'react'
import { PaperStructure, PaperSection, BibEntry } from '../types/research'
import { BookOpen, FileText, ChevronRight, AlertTriangle, ExternalLink, Bookmark, Hash, Layers } from 'lucide-react'

interface PaperViewerProps {
  paper: PaperStructure
  onCitationClick?: (citationKey: string) => void
}

export const PaperViewer: React.FC<PaperViewerProps> = ({ paper, onCitationClick }) => {
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(
    paper.sections.length > 0 ? paper.sections[0].section_id : null
  )
  const [selectedBibEntry, setSelectedBibEntry] = useState<BibEntry | null>(null)
  const [activeTab, setActiveTab] = useState<'paper' | 'references' | 'benchmarks'>('paper')

  const selectedSection = paper.sections.find((s) => s.section_id === selectedSectionId)

  const handleCitationAnchor = (key: string) => {
    const bib = paper.bibliography.find((b) => b.citation_key === key || b.citation_key.includes(key))
    if (bib) {
      setSelectedBibEntry(bib)
    }
    if (onCitationClick) {
      onCitationClick(key)
    }
  }

  const getSectionIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'abstract':
        return <Bookmark size={14} className="text-cyan-400" />
      case 'methodology':
      case 'model':
        return <Layers size={14} className="text-indigo-400" />
      case 'limitations':
        return <AlertTriangle size={14} className="text-amber-400" />
      case 'references':
        return <ExternalLink size={14} className="text-emerald-400" />
      default:
        return <FileText size={14} className="text-slate-400" />
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        backgroundColor: 'var(--bg-card)',
        borderRadius: '12px',
        border: '1px solid var(--border-subtle)',
        padding: '20px',
      }}
    >
      {/* Header Card */}
      <div style={{ borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <BookOpen size={20} style={{ color: 'var(--accent-blue)' }} />
          <span
            style={{
              fontSize: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'var(--accent-blue)',
              fontWeight: 600,
            }}
          >
            Academic Paper Intelligence
          </span>
        </div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 8px 0', color: '#f8fafc' }}>
          {paper.title}
        </h2>
        <div style={{ fontSize: '0.85rem', color: '#94a3b8', display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
          {paper.authors && paper.authors.length > 0 && (
            <span>
              <strong>Authors:</strong> {paper.authors.join(', ')}
            </span>
          )}
          {paper.affiliations && paper.affiliations.length > 0 && (
            <span>
              <strong>Affiliations:</strong> {paper.affiliations.join('; ')}
            </span>
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
        <button
          onClick={() => setActiveTab('paper')}
          style={{
            padding: '6px 14px',
            borderRadius: '6px',
            fontSize: '0.85rem',
            fontWeight: 500,
            border: 'none',
            cursor: 'pointer',
            backgroundColor: activeTab === 'paper' ? 'var(--accent-blue)' : 'transparent',
            color: activeTab === 'paper' ? '#0f172a' : '#94a3b8',
          }}
        >
          Section Tree & Content
        </button>
        <button
          onClick={() => setActiveTab('references')}
          style={{
            padding: '6px 14px',
            borderRadius: '6px',
            fontSize: '0.85rem',
            fontWeight: 500,
            border: 'none',
            cursor: 'pointer',
            backgroundColor: activeTab === 'references' ? 'var(--accent-blue)' : 'transparent',
            color: activeTab === 'references' ? '#0f172a' : '#94a3b8',
          }}
        >
          Bibliography ({paper.bibliography?.length || 0})
        </button>
        {paper.benchmarks && paper.benchmarks.length > 0 && (
          <button
            onClick={() => setActiveTab('benchmarks')}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontWeight: 500,
              border: 'none',
              cursor: 'pointer',
              backgroundColor: activeTab === 'benchmarks' ? 'var(--accent-blue)' : 'transparent',
              color: activeTab === 'benchmarks' ? '#0f172a' : '#94a3b8',
            }}
          >
            Benchmark Evaluations ({paper.benchmarks.length})
          </button>
        )}
      </div>

      {activeTab === 'paper' && (
        <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '20px' }}>
          {/* Section Tree Sidebar */}
          <div
            style={{
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle)',
              padding: '12px',
              maxHeight: '600px',
              overflowY: 'auto',
            }}
          >
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', marginBottom: '8px' }}>
              Structure Outline
            </div>
            {paper.abstract && (
              <div
                onClick={() => setSelectedSectionId('abstract')}
                style={{
                  padding: '6px 10px',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  backgroundColor: selectedSectionId === 'abstract' ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                  color: selectedSectionId === 'abstract' ? 'var(--accent-blue)' : '#cbd5e1',
                  marginBottom: '4px',
                }}
              >
                <Bookmark size={14} />
                <span>Abstract</span>
              </div>
            )}
            {paper.sections.map((sec) => (
              <div
                key={sec.section_id}
                onClick={() => setSelectedSectionId(sec.section_id)}
                style={{
                  padding: '6px 10px',
                  paddingLeft: `${Math.max(10, sec.level * 12)}px`,
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  backgroundColor: selectedSectionId === sec.section_id ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                  color: selectedSectionId === sec.section_id ? 'var(--accent-blue)' : '#cbd5e1',
                  marginBottom: '2px',
                }}
              >
                {getSectionIcon(sec.section_type)}
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {sec.title}
                </span>
              </div>
            ))}
          </div>

          {/* Section Content Pane */}
          <div
            style={{
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle)',
              padding: '20px',
              maxHeight: '600px',
              overflowY: 'auto',
            }}
          >
            {selectedSectionId === 'abstract' ? (
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--accent-blue)', marginTop: 0 }}>
                  Abstract
                </h3>
                <p style={{ lineHeight: '1.6', color: '#e2e8f0', fontSize: '0.95rem' }}>{paper.abstract}</p>
              </div>
            ) : selectedSection ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      backgroundColor: 'rgba(56, 189, 248, 0.15)',
                      color: 'var(--accent-blue)',
                      textTransform: 'uppercase',
                    }}
                  >
                    {selectedSection.section_type}
                  </span>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
                    {selectedSection.title}
                  </h3>
                </div>

                {/* Section Content */}
                <div
                  style={{
                    lineHeight: '1.7',
                    color: '#cbd5e1',
                    fontSize: '0.9rem',
                    whiteSpace: 'pre-line',
                  }}
                >
                  {selectedSection.content}
                </div>

                {/* Inline Citations Referenced */}
                {selectedSection.citations_referenced && selectedSection.citations_referenced.length > 0 && (
                  <div
                    style={{
                      marginTop: '20px',
                      paddingTop: '12px',
                      borderTop: '1px solid var(--border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      flexWrap: 'wrap',
                    }}
                  >
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Referenced Citations:</span>
                    {selectedSection.citations_referenced.map((cite, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleCitationAnchor(cite)}
                        style={{
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          backgroundColor: 'rgba(99, 102, 241, 0.2)',
                          color: '#a5b4fc',
                          border: '1px solid rgba(99, 102, 241, 0.3)',
                          cursor: 'pointer',
                        }}
                      >
                        {cite}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: '#64748b', textAlign: 'center', padding: '40px' }}>
                Select a section from the structure outline.
              </div>
            )}

            {/* Selected Citation Preview Popover */}
            {selectedBibEntry && (
              <div
                style={{
                  marginTop: '20px',
                  backgroundColor: 'rgba(30, 41, 59, 0.9)',
                  border: '1px solid #3b82f6',
                  borderRadius: '8px',
                  padding: '12px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--accent-blue)', fontSize: '0.85rem' }}>
                    Citation {selectedBibEntry.citation_key}
                  </span>
                  <button
                    onClick={() => setSelectedBibEntry(null)}
                    style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                  >
                    ✕
                  </button>
                </div>
                <p style={{ margin: 0, fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.4' }}>
                  {selectedBibEntry.raw_text}
                </p>
                {selectedBibEntry.doi && (
                  <div style={{ marginTop: '6px', fontSize: '0.75rem', color: '#38bdf8' }}>
                    DOI: {selectedBibEntry.doi}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Bibliography Tab */}
      {activeTab === 'references' && (
        <div
          style={{
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
            borderRadius: '8px',
            border: '1px solid var(--border-subtle)',
            padding: '16px',
            maxHeight: '600px',
            overflowY: 'auto',
          }}
        >
          {paper.bibliography && paper.bibliography.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {paper.bibliography.map((bib) => (
                <div
                  key={bib.id}
                  style={{
                    padding: '10px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'rgba(30, 41, 59, 0.4)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '0.85rem',
                    lineHeight: '1.4',
                  }}
                >
                  <span style={{ fontWeight: 600, color: 'var(--accent-blue)', marginRight: '8px' }}>
                    {bib.citation_key}
                  </span>
                  <span style={{ color: '#cbd5e1' }}>{bib.raw_text}</span>
                  {(bib.doi || bib.arxiv_id) && (
                    <div style={{ marginTop: '4px', fontSize: '0.75rem', color: '#94a3b8' }}>
                      {bib.doi && <span style={{ marginRight: '12px' }}>DOI: {bib.doi}</span>}
                      {bib.arxiv_id && <span>arXiv: {bib.arxiv_id}</span>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#64748b', padding: '30px' }}>
              No bibliographic references extracted.
            </div>
          )}
        </div>
      )}

      {/* Stated Limitations Card */}
      {paper.limitations_summary && (
        <div
          style={{
            backgroundColor: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            borderRadius: '8px',
            padding: '14px',
            display: 'flex',
            gap: '12px',
          }}
        >
          <AlertTriangle size={18} style={{ color: 'var(--accent-amber)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-amber)', marginBottom: '4px' }}>
              Stated Limitations & Methodology Assumptions
            </div>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.5' }}>
              {paper.limitations_summary}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
export default PaperViewer
