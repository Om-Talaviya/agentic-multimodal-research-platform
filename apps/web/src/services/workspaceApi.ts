import { api } from './api'
import { Project, ProjectOverview, Workspace, WorkspaceMember } from '../types/workspace'

export const workspaceApi = {
  // Workspaces
  async getWorkspaces(): Promise<Workspace[]> {
    const res = await api.get('/workspaces')
    return res.data.workspaces || []
  },

  async createWorkspace(data: { name: string; description?: string; slug?: string }): Promise<Workspace> {
    const res = await api.post('/workspaces', data)
    return res.data.workspace
  },

  async getWorkspace(id: string): Promise<{ workspace: Workspace; user_role: string; members: WorkspaceMember[] }> {
    const res = await api.get(`/workspaces/${id}`)
    return res.data
  },

  async updateWorkspace(id: string, data: { name?: string; description?: string }): Promise<Workspace> {
    const res = await api.patch(`/workspaces/${id}`, data)
    return res.data.workspace
  },

  async deleteWorkspace(id: string): Promise<boolean> {
    const res = await api.delete(`/workspaces/${id}`)
    return res.data.success
  },

  // Workspace Projects
  async getWorkspaceProjects(workspaceId: string, status?: string): Promise<Project[]> {
    const params = status ? { status_filter: status } : {}
    const res = await api.get(`/workspaces/${workspaceId}/projects`, { params })
    return res.data.projects || []
  },

  async createProject(workspaceId: string, data: { name: string; description?: string; slug?: string }): Promise<Project> {
    const res = await api.post(`/workspaces/${workspaceId}/projects`, data)
    return res.data.project
  },

  // Project Details & Operations
  async getProject(id: string): Promise<Project> {
    const res = await api.get(`/projects/${id}`)
    return res.data.project
  },

  async getProjectOverview(id: string): Promise<ProjectOverview> {
    const res = await api.get(`/projects/${id}/overview`)
    return res.data
  },

  async updateProject(id: string, data: { name?: string; description?: string; status?: string }): Promise<Project> {
    const res = await api.patch(`/projects/${id}`, data)
    return res.data.project
  },

  async deleteProject(id: string): Promise<boolean> {
    const res = await api.delete(`/projects/${id}`)
    return res.data.success
  },
}
