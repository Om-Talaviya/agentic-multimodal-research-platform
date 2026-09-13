"""Repositories for Workspace Invitations, Report Annotations, and Workspace Activities."""

from datetime import UTC, datetime
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.collaboration import (
    DBReportAnnotation,
    DBWorkspaceActivity,
    DBWorkspaceInvite,
    generate_invite_token,
)
from database.models.workspace import DBWorkspaceMember


class WorkspaceInviteRepository:
    """Async repository for managing team workspace invitations and token redemption."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_invite(
        self,
        workspace_id: uuid.UUID,
        email: str,
        role: str = "researcher",
        invited_by: Optional[uuid.UUID] = None,
    ) -> DBWorkspaceInvite:
        """Create a new invite token for an email in a workspace."""
        invite = DBWorkspaceInvite(
            workspace_id=workspace_id,
            email=email.strip().lower(),
            role=role.lower(),
            token=generate_invite_token(),
            invited_by=invited_by,
        )
        self.session.add(invite)
        await self.session.flush()
        return invite

    async def get_by_token(self, token: str) -> Optional[DBWorkspaceInvite]:
        """Fetch invite by token."""
        stmt = (
            select(DBWorkspaceInvite)
            .options(selectinload(DBWorkspaceInvite.workspace), selectinload(DBWorkspaceInvite.inviter))
            .where(DBWorkspaceInvite.token == token)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id(self, invite_id: uuid.UUID) -> Optional[DBWorkspaceInvite]:
        """Fetch invite by ID."""
        stmt = select(DBWorkspaceInvite).where(DBWorkspaceInvite.id == invite_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_for_workspace(
        self,
        workspace_id: uuid.UUID,
        include_accepted: bool = False,
    ) -> List[DBWorkspaceInvite]:
        """List invites for a workspace."""
        stmt = (
            select(DBWorkspaceInvite)
            .options(selectinload(DBWorkspaceInvite.inviter))
            .where(DBWorkspaceInvite.workspace_id == workspace_id)
        )
        if not include_accepted:
            stmt = stmt.where(DBWorkspaceInvite.is_accepted == False)
        stmt = stmt.order_by(desc(DBWorkspaceInvite.created_at))
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def accept_invite(
        self,
        token: str,
        user_id: uuid.UUID,
    ) -> Optional[DBWorkspaceMember]:
        """Accept an invite by token, adding the user as a workspace member."""
        invite = await self.get_by_token(token)
        if not invite:
            return None
        if invite.is_accepted:
            return None
        if invite.expires_at:
            exp = invite.expires_at if invite.expires_at.tzinfo is not None else invite.expires_at.replace(tzinfo=UTC)
            if exp < datetime.now(UTC):
                return None

        # Check if already a member
        stmt = select(DBWorkspaceMember).where(
            DBWorkspaceMember.workspace_id == invite.workspace_id,
            DBWorkspaceMember.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        member = res.scalar_one_or_none()

        if not member:
            member = DBWorkspaceMember(
                workspace_id=invite.workspace_id,
                user_id=user_id,
                role=invite.role,
            )
            self.session.add(member)
        else:
            # Upgrade role if needed
            member.role = invite.role

        invite.is_accepted = True
        await self.session.flush()
        return member

    async def revoke_invite(self, invite_id: uuid.UUID) -> bool:
        """Revoke / delete an invite."""
        stmt = delete(DBWorkspaceInvite).where(DBWorkspaceInvite.id == invite_id)
        res = await self.session.execute(stmt)
        return res.rowcount > 0


class ReportAnnotationRepository:
    """Async repository for managing inline comments and annotations on reports."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_annotation(
        self,
        report_id: uuid.UUID,
        user_id: uuid.UUID,
        comment_text: str,
        section_index: Optional[int] = None,
        selected_text: Optional[str] = None,
    ) -> DBReportAnnotation:
        """Create an inline annotation on a report."""
        annotation = DBReportAnnotation(
            report_id=report_id,
            user_id=user_id,
            comment_text=comment_text.strip(),
            section_index=section_index,
            selected_text=selected_text,
            status="open",
        )
        self.session.add(annotation)
        await self.session.flush()
        # Reload author relationship
        await self.session.refresh(annotation, attribute_names=["author"])
        return annotation

    async def get_by_id(self, annotation_id: uuid.UUID) -> Optional[DBReportAnnotation]:
        """Fetch annotation by ID."""
        stmt = (
            select(DBReportAnnotation)
            .options(selectinload(DBReportAnnotation.author), selectinload(DBReportAnnotation.resolver))
            .where(DBReportAnnotation.id == annotation_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_for_report(
        self,
        report_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> List[DBReportAnnotation]:
        """List annotations for a report ordered by creation time."""
        stmt = (
            select(DBReportAnnotation)
            .options(selectinload(DBReportAnnotation.author), selectinload(DBReportAnnotation.resolver))
            .where(DBReportAnnotation.report_id == report_id)
        )
        if status:
            stmt = stmt.where(DBReportAnnotation.status == status)
        stmt = stmt.order_by(DBReportAnnotation.created_at.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def resolve_annotation(
        self,
        annotation_id: uuid.UUID,
        resolved_by: uuid.UUID,
    ) -> Optional[DBReportAnnotation]:
        """Mark an annotation as resolved."""
        annotation = await self.get_by_id(annotation_id)
        if not annotation:
            return None
        annotation.status = "resolved"
        annotation.resolved_by = resolved_by
        annotation.resolved_at = datetime.now(UTC)
        await self.session.flush()
        return annotation

    async def delete_annotation(self, annotation_id: uuid.UUID) -> bool:
        """Delete an annotation."""
        stmt = delete(DBReportAnnotation).where(DBReportAnnotation.id == annotation_id)
        res = await self.session.execute(stmt)
        return res.rowcount > 0


class WorkspaceActivityRepository:
    """Async repository for workspace activity logging and auditing."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_activity(
        self,
        workspace_id: uuid.UUID,
        action: str,
        user_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        entity_id: Optional[uuid.UUID] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> DBWorkspaceActivity:
        """Log a collaborative action into the workspace activity feed."""
        activity = DBWorkspaceActivity(
            workspace_id=workspace_id,
            action=action,
            user_id=user_id,
            project_id=project_id,
            entity_id=entity_id,
            details_json=details or {},
        )
        self.session.add(activity)
        await self.session.flush()
        return activity

    async def list_for_workspace(
        self,
        workspace_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBWorkspaceActivity]:
        """Fetch chronological activity feed for a workspace."""
        stmt = (
            select(DBWorkspaceActivity)
            .options(selectinload(DBWorkspaceActivity.user))
            .where(DBWorkspaceActivity.workspace_id == workspace_id)
            .order_by(desc(DBWorkspaceActivity.created_at))
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_for_project(
        self,
        project_id: uuid.UUID,
        limit: int = 50,
    ) -> List[DBWorkspaceActivity]:
        """Fetch activity feed for a specific project within a workspace."""
        stmt = (
            select(DBWorkspaceActivity)
            .options(selectinload(DBWorkspaceActivity.user))
            .where(DBWorkspaceActivity.project_id == project_id)
            .order_by(desc(DBWorkspaceActivity.created_at))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
