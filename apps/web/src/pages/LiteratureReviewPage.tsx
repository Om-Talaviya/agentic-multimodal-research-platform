import React, { useState, useEffect } from 'react';
import {
  BookOpenCheck,
  Filter,
  BarChart3,
  ShieldCheck,
  Plus,
  Play,
  CheckCircle2,
  XCircle,
  Layers,
  TrendingUp,
  FileText,
} from 'lucide-react';
import {
  LiteratureReview,
  MetaAnalysisReport,
  PRISMAFlowSummary,
  SLRMetrics,
  CreateReviewPayload,
} from '../types/literature';
import { useWorkspace } from '../context/WorkspaceContext';

export const LiteratureReviewPage: React.FC = () => {
  const { currentWorkspace } = useWorkspace();
  const [activeTab, setActiveTab] = useState<'reviews' | 'screening' | 'meta_analysis' | 'risk_of_bias'>('reviews');
  const [reviews, setReviews] = useState<LiteratureReview[]>([]);
  const [selectedReview, setSelectedReview] = useState<LiteratureReview | null>(null);
  const [prismaFlow, setPrismaFlow] = useState<PRISMAFlowSummary | null>(null);
  const [metrics, setMetrics] = useState<SLRMetrics>({
    total_reviews: 0,
    total_candidates: 0,
    total_included_studies: 0,
    total_meta_analyses: 0,
    average_inclusion_rate: 0,
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showMetaModal, setShowMetaModal] = useState<boolean>(false);

  const [formData, setFormData] = useState<CreateReviewPayload>({
    title: '',
    research_question: '',
    protocol_type: 'PRISMA-2020',
    population: '',
    intervention: '',
    comparator: '',
    outcome: '',
  });

  const [metaForm, setMetaForm] = useState({
    synthesis_name: 'Primary Efficacy Meta-Analysis',
    effect_metric: 'hedges_g',
    model_type: 'random_effects' as 'fixed_effect' | 'random_effects',
  });

  const fetchReviews = async () => {
    setLoading(true);
    try {
      const queryParams = currentWorkspace?.id ? `?workspace_id=${currentWorkspace.id}` : '';
      const [reviewsRes, metricsRes] = await Promise.all([
        fetch(`/api/v1/literature/reviews${queryParams}`),
        fetch(`/api/v1/literature/metrics`),
      ]);

      if (reviewsRes.ok) {
        const data = await reviewsRes.json();
        setReviews(data);
        if (data.length > 0 && !selectedReview) {
          fetchReviewDetails(data[0].id);
        }
      }
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }
    } catch (err) {
      console.error('Failed to load literature reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchReviewDetails = async (id: string) => {
    try {
      const [reviewRes, flowRes] = await Promise.all([
        fetch(`/api/v1/literature/reviews/${id}`),
        fetch(`/api/v1/literature/reviews/${id}/prisma-flow`),
      ]);
      if (reviewRes.ok) {
        const data = await reviewRes.json();
        setSelectedReview(data);
      }
      if (flowRes.ok) {
        const flowData = await flowRes.json();
        setPrismaFlow(flowData);
      }
    } catch (err) {
      console.error('Failed to load review details:', err);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, [currentWorkspace]);

  const handleCreateReview = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        title: formData.title,
        research_question: formData.research_question,
        protocol_type: formData.protocol_type,
        pico_framework: {
          population: formData.population,
          intervention: formData.intervention,
          comparator: formData.comparator,
          outcome: formData.outcome,
        },
        workspace_id: currentWorkspace?.id,
      };

      const res = await fetch('/api/v1/literature/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setShowCreateModal(false);
        setFormData({
          title: '',
          research_question: '',
          protocol_type: 'PRISMA-2020',
          population: '',
          intervention: '',
          comparator: '',
          outcome: '',
        });
        await fetchReviews();
      }
    } catch (err) {
      console.error('Failed to create literature review:', err);
    }
  };

  const handleScreenStudy = async (
    candidateId: string,
    status: 'included' | 'excluded',
    reason?: string,
  ) => {
    if (!selectedReview) return;
    try {
      const res = await fetch(`/api/v1/literature/reviews/${selectedReview.id}/candidates/${candidateId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          screening_status: status,
          exclusion_reason: reason || (status === 'excluded' ? 'Eligibility criteria not met' : undefined),
        }),
      });
      if (res.ok) {
        await fetchReviewDetails(selectedReview.id);
      }
    } catch (err) {
      console.error('Failed to update screening status:', err);
    }
  };

  const handleRunMetaAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReview) return;
    try {
      const res = await fetch(`/api/v1/literature/reviews/${selectedReview.id}/meta-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metaForm),
      });
      if (res.ok) {
        setShowMetaModal(false);
        await fetchReviewDetails(selectedReview.id);
        setActiveTab('meta_analysis');
      }
    } catch (err) {
      console.error('Failed to execute meta-analysis:', err);
    }
  };

  const latestMetaAnalysis: MetaAnalysisReport | undefined =
    selectedReview?.meta_analyses && selectedReview.meta_analyses.length > 0
      ? selectedReview.meta_analyses[0]
      : undefined;

  return (
    <div className="space-y-6">
      {/* Top Banner & Metric Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <BookOpenCheck className="w-8 h-8 text-primary" />
              Systematic Literature Review & Meta-Analysis
            </h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20">
              PRISMA 2020 Compliant
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Automated systematic screening protocols, risk of bias matrix, and random-effects quantitative meta-analyses.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          New Systematic Review
        </button>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Total Reviews</span>
            <Layers className="w-4 h-4 text-primary" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_reviews}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Identified Studies</span>
            <FileText className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_candidates}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Included Studies</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_included_studies}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Meta-Analyses</span>
            <BarChart3 className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_meta_analyses}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Inclusion Rate</span>
            <TrendingUp className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.average_inclusion_rate}%</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border flex items-center gap-6">
        <button
          onClick={() => setActiveTab('reviews')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'reviews'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Layers className="w-4 h-4" />
          PRISMA Flow & Overview
        </button>

        <button
          onClick={() => setActiveTab('screening')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'screening'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Filter className="w-4 h-4" />
          Screening Queue & Triage
          {selectedReview?.candidates && (
            <span className="ml-1.5 px-2 py-0.5 rounded-full text-xs bg-muted text-muted-foreground">
              {selectedReview.candidates.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('meta_analysis')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'meta_analysis'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          Quantitative Meta-Analysis & Forest Plot
        </button>

        <button
          onClick={() => setActiveTab('risk_of_bias')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'risk_of_bias'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Risk of Bias Matrix (RoB 2)
        </button>
      </div>

      {/* Tab 1: PRISMA Flow & Reviews */}
      {activeTab === 'reviews' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Review Selector Sidebar */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
              Active Systematic Reviews
            </h3>
            <div className="space-y-2">
              {reviews.map((r) => (
                <div
                  key={r.id}
                  onClick={() => fetchReviewDetails(r.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition ${
                    selectedReview?.id === r.id
                      ? 'border-primary bg-primary/5 shadow-sm'
                      : 'border-border bg-card hover:border-primary/50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-primary">{r.protocol_type}</span>
                    <span className="text-xs text-muted-foreground uppercase">{r.current_phase}</span>
                  </div>
                  <h4 className="font-medium text-foreground text-sm line-clamp-2">{r.title}</h4>
                  <div className="flex items-center gap-3 mt-3 text-xs text-muted-foreground">
                    <span>{r.total_identified} identified</span>
                    <span>•</span>
                    <span className="text-emerald-500 font-medium">{r.total_included} included</span>
                  </div>
                </div>
              ))}
              {reviews.length === 0 && !loading && (
                <div className="text-center py-8 border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                  No systematic reviews created yet.
                </div>
              )}
            </div>
          </div>

          {/* PRISMA 2020 Flow Diagram Canvas */}
          <div className="lg:col-span-2 space-y-6">
            {selectedReview ? (
              <div className="space-y-6">
                <div className="p-5 rounded-xl border border-border bg-card shadow-sm">
                  <h2 className="text-lg font-bold text-foreground">{selectedReview.title}</h2>
                  <p className="text-sm text-muted-foreground mt-1">{selectedReview.research_question}</p>

                  {selectedReview.pico_framework && (
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-4 pt-4 border-t border-border">
                      <div className="text-xs">
                        <span className="font-semibold text-muted-foreground block">Population (P)</span>
                        <span className="text-foreground">{selectedReview.pico_framework.population || 'All'}</span>
                      </div>
                      <div className="text-xs">
                        <span className="font-semibold text-muted-foreground block">Intervention (I)</span>
                        <span className="text-foreground">{selectedReview.pico_framework.intervention || 'Specified'}</span>
                      </div>
                      <div className="text-xs">
                        <span className="font-semibold text-muted-foreground block">Comparator (C)</span>
                        <span className="text-foreground">{selectedReview.pico_framework.comparator || 'Control'}</span>
                      </div>
                      <div className="text-xs">
                        <span className="font-semibold text-muted-foreground block">Outcome (O)</span>
                        <span className="text-foreground">{selectedReview.pico_framework.outcome || 'Target metric'}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* PRISMA 2020 Interactive Diagram */}
                <div className="p-6 rounded-xl border border-border bg-card shadow-sm space-y-6">
                  <div className="flex items-center justify-between border-b border-border pb-3">
                    <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                      <Layers className="w-5 h-5 text-primary" />
                      PRISMA 2020 Study Flow Diagram
                    </h3>
                    {prismaFlow && (
                      <span className="text-xs font-medium text-muted-foreground">
                        Overall Attrition: {prismaFlow.attrition_rate}%
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
                    {/* Step 1: Identification */}
                    <div className="p-4 rounded-xl border border-blue-500/30 bg-blue-500/5 space-y-2 text-center">
                      <div className="text-xs font-semibold uppercase tracking-wider text-blue-500">
                        1. Identification
                      </div>
                      <div className="text-3xl font-extrabold text-foreground">
                        {selectedReview.total_identified}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Records retrieved from database & automated search sweeps
                      </div>
                    </div>

                    {/* Step 2: Screening */}
                    <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/5 space-y-2 text-center">
                      <div className="text-xs font-semibold uppercase tracking-wider text-amber-500">
                        2. Screening
                      </div>
                      <div className="text-3xl font-extrabold text-foreground">
                        {selectedReview.total_screened}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Title & Abstract assessed against criteria
                      </div>
                    </div>

                    {/* Step 3: Eligibility */}
                    <div className="p-4 rounded-xl border border-purple-500/30 bg-purple-500/5 space-y-2 text-center">
                      <div className="text-xs font-semibold uppercase tracking-wider text-purple-500">
                        3. Eligibility
                      </div>
                      <div className="text-3xl font-extrabold text-foreground">
                        {selectedReview.total_eligible}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Full-text reports evaluated for inclusion
                      </div>
                    </div>

                    {/* Step 4: Included */}
                    <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5 space-y-2 text-center">
                      <div className="text-xs font-semibold uppercase tracking-wider text-emerald-500">
                        4. Included
                      </div>
                      <div className="text-3xl font-extrabold text-emerald-500">
                        {selectedReview.total_included}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Studies included in quantitative synthesis
                      </div>
                    </div>
                  </div>

                  {/* Criteria Summary Pills */}
                  {selectedReview.criteria && selectedReview.criteria.length > 0 && (
                    <div className="space-y-2 pt-2">
                      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Review Eligibility Criteria
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedReview.criteria.map((c) => (
                          <span
                            key={c.id}
                            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium border ${
                              c.criterion_type === 'inclusion'
                                ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
                                : 'bg-red-500/10 text-red-600 border-red-500/20'
                            }`}
                          >
                            <span className="font-semibold uppercase">{c.criterion_type}:</span> {c.description}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-16 border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                Select a systematic review from the left sidebar or create a new one.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Screening Queue */}
      {activeTab === 'screening' && selectedReview && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-foreground">Candidate Studies Screening Queue</h3>
            <div className="text-xs text-muted-foreground">
              {selectedReview.candidates?.length || 0} candidate papers
            </div>
          </div>

          <div className="space-y-3">
            {selectedReview.candidates?.map((study) => (
              <div
                key={study.id}
                className="p-5 rounded-xl border border-border bg-card shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-semibold border ${
                        study.screening_status === 'included'
                          ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                          : study.screening_status === 'excluded'
                          ? 'bg-red-500/10 text-red-500 border-red-500/20'
                          : 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                      }`}
                    >
                      {study.screening_status.replace(/_/g, ' ').toUpperCase()}
                    </span>
                    {study.publication_year && (
                      <span className="text-xs text-muted-foreground font-mono">({study.publication_year})</span>
                    )}
                    {study.methodology_type && (
                      <span className="px-2 py-0.5 rounded text-xs bg-muted text-muted-foreground">
                        {study.methodology_type}
                      </span>
                    )}
                    {study.effect_size !== null && study.effect_size !== undefined && (
                      <span className="text-xs font-mono font-medium text-primary">
                        Effect Size: {study.effect_size} (N={study.sample_size || 'N/A'})
                      </span>
                    )}
                  </div>

                  <h4 className="text-base font-semibold text-foreground">{study.title}</h4>
                  {study.authors && study.authors.length > 0 && (
                    <p className="text-xs text-muted-foreground">{study.authors.join(', ')}</p>
                  )}
                  {study.exclusion_reason && (
                    <p className="text-xs text-red-500 font-medium">Exclusion Reason: {study.exclusion_reason}</p>
                  )}
                </div>

                {/* Screening Action Buttons */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleScreenStudy(study.id, 'included')}
                    className="px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20 text-xs font-medium transition flex items-center gap-1.5 border border-emerald-500/20"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Include
                  </button>
                  <button
                    onClick={() => handleScreenStudy(study.id, 'excluded')}
                    className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-600 hover:bg-red-500/20 text-xs font-medium transition flex items-center gap-1.5 border border-red-500/20"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    Exclude
                  </button>
                </div>
              </div>
            ))}
            {(!selectedReview.candidates || selectedReview.candidates.length === 0) && (
              <div className="text-center py-12 border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                No candidate studies in this review yet.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Quantitative Meta-Analysis & Forest Plot */}
      {activeTab === 'meta_analysis' && selectedReview && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-foreground">Quantitative Meta-Analysis Synthesis</h3>
              <p className="text-xs text-muted-foreground">
                Statistical aggregation, heterogeneity metrics (I² / Tau²), and DerSimonian-Laird forest plot.
              </p>
            </div>
            <button
              onClick={() => setShowMetaModal(true)}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition shadow-sm"
            >
              <Play className="w-3.5 h-3.5" />
              Run Meta-Analysis
            </button>
          </div>

          {latestMetaAnalysis ? (
            <div className="space-y-6">
              {/* Meta-Analysis Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
                  <span className="text-xs font-medium text-muted-foreground uppercase block">Pooled Effect Size</span>
                  <div className="text-2xl font-bold text-primary mt-1">
                    {latestMetaAnalysis.pooled_effect_size}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    95% CI: [{latestMetaAnalysis.pooled_ci_lower}, {latestMetaAnalysis.pooled_ci_upper}]
                  </span>
                </div>

                <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
                  <span className="text-xs font-medium text-muted-foreground uppercase block">Heterogeneity (I²)</span>
                  <div className="text-2xl font-bold text-amber-500 mt-1">
                    {latestMetaAnalysis.i_squared}%
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {latestMetaAnalysis.i_squared > 50 ? 'Substantial heterogeneity' : 'Low to moderate'}
                  </span>
                </div>

                <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
                  <span className="text-xs font-medium text-muted-foreground uppercase block">Test of Effect (p)</span>
                  <div className="text-2xl font-bold text-foreground mt-1">
                    {latestMetaAnalysis.p_value < 0.001 ? '< 0.001' : latestMetaAnalysis.p_value}
                  </div>
                  <span className="text-xs text-emerald-500 font-medium">
                    {latestMetaAnalysis.p_value < 0.05 ? 'Statistically Significant' : 'Not Significant'}
                  </span>
                </div>

                <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
                  <span className="text-xs font-medium text-muted-foreground uppercase block">Studies Synthesized</span>
                  <div className="text-2xl font-bold text-foreground mt-1">
                    {latestMetaAnalysis.total_studies_analyzed}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    Model: {latestMetaAnalysis.model_type.replace('_', ' ')}
                  </span>
                </div>
              </div>

              {/* Interactive Forest Plot Component */}
              <div className="p-6 rounded-xl border border-border bg-card shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-border pb-3">
                  <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-primary" />
                    Forest Plot ({latestMetaAnalysis.synthesis_name})
                  </h4>
                  <span className="text-xs font-mono text-muted-foreground">Metric: {latestMetaAnalysis.effect_metric}</span>
                </div>

                {/* Plot Rows */}
                <div className="space-y-3 pt-2">
                  <div className="grid grid-cols-12 text-xs font-semibold text-muted-foreground pb-1 border-b border-border">
                    <div className="col-span-4">Study / Author</div>
                    <div className="col-span-5 text-center">Effect Size & 95% Confidence Interval</div>
                    <div className="col-span-1 text-right">Weight</div>
                    <div className="col-span-2 text-right">Value [95% CI]</div>
                  </div>

                  {latestMetaAnalysis.forest_plot_data?.map((item, idx) => {
                    const minScale = -2.0;
                    const maxScale = 2.0;
                    const range = maxScale - minScale;
                    const leftPct = Math.max(0, Math.min(100, ((item.ci_lower - minScale) / range) * 100));
                    const rightPct = Math.max(0, Math.min(100, ((item.ci_upper - minScale) / range) * 100));
                    const pointPct = Math.max(0, Math.min(100, ((item.effect_size - minScale) / range) * 100));

                    return (
                      <div key={idx} className="grid grid-cols-12 items-center text-xs py-2 hover:bg-muted/40 rounded-lg px-2">
                        <div className="col-span-4 font-medium text-foreground truncate">
                          {item.title} {item.year ? `(${item.year})` : ''}
                        </div>

                        {/* Visual Bar Canvas */}
                        <div className="col-span-5 relative h-6 flex items-center">
                          {/* Center 0 Line */}
                          <div
                            className="absolute top-0 bottom-0 w-[1px] bg-border z-0"
                            style={{ left: `${((0 - minScale) / range) * 100}%` }}
                          />
                          {/* CI Line */}
                          <div
                            className="absolute h-[2px] bg-primary/70 z-10"
                            style={{
                              left: `${leftPct}%`,
                              width: `${Math.max(2, rightPct - leftPct)}%`,
                            }}
                          />
                          {/* Point Square */}
                          <div
                            className="absolute w-2.5 h-2.5 bg-primary rounded-sm -ml-1 z-20 shadow-sm"
                            style={{ left: `${pointPct}%` }}
                          />
                        </div>

                        <div className="col-span-1 text-right text-muted-foreground font-mono">
                          {item.weight_percentage}%
                        </div>

                        <div className="col-span-2 text-right font-mono font-medium text-foreground">
                          {item.effect_size} [{item.ci_lower}, {item.ci_upper}]
                        </div>
                      </div>
                    );
                  })}

                  {/* Pooled Diamond Summary Row */}
                  <div className="grid grid-cols-12 items-center text-xs py-3 border-t-2 border-border font-bold bg-primary/5 rounded-lg px-2 mt-2">
                    <div className="col-span-4 text-primary">Pooled Summary (Random Effects)</div>
                    <div className="col-span-5 relative h-6 flex items-center">
                      <div
                        className="absolute h-3 bg-primary/30 border border-primary z-20 rounded"
                        style={{
                          left: `${Math.max(0, Math.min(100, ((latestMetaAnalysis.pooled_ci_lower - -2.0) / 4.0) * 100))}%`,
                          width: `${Math.max(
                            4,
                            ((latestMetaAnalysis.pooled_ci_upper - latestMetaAnalysis.pooled_ci_lower) / 4.0) * 100,
                          )}%`,
                        }}
                      />
                    </div>
                    <div className="col-span-1 text-right font-mono text-primary">100.0%</div>
                    <div className="col-span-2 text-right font-mono text-primary">
                      {latestMetaAnalysis.pooled_effect_size} [{latestMetaAnalysis.pooled_ci_lower},{' '}
                      {latestMetaAnalysis.pooled_ci_upper}]
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 border border-dashed border-border rounded-xl text-muted-foreground text-sm space-y-3">
              <BarChart3 className="w-8 h-8 mx-auto text-muted-foreground/60" />
              <p>No meta-analysis runs recorded for this systematic review yet.</p>
              <button
                onClick={() => setShowMetaModal(true)}
                className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition shadow-sm"
              >
                Launch First Meta-Analysis
              </button>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Risk of Bias Matrix (RoB 2) */}
      {activeTab === 'risk_of_bias' && selectedReview && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-foreground">Risk of Bias Matrix (RoB 2 / ROBINS-I)</h3>
              <p className="text-xs text-muted-foreground">
                Domain-level methodological quality assessment across all included candidate studies.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-border bg-card shadow-sm">
            <table className="w-full text-left text-xs">
              <thead className="bg-muted/50 border-b border-border text-muted-foreground font-semibold">
                <tr>
                  <th className="p-3">Study</th>
                  <th className="p-3 text-center">Selection Bias</th>
                  <th className="p-3 text-center">Confounding Bias</th>
                  <th className="p-3 text-center">Measurement Bias</th>
                  <th className="p-3 text-center">Reporting Bias</th>
                  <th className="p-3 text-center">Overall Quality</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {selectedReview.candidates
                  ?.filter((c) => c.screening_status === 'included')
                  .map((study) => {
                    const rob = study.risk_of_bias || {
                      selection_bias: 'low_risk',
                      confounding_bias: 'low_risk',
                      measurement_bias: 'low_risk',
                      reporting_bias: 'low_risk',
                      overall_risk: 'low_risk',
                    };

                    const renderBadge = (val: string) => {
                      if (val === 'low_risk')
                        return (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                            Low Risk
                          </span>
                        );
                      if (val === 'some_concerns')
                        return (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/10 text-amber-500 border border-amber-500/20">
                            Some Concerns
                          </span>
                        );
                      return (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-red-500/10 text-red-500 border border-red-500/20">
                          High Risk
                        </span>
                      );
                    };

                    return (
                      <tr key={study.id} className="hover:bg-muted/30">
                        <td className="p-3 font-medium text-foreground max-w-xs truncate">
                          {study.title} ({study.publication_year || 'N/A'})
                        </td>
                        <td className="p-3 text-center">{renderBadge(rob.selection_bias)}</td>
                        <td className="p-3 text-center">{renderBadge(rob.confounding_bias)}</td>
                        <td className="p-3 text-center">{renderBadge(rob.measurement_bias)}</td>
                        <td className="p-3 text-center">{renderBadge(rob.reporting_bias)}</td>
                        <td className="p-3 text-center font-bold">{renderBadge(rob.overall_risk)}</td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modal: New SLR Review */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-card border border-border rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <BookOpenCheck className="w-5 h-5 text-primary" />
                Create Systematic Literature Review
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-muted-foreground hover:text-foreground text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateReview} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Review Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Efficacy of Multimodal LLMs in Clinical Diagnostic Reasoning"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Research Question</label>
                <textarea
                  required
                  rows={3}
                  placeholder="What is the comparative diagnostic accuracy of multimodal foundation models versus specialist clinicians?"
                  value={formData.research_question}
                  onChange={(e) => setFormData({ ...formData, research_question: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">Population (P)</label>
                  <input
                    type="text"
                    placeholder="e.g. Adult ICU Patients"
                    value={formData.population}
                    onChange={(e) => setFormData({ ...formData, population: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-background border border-border text-xs text-foreground focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">Intervention (I)</label>
                  <input
                    type="text"
                    placeholder="e.g. Agentic Multimodal Reasoning"
                    value={formData.intervention}
                    onChange={(e) => setFormData({ ...formData, intervention: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-background border border-border text-xs text-foreground focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">Comparator (C)</label>
                  <input
                    type="text"
                    placeholder="e.g. Standard Clinical Baseline"
                    value={formData.comparator}
                    onChange={(e) => setFormData({ ...formData, comparator: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-background border border-border text-xs text-foreground focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">Outcome (O)</label>
                  <input
                    type="text"
                    placeholder="e.g. F1 Score / Error Rate"
                    value={formData.outcome}
                    onChange={(e) => setFormData({ ...formData, outcome: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-background border border-border text-xs text-foreground focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg border border-border text-xs font-medium text-muted-foreground hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition"
                >
                  Initialize SLR Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Run Meta-Analysis */}
      {showMetaModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-card border border-border rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-primary" />
                Run Statistical Meta-Analysis
              </h3>
              <button onClick={() => setShowMetaModal(false)} className="text-muted-foreground text-sm">
                ✕
              </button>
            </div>

            <form onSubmit={handleRunMetaAnalysis} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Synthesis Name</label>
                <input
                  type="text"
                  required
                  value={metaForm.synthesis_name}
                  onChange={(e) => setMetaForm({ ...metaForm, synthesis_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Effect Metric</label>
                <select
                  value={metaForm.effect_metric}
                  onChange={(e) => setMetaForm({ ...metaForm, effect_metric: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground focus:outline-none focus:border-primary"
                >
                  <option value="hedges_g">Hedges' g (Corrected Standardized Mean Diff)</option>
                  <option value="cohens_d">Cohen's d (Standardized Mean Diff)</option>
                  <option value="log_odds_ratio">Log Odds Ratio (lnOR)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Statistical Model</label>
                <select
                  value={metaForm.model_type}
                  onChange={(e) =>
                    setMetaForm({ ...metaForm, model_type: e.target.value as 'fixed_effect' | 'random_effects' })
                  }
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground focus:outline-none focus:border-primary"
                >
                  <option value="random_effects">Random Effects (DerSimonian-Laird, Recommended)</option>
                  <option value="fixed_effect">Fixed Effect (Inverse-Variance)</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowMetaModal(false)}
                  className="px-4 py-2 rounded-lg border border-border text-xs font-medium text-muted-foreground hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition"
                >
                  Calculate Synthesis
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
