import React, { useState } from 'react';
import { 
  AlertTriangle, 
  Activity, 
  Sparkles, 
  Layers, 
  Play, 
  CheckCircle2, 
  Heart,
  Skull,
  ShieldCheck,
  Flame,
  FileCode,
  Dna
} from 'lucide-react';

interface StructuralAlertItem {
  alert_name: string;
  smarts_pattern: string;
  toxicophore_category: string;
  severity_level: string;
}

export const ToxicityQSARStudioPage: React.FC = () => {
  const [compoundName, setCompoundName] = useState('Imatinib-Lead-Analog-04');
  const [smiles, setSmiles] = useState('Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CCN(CC5)C');
  const [mw, setMw] = useState(493.6);
  const [logP, setLogP] = useState(3.2);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    screen_id: string;
    ames_status: string;
    ames_prob: number;
    herg_ic50: number;
    herg_risk: string;
    dili_risk: string;
    ld50: number;
    alerts: StructuralAlertItem[];
  } | null>({
    screen_id: 'TOX-QSAR-2026-772',
    ames_status: 'NEGATIVE',
    ames_prob: 8.4,
    herg_ic50: 24.5,
    herg_risk: 'LOW',
    dili_risk: 'LOW',
    ld50: 1350.0,
    alerts: [
      { alert_name: 'Primary Aromatic Amine', smarts_pattern: 'c[NH2]', toxicophore_category: 'Metabolic CYP Bioactivation', severity_level: 'MODERATE' },
    ]
  });

  const handleRunScreen = () => {
    setLoading(true);
    setTimeout(() => {
      setResult({
        screen_id: `TOX-QSAR-${Date.now().toString().slice(-6)}`,
        ames_status: 'NEGATIVE',
        ames_prob: 6.2,
        herg_ic50: 26.2,
        herg_risk: 'LOW',
        dili_risk: 'LOW',
        ld50: 1420.0,
        alerts: []
      });
      setLoading(false);
    }, 500);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                In-Silico Toxicity & QSAR Mutagenicity Matrix Studio
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">
                Ashby Ames mutagenicity, hERG cardiotoxicity, DILI hepatotoxicity, and structural alert toxicophore screening (ADR 071).
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={handleRunScreen}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white px-5 py-2.5 rounded-lg font-medium shadow-lg transition-all"
        >
          <Play className="w-4 h-4 fill-current" />
          {loading ? 'Screening QSAR...' : 'Run Toxicity Matrix'}
        </button>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Compound Name</label>
          <input 
            type="text" 
            value={compoundName} 
            onChange={(e) => setCompoundName(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-red-500"
          />
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl col-span-2">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">SMILES String</label>
          <input 
            type="text" 
            value={smiles} 
            onChange={(e) => setSmiles(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 font-mono text-xs text-red-300 focus:outline-none focus:border-red-500"
          />
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Calculated LogP</label>
          <input 
            type="number" 
            step="0.1" 
            value={logP} 
            onChange={(e) => setLogP(Number(e.target.value))}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-red-500"
          />
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          {/* Telemetry Scorecards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Ames Bacterial Mutagenicity</span>
                <Dna className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2 flex items-center gap-2">
                <span className={result.ames_status === 'NEGATIVE' ? 'text-emerald-400' : 'text-rose-400'}>
                  {result.ames_status}
                </span>
                <span className="text-xs font-mono text-slate-400">({result.ames_prob.toFixed(1)}%)</span>
              </div>
              <p className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Non-Mutagenic Clearance
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>hERG Cardiotoxicity (IC50)</span>
                <Heart className="w-4 h-4 text-rose-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.herg_ic50.toFixed(1)} µM
              </div>
              <p className="text-xs text-emerald-400 mt-1 font-medium">
                Low QT-Prolongation Risk (IC50 &gt; 10µM)
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>DILI Hepatotoxicity Risk</span>
                <Flame className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-bold text-emerald-400 mt-2">
                {result.dili_risk} RISK
              </div>
              <p className="text-xs text-slate-400 mt-1">Liver Enzyme Elevation Window</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Oral Rat LD50</span>
                <Skull className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.ld50.toFixed(0)} mg/kg
              </div>
              <p className="text-xs text-indigo-400 mt-1">GHS Category 4 (Low Acute Tox)</p>
            </div>
          </div>

          {/* Structural Alerts Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                Detected Toxicophores & Ashby Structural Alerts
              </h2>
              <span className="text-xs px-2.5 py-1 bg-slate-800 text-slate-300 rounded-full border border-slate-700">
                {result.alerts.length} Flagged Motifs
              </span>
            </div>
            {result.alerts.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-sm">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                No mutagenic, electrophilic, or reactive toxicophores detected in chemical structure.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-slate-800/60 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Alert Name</th>
                      <th className="px-4 py-3">SMARTS Substructure</th>
                      <th className="px-4 py-3">Toxicophore Mechanism</th>
                      <th className="px-4 py-3">Severity</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {result.alerts.map((a, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="px-4 py-3 font-semibold text-white">{a.alert_name}</td>
                        <td className="px-4 py-3 font-mono text-xs text-red-300 font-semibold">{a.smarts_pattern}</td>
                        <td className="px-4 py-3 text-slate-300">{a.toxicophore_category}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-0.5 text-xs rounded font-medium ${
                            a.severity_level === 'HIGH'
                              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                              : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          }`}>
                            {a.severity_level}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
export default ToxicityQSARStudioPage;
