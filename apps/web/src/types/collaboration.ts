export type CollaborationRole = 'admin' | 'researcher' | 'analyst' | 'reviewer' | 'viewer';

export interface WorkspaceInvite {
  id: string;
  workspace_id: string;
  email: string;
  role: CollaborationRole;
  token: string;
  invited_by?: string | null;
  is_accepted: boolean;
  expires_at?: string | null;
  created_at: string;
}

export interface ReportAnnotation {
  id: string;
  report_id: string;
  user_id: string;
  author_username?: string | null;
  section_index?: number | null;
  selected_text?: string | null;
  comment_text: string;
  status: 'open' | 'resolved';
  resolved_by?: string | null;
  resolved_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceActivity {
  id: string;
  workspace_id: string;
  project_id?: string | null;
  user_id?: string | null;
  username?: string;
  action: string;
  entity_id?: string | null;
  details: Record<string, any>;
  created_at: string;
}
