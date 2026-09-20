import React, { useState, useEffect } from 'react';
import { Grid, Sparkles, MapPin, Activity, Layers, Plus, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface LipidSpecies {
  id: string;
  mz_ratio: number;
  lipid_species: string;
  lipid_class: string;
  adduct_type: string;
  structural_formula?: string;
  mean_intensity: number;
}

interface SpatialSpot {
  lipid_species_id: string;
  x_coord: number;
  y_coord: number;
  normalized_intensity: number;
  region_annotation: string;
}

interface SpatialLipidomicsDataset {
  id: string;
  sample_name: string;
  tissue_type: string;
  matrix_type: string;
  laser_spatial_resolution_um: number;
  total_spots: number;
  detected_lipid_classes: number;
  status: string;
  lipid_species?: LipidSpecies[];
  spatial_spots?: SpatialSpot[];
}

export const SpatialLipidomicsStudioPage: React.FC = () => {
  const [datasets, setDatasets] = useState<SpatialLipidomicsDataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<SpatialLipidomicsDataset | null>(null);
  const [selectedLipidId, setSelectedLipidId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sampleName, setSampleName] = useState('Coronal-Cortex-Lipid-Map');

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/v1/spatial-lipidomics/datasets');
      setDatasets(res.data);
      if (res.data.length > 0) {
        fetchDatasetDetail(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load spatial lipidomics datasets', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDatasetDetail = async (id: string) => {
    try {
      const res = await axios.get(`/api/v1/spatial-lipidomics/datasets/${id}`);
      setSelectedDataset(res.data);
      if (res.data.lipid_species && res.data.lipid_species.length > 0) {
        setSelectedLipidId(res.data.lipid_species[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch dataset details', err);
    }
  };

  const handleProcessNew = async () => {
    setIsProcessing(true);
    try {
      const payload = {
        sample_name: sampleName,
        tissue_type: 'Mouse Brain Sagittal Section',
        matrix_type: 'DHB',
        grid_dim: 8,
        custom_mz_list: [760.585, 788.616, 734.569, 703.575, 566.514]
      };
      const res = await axios.post('/api/v1/spatial-lipidomics/process', payload);
      setDatasets([res.data, ...datasets]);
      setSelectedDataset(res.data);
      if (res.data.lipid_species && res.data.lipid_species.length > 0) {
        setSelectedLipidId(res.data.lipid_species[0].id);
      }
    } catch (err) {
      console.error('Failed to process spatial lipidomics', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const activeSpots = selectedDataset?.spatial_spots?.filter(
    (sp) => sp.lipid_species_id === selectedLipidId
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-400">
              <Grid className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Autonomous Spatial Lipidomics & Imaging MS Studio</h1>
              <p className="text-sm text-slate-400">
                Phase 106 • LIPID MAPS Accurate Mass Identification, False-Color Spatial Ion Maps & Tissue Remodeling
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleProcessNew}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white font-medium rounded-lg transition disabled:opacity-50"
          >
            {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Acquire Spatial Map
          </button>
        </div>
      </div>

      {/* KPI Stats */}
      {selectedDataset && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Total Laser Spots</div>
            <div className="text-2xl font-bold text-white mt-1">{selectedDataset.total_spots}</div>
            <div className="text-xs text-slate-500 mt-1">Grid Resolution: {selectedDataset.laser_spatial_resolution_um} µm</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Lipid Classes</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{selectedDataset.detected_lipid_classes}</div>
            <div className="text-xs text-slate-500 mt-1">PC, PE, SM, PI, Ceramide</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">MALDI Matrix</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{selectedDataset.matrix_type}</div>
            <div className="text-xs text-slate-500 mt-1">Sublimated Matrix Substrate</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Identified Species</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{selectedDataset.lipid_species?.length || 0}</div>
            <div className="text-xs text-slate-500 mt-1">High-Confidence m/z Matches</div>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Identified Lipid Species Selection */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-400" />
            Identified Lipid Ion Channels
          </h2>
          {loading ? (
            <div className="text-center py-8 text-slate-400">Loading datasets...</div>
          ) : selectedDataset?.lipid_species && selectedDataset.lipid_species.length > 0 ? (
            <div className="space-y-3">
              {selectedDataset.lipid_species.map((lip) => (
                <div
                  key={lip.id}
                  onClick={() => setSelectedLipidId(lip.id)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition ${
                    selectedLipidId === lip.id
                      ? 'bg-amber-950/40 border-amber-500/60'
                      : 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-800'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div className="font-semibold text-white text-sm">{lip.lipid_species}</div>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-amber-300 font-mono">
                      m/z {lip.mz_ratio.toFixed(3)}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-400 mt-2">
                    <span>{lip.lipid_class}</span>
                    <span className="font-mono">{lip.adduct_type}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">No lipid channels found. Acquire data above.</div>
          )}
        </div>

        {/* Right: False-Color 2D Spatial Ion Map Canvas */}
        <div className="lg:col-span-2 space-y-6">
          {selectedDataset ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-amber-400" />
                  2D Spatial Ion Intensity Heatmap
                </h2>
                <div className="text-xs text-slate-400 font-mono">
                  {selectedDataset.lipid_species?.find((l) => l.id === selectedLipidId)?.lipid_species}
                </div>
              </div>

              {/* 2D Spot Grid */}
              <div className="bg-slate-950 border border-slate-800 p-6 rounded-xl flex flex-col items-center justify-center">
                <div className="grid grid-cols-8 gap-1.5 max-w-sm w-full">
                  {activeSpots.length > 0 ? (
                    activeSpots.map((sp, idx) => {
                      const alpha = Math.max(0.1, sp.normalized_intensity / 100);
                      return (
                        <div
                          key={idx}
                          title={`(${sp.x_coord}, ${sp.y_coord}) - Intensity: ${sp.normalized_intensity} (${sp.region_annotation})`}
                          className="w-full aspect-square rounded flex items-center justify-center text-[9px] font-mono text-white/70 transition hover:scale-110 cursor-pointer"
                          style={{
                            backgroundColor: `rgba(245, 158, 11, ${alpha})`,
                            border: '1px solid rgba(245, 158, 11, 0.4)'
                          }}
                        >
                          {Math.round(sp.normalized_intensity)}
                        </div>
                      );
                    })
                  ) : (
                    <div className="text-sm text-slate-500 col-span-8 text-center py-8">
                      Select a lipid species to render the 2D spatial heatmap.
                    </div>
                  )}
                </div>

                {/* Legend */}
                <div className="flex items-center gap-4 mt-6 text-xs text-slate-400">
                  <span>Low (5)</span>
                  <div className="w-32 h-2.5 rounded-full bg-gradient-to-r from-amber-950 via-amber-600 to-amber-300" />
                  <span>High (100)</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400">
              Select or acquire a spatial lipidomics dataset to inspect false-color ion intensity maps.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
