export type DatasetFormat = 'alpaca_sft' | 'sharegpt' | 'dpo_preference' | 'rl_trajectory' | 'cot_reasoning';
export type EvolutionStrategy = 'direct_synthesis' | 'in_depth_expansion' | 'in_breadth_variation' | 'constraint_hardening' | 'adversarial_redteaming' | 'cot_decomposition';
export type CurationVerdict = 'accepted' | 'rejected' | 'edited';

export interface InstructionSample {
  id: string;
  sample_index: number;
  instruction: string;
  input_context?: string;
  chosen_response: string;
  rejected_response?: string;
  cot_reasoning_trace?: string;
  evolution_strategy: EvolutionStrategy;
  quality_score: number;
  toxicity_score: number;
  hallucination_risk: number;
  curation_verdict: CurationVerdict;
}

export interface AlignmentExport {
  id: string;
  export_format: string;
  sample_count: number;
  file_size_bytes: number;
  exported_at: string;
}

export interface SyntheticDataset {
  id: string;
  name: string;
  description?: string;
  dataset_format: DatasetFormat;
  domain_field: string;
  target_model_family: string;
  total_samples: number;
  quality_filter_threshold?: number;
  status: 'draft' | 'synthesizing' | 'curated' | 'exported' | 'archived';
  created_at: string;
  samples?: InstructionSample[];
  exports?: AlignmentExport[];
}

export interface DatasetSynthesisMetrics {
  total_synthetic_datasets: number;
  total_instruction_samples: number;
  total_alignment_exports: number;
  average_quality_score: number;
  format_distribution: Record<string, number>;
  evolution_strategy_distribution: Record<string, number>;
}
