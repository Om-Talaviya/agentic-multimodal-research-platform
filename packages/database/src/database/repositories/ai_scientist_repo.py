"""
Repository for Autonomous AI Scientist Self-Evolving Discovery Engine.
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.ai_scientist import (
    DBAutonomousScientistProgram,
    DBResearchIterationCycle,
    DBDiscoveryBreakthrough
)

class AutonomousScientistRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_program(
        self,
        title: str,
        research_domain: str,
        goal_statement: str,
        exploration_mode: str = "EXPLOIT_FRONTIER",
        max_cycles: int = 5,
        overall_novelty_score: float = 0.94,
        user_id: Optional[uuid.UUID] = None
    ) -> DBAutonomousScientistProgram:
        program = DBAutonomousScientistProgram(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            research_domain=research_domain,
            goal_statement=goal_statement,
            exploration_mode=exploration_mode,
            max_cycles=max_cycles,
            current_cycle=max_cycles,
            overall_novelty_score=overall_novelty_score,
            status="BREAKTHROUGH_ACHIEVED"
        )
        self.session.add(program)
        await self.session.commit()
        await self.session.refresh(program)
        return program

    async def get_program(self, program_id: uuid.UUID) -> Optional[DBAutonomousScientistProgram]:
        query = (
            select(DBAutonomousScientistProgram)
            .options(
                selectinload(DBAutonomousScientistProgram.iteration_cycles),
                selectinload(DBAutonomousScientistProgram.breakthroughs)
            )
            .where(DBAutonomousScientistProgram.id == program_id)
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def list_programs(self, limit: int = 50) -> List[DBAutonomousScientistProgram]:
        query = select(DBAutonomousScientistProgram).order_by(DBAutonomousScientistProgram.created_at.desc()).limit(limit)
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def add_cycle(
        self,
        program_id: uuid.UUID,
        cycle_index: int,
        hypothesis: str,
        experimental_protocol: str,
        simulation_metrics: Dict[str, Any],
        metacognitive_reflection: str,
        novelty_delta: float = 0.15
    ) -> DBResearchIterationCycle:
        cycle = DBResearchIterationCycle(
            id=uuid.uuid4(),
            program_id=program_id,
            cycle_index=cycle_index,
            hypothesis=hypothesis,
            experimental_protocol=experimental_protocol,
            simulation_metrics=simulation_metrics,
            metacognitive_reflection=metacognitive_reflection,
            cycle_novelty_delta=novelty_delta
        )
        self.session.add(cycle)
        await self.session.commit()
        await self.session.refresh(cycle)
        return cycle

    async def add_breakthrough(
        self,
        program_id: uuid.UUID,
        title: str,
        breakthrough_class: str,
        novelty_score: float,
        empirical_validity: float,
        falsifiability: float,
        formal_conclusion: str,
        whitepaper_summary: str
    ) -> DBDiscoveryBreakthrough:
        bt = DBDiscoveryBreakthrough(
            id=uuid.uuid4(),
            program_id=program_id,
            title=title,
            breakthrough_class=breakthrough_class,
            novelty_score=novelty_score,
            empirical_validity_score=empirical_validity,
            falsifiability_index=falsifiability,
            formal_conclusion=formal_conclusion,
            whitepaper_summary=whitepaper_summary
        )
        self.session.add(bt)
        await self.session.commit()
        await self.session.refresh(bt)
        return bt
