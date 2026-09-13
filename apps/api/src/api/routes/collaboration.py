"""REST API routes for Team Collaboration: Workspace Invites, Report Annotations, and Activity Feed."""

from datetime import UTC, datetime
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

from api.dependencies import (
    get_current_user,
    get_report_annotation_repository,
    get_workspace_activity_repository,
    get_workspace_invite_repository,
    get_workspace_repository,
)
from database.repositories.collaboration_repo import (
    ReportAnnotationRepository,
    WorkspaceActivityRepository,
    WorkspaceInviteRepository,
)
from database.repositories.workspace_repo import WorkspaceRepository
from shared.auth import User

router = APIRouter(tags=["collaboration"])


# --- Schemas ---

class CreateInviteRequest(BaseModel):
    email: EmailStr
    role: str = Field("researcher", pattern="^(admin|researcher|analyst|reviewer|viewer)$")


class CreateAnnotationRequest(BaseModel):
    comment_text: str = Field(..., min_length=1, max_length=5000)
    section_index: Optional[int] = None
    selected_text: Optional[str] = None


# --- Workspace Invites Endpoints ---

@router.post("/workspaces/{workspace_id}/invites", status_code=status.HTTP_201_CREATED)
async def create_workspace_invite(
    workspace_id: uuid.UUID,
    body: CreateInviteRequest,
    current_user: User = Depends(get_current_user),
    invite_repo: WorkspaceInviteRepository = Depends(get_workspace_invite_repository),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
    activity_repo: WorkspaceActivityRepository = Depends(get_workspace_activity_repository),
) -> Dict[str, Any]:
    """Create an invite for an email address to join a workspace."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    
    # Check caller has admin/owner permission in the workspace
    member = await ws_repo.get_member(workspace_id, user_uuid)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workspace owners and admins can invite new members",
        )

    invite = await invite_repo.create_invite(
        workspace_id=workspace_id,
        email=body.email,
        role=body.role,
        invited_by=user_uuid,
    )

    # Log activity
    await activity_repo.log_activity(
        workspace_id=workspace_id,
        action="member_invited",
        user_id=user_uuid,
        entity_id=invite.id,
        details={"email": body.email, "role": body.role},
    )

    return {
        "invite": invite.to_dict(),
        "invite_link": f"/invites/{invite.token}",
        "message": f"Invitation created for {body.email}",
    }


@router.get("/workspaces/{workspace_id}/invites")
async def list_workspace_invites(
    workspace_id: uuid.UUID,
    include_accepted: bool = Query(False),
    current_user: User = Depends(get_current_user),
    invite_repo: WorkspaceInviteRepository = Depends(get_workspace_invite_repository),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """List pending or all invitations for a workspace."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    member = await ws_repo.get_member(workspace_id, user_uuid)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workspace owners and admins can view invite lists",
        )

    invites = await invite_repo.list_for_workspace(workspace_id, include_accepted=include_accepted)
    return {
        "workspace_id": str(workspace_id),
        "total": len(invites),
        "invites": [inv.to_dict() for inv in invites],
    }


@router.get("/invites/{token}")
async def get_invite_by_token(
    token: str,
    invite_repo: WorkspaceInviteRepository = Depends(get_workspace_invite_repository),
) -> Dict[str, Any]:
    """Inspect invite details before accepting."""
    invite = await invite_repo.get_by_token(token)
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation token is invalid or does not exist",
        )
    is_expired = False
    if invite.expires_at:
        exp = invite.expires_at if invite.expires_at.tzinfo is not None else invite.expires_at.replace(tzinfo=UTC)
        is_expired = exp < datetime.now(UTC)

    return {
        "invite": invite.to_dict(),
        "workspace_name": invite.workspace.name if invite.workspace else None,
        "is_expired": is_expired,
    }


@router.post("/invites/{token}/accept")
async def accept_workspace_invite(
    token: str,
    current_user: User = Depends(get_current_user),
    invite_repo: WorkspaceInviteRepository = Depends(get_workspace_invite_repository),
    activity_repo: WorkspaceActivityRepository = Depends(get_workspace_activity_repository),
) -> Dict[str, Any]:
    """Accept an invitation token with the currently authenticated user."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    
    invite = await invite_repo.get_by_token(token)
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation token is invalid or expired",
        )

    workspace_id = invite.workspace_id
    member = await invite_repo.accept_invite(token=token, user_id=user_uuid)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation is either already accepted or has expired",
        )

    # Log activity
    await activity_repo.log_activity(
        workspace_id=workspace_id,
        action="member_joined",
        user_id=user_uuid,
        entity_id=member.id,
        details={"role": member.role, "email": current_user.email or current_user.username},
    )

    return {
        "message": "Successfully joined workspace",
        "workspace_id": str(workspace_id),
        "member": member.to_dict(),
    }


@router.delete("/invites/{invite_id}")
async def revoke_workspace_invite(
    invite_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    invite_repo: WorkspaceInviteRepository = Depends(get_workspace_invite_repository),
    ws_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Dict[str, Any]:
    """Revoke a workspace invite."""
    invite = await invite_repo.get_by_id(invite_id)
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found",
        )

    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    member = await ws_repo.get_member(invite.workspace_id, user_uuid)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workspace owners and admins can revoke invites",
        )

    success = await invite_repo.revoke_invite(invite_id)
    return {"success": success, "message": "Invite revoked successfully"}


# --- Report Annotations Endpoints ---

@router.post("/reports/{report_id}/annotations", status_code=status.HTTP_201_CREATED)
async def create_report_annotation(
    report_id: uuid.UUID,
    body: CreateAnnotationRequest,
    current_user: User = Depends(get_current_user),
    annotation_repo: ReportAnnotationRepository = Depends(get_report_annotation_repository),
) -> Dict[str, Any]:
    """Add an inline comment or annotation to a report."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    
    annotation = await annotation_repo.create_annotation(
        report_id=report_id,
        user_id=user_uuid,
        comment_text=body.comment_text,
        section_index=body.section_index,
        selected_text=body.selected_text,
    )
    return {
        "annotation": annotation.to_dict(),
        "message": "Annotation created successfully",
    }


@router.get("/reports/{report_id}/annotations")
async def list_report_annotations(
    report_id: uuid.UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    annotation_repo: ReportAnnotationRepository = Depends(get_report_annotation_repository),
) -> Dict[str, Any]:
    """List all annotations on a research report."""
    annotations = await annotation_repo.list_for_report(report_id=report_id, status=status_filter)
    return {
        "report_id": str(report_id),
        "total": len(annotations),
        "annotations": [ann.to_dict() for ann in annotations],
    }


@router.patch("/annotations/{annotation_id}/resolve")
async def resolve_report_annotation(
    annotation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    annotation_repo: ReportAnnotationRepository = Depends(get_report_annotation_repository),
) -> Dict[str, Any]:
    """Mark an annotation as resolved."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    
    annotation = await annotation_repo.resolve_annotation(
        annotation_id=annotation_id,
        resolved_by=user_uuid,
    )
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )
    return {
        "annotation": annotation.to_dict(),
        "message": "Annotation resolved successfully",
    }


@router.delete("/annotations/{annotation_id}")
async def delete_report_annotation(
    annotation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    annotation_repo: ReportAnnotationRepository = Depends(get_report_annotation_repository),
) -> Dict[str, Any]:
    """Delete an annotation."""
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    annotation = await annotation_repo.get_by_id(annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )

    # Only author or admin can delete
    if annotation.user_id != user_uuid and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own annotations",
        )

    success = await annotation_repo.delete_annotation(annotation_id)
    return {"success": success, "message": "Annotation deleted successfully"}


# --- Workspace & Project Activities Endpoints ---

@router.get("/workspaces/{workspace_id}/activities")
async def get_workspace_activities(
    workspace_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    activity_repo: WorkspaceActivityRepository = Depends(get_workspace_activity_repository),
) -> Dict[str, Any]:
    """Fetch collaborative audit activity feed for a workspace."""
    activities = await activity_repo.list_for_workspace(
        workspace_id=workspace_id,
        limit=limit,
        offset=offset,
    )
    return {
        "workspace_id": str(workspace_id),
        "total": len(activities),
        "activities": [act.to_dict() for act in activities],
    }


@router.get("/projects/{project_id}/activities")
async def get_project_activities(
    project_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    activity_repo: WorkspaceActivityRepository = Depends(get_workspace_activity_repository),
) -> Dict[str, Any]:
    """Fetch audit activity feed for a specific project."""
    activities = await activity_repo.list_for_project(
        project_id=project_id,
        limit=limit,
    )
    return {
        "project_id": str(project_id),
        "total": len(activities),
        "activities": [act.to_dict() for act in activities],
    }
