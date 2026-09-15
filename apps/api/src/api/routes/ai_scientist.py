"""
FastAPI Route Handlers for Phase 50: Autonomous AI Scientist & Nobel-Turing Discovery.
"""
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_current_user
from database.models.user import User as DBUser
from database.repositories.ai_scientist_repo import AutonomousScientistRepository
from research.ai_scientist_engine import AutonomousScientistEngine

router = APIRouter(prefix="/ai-scientist", tags=["Autonomous AI Scientist (Phase 50)"])

class RunProgramRequest(BaseModel):
    title: str = Field(..., example="Autonomous Discovery of Pan-KRAS Overcoming Therapeutic Modalities")
    research_domain: str = Field(..., example="Precision Oncology & Structural Therapeutics")
    goal_statement: str = Field(..., example="Discover and validate a next-generation therapeutic strategy that prevents resistance in oncogenic driver mutations.")
    cycles_count: int = Field(default=3, example=3)

class ProgramResponse(BaseModel):
    id: uuid.UUID
    title: str
    research_domain: str
    goal_statement: str
    exploration_mode: str
    max_cycles: int
    current_cycle: int
    overall_novelty_score: float
    status: str
    created_at: Any

    class Config:
        from_attributes = True

@router.post("/run", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def run_autonomous_program(
    payload: RunProgramRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    engine = AutonomousScientistEngine()
    result = engine.run_autonomous_program(
        title=payload.title,
        domain=payload.research_domain,
        goal=payload.goal_statement,
        cycles_count=payload.cycles_count
    )

    repo = AutonomousScientistRepository(db)
    program = await repo.create_program(
        title=result["title"],
        research_domain=result["research_domain"],
        goal_statement=result["goal_statement"],
        exploration_mode=result["exploration_mode"],
        max_cycles=result["max_cycles"],
        overall_novelty_score=result["overall_novelty"],
        user_id=current_user.id
    )

    for c in result["cycles"]:
        await repo.add_cycle(
            program_id=program.id,
            cycle_index=c["cycle_index"],
            hypothesis=c["hypothesis"],
            experimental_protocol=c["experimental_protocol"],
            simulation_metrics=c["simulation_metrics"],
            metacognitive_reflection=c["metacognitive_reflection"],
            novelty_delta=c["novelty_delta"]
        )

    bt = result["breakthrough"]
    await repo.add_breakthrough(
        program_id=program.id,
        title=bt["title"],
        breakthrough_class=bt["breakthrough_class"],
        novelty_score=bt["novelty_score"],
        empirical_validity=bt["empirical_validity"],
        falsifiability=bt["falsifiability"],
        formal_conclusion=bt["formal_conclusion"],
        whitepaper_summary=bt["whitepaper_summary"]
    )

    return program

@router.get("/programs", response_model=List[ProgramResponse])
async def list_programs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = AutonomousScientistRepository(db)
    return await repo.list_programs(limit=limit)

@router.get("/programs/{program_id}")
async def get_program_details(
    program_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = AutonomousScientistRepository(db)
    p = await repo.get_program(program_id)
    if not p:
        raise HTTPException(status_code=404, detail="Autonomous Scientist program not found")
    return {
        "id": str(p.id),
        "title": p.title,
        "domain": p.research_domain,
        "goal": p.goal_statement,
        "mode": p.exploration_mode,
        "novelty": p.overall_novelty_score,
        "status": p.status,
        "cycles": [
            {
                "cycle": c.cycle_index,
                "hypothesis": c.hypothesis,
                "protocol": c.experimental_protocol,
                "metrics": c.simulation_metrics,
                "reflection": c.metacognitive_reflection,
                "novelty_delta": c.cycle_novelty_delta
            } for c in p.iteration_cycles
        ],
        "breakthroughs": [
            {
                "title": b.title,
                "class": b.breakthrough_class,
                "novelty": b.novelty_score,
                "validity": b.empirical_validity_score,
                "falsifiability": b.falsifiability_index,
                "conclusion": b.formal_conclusion,
                "whitepaper": b.whitepaper_summary
            } for b in p.breakthroughs
        ]
    }
