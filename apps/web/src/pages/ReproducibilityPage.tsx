import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Terminal,
  Play,
  Plus,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Layers,
  FileCode2,
  TrendingUp,
  Percent,
  CheckCheck,
  RotateCw,
} from 'lucide-react';
import {
  ExperimentProtocol,
  ReproducibilityRun,
  ReproducibilityMetrics,
  CreateProtocolPayload,
} from '../types/reproducibility';
import { useWorkspace } from '../context/WorkspaceContext';

export const ReproducibilityPage: React.FC = () => {
  const { currentWorkspace } = useWorkspace();
  const [activeTab, setActiveTab] = useState<'protocols' | 'console' | 'claims' | 'history'>('protocols');
  const [protocols, setProtocols] = useState<ExperimentProtocol[]>([]);
  const [selectedProtocol, setSelectedProtocol] = useState<ExperimentProtocol | null>(null);
  const [metrics, setMetrics] = useState<ReproducibilityMetrics>({
    total_protocols: 0,
    total_runs: 0,
    succeeded_runs: 0,
    run_success_rate: 0,
    total_verified_claims: 0,
    reproduced_claims: 0,
    claim_reproducibility_rate: 0,
    average_reproducibility_score: 0,
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [executing, setExecuting] = useState<boolean>(false);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);

  const [formData, setFormData] = useState<CreateProtocolPayload>({
    name: '',
    description: '',
    source_paper_title: '',
    source_doi: '',
    runtime_language: 'python3',
    executable_code: `# Example In-Silico Computational Protocol
import math
import statistics

# Parameters
n_samples = 1000
alpha = 0.05

# Empirical Simulation
data = [math.sin(i * 0.1) + (i % 5) * 0.2 for i in range(n_samples)]
mean_val = statistics.mean(data)
std_val = statistics.stdev(data)

# Output metrics dictionary
metrics = {
    "mean_accuracy": round(mean_val, 4),
    "dispersion_stdev": round(std_val, 4),
    "convergence_rate": 0.985
}
`,
    claimed_metrics: {
      mean_accuracy: 0.4000,
      dispersion_stdev: 0.8165,
      convergence_rate: 0.9850,
    },
  });

  const fetchProtocols = async () => {
    setLoading(true);
    try {
      const queryParams = currentWorkspace?.id ? `?workspace_id=${currentWorkspace.id}` : '';
      const [protocolsRes, metricsRes] = await Promise.all([
        fetch(`/api/v1/reproducibility/protocols${queryParams}`),
        fetch(`/api/v1/reproducibility/metrics`),
      ]);

      if (protocolsRes.ok) {
        const data = await protocolsRes.json();
        setProtocols(data);
        if (data.length > 0 && !selectedProtocol) {
          fetchProtocolDetails(data[0].id);
        }
      }
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }
    } catch (err) {
      console.error('Failed to load experiment protocols:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProtocolDetails = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/reproducibility/protocols/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedProtocol(data);
      }
    } catch (err) {
      console.error('Failed to load protocol details:', err);
    }
  };

  useEffect(() => {
    fetchProtocols();
  }, [currentWorkspace]);

  const handleCreateProtocol = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        workspace_id: currentWorkspace?.id,
      };

      const res = await fetch('/api/v1/reproducibility/protocols', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setShowCreateModal(false);
        setFormData({
          name: '',
          description: '',
          source_paper_title: '',
          source_doi: '',
          runtime_language: 'python3',
          executable_code: '',
          claimed_metrics: {},
        });
        await fetchProtocols();
      }
    } catch (err) {
      console.error('Failed to create protocol:', err);
    }
  };

  const handleExecuteProtocol = async () => {
    if (!selectedProtocol) return;
    setExecuting(true);
    try {
      const res = await fetch(`/api/v1/reproducibility/protocols/${selectedProtocol.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tolerance_threshold: 0.05 }),
      });
      if (res.ok) {
        await fetchProtocolDetails(selectedProtocol.id);
        setActiveTab('console');
      }
    } catch (err) {
      console.error('Execution failed:', err);
    } finally {
      setExecuting(false);
    }
  };

  const latestRun: ReproducibilityRun | undefined =
    selectedProtocol?.runs && selectedProtocol.runs.length > 0 ? selectedProtocol.runs[0] : undefined;

  return (
    <div className="space-y-6">
      {/* Top Banner & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Cpu className="w-8 h-8 text-primary" />
              In-Silico Experimentation & Reproducibility
            </h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
              Sandboxed Verification
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Automated computational execution, AST safety validation, and empirical claim verification against published baselines.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          New Experiment Protocol
        </button>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Protocols</span>
            <FileCode2 className="w-4 h-4 text-primary" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_protocols}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">In-Silico Runs</span>
            <Terminal className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_runs}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Run Success Rate</span>
            <Percent className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.run_success_rate}%</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Claims Verified</span>
            <CheckCheck className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_verified_claims}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Reproducibility</span>
            <TrendingUp className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">
            {metrics.average_reproducibility_score ? Math.round(metrics.average_reproducibility_score * 100) : 0}%
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border flex items-center gap-6">
        <button
          onClick={() => setActiveTab('protocols')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'protocols'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Layers className="w-4 h-4" />
          Protocols & Code Studio
        </button>

        <button
          onClick={() => setActiveTab('console')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'console'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Terminal className="w-4 h-4" />
          Simulation Console & Telemetry
        </button>

        <button
          onClick={() => setActiveTab('claims')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'claims'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <CheckCheck className="w-4 h-4" />
          Claim Verification Matrix
          {selectedProtocol?.verification_traces && (
            <span className="ml-1.5 px-2 py-0.5 rounded-full text-xs bg-muted text-muted-foreground">
              {selectedProtocol.verification_traces.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'history'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <RotateCw className="w-4 h-4" />
          Run History & Scorecard
        </button>
      </div>

      {/* Tab 1: Protocols & Code Studio */}
      {activeTab === 'protocols' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Protocol Selector Sidebar */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
              Computational Protocols
            </h3>
            <div className="space-y-2">
              {protocols.map((p) => (
                <div
                  key={p.id}
                  onClick={() => fetchProtocolDetails(p.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition ${
                    selectedProtocol?.id === p.id
                      ? 'border-primary bg-primary/5 shadow-sm'
                      : 'border-border bg-card hover:border-primary/50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-primary font-mono">{p.runtime_language}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded font-medium border ${
                        p.verification_status === 'fully_reproduced'
                          ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                          : p.verification_status === 'partially_reproduced'
                          ? 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                          : p.verification_status === 'discrepant'
                          ? 'bg-red-500/10 text-red-500 border-red-500/20'
                          : 'bg-muted text-muted-foreground'
                      }`}
                    >
                      {p.verification_status.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <h4 className="font-medium text-foreground text-sm line-clamp-2">{p.name}</h4>
                  {p.source_paper_title && (
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-1">Paper: {p.source_paper_title}</p>
                  )}
                </div>
              ))}
              {protocols.length === 0 && !loading && (
                <div className="text-center py-8 border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                  No computational protocols created yet.
                </div>
              )}
            </div>
          </div>

          {/* Protocol Inspector & Code Viewer */}
          <div className="lg:col-span-2 space-y-6">
            {selectedProtocol ? (
              <div className="space-y-6">
                <div className="p-5 rounded-xl border border-border bg-card shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-bold text-foreground">{selectedProtocol.name}</h2>
                    {selectedProtocol.description && (
                      <p className="text-sm text-muted-foreground mt-1">{selectedProtocol.description}</p>
                    )}
                    {selectedProtocol.source_paper_title && (
                      <span className="text-xs text-primary font-medium block mt-2">
                        Ref: {selectedProtocol.source_paper_title} {selectedProtocol.source_doi ? `(${selectedProtocol.source_doi})` : ''}
                      </span>
                    )}
                  </div>

                  <button
                    onClick={handleExecuteProtocol}
                    disabled={executing}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition shadow-sm disabled:opacity-50 shrink-0"
                  >
                    <Play className="w-4 h-4" />
                    {executing ? 'Simulating...' : 'Run Simulation'}
                  </button>
                </div>

                {/* Claimed Metrics Overview */}
                {selectedProtocol.claimed_metrics && Object.keys(selectedProtocol.claimed_metrics).length > 0 && (
                  <div className="p-4 rounded-xl border border-border bg-card shadow-sm space-y-2">
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Published Benchmark Baseline Claims
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      {Object.entries(selectedProtocol.claimed_metrics).map(([key, val]) => (
                        <div key={key} className="p-3 rounded-lg bg-muted/40 border border-border">
                          <span className="text-xs text-muted-foreground block truncate">{key}</span>
                          <span className="text-lg font-mono font-bold text-foreground">{val}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Code Block */}
                <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
                  <div className="bg-muted/60 px-4 py-2 border-b border-border flex items-center justify-between text-xs font-mono text-muted-foreground">
                    <span>Protocol Script ({selectedProtocol.runtime_language})</span>
                    <span>AST Sandboxed</span>
                  </div>
                  <pre className="p-4 text-xs font-mono text-foreground overflow-x-auto bg-card leading-relaxed">
                    {selectedProtocol.executable_code}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="text-center py-16 border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                Select an experiment protocol from the left sidebar to inspect and run.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Simulation Console & Telemetry */}
      {activeTab === 'console' && selectedProtocol && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-foreground">In-Silico Simulation Telemetry</h3>
            <button
              onClick={handleExecuteProtocol}
              disabled={executing}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition shadow-sm disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              {executing ? 'Executing...' : 'Re-Run Protocol'}
            </button>
          </div>

          {latestRun ? (
            <div className="space-y-6">
              {/* Telemetry Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
                  <span className="text-xs font-medium text-muted-foreground uppercase block">Execution Status</span>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className={`text-lg font-bold capitalize ${
                        latestRun.status === 'succeeded' ? 'text-emerald-500' : 'text-red-500'
                      }`}
                    >
                      {latestRun.status}
                    </span>
                  </div>
                </div>

                <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
                  <span className="text-xs font-medium text-muted-foreground uppercase block">Execution Time</span>
                  <div className="text-2xl font-mono font-bold text-foreground mt-1">
                    {latestRun.execution_time_ms} ms
                  </div>
                </div>

                <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
                  <span className="text-xs font-medium text-muted-foreground uppercase block">Peak Heap Memory</span>
                  <div className="text-2xl font-mono font-bold text-foreground mt-1">
                    {latestRun.memory_peak_mb} MB
                  </div>
                </div>

                <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
                  <span className="text-xs font-medium text-muted-foreground uppercase block">Reproducibility Score</span>
                  <div className="text-2xl font-bold text-primary mt-1">
                    {Math.round(latestRun.reproducibility_score * 100)}%
                  </div>
                </div>
              </div>

              {/* Terminal Logs Output */}
              <div className="rounded-xl border border-border bg-black/90 shadow-lg overflow-hidden">
                <div className="bg-zinc-900 px-4 py-2 border-b border-zinc-800 flex items-center justify-between text-xs font-mono text-zinc-400">
                  <span className="flex items-center gap-2">
                    <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                    stdout / In-Silico Runtime Terminal
                  </span>
                  <span>Exit Code 0</span>
                </div>
                <div className="p-4 font-mono text-xs text-emerald-400 space-y-1 min-h-[140px] whitespace-pre-wrap">
                  {latestRun.runtime_logs || 'No stdout output captured during execution.'}
                </div>
              </div>

              {/* Extracted Output Variables */}
              <div className="p-5 rounded-xl border border-border bg-card shadow-sm space-y-3">
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Computed Output Metrics Matrix
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {Object.entries(latestRun.reproduced_metrics || {}).map(([key, val]) => (
                    <div key={key} className="p-3 rounded-lg bg-muted/40 border border-border">
                      <span className="text-xs text-muted-foreground block truncate">{key}</span>
                      <span className="text-lg font-mono font-bold text-primary">{val}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 border border-dashed border-border rounded-xl text-muted-foreground text-sm space-y-3">
              <Terminal className="w-8 h-8 mx-auto text-muted-foreground/60" />
              <p>No execution runs recorded for this protocol yet.</p>
              <button
                onClick={handleExecuteProtocol}
                className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition shadow-sm"
              >
                Execute First Simulation
              </button>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Claim Verification Matrix */}
      {activeTab === 'claims' && selectedProtocol && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-foreground">Empirical Claim Verification Matrix</h3>
              <p className="text-xs text-muted-foreground">
                Granular delta error analysis between published claims and reproduced metrics.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-border bg-card shadow-sm">
            <table className="w-full text-left text-xs">
              <thead className="bg-muted/50 border-b border-border text-muted-foreground font-semibold">
                <tr>
                  <th className="p-3">Claim Statement / Metric</th>
                  <th className="p-3 text-right">Claimed Baseline</th>
                  <th className="p-3 text-right">Reproduced Value</th>
                  <th className="p-3 text-right">Relative Delta</th>
                  <th className="p-3 text-center">Verdict</th>
                  <th className="p-3">Analysis Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {selectedProtocol.verification_traces?.map((trace) => {
                  const renderVerdict = (verdict: string) => {
                    if (verdict === 'reproduced')
                      return (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                          <CheckCircle2 className="w-3 h-3" />
                          Reproduced
                        </span>
                      );
                    if (verdict === 'discrepant')
                      return (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-500 border border-amber-500/20">
                          <AlertTriangle className="w-3 h-3" />
                          Discrepant
                        </span>
                      );
                    return (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-500 border border-red-500/20">
                        <XCircle className="w-3 h-3" />
                        Refuted
                      </span>
                    );
                  };

                  return (
                    <tr key={trace.id} className="hover:bg-muted/30">
                      <td className="p-3 font-medium text-foreground">
                        <div>{trace.metric_name}</div>
                        <div className="text-[11px] text-muted-foreground">{trace.claim_statement}</div>
                      </td>
                      <td className="p-3 text-right font-mono font-semibold text-foreground">
                        {trace.claimed_value}
                      </td>
                      <td className="p-3 text-right font-mono font-semibold text-primary">
                        {trace.reproduced_value}
                      </td>
                      <td className="p-3 text-right font-mono">
                        {Math.round(trace.delta_relative_error * 1000) / 10}%
                      </td>
                      <td className="p-3 text-center">{renderVerdict(trace.verdict)}</td>
                      <td className="p-3 text-muted-foreground text-[11px] max-w-xs">{trace.analysis_notes}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {(!selectedProtocol.verification_traces || selectedProtocol.verification_traces.length === 0) && (
              <div className="text-center py-12 text-muted-foreground text-sm">
                No claim verification traces recorded yet. Run a simulation to evaluate claims.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 4: Run History & Scorecard */}
      {activeTab === 'history' && selectedProtocol && (
        <div className="space-y-4">
          <h3 className="text-base font-bold text-foreground">Historical Execution Runs</h3>
          <div className="space-y-3">
            {selectedProtocol.runs?.map((r) => (
              <div
                key={r.id}
                className="p-4 rounded-xl border border-border bg-card shadow-sm flex items-center justify-between"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded font-semibold capitalize ${
                        r.status === 'succeeded'
                          ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                          : 'bg-red-500/10 text-red-500 border border-red-500/20'
                      }`}
                    >
                      {r.status}
                    </span>
                    <span className="text-xs text-muted-foreground">{new Date(r.created_at).toLocaleString()}</span>
                  </div>
                  <div className="text-xs font-mono text-muted-foreground">
                    Runtime: {r.execution_time_ms} ms • Memory: {r.memory_peak_mb} MB
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs text-muted-foreground block">Reproducibility</span>
                  <span className="text-xl font-bold text-primary">{Math.round(r.reproducibility_score * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal: New Experiment Protocol */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-card border border-border rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <FileCode2 className="w-5 h-5 text-primary" />
                Register Experiment Protocol
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-muted-foreground hover:text-foreground text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateProtocol} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Protocol Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. FlashAttention-3 Kernel Speedup Simulation"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">Source Paper Title</label>
                  <input
                    type="text"
                    placeholder="e.g. Dao et al., 2024"
                    value={formData.source_paper_title || ''}
                    onChange={(e) => setFormData({ ...formData, source_paper_title: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-background border border-border text-xs text-foreground focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">DOI / Identifier</label>
                  <input
                    type="text"
                    placeholder="e.g. 10.48550/arXiv.2407.08608"
                    value={formData.source_doi || ''}
                    onChange={(e) => setFormData({ ...formData, source_doi: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-background border border-border text-xs text-foreground focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">
                  Executable Python Script (In-Silico Sandbox)
                </label>
                <textarea
                  required
                  rows={8}
                  value={formData.executable_code}
                  onChange={(e) => setFormData({ ...formData, executable_code: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border font-mono text-xs text-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-border">
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
                  Register Protocol
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
