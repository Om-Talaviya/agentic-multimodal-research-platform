/**
 * Developer Platform & API Key TypeScript Types (Phase 25)
 */

export interface DeveloperApiKey {
  id: string;
  user_id: string;
  workspace_id: string | null;
  name: string;
  key_prefix: string;
  masked_key: string;
  scopes: string[];
  rate_limit_tier: 'free' | 'pro' | 'enterprise';
  rate_limit_rpm: number;
  is_active: boolean;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateApiKeyPayload {
  name: string;
  scopes: string[];
  rate_limit_tier: 'free' | 'pro' | 'enterprise';
  workspace_id?: string | null;
  expires_in_days?: number | null;
}

export interface ApiKeyCreatedResponse {
  message: string;
  api_key: DeveloperApiKey;
  secret_key: string;
}

export interface DeveloperApiUsage {
  key_id: string;
  name: string;
  tier: string;
  rate_limit_rpm: number;
  rate_limit_remaining: number;
  scopes: string[];
  last_used_at: string | null;
}
