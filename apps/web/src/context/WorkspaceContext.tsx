import React, { createContext, useContext, useEffect, useState } from 'react'
import { Project, Workspace } from '../types/workspace'
import { workspaceApi } from '../services/workspaceApi'

interface WorkspaceContextType {
  workspaces: Workspace[]
  currentWorkspace: Workspace | null
  projects: Project[]
  currentProject: Project | null
  isLoading: boolean
  setCurrentWorkspace: (workspace: Workspace) => void
  setCurrentProject: (project: Project) => void
  refreshWorkspaces: () => Promise<void>
  refreshProjects: () => Promise<void>
  createWorkspace: (name: string, description?: string) => Promise<Workspace>
  createProject: (name: string, description?: string) => Promise<Project>
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined)

export const WorkspaceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [currentWorkspace, setCurrentWorkspaceState] = useState<Workspace | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [currentProject, setCurrentProjectState] = useState<Project | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const refreshWorkspaces = async () => {
    try {
      const list = await workspaceApi.getWorkspaces()
      setWorkspaces(list)

      const savedWsId = localStorage.getItem('active_workspace_id')
      const activeWs = list.find(w => w.id === savedWsId) || list[0] || null

      if (activeWs) {
        setCurrentWorkspaceState(activeWs)
        localStorage.setItem('active_workspace_id', activeWs.id)
      }
    } catch (err) {
      console.error('Failed to load workspaces:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const refreshProjects = async () => {
    if (!currentWorkspace) {
      setProjects([])
      setCurrentProjectState(null)
      return
    }

    try {
      const projList = await workspaceApi.getWorkspaceProjects(currentWorkspace.id)
      setProjects(projList)

      const savedProjId = localStorage.getItem(`active_project_id_${currentWorkspace.id}`)
      const activeProj = projList.find(p => p.id === savedProjId) || projList[0] || null

      if (activeProj) {
        setCurrentProjectState(activeProj)
        localStorage.setItem(`active_project_id_${currentWorkspace.id}`, activeProj.id)
      } else {
        setCurrentProjectState(null)
      }
    } catch (err) {
      console.error('Failed to load projects for workspace:', err)
    }
  }

  useEffect(() => {
    refreshWorkspaces()
  }, [])

  useEffect(() => {
    if (currentWorkspace) {
      refreshProjects()
    }
  }, [currentWorkspace?.id])

  const setCurrentWorkspace = (workspace: Workspace) => {
    setCurrentWorkspaceState(workspace)
    localStorage.setItem('active_workspace_id', workspace.id)
  }

  const setCurrentProject = (project: Project) => {
    setCurrentProjectState(project)
    if (currentWorkspace) {
      localStorage.setItem(`active_project_id_${currentWorkspace.id}`, project.id)
    }
  }

  const createWorkspace = async (name: string, description?: string): Promise<Workspace> => {
    const ws = await workspaceApi.createWorkspace({ name, description })
    await refreshWorkspaces()
    setCurrentWorkspace(ws)
    return ws
  }

  const createProject = async (name: string, description?: string): Promise<Project> => {
    if (!currentWorkspace) throw new Error('No active workspace selected')
    const proj = await workspaceApi.createProject(currentWorkspace.id, { name, description })
    await refreshProjects()
    setCurrentProject(proj)
    return proj
  }

  return (
    <WorkspaceContext.Provider
      value={{
        workspaces,
        currentWorkspace,
        projects,
        currentProject,
        isLoading,
        setCurrentWorkspace,
        setCurrentProject,
        refreshWorkspaces,
        refreshProjects,
        createWorkspace,
        createProject,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  )
}

export const useWorkspace = (): WorkspaceContextType => {
  const context = useContext(WorkspaceContext)
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider')
  }
  return context
}
