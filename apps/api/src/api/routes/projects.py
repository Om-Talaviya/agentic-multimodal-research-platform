"""REST API routes for Project management and aggregate metric overviews."""

import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api.dependencies import (
    get_current_user,
    get_project_repository,
    get_workspace_repository,
)
from database.repositories.project_repo import ProjectRepository
from database.repositories.workspace_repo import WorkspaceRepository
from shared.auth import User

router = APIRouter(prefix="/projects", tags=["projects"])


# --- Schemas ---

class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|archived)$")
    settings: Optional[Dict[str, Any]] = None


# --- Endpoints ---

@router.get("/{project_id}")
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    proj_repo: ProjectRepository = Depends(get_project_repository),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Get project details."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    project = await proj_repo.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check workspace membership
    membership = await ws_repo.get_user_membership(project.workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(project.workspace_id)

    if not workspace or (workspace.owner_id != user_uuid and not membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")

    return {
        "project": project.to_dict(),
    }


@router.patch("/{project_id}")
async def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    proj_repo: ProjectRepository = Depends(get_project_repository),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Update project details."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    project = await proj_repo.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    membership = await ws_repo.get_user_membership(project.workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(project.workspace_id)

    if not workspace or (workspace.owner_id != user_uuid and (not membership or membership.role == "viewer")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied to update project")

    updated = await proj_repo.update_project(
        project_id=project_id,
        name=body.name,
        description=body.description,
        status=body.status,
        settings=body.settings,
    )
    return {"success": True, "project": updated.to_dict()}


@router.delete("/{project_id}")
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    proj_repo: ProjectRepository = Depends(get_project_repository),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Delete a project."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    project = await proj_repo.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    membership = await ws_repo.get_user_membership(project.workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(project.workspace_id)

    if not workspace or (workspace.owner_id != user_uuid and (not membership or membership.role not in ["owner", "admin"])):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or owner role required to delete project")

    success = await proj_repo.delete_project(project_id)
    return {"success": success, "deleted_id": str(project_id)}


@router.get("/{project_id}/overview")
async def get_project_overview(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    proj_repo: ProjectRepository = Depends(get_project_repository),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Get statistical counts and overview for the project."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    project = await proj_repo.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    membership = await ws_repo.get_user_membership(project.workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(project.workspace_id)

    if not workspace or (workspace.owner_id != user_uuid and not membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    overview = await proj_repo.get_project_overview(project_id)
    return overview
