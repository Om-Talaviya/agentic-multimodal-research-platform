import { api } from './api'
import {
  CollaborationRole,
  ReportAnnotation,
  WorkspaceActivity,
  WorkspaceInvite,
} from '../types/collaboration'

export const collaborationApi = {
  // --- Workspace Invitations ---
  async createInvite(
    workspaceId: string,
    data: { email: string; role?: CollaborationRole }
  ): Promise<{ invite: WorkspaceInvite; invite_link: string; message: string }> {
    const res = await api.post(`/workspaces/${workspaceId}/invites`, data)
    return res.data
  },

  async listWorkspaceInvites(
    workspaceId: string,
    includeAccepted = false
  ): Promise<WorkspaceInvite[]> {
    const res = await api.get(`/workspaces/${workspaceId}/invites`, {
      params: { include_accepted: includeAccepted },
    })
    return res.data.invites || []
  },

  async getInviteByToken(
    token: string
  ): Promise<{ invite: WorkspaceInvite; workspace_name?: string; is_expired: boolean }> {
    const res = await api.get(`/invites/${token}`)
    return res.data
  },

  async acceptInvite(token: string): Promise<{ message: string; workspace_id: string; member: any }> {
    const res = await api.post(`/invites/${token}/accept`)
    return res.data
  },

  async revokeInvite(inviteId: string): Promise<boolean> {
    const res = await api.delete(`/invites/${inviteId}`)
    return res.data.success
  },

  // --- Report Annotations ---
  async createAnnotation(
    reportId: string,
    data: {
      comment_text: string
      section_index?: number
      selected_text?: string
    }
  ): Promise<ReportAnnotation> {
    const res = await api.post(`/reports/${reportId}/annotations`, data)
    return res.data.annotation
  },

  async listAnnotations(
    reportId: string,
    status?: 'open' | 'resolved'
  ): Promise<ReportAnnotation[]> {
    const params = status ? { status } : {}
    const res = await api.get(`/reports/${reportId}/annotations`, { params })
    return res.data.annotations || []
  },

  async resolveAnnotation(annotationId: string): Promise<ReportAnnotation> {
    const res = await api.patch(`/annotations/${annotationId}/resolve`)
    return res.data.annotation
  },

  async deleteAnnotation(annotationId: string): Promise<boolean> {
    const res = await api.delete(`/annotations/${annotationId}`)
    return res.data.success
  },

  // --- Workspace & Project Activities ---
  async getWorkspaceActivities(
    workspaceId: string,
    limit = 50,
    offset = 0
  ): Promise<WorkspaceActivity[]> {
    const res = await api.get(`/workspaces/${workspaceId}/activities`, {
      params: { limit, offset },
    })
    return res.data.activities || []
  },

  async getProjectActivities(
    projectId: string,
    limit = 50
  ): Promise<WorkspaceActivity[]> {
    const res = await api.get(`/projects/${projectId}/activities`, {
      params: { limit },
    })
    return res.data.activities || []
  },
}
