import React, { useState, useEffect, useMemo } from 'react';
import {
  Award,
  BookOpen,
  CheckCircle2,
  AlertCircle,
  FileText,
  Send,
  Sparkles,
  RefreshCw,
  Plus,
  Copy,
  ChevronRight,
  ShieldCheck,
  Check,
} from 'lucide-react';

import {
  ManuscriptStatus,
  PeerReviewManuscript,
  PeerReviewReport,
  PeerReviewMetrics,
} from '../types/peerReview';

const SAMPLE_MANUSCRIPTS: PeerReviewManuscript[] = [
  {
    id: 'm-101',
    title: 'Self-Supervised Multimodal Representation Alignment across Heterogeneous Latent Spaces',
    abstract:
      'We present a theoretical and empirical formulation for cross-modal contrastive alignment that achieves zero-entropy information loss across dense tabular, textual, and visual representations.',
    field_of_study: 'computer_science',
    venue_format: 'nature',
    status: 'under_review',
    claimed_contributions: [
      'Asymmetric contrastive loss with provable gradient convergence bounds',
      'Evaluation across 14 multimodal benchmark distributions with 3.4% error reduction',
      'Zero-shot transfer generalization on unseen scientific datasets',
    ],
    keywords: ['Multimodal AI', 'Representation Learning', 'Contrastive Alignment', 'Meta-Science'],
    overall_score: 8.4,
    created_at: new Date().toISOString(),
    reports: [
      {
        id: 'rep-1',
        reviewer_persona: 'methodology_critic',
        reviewer_title: 'Senior Methodologist & Experimental Design Auditor',
        originality_score: 8.5,
        methodology_score: 8.8,
        empirical_soundness: 8.2,
        clarity_score: 8.0,
        composite_score: 8.48,
        recommendation: 'minor_revision',
        summary_verdict: 'Rigorous theoretical framework with robust experimental benchmarks across 14 distributions.',
        strengths: [
          'Solid theoretical proofs for loss convergence in Theorem 2',
          'Extensive ablations isolating cross-modal projections',
        ],
        weaknesses: [
          'Sensitivity analysis on sparse multimodal datasets requires minor clarification',
        ],
        detailed_critique:
          'The paper demonstrates exceptional methodological rigor. The contrastive formulation is well derived. Minor clarifications regarding hyperparameter sensitivity under sparse inputs should be addressed in the camera-ready version.',
        required_revisions: [
          'Add confidence interval bounds to Table 3 benchmark figures',
          'Clarify memory footprint scaling in Section 4.2',
        ],
        created_at: new Date().toISOString(),
      },
      {
        id: 'rep-2',
        reviewer_persona: 'statistical_auditor',
        reviewer_title: 'Quantitative & Statistical Significance Referee',
        originality_score: 8.0,
        methodology_score: 8.4,
        empirical_soundness: 8.9,
        clarity_score: 8.2,
        composite_score: 8.52,
        recommendation: 'accept',
        summary_verdict: 'Statistical significance is verified across all primary benchmarks (p < 0.001).',
        strengths: [
          'Well-designed paired t-tests and Wilcoxon signed-rank evaluations',
          'Confidence intervals reported across primary metric tables',
        ],
        weaknesses: [
          'Include exact random seed distributions in supplementary material',
        ],
        detailed_critique:
          'The quantitative rigor is exemplary. The statistical reporting satisfies all stringent guidelines for high-impact publication.',
        required_revisions: [
          'Disclose seed variance across all 5-fold cross-validation runs',
        ],
        created_at: new Date().toISOString(),
      },
      {
        id: 'rep-3',
        reviewer_persona: 'domain_specialist',
        reviewer_title: 'Principal Domain Specialist & Literature Authority',
        originality_score: 8.9,
        methodology_score: 8.0,
        empirical_soundness: 8.1,
        clarity_score: 8.4,
        composite_score: 8.49,
        recommendation: 'minor_revision',
        summary_verdict: 'High-novelty contribution to multimodal representation theory with wide applicability.',
        strengths: [
          'Novel bridge between heterogeneous latent space projections and optimal transport',
          'Comprehensive related work section situating the contribution within 2025/2026 literature',
        ],
        weaknesses: [
          'Discuss future implications for edge-computing inference',
        ],
        detailed_critique:
          'A landmark conceptual investigation that provides immediate practical utility to the multimodal scientific community.',
        required_revisions: [
          'Expand discussion on computational overhead in the conclusion',
        ],
        created_at: new Date().toISOString(),
      },
    ],
    revisions: [
      {
        id: 'rev-1',
        revision_round: 1,
        rebuttal_letter:
          'We sincerely thank the three referees for their constructive and encouraging reviews. In this revision, we have included exact 95% confidence intervals in Table 3, disclosed seed variances, and expanded the computational overhead analysis.',
        diff_summary: 'Augmented Table 3 confidence intervals and added Section 4.3 runtime telemetry.',
        point_by_point_responses: [
          {
            reviewer_id: 'Reviewer #1 (Methodology)',
            comment_summary: 'Add confidence interval bounds to Table 3',
            author_response: 'Completed in revised manuscript with 95% bootstrap intervals.',
            action_taken: 'Updated Table 3.',
          },
        ],
        status: 'submitted',
        created_at: new Date().toISOString(),
      },
    ],
  },
];

export const PeerReviewPage: React.FC = () => {
  const [manuscripts, setManuscripts] = useState<PeerReviewManuscript[]>(SAMPLE_MANUSCRIPTS);
  const [selectedManuscriptId, setSelectedManuscriptId] = useState<string>(SAMPLE_MANUSCRIPTS[0].id);
  const [activeTab, setActiveTab] = useState<'review_panel' | 'rebuttal' | 'camera_ready' | 'list'>('review_panel');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copiedBibtex, setCopiedBibtex] = useState<boolean>(false);
  const [copiedLatex, setCopiedLatex] = useState<boolean>(false);

  // New manuscript modal
  const [showNewModal, setShowNewModal] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newAbstract, setNewAbstract] = useState<string>('');
  const [newField, setNewField] = useState<string>('computer_science');
  const [newVenue, setNewVenue] = useState<string>('nature');
  const [newContributions, setNewContributions] = useState<string>('Novel algorithmic paradigm\nEmpirical benchmark validation');

  // Load from API
  const fetchManuscripts = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/publishing/manuscripts');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          // Fetch detail of first manuscript
          const detailRes = await fetch(`/api/v1/publishing/manuscripts/${data[0].id}`);
          if (detailRes.ok) {
            const detailData = await detailRes.json();
            setManuscripts([detailData, ...data.slice(1)]);
            setSelectedManuscriptId(detailData.id);
          } else {
            setManuscripts(data);
            setSelectedManuscriptId(data[0].id);
          }
        }
      }
    } catch {
      // fallback to mock
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchManuscripts();
  }, []);

  const selectedManuscript = useMemo(() => {
    return manuscripts.find((m) => m.id === selectedManuscriptId) || manuscripts[0];
  }, [manuscripts, selectedManuscriptId]);

  const metrics: PeerReviewMetrics = useMemo(() => {
    const total = manuscripts.length;
    const reportsCount = manuscripts.reduce((acc, m) => acc + (m.reports?.length || 0), 0);
    const avgScore = total > 0 ? manuscripts.reduce((acc, m) => acc + (m.overall_score || 0), 0) / total : 0;
    const dist: Record<string, number> = {};
    manuscripts.forEach((m) => {
      dist[m.status] = (dist[m.status] || 0) + 1;
    });
    return {
      total_manuscripts: total,
      total_referee_reports: reportsCount,
      average_manuscript_score: Number(avgScore.toFixed(2)),
      status_distribution: dist,
      acceptance_rate: total > 0 ? Number(((dist['accepted'] || 0) + (dist['published'] || 0)) / total) : 0,
    };
  }, [manuscripts]);

  // Trigger Review
  const handleTriggerReview = async () => {
    if (!selectedManuscript) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/publishing/manuscripts/${selectedManuscript.id}/review`, {
        method: 'POST',
      });
      if (res.ok) {
        const detailRes = await fetch(`/api/v1/publishing/manuscripts/${selectedManuscript.id}`);
        if (detailRes.ok) {
          const updated = await detailRes.json();
          setManuscripts((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
        }
      }
    } catch {
      // Local fallback simulation
      const mockReports: PeerReviewReport[] = [
        {
          id: 'mock-1',
          reviewer_persona: 'methodology_critic',
          reviewer_title: 'Senior Methodologist & Experimental Design Auditor',
          originality_score: 8.6,
          methodology_score: 8.9,
          empirical_soundness: 8.5,
          clarity_score: 8.2,
          composite_score: 8.65,
          recommendation: 'accept',
          summary_verdict: 'Rigorous methodology with comprehensive empirical benchmarks.',
          strengths: ['Clear mathematical formulation', 'Valid ablation studies'],
          weaknesses: ['Minor notation formatting in Appendix A'],
          detailed_critique: 'The submission demonstrates sound experimental rigor.',
          required_revisions: ['Clarify notation in Section 2'],
          created_at: new Date().toISOString(),
        },
      ];
      setManuscripts((prev) =>
        prev.map((m) =>
          m.id === selectedManuscript.id
            ? { ...m, status: 'accepted' as ManuscriptStatus, overall_score: 8.65, reports: mockReports }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Publish Manuscript
  const handlePublish = async () => {
    if (!selectedManuscript) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/publishing/manuscripts/${selectedManuscript.id}/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          authors: ['Om Talaviya', 'Agentic Multimodal Research Systems'],
          publication_year: 2026,
        }),
      });
      if (res.ok) {
        const pubData = await res.json();
        setManuscripts((prev) =>
          prev.map((m) =>
            m.id === selectedManuscript.id
              ? {
                  ...m,
                  status: 'published' as ManuscriptStatus,
                  camera_ready_doi: pubData.camera_ready_doi,
                  bibtex_citation: pubData.bibtex_citation,
                  published_latex: pubData.published_latex_preview,
                }
              : m
          )
        );
      }
    } catch {
      const doi = `10.1038/s41586-026.${selectedManuscript.id.slice(0, 8)}`;
      setManuscripts((prev) =>
        prev.map((m) =>
          m.id === selectedManuscript.id
            ? {
                ...m,
                status: 'published' as ManuscriptStatus,
                camera_ready_doi: doi,
                bibtex_citation: `@article{talaviya2026,\n  title={${m.title}},\n  doi={${doi}}\n}`,
              }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Submit new manuscript
  const handleCreateManuscript = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newAbstract.trim()) return;

    const payload = {
      title: newTitle,
      abstract: newAbstract,
      field_of_study: newField,
      venue_format: newVenue,
      claimed_contributions: newContributions.split('\n').filter((c) => c.trim().length > 0),
      keywords: [newField, newVenue, 'Peer Review'],
    };

    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/publishing/manuscripts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const created = await res.json();
        setManuscripts([created, ...manuscripts]);
        setSelectedManuscriptId(created.id);
        setShowNewModal(false);
      }
    } catch {
      const localNew: PeerReviewManuscript = {
        id: `m-${Date.now()}`,
        title: newTitle,
        abstract: newAbstract,
        field_of_study: newField,
        venue_format: newVenue,
        status: 'submitted',
        claimed_contributions: payload.claimed_contributions,
        keywords: payload.keywords,
        overall_score: 0.0,
        created_at: new Date().toISOString(),
      };
      setManuscripts([localNew, ...manuscripts]);
      setSelectedManuscriptId(localNew.id);
      setShowNewModal(false);
    } finally {
      setIsLoading(false);
      setNewTitle('');
      setNewAbstract('');
    }
  };

  const getStatusBadge = (status: ManuscriptStatus) => {
    switch (status) {
      case 'accepted':
      case 'published':
        return <span className="badge badge-success">{status.toUpperCase()}</span>;
      case 'revisions_requested':
        return <span className="badge badge-warning">REVISIONS REQUESTED</span>;
      case 'under_review':
        return <span className="badge badge-info">UNDER REVIEW</span>;
      case 'rejected':
        return <span className="badge badge-danger">REJECTED</span>;
      default:
        return <span className="badge badge-neutral">SUBMITTED</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-primary/10 border border-primary/20 text-primary">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Autonomous Peer Review & Publishing Studio</h1>
              <p className="text-sm text-text-secondary">
                Double-blind multi-agent referee evaluation, author rebuttals, and camera-ready preprint generator
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={fetchManuscripts} disabled={isLoading} className="btn btn-secondary text-sm">
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button onClick={() => setShowNewModal(true)} className="btn btn-primary text-sm">
            <Plus className="w-4 h-4 mr-2" />
            Submit Manuscript
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-text-secondary uppercase tracking-wider">Total Manuscripts</div>
            <div className="text-2xl font-bold mt-1">{metrics.total_manuscripts}</div>
          </div>
          <BookOpen className="w-8 h-8 text-primary/40" />
        </div>
        <div className="card p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-text-secondary uppercase tracking-wider">Referee Reports</div>
            <div className="text-2xl font-bold mt-1 text-info">{metrics.total_referee_reports}</div>
          </div>
          <ShieldCheck className="w-8 h-8 text-info/40" />
        </div>
        <div className="card p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-text-secondary uppercase tracking-wider">Avg Quality Score</div>
            <div className="text-2xl font-bold mt-1 text-success">{metrics.average_manuscript_score} / 10</div>
          </div>
          <CheckCircle2 className="w-8 h-8 text-success/40" />
        </div>
        <div className="card p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-text-secondary uppercase tracking-wider">Acceptance Rate</div>
            <div className="text-2xl font-bold mt-1 text-warning">{(metrics.acceptance_rate * 100).toFixed(1)}%</div>
          </div>
          <Award className="w-8 h-8 text-warning/40" />
        </div>
      </div>

      {/* Main Studio Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Manuscript Selector */}
        <div className="lg:col-span-4 space-y-4">
          <div className="card p-4 space-y-3">
            <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">Manuscript Archive</h2>
            <div className="space-y-2 max-h-[580px] overflow-y-auto pr-1">
              {manuscripts.map((m) => {
                const isSelected = m.id === selectedManuscript?.id;
                return (
                  <div
                    key={m.id}
                    onClick={() => setSelectedManuscriptId(m.id)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-primary/5 border-primary/40 shadow-sm'
                        : 'bg-surface border-border hover:border-border-hover'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="font-medium text-sm line-clamp-2">{m.title}</div>
                      <ChevronRight className={`w-4 h-4 shrink-0 transition-transform ${isSelected ? 'text-primary rotate-90' : 'text-text-secondary'}`} />
                    </div>
                    <div className="flex items-center gap-2 mt-2 text-xs text-text-secondary">
                      {getStatusBadge(m.status)}
                      <span className="capitalize">{m.venue_format}</span>
                      <span>•</span>
                      <span className="font-semibold text-primary">{m.overall_score > 0 ? `${m.overall_score}/10` : 'Pending'}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Manuscript Review & Publishing Studio */}
        <div className="lg:col-span-8 space-y-4">
          {selectedManuscript && (
            <div className="card p-6 space-y-6">
              {/* Header Details */}
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b border-border pb-4">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2">
                    {getStatusBadge(selectedManuscript.status)}
                    <span className="text-xs uppercase px-2 py-0.5 rounded bg-surface-alt border border-border text-text-secondary font-mono">
                      {selectedManuscript.venue_format.toUpperCase()}
                    </span>
                    {selectedManuscript.camera_ready_doi && (
                      <span className="text-xs text-primary font-mono bg-primary/10 px-2 py-0.5 rounded border border-primary/20">
                        DOI: {selectedManuscript.camera_ready_doi}
                      </span>
                    )}
                  </div>
                  <h2 className="text-lg font-bold">{selectedManuscript.title}</h2>
                  <p className="text-xs text-text-secondary line-clamp-2">{selectedManuscript.abstract}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {selectedManuscript.status !== 'published' && selectedManuscript.status !== 'accepted' && (
                    <button
                      onClick={handleTriggerReview}
                      disabled={isLoading}
                      className="btn btn-primary text-xs"
                    >
                      <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                      Run Blind Review
                    </button>
                  )}
                  {selectedManuscript.status === 'accepted' && (
                    <button
                      onClick={handlePublish}
                      disabled={isLoading}
                      className="btn btn-success text-xs"
                    >
                      <Award className="w-3.5 h-3.5 mr-1.5" />
                      Publish Camera-Ready
                    </button>
                  )}
                </div>
              </div>

              {/* Tabs Navigation */}
              <div className="flex border-b border-border gap-6">
                <button
                  onClick={() => setActiveTab('review_panel')}
                  className={`pb-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                    activeTab === 'review_panel'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-text-secondary hover:text-text'
                  }`}
                >
                  <ShieldCheck className="w-4 h-4" />
                  Blind Referee Panel ({selectedManuscript.reports?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('rebuttal')}
                  className={`pb-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                    activeTab === 'rebuttal'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-text-secondary hover:text-text'
                  }`}
                >
                  <Send className="w-4 h-4" />
                  Author Rebuttal & Revisions ({selectedManuscript.revisions?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('camera_ready')}
                  className={`pb-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                    activeTab === 'camera_ready'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-text-secondary hover:text-text'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  Camera-Ready Preprint
                </button>
              </div>

              {/* Tab 1: Referee Panel */}
              {activeTab === 'review_panel' && (
                <div className="space-y-4">
                  {(!selectedManuscript.reports || selectedManuscript.reports.length === 0) ? (
                    <div className="p-8 text-center border border-dashed border-border rounded-xl space-y-3">
                      <AlertCircle className="w-8 h-8 text-text-secondary mx-auto" />
                      <div className="text-sm font-medium">No referee evaluations yet</div>
                      <p className="text-xs text-text-secondary">
                        Click 'Run Blind Review' to simulate independent reviews from the Methodology Critic, Statistical Auditor, and Domain Specialist.
                      </p>
                      <button onClick={handleTriggerReview} className="btn btn-primary text-xs">
                        <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                        Start Double-Blind Review
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {selectedManuscript.reports.map((rep, idx) => (
                        <div key={rep.id || idx} className="p-4 rounded-xl border border-border bg-surface-alt space-y-3">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/60 pb-3">
                            <div>
                              <div className="text-xs font-semibold text-primary uppercase tracking-wider">Reviewer #{idx + 1}</div>
                              <div className="font-semibold text-sm">{rep.reviewer_title}</div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-mono font-bold bg-primary/10 px-2 py-0.5 rounded text-primary border border-primary/20">
                                Score: {rep.composite_score}/10
                              </span>
                              <span className={`text-xs px-2 py-0.5 rounded font-semibold uppercase ${
                                rep.recommendation === 'accept'
                                  ? 'bg-success/15 text-success'
                                  : rep.recommendation === 'reject'
                                  ? 'bg-danger/15 text-danger'
                                  : 'bg-warning/15 text-warning'
                              }`}>
                                {rep.recommendation.replace('_', ' ')}
                              </span>
                            </div>
                          </div>

                          {/* Score Breakdowns */}
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                            <div className="p-2 rounded bg-surface border border-border">
                              <div className="text-text-secondary">Originality</div>
                              <div className="font-bold text-sm mt-0.5">{rep.originality_score}/10</div>
                            </div>
                            <div className="p-2 rounded bg-surface border border-border">
                              <div className="text-text-secondary">Methodology</div>
                              <div className="font-bold text-sm mt-0.5">{rep.methodology_score}/10</div>
                            </div>
                            <div className="p-2 rounded bg-surface border border-border">
                              <div className="text-text-secondary">Empirical</div>
                              <div className="font-bold text-sm mt-0.5">{rep.empirical_soundness}/10</div>
                            </div>
                            <div className="p-2 rounded bg-surface border border-border">
                              <div className="text-text-secondary">Clarity</div>
                              <div className="font-bold text-sm mt-0.5">{rep.clarity_score}/10</div>
                            </div>
                          </div>

                          {/* Verdict & Critique */}
                          <div className="space-y-1">
                            <div className="text-xs font-semibold text-text-secondary">Summary Verdict:</div>
                            <p className="text-xs leading-relaxed italic text-text">{rep.summary_verdict}</p>
                          </div>

                          <div className="space-y-1">
                            <div className="text-xs font-semibold text-text-secondary">Required Revisions:</div>
                            <ul className="text-xs list-disc list-inside space-y-1 text-text-secondary">
                              {rep.required_revisions.map((rev, rIdx) => (
                                <li key={rIdx}>{rev}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Tab 2: Rebuttals & Revisions */}
              {activeTab === 'rebuttal' && (
                <div className="space-y-4">
                  {(!selectedManuscript.revisions || selectedManuscript.revisions.length === 0) ? (
                    <div className="p-6 text-center border border-dashed border-border rounded-xl space-y-2">
                      <div className="text-sm font-medium">No revision rounds recorded yet</div>
                      <p className="text-xs text-text-secondary">
                        Author rebuttals address referee points with point-by-point evidence mappings.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {selectedManuscript.revisions.map((rev, idx) => (
                        <div key={rev.id || idx} className="p-4 rounded-xl border border-border bg-surface-alt space-y-3">
                          <div className="flex items-center justify-between border-b border-border/60 pb-2">
                            <div className="font-semibold text-sm">Revision Round #{rev.revision_round}</div>
                            <span className="badge badge-neutral text-xs">{rev.status}</span>
                          </div>
                          <div className="space-y-1">
                            <div className="text-xs font-semibold text-text-secondary">Rebuttal Letter:</div>
                            <p className="text-xs leading-relaxed whitespace-pre-line text-text bg-surface p-3 rounded-lg border border-border font-sans">
                              {rev.rebuttal_letter}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Tab 3: Camera-Ready Preprint */}
              {activeTab === 'camera_ready' && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl border border-border bg-surface-alt space-y-3">
                    <div className="flex items-center justify-between border-b border-border/60 pb-2">
                      <div className="font-semibold text-sm">BibTeX Citation Block</div>
                      <button
                        onClick={() => {
                          const bib = selectedManuscript.bibtex_citation || `@article{talaviya2026,\n  title={${selectedManuscript.title}}\n}`;
                          navigator.clipboard.writeText(bib);
                          setCopiedBibtex(true);
                          setTimeout(() => setCopiedBibtex(false), 2000);
                        }}
                        className="btn btn-secondary text-xs"
                      >
                        {copiedBibtex ? <Check className="w-3.5 h-3.5 text-success mr-1" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
                        {copiedBibtex ? 'Copied' : 'Copy BibTeX'}
                      </button>
                    </div>
                    <pre className="text-xs font-mono p-3 rounded-lg bg-surface border border-border overflow-x-auto text-text-secondary">
                      {selectedManuscript.bibtex_citation ||
                        `@article{research2026,\n  title = {{${selectedManuscript.title}}},\n  journal = {Nature Scientific Intelligence},\n  year = {2026},\n  doi = {${selectedManuscript.camera_ready_doi || '10.1038/s41586-026.preprint'}}\n}`}
                    </pre>
                  </div>

                  <div className="p-4 rounded-xl border border-border bg-surface-alt space-y-3">
                    <div className="flex items-center justify-between border-b border-border/60 pb-2">
                      <div className="font-semibold text-sm">LaTeX Preprint Template</div>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(selectedManuscript.published_latex || '\\documentclass{article}');
                          setCopiedLatex(true);
                          setTimeout(() => setCopiedLatex(false), 2000);
                        }}
                        className="btn btn-secondary text-xs"
                      >
                        {copiedLatex ? <Check className="w-3.5 h-3.5 text-success mr-1" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
                        {copiedLatex ? 'Copied' : 'Copy LaTeX'}
                      </button>
                    </div>
                    <pre className="text-xs font-mono p-3 rounded-lg bg-surface border border-border overflow-x-auto text-text-secondary max-h-56">
                      {selectedManuscript.published_latex ||
                        `\\documentclass[11pt,twocolumn]{article}\n\\title{${selectedManuscript.title}}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\n${selectedManuscript.abstract}\n\\end{abstract}\n\\end{document}`}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* New Manuscript Modal */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="card max-w-lg w-full p-6 space-y-4 shadow-2xl border border-border animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="font-bold text-base">Submit Research Manuscript</h3>
              <button onClick={() => setShowNewModal(false)} className="text-text-secondary hover:text-text">
                ✕
              </button>
            </div>
            <form onSubmit={handleCreateManuscript} className="space-y-3 text-sm">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Paper Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Asymmetric Representation Learning under Sparse Modalities"
                  className="input w-full text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Abstract</label>
                <textarea
                  required
                  rows={4}
                  value={newAbstract}
                  onChange={(e) => setNewAbstract(e.target.value)}
                  placeholder="Comprehensive scientific abstract outlining theoretical formulation, empirical setup, and key results..."
                  className="input w-full text-xs"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1">Field of Study</label>
                  <select
                    value={newField}
                    onChange={(e) => setNewField(e.target.value)}
                    className="input w-full text-xs"
                  >
                    <option value="computer_science">Computer Science</option>
                    <option value="artificial_intelligence">Artificial Intelligence</option>
                    <option value="quantum_computing">Quantum Computing</option>
                    <option value="computational_biology">Computational Biology</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1">Target Venue Format</label>
                  <select
                    value={newVenue}
                    onChange={(e) => setNewVenue(e.target.value)}
                    className="input w-full text-xs"
                  >
                    <option value="nature">Nature / Springer</option>
                    <option value="ieee">IEEE Transactions</option>
                    <option value="acm">ACM Computing</option>
                    <option value="arxiv">arXiv Preprint</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Claimed Contributions (one per line)</label>
                <textarea
                  rows={2}
                  value={newContributions}
                  onChange={(e) => setNewContributions(e.target.value)}
                  className="input w-full text-xs font-mono"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-border">
                <button type="button" onClick={() => setShowNewModal(false)} className="btn btn-secondary text-xs">
                  Cancel
                </button>
                <button type="submit" disabled={isLoading} className="btn btn-primary text-xs">
                  Submit for Peer Review
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
