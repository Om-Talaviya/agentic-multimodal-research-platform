import { MilestoneV19StudioPage } from './pages/MilestoneV19StudioPage';
import { smFRETKineticsStudioPage } from './pages/smFRETKineticsStudioPage';
import { CRISPREpigeneticStudioPage } from './pages/CRISPREpigeneticStudioPage';
import { TCellEngagerStudioPage } from './pages/TCellEngagerStudioPage';
import { CFPSTXTLStudioPage } from './pages/CFPSTXTLStudioPage';
import { PROTACKineticsStudioPage } from './pages/PROTACKineticsStudioPage';
import { SpatialProteomicsCODEXStudioPage } from './pages/SpatialProteomicsCODEXStudioPage';
import { MilestoneV18StudioPage } from './pages/MilestoneV18StudioPage';
import { mRNACodonStudioPage } from './pages/mRNACodonStudioPage';
import { ChromatinLoopStudioPage } from './pages/ChromatinLoopStudioPage';
import { CapsidAssemblyStudioPage } from './pages/CapsidAssemblyStudioPage';
import { SpatialFluxStudioPage } from './pages/SpatialFluxStudioPage';
import { DNAOrigamiStudioPage } from './pages/DNAOrigamiStudioPage';
import { GlycanMicroarrayStudioPage } from './pages/GlycanMicroarrayStudioPage';
import { OrganoidMorphometryStudioPage } from './pages/OrganoidMorphometryStudioPage';
import { SpatialRNAVelocityStudioPage } from './pages/SpatialRNAVelocityStudioPage'
import { TCRpMHCStudioPage } from './pages/TCRpMHCStudioPage'
import { MitochondrialBioenergeticsStudioPage } from './pages/MitochondrialBioenergeticsStudioPage'
import { AptamerEvolutionStudioPage } from './pages/AptamerEvolutionStudioPage'
import { CYP450MetabolismStudioPage } from './pages/CYP450MetabolismStudioPage'
import { ClinicalePROStudioPage } from './pages/ClinicalePROStudioPage'
import { MembranePermeabilityStudioPage } from './pages/MembranePermeabilityStudioPage'
import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { ProjectsPage } from './pages/ProjectsPage'
import { NewResearch } from './pages/NewResearch'
import { ResearchDetail } from './pages/ResearchDetail'
import { Settings } from './pages/Settings'
import { MemoryPage } from './pages/MemoryPage'
import { KnowledgeGraphPage } from './pages/KnowledgeGraphPage'
import { ModelEvaluationPage } from './pages/ModelEvaluationPage'
import { AgentEvaluationPage } from './pages/AgentEvaluationPage'
import { EnterpriseSecurityPage } from './pages/EnterpriseSecurityPage'
import { ProductionInfrastructurePage } from './pages/ProductionInfrastructurePage'
import { DeveloperPlatformPage } from './pages/DeveloperPlatformPage'
import { ResearchAutomationPage } from './pages/ResearchAutomationPage'
import { DebateArenaPage } from './pages/DebateArenaPage'
import { LiteratureReviewPage } from './pages/LiteratureReviewPage'
import { ReproducibilityPage } from './pages/ReproducibilityPage'
import { PresentationStudioPage } from './pages/PresentationStudioPage'
import { PeerReviewPage } from './pages/PeerReviewPage'
import { ResearchCanvasPage } from './pages/ResearchCanvasPage'
import { DatasetSynthesisPage } from './pages/DatasetSynthesisPage'
import { PatentLandscapePage } from './pages/PatentLandscapePage'
import { GrantProposalStudioPage } from './pages/GrantProposalStudioPage'
import { ClinicalTrialsPage } from './pages/ClinicalTrialsPage'
import { LabAutomationPage } from './pages/LabAutomationPage'
import { MolecularStructurePage } from './pages/MolecularStructurePage'
import { MolecularDynamicsPage } from './pages/MolecularDynamicsPage'
import { CRISPRStudioPage } from './pages/CRISPRStudioPage'
import { SingleCellStudioPage } from './pages/SingleCellStudioPage'
import { SpatialTranscriptomicsPage } from './pages/SpatialTranscriptomicsPage'
import { GenerativeChemistryPage } from './pages/GenerativeChemistryPage'
import { SuperGraphStudioPage } from './pages/SuperGraphStudioPage'
import { DrugSynergyStudioPage } from './pages/DrugSynergyStudioPage'
import { ClinicalTrialStudioPage } from './pages/ClinicalTrialStudioPage'
import { CryoEMStudioPage } from './pages/CryoEMStudioPage'
import { PathwaySimulatorPage } from './pages/PathwaySimulatorPage'
import { PharmacovigilanceStudioPage } from './pages/PharmacovigilanceStudioPage'
import { AIScientistStudioPage } from './pages/AIScientistStudioPage'
import { RagasStudioPage } from './pages/RagasStudioPage'
import { LakehouseStudioPage } from './pages/LakehouseStudioPage'
import { ELNStudioPage } from './pages/ELNStudioPage'
import { VHTSStudioPage } from './pages/VHTSStudioPage'
import { ImmunologyStudioPage } from './pages/ImmunologyStudioPage'
import { EpigenomicsStudioPage } from './pages/EpigenomicsStudioPage'
import { SpatialMetabolomicsStudioPage } from './pages/SpatialMetabolomicsStudioPage'
import { PPIInteractomeStudioPage } from './pages/PPIInteractomeStudioPage'
import { ADCDesignStudioPage } from './pages/ADCDesignStudioPage'
import { NanomedicinePBPKStudioPage } from './pages/NanomedicinePBPKStudioPage'
import { RareDiseaseHPOStudioPage } from './pages/RareDiseaseHPOStudioPage'
import { BioprocessDigitalTwinStudioPage } from './pages/BioprocessDigitalTwinStudioPage'
import { ClinicalLogisticsStudioPage } from './pages/ClinicalLogisticsStudioPage'
import { PeerReviewStudioPage } from './pages/PeerReviewStudioPage'
import { SyntheticBiologyStudioPage } from './pages/SyntheticBiologyStudioPage'
import { CARTStudioPage } from './pages/CARTStudioPage'
import { CancerVaccineStudioPage } from './pages/CancerVaccineStudioPage'
import { FlowCytometryStudioPage } from './pages/FlowCytometryStudioPage'
import { BiotherapeuticStabilityStudioPage } from './pages/BiotherapeuticStabilityStudioPage'
import { SyntheticLethalityStudioPage } from './pages/SyntheticLethalityStudioPage'
import { ToxicityQSARStudioPage } from './pages/ToxicityQSARStudioPage'
import { GeneCircuitBurdenStudioPage } from './pages/GeneCircuitBurdenStudioPage'
import { ClinicalSiteSelectionStudioPage } from './pages/ClinicalSiteSelectionStudioPage'
import { VariantPathogenicityStudioPage } from './pages/VariantPathogenicityStudioPage'
import { LiquidBiopsyStudioPage } from './pages/LiquidBiopsyStudioPage'
import { PVSignalMiningStudioPage } from './pages/PVSignalMiningStudioPage'
import { CryoETStudioPage } from './pages/CryoETStudioPage'
import { ChemogenomicsStudioPage } from './pages/ChemogenomicsStudioPage'
import { SmFRETStudioPage } from './pages/SmFRETStudioPage'
import { BiomarkerDiscoveryStudioPage } from './pages/BiomarkerDiscoveryStudioPage'
import { LNPFormulationStudioPage } from './pages/LNPFormulationStudioPage'
import { AMRSurveillanceStudioPage } from './pages/AMRSurveillanceStudioPage'
import { ImmuneRepertoireStudioPage } from './pages/ImmuneRepertoireStudioPage'
import { HDXMSStudioPage } from './pages/HDXMSStudioPage'
import { SpatialLipidomicsStudioPage } from './pages/SpatialLipidomicsStudioPage'
import { CrypticPocketsStudioPage } from './pages/CrypticPocketsStudioPage'
import { OrganChipStudioPage } from './pages/OrganChipStudioPage'
import { CyTOFStudioPage } from './pages/CyTOFStudioPage'
import { SurvivalPrognosisStudioPage } from './pages/SurvivalPrognosisStudioPage'
import { T2TAssemblyStudioPage } from './pages/T2TAssemblyStudioPage'
import { AntibodyMaturationStudioPage } from './pages/AntibodyMaturationStudioPage'
import { CITEseqStudioPage } from './pages/CITEseqStudioPage'
import { PanDDACrystallographyStudioPage } from './pages/PanDDACrystallographyStudioPage'
import { AdaptiveResistanceStudioPage } from './pages/AdaptiveResistanceStudioPage'
import { BiocomputerLogicStudioPage } from './pages/BiocomputerLogicStudioPage'
import { ViralPhylodynamicsStudioPage } from './pages/ViralPhylodynamicsStudioPage'
import { CryoETClusteringStudioPage } from './pages/CryoETClusteringStudioPage'
import { RiboswitchKineticsStudioPage } from './pages/RiboswitchKineticsStudioPage'
import { HLALOHResistanceStudioPage } from './pages/HLALOHResistanceStudioPage'
import { HistoneAcetylationStudioPage } from './pages/HistoneAcetylationStudioPage'
import { CARMacrophageStudioPage } from './pages/CARMacrophageStudioPage'
import { LNPEncapsulationStudioPage } from './pages/LNPEncapsulationStudioPage'
import { SpatialGNNStudioPage } from './pages/SpatialGNNStudioPage'
import { SpatialMicrodissectionStudioPage } from './pages/SpatialMicrodissectionStudioPage'
import { RNAThermodynamicsStudioPage } from './pages/RNAThermodynamicsStudioPage'
import { CRISPRBaseEditorStudioPage } from './pages/CRISPRBaseEditorStudioPage'
import { PDCConjugateStudioPage } from './pages/PDCConjugateStudioPage'
import { MicroEDStructuralStudioPage } from './pages/MicroEDStructuralStudioPage'
import { SingleCellPerturbationStudioPage } from './pages/SingleCellPerturbationStudioPage'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { WorkspaceProvider } from './context/WorkspaceContext'
import { Loader2 } from 'lucide-react'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [refreshInProgress, setRefreshInProgress] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const refreshToken = localStorage.getItem('refresh_token')

    if (token) {
      import('./services/api').then(({ api }) => {
        api.get('/auth/me').then(() => {
          setIsAuthenticated(true)
        }).catch(async (_err: unknown) => {
          if (!refreshInProgress && refreshToken) {
            setRefreshInProgress(true)
            try {
              const resp = await api.post('/auth/token/refresh', {
                refresh_token: refreshToken,
              })
              const { access_token, refresh_token: newRefreshToken } = resp.data
              localStorage.setItem('token', access_token)
              localStorage.setItem('refresh_token', newRefreshToken)
              setIsAuthenticated(true)
            } catch (refreshErr) {
              localStorage.removeItem('token')
              localStorage.removeItem('refresh_token')
              setIsAuthenticated(false)
            } finally {
              setRefreshInProgress(false)
            }
          } else {
            localStorage.removeItem('token')
            localStorage.removeItem('refresh_token')
            setIsAuthenticated(false)
          }
        }).finally(() => {
          setIsLoading(false)
        })
      })
    } else {
      setIsLoading(false)
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    setIsAuthenticated(false)
  }

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
        <Loader2 className="loading-spinner" size={32} />
      </div>
    )
  }

  const authenticatedRoutes = (
    <WorkspaceProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="research/new" element={<NewResearch />} />
          <Route path="research/:id" element={<ResearchDetail />} />
          <Route path="memory" element={<MemoryPage />} />
          <Route path="graph" element={<KnowledgeGraphPage />} />
          <Route path="evaluations" element={<ModelEvaluationPage />} />
          <Route path="agents/evaluations" element={<AgentEvaluationPage />} />
          <Route path="security" element={<EnterpriseSecurityPage />} />
          <Route path="infrastructure" element={<ProductionInfrastructurePage />} />
          <Route path="developer" element={<DeveloperPlatformPage />} />
          <Route path="automation" element={<ResearchAutomationPage />} />
          <Route path="debates" element={<DebateArenaPage />} />
          <Route path="literature" element={<LiteratureReviewPage />} />
          <Route path="reproducibility" element={<ReproducibilityPage />} />
          <Route path="presentations" element={<PresentationStudioPage />} />
          <Route path="publishing" element={<PeerReviewPage />} />
          <Route path="canvas" element={<ResearchCanvasPage />} />
          <Route path="datasets" element={<DatasetSynthesisPage />} />
          <Route path="patents" element={<PatentLandscapePage />} />
          <Route path="grants" element={<GrantProposalStudioPage />} />
          <Route path="clinical" element={<ClinicalTrialsPage />} />
          <Route path="lab" element={<LabAutomationPage />} />
          <Route path="molecular" element={<MolecularStructurePage />} />
          <Route path="dynamics" element={<MolecularDynamicsPage />} />
          <Route path="crispr" element={<CRISPRStudioPage />} />
          <Route path="single-cell" element={<SingleCellStudioPage />} />
          <Route path="spatial" element={<SpatialTranscriptomicsPage />} />
          <Route path="chemistry" element={<GenerativeChemistryPage />} />
          <Route path="supergraph" element={<SuperGraphStudioPage />} />
          <Route path="synergy" element={<DrugSynergyStudioPage />} />
          <Route path="clinical-trials" element={<ClinicalTrialStudioPage />} />
          <Route path="cryoem" element={<CryoEMStudioPage />} />
          <Route path="pathways" element={<PathwaySimulatorPage />} />
          <Route path="pharmacovigilance" element={<PharmacovigilanceStudioPage />} />
          <Route path="ai-scientist" element={<AIScientistStudioPage />} />
          <Route path="ragas-eval" element={<RagasStudioPage />} />
          <Route path="lakehouse" element={<LakehouseStudioPage />} />
          <Route path="eln" element={<ELNStudioPage />} />
          <Route path="vhts" element={<VHTSStudioPage />} />
          <Route path="immunology" element={<ImmunologyStudioPage />} />
          <Route path="epigenomics" element={<EpigenomicsStudioPage />} />
          <Route path="spatial-metabolomics" element={<SpatialMetabolomicsStudioPage />} />
          <Route path="ppi-interactome" element={<PPIInteractomeStudioPage />} />
          <Route path="adc-design" element={<ADCDesignStudioPage />} />
          <Route path="pbpk-nanomedicine" element={<NanomedicinePBPKStudioPage />} />
          <Route path="rare-disease" element={<RareDiseaseHPOStudioPage />} />
          <Route path="bioprocess" element={<BioprocessDigitalTwinStudioPage />} />
          <Route path="clinical-logistics" element={<ClinicalLogisticsStudioPage />} />
          <Route path="peer-review" element={<PeerReviewStudioPage />} />
          <Route path="synthetic-biology" element={<SyntheticBiologyStudioPage />} />
          <Route path="cart" element={<CARTStudioPage />} />
          <Route path="cancer-vaccines" element={<CancerVaccineStudioPage />} />
          <Route path="flow-cytometry" element={<FlowCytometryStudioPage />} />
          <Route path="biotherapeutic-stability" element={<BiotherapeuticStabilityStudioPage />} />
          <Route path="synthetic-lethality" element={<SyntheticLethalityStudioPage />} />
          <Route path="toxicity-qsar" element={<ToxicityQSARStudioPage />} />
          <Route path="gene-circuits" element={<GeneCircuitBurdenStudioPage />} />
          <Route path="clinical-site-selection" element={<ClinicalSiteSelectionStudioPage />} />
          <Route path="variant-pathogenicity" element={<VariantPathogenicityStudioPage />} />
          <Route path="liquid-biopsy" element={<LiquidBiopsyStudioPage />} />
          <Route path="pv-sentinel" element={<PVSignalMiningStudioPage />} />
          <Route path="cryoet" element={<CryoETStudioPage />} />
          <Route path="chemogenomics" element={<ChemogenomicsStudioPage />} />
          <Route path="smfret" element={<SmFRETStudioPage />} />
          <Route path="biomarkers" element={<BiomarkerDiscoveryStudioPage />} />
          <Route path="lnp-formulation" element={<LNPFormulationStudioPage />} />
          <Route path="amr-surveillance" element={<AMRSurveillanceStudioPage />} />
          <Route path="immune-repertoire" element={<ImmuneRepertoireStudioPage />} />
          <Route path="hdx-ms" element={<HDXMSStudioPage />} />
          <Route path="spatial-lipidomics" element={<SpatialLipidomicsStudioPage />} />
          <Route path="cryptic-pockets" element={<CrypticPocketsStudioPage />} />
          <Route path="organ-chip" element={<OrganChipStudioPage />} />
          <Route path="cytof" element={<CyTOFStudioPage />} />
          <Route path="survival-prognosis" element={<SurvivalPrognosisStudioPage />} />
          <Route path="t2t-assembly" element={<T2TAssemblyStudioPage />} />
          <Route path="antibody-maturation" element={<AntibodyMaturationStudioPage />} />
          <Route path="citeseq" element={<CITEseqStudioPage />} />
          <Route path="pandda-crystallography" element={<PanDDACrystallographyStudioPage />} />
          <Route path="adaptive-resistance" element={<AdaptiveResistanceStudioPage />} />
          <Route path="biocomputer-logic" element={<BiocomputerLogicStudioPage />} />
          <Route path="viral-phylodynamics" element={<ViralPhylodynamicsStudioPage />} />
          <Route path="cryoet-clustering" element={<CryoETClusteringStudioPage />} />
          <Route path="riboswitch-kinetics" element={<RiboswitchKineticsStudioPage />} />
          <Route path="hla-loh" element={<HLALOHResistanceStudioPage />} />
          <Route path="histone-acetylation" element={<HistoneAcetylationStudioPage />} />
          <Route path="car-macrophage" element={<CARMacrophageStudioPage />} />
          <Route path="lnp-encapsulation" element={<LNPEncapsulationStudioPage />} />
          <Route path="spatial-gnn" element={<SpatialGNNStudioPage />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        <Route path="/login" element={<Navigate to="/dashboard" replace />} />
        <Route path="/register" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/logout"
          element={
            <>
              {handleLogout()}
              <Navigate to="/login" replace />
            </>
          }
        />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/organoid-morphometry" element={<OrganoidMorphometryStudioPage />} />
                      <Route path="/glycan-microarray" element={<GlycanMicroarrayStudioPage />} />
                      <Route path="/dna-origami" element={<DNAOrigamiStudioPage />} />
                      <Route path="/spatial-flux" element={<SpatialFluxStudioPage />} />
                      <Route path="/capsid-assembly" element={<CapsidAssemblyStudioPage />} />
                      <Route path="/chromatin-loop" element={<ChromatinLoopStudioPage />} />
                      <Route path="/mrna-codon" element={<mRNACodonStudioPage />} />
                      <Route path="/milestone-v1-8" element={<MilestoneV18StudioPage />} />
                      <Route path="/spatial-proteomics-codex" element={<SpatialProteomicsCODEXStudioPage />} />
                      <Route path="/protac-kinetics" element={<PROTACKineticsStudioPage />} />
                      <Route path="/cfps-txtl" element={<CFPSTXTLStudioPage />} />
                      <Route path="/tcell-engager" element={<TCellEngagerStudioPage />} />
                      <Route path="/crispr-epigenetic" element={<CRISPREpigeneticStudioPage />} />
                      <Route path="/smfret-kinetics" element={<smFRETKineticsStudioPage />} />
                      <Route path="/milestone-v1-9" element={<MilestoneV19StudioPage />} />
                      <Route path="/spatial-microdissection" element={<SpatialMicrodissectionStudioPage />} />
                      <Route path="/rna-thermodynamics" element={<RNAThermodynamicsStudioPage />} />
                      <Route path="/crispr-base-editor" element={<CRISPRBaseEditorStudioPage />} />
                      <Route path="/pdc-conjugate" element={<PDCConjugateStudioPage />} />
                      <Route path="/microed-structural" element={<MicroEDStructuralStudioPage />} />
                      <Route path="/single-cell-perturbation" element={<SingleCellPerturbationStudioPage />} />
          </Routes>
    </WorkspaceProvider>
  )

  const unauthenticatedRoutes = (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
                <Route path="/organoid-morphometry" element={<OrganoidMorphometryStudioPage />} />
                      <Route path="/glycan-microarray" element={<GlycanMicroarrayStudioPage />} />
                      <Route path="/dna-origami" element={<DNAOrigamiStudioPage />} />
                      <Route path="/spatial-flux" element={<SpatialFluxStudioPage />} />
                      <Route path="/capsid-assembly" element={<CapsidAssemblyStudioPage />} />
                      <Route path="/chromatin-loop" element={<ChromatinLoopStudioPage />} />
                      <Route path="/mrna-codon" element={<mRNACodonStudioPage />} />
                      <Route path="/milestone-v1-8" element={<MilestoneV18StudioPage />} />
                      <Route path="/spatial-proteomics-codex" element={<SpatialProteomicsCODEXStudioPage />} />
                      <Route path="/protac-kinetics" element={<PROTACKineticsStudioPage />} />
                      <Route path="/cfps-txtl" element={<CFPSTXTLStudioPage />} />
                      <Route path="/tcell-engager" element={<TCellEngagerStudioPage />} />
                      <Route path="/crispr-epigenetic" element={<CRISPREpigeneticStudioPage />} />
                      <Route path="/smfret-kinetics" element={<smFRETKineticsStudioPage />} />
                      <Route path="/milestone-v1-9" element={<MilestoneV19StudioPage />} />
          </Routes>
  )

  return isAuthenticated ? authenticatedRoutes : unauthenticatedRoutes
}

export default App
