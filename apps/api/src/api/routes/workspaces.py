"""REST API routes for Workspace management and membership isolation."""

import uuid
from typing import Any, Dict, List, Optional
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

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


# --- Schemas ---

class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    slug: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceMemberAddRequest(BaseModel):
    user_id: uuid.UUID
    role: str = Field("member", pattern="^(owner|admin|researcher|member|viewer)$")


class ProjectCreateInWorkspaceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    slug: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


# --- Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    body: WorkspaceCreateRequest,
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
    proj_repo: ProjectRepository = Depends(get_project_repository),
) -> Dict[str, Any]:
    """Create a new workspace and auto-initialize a default 'General Research' project."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    workspace = await ws_repo.create_workspace(
        name=body.name,
        owner_id=user_uuid,
        slug=body.slug,
        description=body.description,
        settings=body.settings,
    )

    # Automatically provision initial default project
    await proj_repo.ensure_default_project(workspace.id, user_uuid)

    return {
        "success": True,
        "workspace": workspace.to_dict(),
    }


@router.get("")
async def list_user_workspaces(
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
    proj_repo: ProjectRepository = Depends(get_project_repository),
) -> Dict[str, Any]:
    """List all workspaces the authenticated user belongs to. Auto-provisions default workspace if none exists."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    workspaces = await ws_repo.list_for_user(user_uuid)

    # Provision default personal workspace on first access
    if not workspaces:
        default_ws = await ws_repo.ensure_default_workspace(user_uuid, current_user.username)
        await proj_repo.ensure_default_project(default_ws.id, user_uuid)
        workspaces = [default_ws]

    return {
        "workspaces": [ws.to_dict() for ws in workspaces],
        "total": len(workspaces),
    }


@router.get("/{workspace_id}")
async def get_workspace_details(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Get workspace details and its registered members."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    membership = await ws_repo.get_user_membership(workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(workspace_id)

    if not workspace or (workspace.owner_id != user_uuid and not membership):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    members = await ws_repo.get_members(workspace_id)

    return {
        "workspace": workspace.to_dict(),
        "user_role": "owner" if workspace.owner_id == user_uuid else (membership.role if membership else "member"),
        "members": [m.to_dict() for m in members],
    }


@router.patch("/{workspace_id}")
async def update_workspace(
    workspace_id: uuid.UUID,
    body: WorkspaceUpdateRequest,
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Update workspace name, description, or settings."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    membership = await ws_repo.get_user_membership(workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(workspace_id)

    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    user_role = "owner" if workspace.owner_id == user_uuid else (membership.role if membership else None)
    if user_role not in ["owner", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners or admins can update workspace settings")

    updated = await ws_repo.update_workspace(
        workspace_id=workspace_id,
        name=body.name,
        description=body.description,
        settings=body.settings,
    )
    return {"success": True, "workspace": updated.to_dict()}


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Delete workspace (Owner only)."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    workspace = await ws_repo.get_by_id(workspace_id)

    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    if workspace.owner_id != user_uuid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the workspace owner can delete this workspace")

    success = await ws_repo.delete_workspace(workspace_id)
    return {"success": success, "deleted_id": str(workspace_id)}


@router.get("/{workspace_id}/projects")
async def list_workspace_projects(
    workspace_id: uuid.UUID,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
    proj_repo: ProjectRepository = Depends(get_project_repository),
) -> Dict[str, Any]:
    """List all projects in the workspace."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    membership = await ws_repo.get_user_membership(workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(workspace_id)

    if not workspace or (workspace.owner_id != user_uuid and not membership):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found or access denied")

    projects = await proj_repo.list_for_workspace(workspace_id, status=status_filter)
    return {
        "workspace_id": str(workspace_id),
        "projects": [p.to_dict() for p in projects],
        "total": len(projects),
    }


@router.post("/{workspace_id}/projects", status_code=status.HTTP_201_CREATED)
async def create_workspace_project(
    workspace_id: uuid.UUID,
    body: ProjectCreateInWorkspaceRequest,
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
    proj_repo: ProjectRepository = Depends(get_project_repository),
) -> Dict[str, Any]:
    """Create a new project inside the specified workspace."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    membership = await ws_repo.get_user_membership(workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(workspace_id)

    if not workspace or (workspace.owner_id != user_uuid and not membership):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found or access denied")

    user_role = "owner" if workspace.owner_id == user_uuid else (membership.role if membership else "viewer")
    if user_role == "viewer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Viewers cannot create projects")

    project = await proj_repo.create_project(
        workspace_id=workspace_id,
        name=body.name,
        created_by=user_uuid,
        slug=body.slug,
        description=body.description,
        settings=body.settings,
    )
    return {"success": True, "project": project.to_dict()}


@router.get("/{workspace_id}/members")
async def list_workspace_members(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """List members of a workspace."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    membership = await ws_repo.get_user_membership(workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(workspace_id)

    if not workspace or (workspace.owner_id != user_uuid and not membership):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found or access denied")

    members = await ws_repo.get_members(workspace_id)
    return {"members": [m.to_dict() for m in members]}


@router.post("/{workspace_id}/members")
async def add_or_update_member(
    workspace_id: uuid.UUID,
    body: WorkspaceMemberAddRequest,
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Add or update member role in workspace (Admin/Owner only)."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    membership = await ws_repo.get_user_membership(workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(workspace_id)

    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    user_role = "owner" if workspace.owner_id == user_uuid else (membership.role if membership else None)
    if user_role not in ["owner", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or owner role required to manage members")

    member = await ws_repo.add_member(workspace_id, body.user_id, role=body.role)
    return {"success": True, "member": member.to_dict()}


@router.delete("/{workspace_id}/members/{member_user_id}")
async def remove_member(
    workspace_id: uuid.UUID,
    member_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Remove a member from the workspace."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    membership = await ws_repo.get_user_membership(workspace_id, user_uuid)
    workspace = await ws_repo.get_by_id(workspace_id)

    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    # Owners/admins can remove others, users can remove themselves
    user_role = "owner" if workspace.owner_id == user_uuid else (membership.role if membership else None)
    if user_role not in ["owner", "admin"] and user_uuid != member_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    if member_user_id == workspace.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove workspace owner")

    success = await ws_repo.remove_member(workspace_id, member_user_id)
    return {"success": success}
