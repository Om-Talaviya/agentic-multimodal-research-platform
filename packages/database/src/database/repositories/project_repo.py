"""Repository for Project database persistence and overview metrics."""

import re
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.document import Document
from database.models.graph import DBKnowledgeEntity
from database.models.memory import DBResearchMemory
from database.models.research_job import ResearchJob
from database.models.workspace import DBProject
from database.repositories.workspace_repo import generate_slug


class ProjectRepository:
    """Async repository for project management within workspaces."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(
        self,
        workspace_id: uuid.UUID,
        name: str,
        created_by: Optional[uuid.UUID] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> DBProject:
        """Create a new project within a workspace."""
        base_slug = generate_slug(slug or name)
        final_slug = base_slug

        # Ensure slug uniqueness within the workspace
        count = 1
        while True:
            existing = await self.get_by_slug(workspace_id, final_slug)
            if not existing:
                break
            final_slug = f"{base_slug}-{count}"
            count += 1

        project = DBProject(
            workspace_id=workspace_id,
            name=name,
            slug=final_slug,
            description=description,
            created_by=created_by,
            settings_json=settings or {},
        )
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def get_by_id(self, project_id: uuid.UUID) -> Optional[DBProject]:
        """Fetch a project by ID."""
        stmt = select(DBProject).where(DBProject.id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, workspace_id: uuid.UUID, slug: str) -> Optional[DBProject]:
        """Fetch a project by workspace ID and slug."""
        stmt = select(DBProject).where(
            DBProject.workspace_id == workspace_id,
            DBProject.slug == slug,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_workspace(
        self,
        workspace_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> List[DBProject]:
        """List all projects in a workspace, optionally filtered by status."""
        stmt = select(DBProject).where(DBProject.workspace_id == workspace_id)
        if status:
            stmt = stmt.where(DBProject.status == status)
        stmt = stmt.order_by(DBProject.created_at.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_project(
        self,
        project_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Optional[DBProject]:
        """Update project details."""
        project = await self.get_by_id(project_id)
        if not project:
            return None

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if status is not None:
            project.status = status
        if settings is not None:
            project.settings_json = settings

        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete_project(self, project_id: uuid.UUID) -> bool:
        """Delete a project."""
        project = await self.get_by_id(project_id)
        if not project:
            return False

        await self.session.delete(project)
        await self.session.commit()
        return True

    async def get_project_overview(self, project_id: uuid.UUID) -> Dict[str, Any]:
        """Aggregate statistical metrics for a project."""
        project = await self.get_by_id(project_id)
        if not project:
            return {}

        project_id_str = str(project_id)

        # Count research jobs
        jobs_stmt = select(func.count(ResearchJob.id)).where(ResearchJob.project_id == project_id)
        jobs_count = (await self.session.execute(jobs_stmt)).scalar() or 0

        # Count documents
        docs_stmt = select(func.count(Document.id)).where(Document.project_id == project_id)
        docs_count = (await self.session.execute(docs_stmt)).scalar() or 0

        # Count memories
        mem_stmt = select(func.count(DBResearchMemory.id)).where(
            (DBResearchMemory.project_id == project_id_str)
        )
        mem_count = (await self.session.execute(mem_stmt)).scalar() or 0

        # Count knowledge graph entities
        graph_stmt = select(func.count(DBKnowledgeEntity.id)).where(
            DBKnowledgeEntity.project_id == project_id
        )
        graph_count = (await self.session.execute(graph_stmt)).scalar() or 0

        return {
            "project": project.to_dict(),
            "metrics": {
                "total_jobs": jobs_count,
                "total_documents": docs_count,
                "total_memories": mem_count,
                "total_graph_entities": graph_count,
            },
        }

    async def ensure_default_project(
        self,
        workspace_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> DBProject:
        """Ensure a workspace has at least one default project."""
        projects = await self.list_for_workspace(workspace_id)
        if projects:
            return projects[0]

        return await self.create_project(
            workspace_id=workspace_id,
            name="General Research",
            slug="general-research",
            description="Default project for research jobs, documents, and knowledge",
            created_by=user_id,
        )
