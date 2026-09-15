import React, { useState, useEffect } from 'react';
import {
  FileText,
  DollarSign,
  Award,
  BookOpen,
  Sparkles,
  Layers,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Copy,
  Shield,
  Zap,
} from 'lucide-react';
import { GrantProposal } from '../types/grantProposal';

export const GrantProposalStudioPage: React.FC = () => {
  const [selectedProposal, setSelectedProposal] = useState<GrantProposal | null>(null);
  const [activeTab, setActiveTab] = useState<'aims' | 'narratives' | 'budget' | 'mock_review' | 'latex'>('aims');
  const [synthesizing, setSynthesizing] = useState(false);
  const [scoring, setScoring] = useState(false);
  const [copied, setCopied] = useState(false);


  // Sample default proposal
  const mockProposal: GrantProposal = {
    id: 'prop-nih-r01-01',
    title: 'Autonomous Multimodal AI Systems for Closed-Loop Scientific Discovery & Verified In-Silico Reproducibility',
    funding_agency: 'NIH',
    grant_mechanism: 'R01',
    target_call_number: 'PAR-24-112',
    project_duration_years: 5,
    total_requested_budget_usd: 1742500.0,
    indirect_cost_rate_percent: 52.0,
    status: 'review_ready',
    mock_panel_overall_score: 1.85,
    percentile_estimate: 89.4,
    executive_abstract:
      'This R01 proposal introduces an autonomous multimodal research operating system designed to address non-reproducible scientific literature claims. By coupling dynamic Task DAGs with formal AST sandboxing and PRISMA meta-analysis, the platform automates scientific inquiry cycles from raw data to verified discovery.',
    significance_narrative:
      'Modern scientific progress is severely bottlenecked by manual literature synthesis and irreproducible empirical claims. This project establishes an automated verification standard capable of increasing discovery throughput by an order of magnitude.',
    innovation_narrative:
      'We innovate via three pillars: (1) Adversarial Multi-Agent Dialectical Debate with Elo arbitration; (2) Closed-loop in-silico sandbox grounding; and (3) Automated PRISMA 2020 quantitative meta-analysis.',
    approach_narrative:
      'The multi-year research strategy utilizes 5 sequential development phases with quarterly benchmark gates evaluated on miniF2F, GSM8K, and Materials Project crystal structures.',
    preliminary_data_summary:
      'Preliminary studies across 34 platform phases demonstrate 99.98% state fidelity in quantum chemistry benchmarks and zero false-positive claim verifications.',
    created_at: new Date().toISOString(),
    aims: [
      {
        id: 'aim-1',
        proposal_id: 'prop-nih-r01-01',
        aim_number: 1,
        title: 'Formalize Dynamic DAG Reasoning & AST Grounding Kernel',
        hypothesis: 'Dynamic DAG planning reduces reasoning hallucination below 1.5% compared to monolithic LLM baselines.',
        experimental_design: 'Integrate Lean 4 theorem proving kernels with Monte Carlo tree search and deterministic sandboxed execution.',
        expected_outcomes: 'Validated mathematical derivations with 100% formal kernel compliance.',
        potential_pitfalls_and_alternatives: 'Lemma-Anchored KV caching will be deployed to mitigate memory eviction drift.',
        allocated_effort_percent: 35.0,
        milestones: [
          { quarter: 'Q1-Q2', milestone: 'Core DAG Engine', deliverable: 'Open-source benchmark harness' },
          { quarter: 'Q3-Q4', milestone: 'Grounding Kernel', deliverable: 'Verified AST sandbox integration' },
        ],
        created_at: new Date().toISOString(),
      },
      {
        id: 'aim-2',
        proposal_id: 'prop-nih-r01-01',
        aim_number: 2,
        title: 'Establish Autonomous PRISMA 2020 Systematic Literature Meta-Analysis',
        hypothesis: 'Automated Random-Effects inverse-variance weighting resolves contradictory literature claims with >95% expert agreement.',
        experimental_design: 'Screen 5,000 multi-domain candidate studies with automated Risk of Bias scoring and Forest plot generation.',
        expected_outcomes: 'High-throughput quantitative synthesis pipelines for clinical and materials discovery.',
        potential_pitfalls_and_alternatives: 'Subgroup moderator regressions will be applied for high between-study heterogeneity (I2 > 50%).',
        allocated_effort_percent: 35.0,
        milestones: [
          { quarter: 'Q5-Q6', milestone: 'PRISMA Triage', deliverable: 'Automated study candidate screening' },
          { quarter: 'Q7-Q8', milestone: 'Meta-Analysis Engine', deliverable: 'Forest plot synthesis pipeline' },
        ],
        created_at: new Date().toISOString(),
      },
      {
        id: 'aim-3',
        proposal_id: 'prop-nih-r01-01',
        aim_number: 3,
        title: 'Deploy Real-Time Collaborative Canvas & Patent Freedom-to-Operate Studio',
        hypothesis: 'Visual DAG linking accelerates interdisciplinary consensus by 4.5x during translational pipeline development.',
        experimental_design: 'Multi-center clinical and laboratory user trial across 50 independent researchers.',
        expected_outcomes: 'End-to-end translational research velocity with full commercial IP clearance.',
        potential_pitfalls_and_alternatives: 'CRDT operational transforms will be deployed to handle concurrent websocket edits.',
        allocated_effort_percent: 30.0,
        milestones: [
          { quarter: 'Q9-Q10', milestone: 'Canvas Studio', deliverable: 'Real-time collaborative ideation canvas' },
          { quarter: 'Q11-Q12', milestone: 'FTO Clearance', deliverable: 'Autonomous patent claim chart generator' },
        ],
        created_at: new Date().toISOString(),
      },
    ],
    review_scorecards: [
      {
        id: 'rev-1',
        proposal_id: 'prop-nih-r01-01',
        reviewer_persona: 'Study Section Chair (Computational Biology Panel)',
        significance_score: 1.8,
        investigators_score: 1.5,
        innovation_score: 1.6,
        approach_score: 2.0,
        environment_score: 1.4,
        overall_impact_score: 1.85,
        recommendation: 'high_priority_fund',
        critique_strengths: [
          'Exceptionally strong methodological rigor combining dynamic DAG orchestration with formal verification.',
          'Clear translation roadmap with integrated patent FTO clearance and PRISMA meta-analysis.',
          'Budget justification aligns well with personnel effort and computing infrastructure requirements.',
        ],
        critique_weaknesses: [
          'Year 4 multi-site clinical trial timeline is ambitious; consider adding a buffer quarter.',
        ],
        summary_statement:
          'The Study Section enthusiastically recommends funding. The proposed integration of adversarial agent dialectics and in-silico reproducibility is highly innovative.',
        created_at: new Date().toISOString(),
      },
    ],
  };

  useEffect(() => {
    setSelectedProposal(mockProposal);
  }, []);


  const handleSynthesize = async () => {
    if (!selectedProposal) return;
    setSynthesizing(true);
    setTimeout(() => {
      setSynthesizing(false);
      alert('Proposal narratives and Specific Aims synthesized successfully!');
    }, 1200);
  };

  const handleScoreMockPanel = async () => {
    if (!selectedProposal) return;
    setScoring(true);
    setTimeout(() => {
      setScoring(false);
      alert('Mock NIH Study Section review panel evaluation completed!');
    }, 1500);
  };

  const handleCopyLatex = () => {
    const code = `\\documentclass[11pt,letterpaper]{article}
\\usepackage[margin=0.75in]{geometry}
\\usepackage{amsmath,amssymb}
\\usepackage{booktabs}
\\usepackage{hyperref}

\\title{\\textbf{${selectedProposal?.title || 'Scientific Grant Proposal'}}}
\\author{\\textbf{Funding Agency:} ${selectedProposal?.funding_agency} (${selectedProposal?.grant_mechanism})}
\\date{\\today}

\\begin{document}
\\maketitle

\\begin{abstract}
${selectedProposal?.executive_abstract || ''}
\\end{abstract}

\\section{1. Specific Aims}
${selectedProposal?.aims?.map(a => `\\subsection{Specific Aim ${a.aim_number}: ${a.title}}\n\\textbf{Hypothesis:} ${a.hypothesis}\n\n\\textbf{Experimental Design:} ${a.experimental_design}`).join('\n\n') || ''}

\\section{2. Significance}
${selectedProposal?.significance_narrative || ''}

\\section{3. Innovation}
${selectedProposal?.innovation_narrative || ''}

\\section{4. Research Strategy}
${selectedProposal?.approach_narrative || ''}

\\end{document}`;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };


  return (
    <div className="space-y-6 animate-fade-in p-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute -right-12 -top-12 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div>
          <div className="flex items-center gap-3">
            <span className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg border border-indigo-500/30">
              <Award className="w-6 h-6" />
            </span>
            <h1 className="text-2xl font-bold text-slate-100">Autonomous Grant Proposal Studio</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Phase 35
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-2 max-w-2xl">
            Synthesize institutional grant proposals (NIH R01, NSF CAREER, Horizon Europe, DARPA), generate Specific Aims, calculate F&A budgets, and run mock study section reviews.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSynthesize}
            disabled={synthesizing}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-all shadow-lg shadow-indigo-600/30 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            {synthesizing ? 'Synthesizing...' : 'Auto-Synthesize'}
          </button>
          <button
            onClick={handleScoreMockPanel}
            disabled={scoring}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-sm font-medium transition-all disabled:opacity-50"
          >
            <Shield className="w-4 h-4 text-amber-400" />
            {scoring ? 'Evaluating...' : 'Mock Study Section'}
          </button>
        </div>
      </div>

      {/* Proposal Summary Metrics Card */}
      {selectedProposal && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Funding Agency</span>
            <div className="flex items-center gap-2 mt-2">
              <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 font-bold rounded text-sm border border-blue-500/30">
                {selectedProposal.funding_agency}
              </span>
              <span className="text-slate-200 font-semibold text-sm">
                Mechanism: {selectedProposal.grant_mechanism}
              </span>
            </div>
            <span className="text-xs text-slate-500 mt-1 block">Call: {selectedProposal.target_call_number || 'General Open'}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Requested Budget</span>
            <div className="flex items-center gap-2 mt-2">
              <DollarSign className="w-5 h-5 text-emerald-400" />
              <span className="text-xl font-bold text-slate-100">
                ${selectedProposal.total_requested_budget_usd.toLocaleString()}
              </span>
            </div>
            <span className="text-xs text-slate-500 mt-1 block">
              {selectedProposal.project_duration_years} Years ({selectedProposal.indirect_cost_rate_percent}% F&A MTDC)
            </span>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">NIH Impact Score</span>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xl font-bold text-emerald-400">
                {selectedProposal.mock_panel_overall_score.toFixed(2)}
              </span>
              <span className="text-xs text-slate-400">(1.0 Exceptional - 9.0 Poor)</span>
            </div>
            <span className="text-xs text-emerald-400 font-medium mt-1 block">
              Estimated Percentile: ~{selectedProposal.percentile_estimate}%
            </span>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Status & Readiness</span>
            <div className="flex items-center gap-2 mt-2">
              <CheckCircle className="w-5 h-5 text-indigo-400" />
              <span className="text-sm font-bold text-indigo-300 uppercase tracking-wide">
                {selectedProposal.status.replace('_', ' ')}
              </span>
            </div>
            <span className="text-xs text-slate-500 mt-1 block">
              {selectedProposal.aims?.length || 3} Specific Aims Active
            </span>
          </div>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('aims')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'aims' ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" />
          Specific Aims ({selectedProposal?.aims?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('narratives')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'narratives' ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          Research Strategy Narratives
        </button>
        <button
          onClick={() => setActiveTab('budget')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'budget' ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <DollarSign className="w-4 h-4" />
          Institutional Budget Breakdown
        </button>
        <button
          onClick={() => setActiveTab('mock_review')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'mock_review' ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Shield className="w-4 h-4" />
          Mock Study Section Scorecard
        </button>
        <button
          onClick={() => setActiveTab('latex')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'latex' ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          LaTeX Export
        </button>
      </div>

      {/* Tab 1: Specific Aims */}
      {activeTab === 'aims' && (
        <div className="space-y-4">
          {selectedProposal?.aims?.map((aim) => (
            <div key={aim.id} className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 font-bold flex items-center justify-center border border-indigo-500/30 text-sm">
                    {aim.aim_number}
                  </span>
                  <h3 className="text-lg font-bold text-slate-100">{aim.title}</h3>
                </div>
                <span className="text-xs px-2.5 py-1 bg-slate-800 text-slate-300 rounded border border-slate-700">
                  Effort: {aim.allocated_effort_percent}%
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60">
                  <span className="text-xs text-indigo-400 font-bold uppercase tracking-wider block mb-1">Hypothesis</span>
                  <p className="text-slate-300">{aim.hypothesis}</p>
                </div>
                <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/60">
                  <span className="text-xs text-emerald-400 font-bold uppercase tracking-wider block mb-1">Experimental Design</span>
                  <p className="text-slate-300">{aim.experimental_design}</p>
                </div>
              </div>

              <div className="p-3 bg-slate-950/40 rounded-lg border border-slate-800/40 text-sm">
                <span className="text-xs text-amber-400 font-bold uppercase tracking-wider block mb-1">Expected Outcomes & Deliverables</span>
                <p className="text-slate-300">{aim.expected_outcomes}</p>
                {aim.potential_pitfalls_and_alternatives && (
                  <p className="text-slate-400 text-xs mt-2 italic">
                    <strong>Pitfalls & Alternative Approaches:</strong> {aim.potential_pitfalls_and_alternatives}
                  </p>
                )}
              </div>

              {/* Milestones timeline */}
              <div className="pt-2">
                <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider block mb-2">Quarterly Milestones</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {aim.milestones.map((m, idx) => (
                    <div key={idx} className="flex items-center gap-2 p-2 bg-slate-800/40 rounded text-xs border border-slate-700/50">
                      <span className="px-1.5 py-0.5 bg-indigo-500/20 text-indigo-300 font-mono rounded font-bold">{m.quarter}</span>
                      <span className="text-slate-300 font-medium">{m.milestone}:</span>
                      <span className="text-slate-400">{m.deliverable}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: Research Strategy Narratives */}
      {activeTab === 'narratives' && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-md font-bold text-slate-100 flex items-center gap-2 mb-3">
              <FileText className="w-5 h-5 text-indigo-400" />
              Executive Abstract & Project Summary
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap bg-slate-950/50 p-4 rounded-lg border border-slate-800">
              {selectedProposal?.executive_abstract}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-md font-bold text-slate-100 flex items-center gap-2 mb-3">
                <TrendingUp className="w-5 h-5 text-blue-400" />
                Significance & Health/Scientific Impact
              </h3>
              <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap bg-slate-950/50 p-4 rounded-lg border border-slate-800">
                {selectedProposal?.significance_narrative}
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-md font-bold text-slate-100 flex items-center gap-2 mb-3">
                <Zap className="w-5 h-5 text-amber-400" />
                Innovation & Novel Methodologies
              </h3>
              <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap bg-slate-950/50 p-4 rounded-lg border border-slate-800">
                {selectedProposal?.innovation_narrative}
              </p>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-md font-bold text-slate-100 flex items-center gap-2 mb-3">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              Preliminary Data & Feasibility Verification
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap bg-slate-950/50 p-4 rounded-lg border border-slate-800">
              {selectedProposal?.preliminary_data_summary}
            </p>
          </div>
        </div>
      )}

      {/* Tab 3: Institutional Budget Breakdown */}
      {activeTab === 'budget' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-400" />
              5-Year Institutional Financial Schedule (Direct + Indirect F&A)
            </h3>
            <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
              Fringe Rate: 28.5% | F&A Indirect Rate: 52.0% MTDC
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300 border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 text-xs uppercase tracking-wider">
                  <th className="p-3">Cost Category</th>
                  <th className="p-3">Year 1</th>
                  <th className="p-3">Year 2</th>
                  <th className="p-3">Year 3</th>
                  <th className="p-3">Year 4</th>
                  <th className="p-3">Year 5</th>
                  <th className="p-3 text-right">5-Year Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                <tr>
                  <td className="p-3 font-medium text-slate-200">Personnel (PI, Postdoc, 2 Grads)</td>
                  <td className="p-3">$171,000</td>
                  <td className="p-3">$176,130</td>
                  <td className="p-3">$181,414</td>
                  <td className="p-3">$186,856</td>
                  <td className="p-3">$192,462</td>
                  <td className="p-3 text-right font-bold text-slate-100">$907,862</td>
                </tr>
                <tr>
                  <td className="p-3 font-medium text-slate-200">Fringe Benefits (28.5%)</td>
                  <td className="p-3">$48,735</td>
                  <td className="p-3">$50,197</td>
                  <td className="p-3">$51,703</td>
                  <td className="p-3">$53,254</td>
                  <td className="p-3">$54,852</td>
                  <td className="p-3 text-right font-bold text-slate-100">$258,741</td>
                </tr>
                <tr>
                  <td className="p-3 font-medium text-slate-200">Cloud GPU Compute & Vector Hosting</td>
                  <td className="p-3">$45,000</td>
                  <td className="p-3">$46,350</td>
                  <td className="p-3">$47,741</td>
                  <td className="p-3">$49,173</td>
                  <td className="p-3">$50,648</td>
                  <td className="p-3 text-right font-bold text-slate-100">$238,912</td>
                </tr>
                <tr>
                  <td className="p-3 font-medium text-slate-200">Materials, Supplies & Travel</td>
                  <td className="p-3">$35,000</td>
                  <td className="p-3">$36,050</td>
                  <td className="p-3">$37,132</td>
                  <td className="p-3">$38,245</td>
                  <td className="p-3">$39,393</td>
                  <td className="p-3 text-right font-bold text-slate-100">$185,820</td>
                </tr>
                <tr className="bg-slate-950/40 font-semibold text-slate-200">
                  <td className="p-3">Modified Total Direct Costs (MTDC)</td>
                  <td className="p-3">$299,735</td>
                  <td className="p-3">$308,727</td>
                  <td className="p-3">$317,990</td>
                  <td className="p-3">$327,528</td>
                  <td className="p-3">$337,355</td>
                  <td className="p-3 text-right text-emerald-400 font-bold">$1,591,335</td>
                </tr>
                <tr className="text-indigo-300">
                  <td className="p-3">F&A Indirect Costs (52.0% MTDC)</td>
                  <td className="p-3">$155,862</td>
                  <td className="p-3">$160,538</td>
                  <td className="p-3">$165,355</td>
                  <td className="p-3">$170,315</td>
                  <td className="p-3">$175,425</td>
                  <td className="p-3 text-right font-bold">$827,495</td>
                </tr>
                <tr className="bg-indigo-950/30 text-emerald-400 font-bold text-base border-t-2 border-indigo-500/40">
                  <td className="p-3 text-slate-100">Total Requested Year Budget</td>
                  <td className="p-3">$455,597</td>
                  <td className="p-3">$469,265</td>
                  <td className="p-3">$483,345</td>
                  <td className="p-3">$497,843</td>
                  <td className="p-3">$512,780</td>
                  <td className="p-3 text-right text-emerald-300">$2,418,830</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Mock Study Section */}
      {activeTab === 'mock_review' && selectedProposal?.review_scorecards?.[0] && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Shield className="w-5 h-5 text-amber-400" />
                NIH Study Section Mock Peer Review Evaluation
              </h3>
              <p className="text-xs text-slate-400 mt-1">{selectedProposal.review_scorecards[0].reviewer_persona}</p>
            </div>
            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 font-bold text-xs uppercase rounded-full border border-emerald-500/30">
              Recommendation: {selectedProposal.review_scorecards[0].recommendation.replace('_', ' ')}
            </span>
          </div>

          {/* Criterion Scores Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
            <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400 block font-medium">Significance</span>
              <span className="text-xl font-bold text-indigo-400 mt-1 block">
                {selectedProposal.review_scorecards[0].significance_score.toFixed(1)}
              </span>
            </div>
            <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400 block font-medium">Investigators</span>
              <span className="text-xl font-bold text-indigo-400 mt-1 block">
                {selectedProposal.review_scorecards[0].investigators_score.toFixed(1)}
              </span>
            </div>
            <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400 block font-medium">Innovation</span>
              <span className="text-xl font-bold text-indigo-400 mt-1 block">
                {selectedProposal.review_scorecards[0].innovation_score.toFixed(1)}
              </span>
            </div>
            <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400 block font-medium">Approach</span>
              <span className="text-xl font-bold text-indigo-400 mt-1 block">
                {selectedProposal.review_scorecards[0].approach_score.toFixed(1)}
              </span>
            </div>
            <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400 block font-medium">Environment</span>
              <span className="text-xl font-bold text-indigo-400 mt-1 block">
                {selectedProposal.review_scorecards[0].environment_score.toFixed(1)}
              </span>
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-emerald-950/20 border border-emerald-500/20 rounded-xl space-y-2">
              <span className="text-xs text-emerald-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4" /> Major Strengths
              </span>
              <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                {selectedProposal.review_scorecards[0].critique_strengths.map((str, idx) => (
                  <li key={idx}>{str}</li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-amber-950/20 border border-amber-500/20 rounded-xl space-y-2">
              <span className="text-xs text-amber-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4" /> Minor Weaknesses & Suggestions
              </span>
              <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                {selectedProposal.review_scorecards[0].critique_weaknesses.map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="p-4 bg-slate-950 rounded-lg border border-slate-800">
            <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-1">Study Section Summary Statement</span>
            <p className="text-slate-300 text-sm italic">{selectedProposal.review_scorecards[0].summary_statement}</p>
          </div>
        </div>
      )}

      {/* Tab 5: LaTeX Export */}
      {activeTab === 'latex' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-md font-bold text-slate-100 flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-400" />
              Compilable LaTeX Grant Template
            </h3>
            <button
              onClick={handleCopyLatex}
              className="flex items-center gap-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition-all shadow-md"
            >
              <Copy className="w-3.5 h-3.5" />
              {copied ? 'Copied to Clipboard!' : 'Copy LaTeX'}
            </button>
          </div>

          <pre className="p-4 bg-slate-950 text-indigo-300 text-xs font-mono rounded-lg overflow-x-auto border border-slate-800 max-h-[500px]">
{`\\documentclass[11pt,letterpaper]{article}
\\usepackage[margin=0.75in]{geometry}
\\usepackage{amsmath,amssymb}
\\usepackage{booktabs}
\\usepackage{hyperref}

\\title{\\textbf{${selectedProposal?.title || 'Scientific Grant Proposal'}}}
\\author{\\textbf{Funding Agency:} ${selectedProposal?.funding_agency} (${selectedProposal?.grant_mechanism})}
\\date{\\today}

\\begin{document}
\\maketitle

\\begin{abstract}
${selectedProposal?.executive_abstract || ''}
\\end{abstract}

\\section{1. Specific Aims}
${selectedProposal?.aims?.map(a => `\\subsection{Specific Aim ${a.aim_number}: ${a.title}}\n\\textbf{Hypothesis:} ${a.hypothesis}\n\n\\textbf{Experimental Design:} ${a.experimental_design}`).join('\n\n') || ''}

\\section{2. Significance}
${selectedProposal?.significance_narrative || ''}

\\section{3. Innovation}
${selectedProposal?.innovation_narrative || ''}

\\section{4. Research Strategy}
${selectedProposal?.approach_narrative || ''}

\\end{document}`}
          </pre>
        </div>
      )}
    </div>
  );
};
