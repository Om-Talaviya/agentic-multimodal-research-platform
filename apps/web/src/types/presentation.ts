export interface PresentationSlide {
  id: string;
  slide_number: number;
  layout_type: 'title' | 'bullet_points' | 'two_column' | 'chart_comparison' | 'callout_quote';
  headline: string;
  bullet_points: string[];
  speaker_notes?: string;
  visual_metadata?: Record<string, any>;
}

export interface SynthesisPresentation {
  id: string;
  title: string;
  subtitle?: string;
  target_audience: 'executive' | 'scientific' | 'technical' | 'general';
  theme: string;
  estimated_duration_min: number;
  total_slides: number;
  slides?: PresentationSlide[];
  created_at: string;
}

export interface DialogueTurn {
  turn_index: number;
  speaker: string;
  text: string;
  audio_cue?: string;
  timestamp_start_sec: number;
  timestamp_end_sec: number;
  duration_sec: number;
}

export interface PodcastBriefing {
  id: string;
  title: string;
  episode_topic: string;
  host_name: string;
  expert_name: string;
  total_duration_sec: number;
  total_dialogue_turns: number;
  dialogue_transcript_json: DialogueTurn[];
  audio_url?: string;
  status: string;
  created_at: string;
}

export interface PresentationMetrics {
  total_presentations: number;
  total_slides: number;
  average_slides_per_deck: number;
  total_podcasts: number;
  total_audio_minutes: number;
}

export interface GeneratePresentationPayload {
  title: string;
  research_content: string;
  subtitle?: string;
  target_audience: 'executive' | 'scientific' | 'technical' | 'general';
  theme?: string;
  workspace_id?: string;
  project_id?: string;
}

export interface GeneratePodcastPayload {
  topic: string;
  key_findings: string;
  host_name?: string;
  expert_name?: string;
  workspace_id?: string;
  project_id?: string;
}
