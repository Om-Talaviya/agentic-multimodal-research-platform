/**
 * TypeScript types for Peer Review & Academic Publishing Studio.
 */

export type ManuscriptStatus =
  | 'submitted'
  | 'under_review'
  | 'revisions_requested'
  | 'accepted'
  | 'rejected'
  | 'published';

export type ReviewerPersona = 'methodology_critic' | 'statistical_auditor' | 'domain_specialist';

export type RecommendationType = 'accept' | 'minor_revision' | 'major_revision' | 'reject';

export interface PeerReviewReport {
  id: string;
  reviewer_persona: ReviewerPersona;
  reviewer_title: string;
  originality_score: number;
  methodology_score: number;
  empirical_soundness: number;
  clarity_score: number;
  composite_score: number;
  recommendation: RecommendationType;
  summary_verdict: string;
  strengths: string[];
  weaknesses: string[];
  detailed_critique: string;
  required_revisions: string[];
  created_at: string;
}

export interface PointByPointResponse {
  reviewer_id: string;
  comment_summary: string;
  author_response: string;
  action_taken: string;
}

export interface ManuscriptRevision {
  id: string;
  revision_round: number;
  rebuttal_letter: string;
  diff_summary: string;
  point_by_point_responses: PointByPointResponse[];
  status: string;
  created_at: string;
}

export interface PeerReviewManuscript {
  id: string;
  title: string;
  abstract: string;
  field_of_study: string;
  venue_format: string;
  status: ManuscriptStatus;
  manuscript_content?: string;
  claimed_contributions: string[];
  keywords: string[];
  overall_score: number;
  camera_ready_doi?: string;
  published_latex?: string;
  bibtex_citation?: string;
  created_at: string;
  reports?: PeerReviewReport[];
  revisions?: ManuscriptRevision[];
}

export interface PeerReviewMetrics {
  total_manuscripts: number;
  total_referee_reports: number;
  average_manuscript_score: number;
  status_distribution: Record<string, number>;
  acceptance_rate: number;
}
