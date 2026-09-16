"""Repository for RAGAS Groundedness Evaluation and Adversarial Probes."""
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.ragas_eval import (
    DBRagasEvaluationSuite,
    DBRagasSampleMetric,
    DBAdversarialRedTeamProbe,
)


class RagasEvaluationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_suite(
        self,
        name: str,
        description: Optional[str] = None,
        target_pipeline_id: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBRagasEvaluationSuite:
        suite = DBRagasEvaluationSuite(
            name=name,
            description=description,
            target_pipeline_id=target_pipeline_id,
            metadata_json=metadata_json or {},
        )
        self.session.add(suite)
        await self.session.commit()
        await self.session.refresh(suite)
        return suite

    async def get_suite(self, suite_id: UUID) -> Optional[DBRagasEvaluationSuite]:
        stmt = select(DBRagasEvaluationSuite).where(DBRagasEvaluationSuite.id == suite_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_suites(self, limit: int = 50) -> List[DBRagasEvaluationSuite]:
        stmt = select(DBRagasEvaluationSuite).order_by(desc(DBRagasEvaluationSuite.created_at)).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_sample(
        self,
        suite_id: UUID,
        query: str,
        generated_answer: str,
        retrieved_contexts: List[str],
        ground_truth: Optional[str] = None,
        faithfulness_score: float = 0.95,
        answer_relevancy_score: float = 0.92,
        context_precision_score: float = 0.90,
        context_recall_score: float = 0.88,
        groundedness_score: float = 0.94,
        hallucination_flag: bool = False,
    ) -> DBRagasSampleMetric:
        sample = DBRagasSampleMetric(
            suite_id=suite_id,
            query=query,
            generated_answer=generated_answer,
            ground_truth=ground_truth,
            retrieved_contexts=retrieved_contexts,
            faithfulness_score=faithfulness_score,
            answer_relevancy_score=answer_relevancy_score,
            context_precision_score=context_precision_score,
            context_recall_score=context_recall_score,
            groundedness_score=groundedness_score,
            hallucination_flag=hallucination_flag,
        )
        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def list_samples(self, suite_id: UUID) -> List[DBRagasSampleMetric]:
        stmt = select(DBRagasSampleMetric).where(DBRagasSampleMetric.suite_id == suite_id).order_by(DBRagasSampleMetric.created_at)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_probe(
        self,
        suite_id: UUID,
        attack_category: str,
        prompt_payload: str,
        guardrail_verdict: str = "BLOCKED",
        mitigation_applied: str = "Input Sanitizer Filter & SSRF Firewall",
        is_defense_successful: bool = True,
        latency_ms: float = 12.5,
    ) -> DBAdversarialRedTeamProbe:
        probe = DBAdversarialRedTeamProbe(
            suite_id=suite_id,
            attack_category=attack_category,
            prompt_payload=prompt_payload,
            guardrail_verdict=guardrail_verdict,
            mitigation_applied=mitigation_applied,
            is_defense_successful=is_defense_successful,
            latency_ms=latency_ms,
        )
        self.session.add(probe)
        await self.session.commit()
        await self.session.refresh(probe)
        return probe

    async def list_probes(self, suite_id: UUID) -> List[DBAdversarialRedTeamProbe]:
        stmt = select(DBAdversarialRedTeamProbe).where(DBAdversarialRedTeamProbe.suite_id == suite_id).order_by(DBAdversarialRedTeamProbe.created_at)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_suite_metrics(
        self,
        suite_id: UUID,
        total_samples: int,
        avg_faithfulness: float,
        avg_answer_relevancy: float,
        avg_context_precision: float,
        avg_context_recall: float,
        avg_groundedness: float,
        red_team_defense_rate: float,
    ) -> Optional[DBRagasEvaluationSuite]:
        suite = await self.get_suite(suite_id)
        if not suite:
            return None
        suite.total_samples = total_samples
        suite.avg_faithfulness = avg_faithfulness
        suite.avg_answer_relevancy = avg_answer_relevancy
        suite.avg_context_precision = avg_context_precision
        suite.avg_context_recall = avg_context_recall
        suite.avg_groundedness = avg_groundedness
        suite.red_team_defense_rate = red_team_defense_rate
        suite.status = "COMPLETED"
        await self.session.commit()
        await self.session.refresh(suite)
        return suite
