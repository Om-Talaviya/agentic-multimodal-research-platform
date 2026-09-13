"""Repository for Workspace and WorkspaceMember database persistence."""

import re
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.workspace import DBWorkspace, DBWorkspaceMember


def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = re.sub(r"^-+|-+$", "", slug)
    return slug or "workspace"


class WorkspaceRepository:
    """Async repository for workspace management and membership RBAC."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_workspace(
        self,
        name: str,
        owner_id: uuid.UUID,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        is_personal: bool = False,
        settings: Optional[Dict[str, Any]] = None,
    ) -> DBWorkspace:
        """Create a new workspace and register the creator as owner in workspace_members."""
        base_slug = generate_slug(slug or name)
        final_slug = base_slug

        # Check for slug collision and make unique
        count = 1
        while True:
            existing = await self.get_by_slug(final_slug)
            if not existing:
                break
            final_slug = f"{base_slug}-{count}"
            count += 1

        workspace = DBWorkspace(
            name=name,
            slug=final_slug,
            description=description,
            owner_id=owner_id,
            is_personal=is_personal,
            settings_json=settings or {},
        )
        self.session.add(workspace)
        await self.session.flush()

        # Add creator as owner member
        owner_member = DBWorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role="owner",
        )
        self.session.add(owner_member)
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def get_by_id(self, workspace_id: uuid.UUID) -> Optional[DBWorkspace]:
        """Fetch a workspace by ID."""
        stmt = select(DBWorkspace).where(DBWorkspace.id == workspace_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[DBWorkspace]:
        """Fetch a workspace by its unique slug."""
        stmt = select(DBWorkspace).where(DBWorkspace.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> List[DBWorkspace]:
        """List all workspaces that a user owns or is a member of."""
        stmt = (
            select(DBWorkspace)
            .outerjoin(DBWorkspaceMember, DBWorkspace.id == DBWorkspaceMember.workspace_id)
            .where(
                or_(
                    DBWorkspace.owner_id == user_id,
                    DBWorkspaceMember.user_id == user_id,
                )
            )
            .distinct()
            .order_by(DBWorkspace.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_workspace(
        self,
        workspace_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Optional[DBWorkspace]:
        """Update workspace metadata."""
        workspace = await self.get_by_id(workspace_id)
        if not workspace:
            return None

        if name is not None:
            workspace.name = name
        if description is not None:
            workspace.description = description
        if settings is not None:
            workspace.settings_json = settings

        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def delete_workspace(self, workspace_id: uuid.UUID) -> bool:
        """Delete a workspace and cascade delete all members and projects."""
        workspace = await self.get_by_id(workspace_id)
        if not workspace:
            return False

        await self.session.delete(workspace)
        await self.session.commit()
        return True

    async def add_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str = "member",
    ) -> DBWorkspaceMember:
        """Add or update a member's role in a workspace."""
        stmt = select(DBWorkspaceMember).where(
            DBWorkspaceMember.workspace_id == workspace_id,
            DBWorkspaceMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if member:
            member.role = role
        else:
            member = DBWorkspaceMember(
                workspace_id=workspace_id,
                user_id=user_id,
                role=role,
            )
            self.session.add(member)

        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def remove_member(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Remove a member from a workspace."""
        stmt = delete(DBWorkspaceMember).where(
            DBWorkspaceMember.workspace_id == workspace_id,
            DBWorkspaceMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return (result.rowcount or 0) > 0

    async def get_members(self, workspace_id: uuid.UUID) -> List[DBWorkspaceMember]:
        """Fetch all members of a workspace."""
        stmt = (
            select(DBWorkspaceMember)
            .where(DBWorkspaceMember.workspace_id == workspace_id)
            .order_by(DBWorkspaceMember.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_membership(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[DBWorkspaceMember]:
        """Get membership details for a specific user in a workspace."""
        stmt = select(DBWorkspaceMember).where(
            DBWorkspaceMember.workspace_id == workspace_id,
            DBWorkspaceMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def ensure_default_workspace(self, user_id: uuid.UUID, username: str) -> DBWorkspace:
        """Ensure a user has at least one personal workspace, creating one if not found."""
        workspaces = await self.list_for_user(user_id)
        if workspaces:
            return workspaces[0]

        return await self.create_workspace(
            name=f"{username.capitalize()}'s Workspace",
            owner_id=user_id,
            slug=f"{generate_slug(username)}-workspace",
            description="Personal default workspace",
            is_personal=True,
        )
