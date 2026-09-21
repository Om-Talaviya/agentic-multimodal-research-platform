"""Preprint Latex Routes (Phase 124)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.preprint_latex_repo import PreprintLatexRepository
from research.publishing.latex_engine import PreprintLatexCompilerEngine

router = APIRouter(prefix="/preprint-latex", tags=["Preprint LaTeX Compiler Engine"])

class PreprintRequest(BaseModel):
    manuscript_title: str = Field(..., example="Autonomous Multi-Modal In-Silico Scientific Discovery Platform")
    journal_target_format: str = Field(default="Nature Biotechnology", example="Nature Biotechnology")
    abstract_text: str = Field(default="Autonomous AI systems represent a paradigm shift...", example="Autonomous AI...")
    workspace_id: Optional[str] = None

@router.post("/compile", status_code=status.HTTP_201_CREATED)
async def compile_preprint_endpoint(req: PreprintRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = PreprintLatexCompilerEngine()
    res = engine.compile_pre_print(req.manuscript_title, req.journal_target_format, req.abstract_text)
    repo = PreprintLatexRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    m = await repo.create_manuscript(
        workspace_id=ws_id,
        manuscript_title=res["title"],
        journal_target_format=res["format"],
        total_words=res["words"],
        compilation_status=res["status"],
        latex_source_code=res["latex"]
    )
    for c in res["citations"]:
        await repo.add_citation(
            manuscript_id=m.id,
            citation_key=c["key"],
            doi_or_pmid=c["doi"],
            bibtex_entry=c["bibtex"]
        )
    return {"status": "SUCCESS", "manuscript_id": str(m.id), "result": res}

@router.get("/manuscripts/{manuscript_id}")
async def get_manuscript(manuscript_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = PreprintLatexRepository(db)
    try:
        mid = uuid.UUID(manuscript_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    m = await repo.get_manuscript(mid)
    if not m:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    return {"id": str(m.id), "title": m.manuscript_title}
