"""Repository for Systematic Literature Review (SLR), Screening, RoB, and Meta-Analysis persistence."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.literature import (
    DBLiteratureReview,
    DBSLRCriterion,
    DBSLRStudyCandidate,
    DBMetaAnalysisReport,
    DBRiskOfBiasAssessment,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class LiteratureRepository:
    """Async repository for managing Systematic Literature Reviews, candidate screening, and meta-analyses."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_literature_review(
        self,
        user_id: uuid.UUID,
        title: str,
        research_question: str,
        protocol_type: str = "PRISMA-2020",
        pico_framework: Optional[Dict[str, Any]] = None,
        search_strategy: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBLiteratureReview:
        """Create a new Systematic Literature Review project."""
        review = DBLiteratureReview(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            title=title,
            research_question=research_question,
            protocol_type=protocol_type,
            current_phase="identification",
            pico_framework=pico_framework or {},
            search_strategy=search_strategy or {},
            total_identified=0,
            total_screened=0,
            total_eligible=0,
            total_included=0,
            total_excluded=0,
        )
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        logger.info("literature_review_created", review_id=str(review.id), title=title)
        return review

    async def get_literature_review(
        self,
        review_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        include_criteria: bool = True,
        include_candidates: bool = True,
        include_meta_analyses: bool = True,
    ) -> Optional[DBLiteratureReview]:
        """Fetch an SLR review by ID with eager loading."""
        stmt = select(DBLiteratureReview).where(DBLiteratureReview.id == review_id)
        if user_id:
            stmt = stmt.where(DBLiteratureReview.user_id == user_id)

        if include_criteria:
            stmt = stmt.options(selectinload(DBLiteratureReview.criteria))
        if include_candidates:
            stmt = stmt.options(
                selectinload(DBLiteratureReview.candidates).selectinload(DBSLRStudyCandidate.risk_of_bias)
            )
        if include_meta_analyses:
            stmt = stmt.options(selectinload(DBLiteratureReview.meta_analyses))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_literature_reviews(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        current_phase: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBLiteratureReview]:
        """Query SLR reviews with filtering."""
        stmt = (
            select(DBLiteratureReview)
            .options(
                selectinload(DBLiteratureReview.criteria),
                selectinload(DBLiteratureReview.meta_analyses),
            )
            .order_by(DBLiteratureReview.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if user_id:
            stmt = stmt.where(DBLiteratureReview.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBLiteratureReview.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBLiteratureReview.project_id == project_id)
        if current_phase:
            stmt = stmt.where(DBLiteratureReview.current_phase == current_phase)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_review_phase(
        self,
        review_id: uuid.UUID,
        current_phase: str,
    ) -> Optional[DBLiteratureReview]:
        """Update current PRISMA phase status."""
        stmt = (
            update(DBLiteratureReview)
            .where(DBLiteratureReview.id == review_id)
            .values(current_phase=current_phase, updated_at=datetime.now(timezone.utc))
            .returning(DBLiteratureReview)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalars().first()

    async def recalculate_review_counts(self, review_id: uuid.UUID) -> Optional[DBLiteratureReview]:
        """Recalculate PRISMA counts based on study candidate screening status."""
        stmt = select(
            DBSLRStudyCandidate.screening_status,
            func.count(DBSLRStudyCandidate.id),
        ).where(DBSLRStudyCandidate.review_id == review_id).group_by(DBSLRStudyCandidate.screening_status)
        
        result = await self.session.execute(stmt)
        counts = dict(result.all())

        identified = sum(counts.values())
        screened = counts.get("title_abstract_screened", 0) + counts.get("full_text_screened", 0) + counts.get("included", 0) + counts.get("excluded", 0)
        eligible = counts.get("full_text_screened", 0) + counts.get("included", 0)
        included = counts.get("included", 0)
        excluded = counts.get("excluded", 0)

        update_stmt = (
            update(DBLiteratureReview)
            .where(DBLiteratureReview.id == review_id)
            .values(
                total_identified=identified,
                total_screened=screened,
                total_eligible=eligible,
                total_included=included,
                total_excluded=excluded,
                updated_at=datetime.now(timezone.utc),
            )
            .returning(DBLiteratureReview)
        )
        res = await self.session.execute(update_stmt)
        await self.session.commit()
        return res.scalars().first()

    async def delete_literature_review(self, review_id: uuid.UUID) -> bool:
        """Delete an SLR review and cascade child entities."""
        stmt = delete(DBLiteratureReview).where(DBLiteratureReview.id == review_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return (result.rowcount or 0) > 0

    # ---------------- Criteria Operations ----------------

    async def add_criterion(
        self,
        review_id: uuid.UUID,
        criterion_type: str,
        description: str,
        category: str = "general",
        order_index: int = 0,
    ) -> DBSLRCriterion:
        """Add an inclusion or exclusion criterion."""
        criterion = DBSLRCriterion(
            id=uuid.uuid4(),
            review_id=review_id,
            criterion_type=criterion_type,
            category=category,
            description=description,
            order_index=order_index,
            is_active=True,
        )
        self.session.add(criterion)
        await self.session.commit()
        await self.session.refresh(criterion)
        return criterion

    async def list_criteria(self, review_id: uuid.UUID) -> List[DBSLRCriterion]:
        """List all criteria for a review."""
        stmt = (
            select(DBSLRCriterion)
            .where(DBSLRCriterion.review_id == review_id)
            .order_by(DBSLRCriterion.order_index.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ---------------- Study Candidate Operations ----------------

    async def add_candidate_studies(
        self,
        review_id: uuid.UUID,
        studies: List[Dict[str, Any]],
    ) -> List[DBSLRStudyCandidate]:
        """Batch add candidate studies to an SLR."""
        created_studies = []
        for study_data in studies:
            candidate = DBSLRStudyCandidate(
                id=uuid.uuid4(),
                review_id=review_id,
                title=study_data.get("title", "Untitled Study"),
                authors=study_data.get("authors", []),
                publication_year=study_data.get("publication_year"),
                venue=study_data.get("venue"),
                doi=study_data.get("doi"),
                url=study_data.get("url"),
                abstract=study_data.get("abstract"),
                screening_status=study_data.get("screening_status", "identified"),
                exclusion_reason=study_data.get("exclusion_reason"),
                relevance_score=study_data.get("relevance_score", 0.0),
                methodology_type=study_data.get("methodology_type"),
                sample_size=study_data.get("sample_size"),
                effect_size=study_data.get("effect_size"),
                variance=study_data.get("variance"),
                standard_error=study_data.get("standard_error"),
                confidence_interval_low=study_data.get("confidence_interval_low"),
                confidence_interval_high=study_data.get("confidence_interval_high"),
                metric_name=study_data.get("metric_name"),
                metadata_json=study_data.get("metadata_json", {}),
            )
            self.session.add(candidate)
            created_studies.append(candidate)

        await self.session.commit()
        await self.recalculate_review_counts(review_id)
        for s in created_studies:
            await self.session.refresh(s)
        return created_studies

    async def get_candidate_study(self, candidate_id: uuid.UUID) -> Optional[DBSLRStudyCandidate]:
        """Fetch candidate study with risk of bias."""
        stmt = (
            select(DBSLRStudyCandidate)
            .options(selectinload(DBSLRStudyCandidate.risk_of_bias))
            .where(DBSLRStudyCandidate.id == candidate_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_candidate_screening(
        self,
        candidate_id: uuid.UUID,
        screening_status: str,
        exclusion_reason: Optional[str] = None,
        relevance_score: Optional[float] = None,
        methodology_type: Optional[str] = None,
        effect_size: Optional[float] = None,
        variance: Optional[float] = None,
        sample_size: Optional[int] = None,
    ) -> Optional[DBSLRStudyCandidate]:
        """Update screening status and extracted parameters for a study."""
        values: Dict[str, Any] = {
            "screening_status": screening_status,
            "updated_at": datetime.now(timezone.utc),
        }
        if exclusion_reason is not None:
            values["exclusion_reason"] = exclusion_reason
        if relevance_score is not None:
            values["relevance_score"] = relevance_score
        if methodology_type is not None:
            values["methodology_type"] = methodology_type
        if effect_size is not None:
            values["effect_size"] = effect_size
        if variance is not None:
            values["variance"] = variance
        if sample_size is not None:
            values["sample_size"] = sample_size

        stmt = (
            update(DBSLRStudyCandidate)
            .where(DBSLRStudyCandidate.id == candidate_id)
            .values(**values)
            .returning(DBSLRStudyCandidate)
        )
        result = await self.session.execute(stmt)
        candidate = result.scalars().first()
        if candidate:
            await self.session.commit()
            await self.recalculate_review_counts(candidate.review_id)
            await self.session.refresh(candidate)
        return candidate

    async def list_candidate_studies(
        self,
        review_id: uuid.UUID,
        screening_status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DBSLRStudyCandidate]:
        """Query candidate studies with optional status filter."""
        stmt = (
            select(DBSLRStudyCandidate)
            .options(selectinload(DBSLRStudyCandidate.risk_of_bias))
            .where(DBSLRStudyCandidate.review_id == review_id)
            .order_by(DBSLRStudyCandidate.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if screening_status:
            stmt = stmt.where(DBSLRStudyCandidate.screening_status == screening_status)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ---------------- Risk of Bias (RoB) Operations ----------------

    async def save_risk_of_bias(
        self,
        candidate_id: uuid.UUID,
        selection_bias: str = "low_risk",
        confounding_bias: str = "low_risk",
        measurement_bias: str = "low_risk",
        reporting_bias: str = "low_risk",
        overall_risk: str = "low_risk",
        justification_notes: Optional[str] = None,
        evaluated_by: str = "auto_arbiter",
        domain_scores: Optional[Dict[str, Any]] = None,
    ) -> DBRiskOfBiasAssessment:
        """Create or update structured risk of bias evaluation for a study."""
        existing_stmt = select(DBRiskOfBiasAssessment).where(
            DBRiskOfBiasAssessment.candidate_id == candidate_id
        )
        existing_res = await self.session.execute(existing_stmt)
        existing = existing_res.scalars().first()

        if existing:
            existing.selection_bias = selection_bias
            existing.confounding_bias = confounding_bias
            existing.measurement_bias = measurement_bias
            existing.reporting_bias = reporting_bias
            existing.overall_risk = overall_risk
            existing.justification_notes = justification_notes
            existing.evaluated_by = evaluated_by
            existing.domain_scores = domain_scores or {}
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        rob = DBRiskOfBiasAssessment(
            id=uuid.uuid4(),
            candidate_id=candidate_id,
            selection_bias=selection_bias,
            confounding_bias=confounding_bias,
            measurement_bias=measurement_bias,
            reporting_bias=reporting_bias,
            overall_risk=overall_risk,
            justification_notes=justification_notes,
            evaluated_by=evaluated_by,
            domain_scores=domain_scores or {},
        )
        self.session.add(rob)
        await self.session.commit()
        await self.session.refresh(rob)
        return rob

    # ---------------- Meta-Analysis Operations ----------------

    async def save_meta_analysis_report(
        self,
        review_id: uuid.UUID,
        synthesis_name: str,
        effect_metric: str,
        model_type: str,
        total_studies_analyzed: int,
        pooled_effect_size: float,
        pooled_ci_lower: float,
        pooled_ci_upper: float,
        pooled_p_value: float,
        z_score: float,
        q_statistic: float,
        degrees_of_freedom: int,
        i_squared: float,
        tau_squared: float,
        forest_plot_data: List[Dict[str, Any]],
        subgroup_analyses: Optional[Dict[str, Any]] = None,
        summary_markdown: Optional[str] = None,
    ) -> DBMetaAnalysisReport:
        """Save a quantitative meta-analysis report."""
        report = DBMetaAnalysisReport(
            id=uuid.uuid4(),
            review_id=review_id,
            synthesis_name=synthesis_name,
            effect_metric=effect_metric,
            model_type=model_type,
            total_studies_analyzed=total_studies_analyzed,
            pooled_effect_size=pooled_effect_size,
            pooled_ci_lower=pooled_ci_lower,
            pooled_ci_upper=pooled_ci_upper,
            pooled_p_value=pooled_p_value,
            z_score=z_score,
            q_statistic=q_statistic,
            degrees_of_freedom=degrees_of_freedom,
            i_squared=i_squared,
            tau_squared=tau_squared,
            forest_plot_data=forest_plot_data,
            subgroup_analyses=subgroup_analyses or {},
            summary_markdown=summary_markdown,
        )
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        logger.info("meta_analysis_report_saved", report_id=str(report.id), review_id=str(review_id))
        return report

    async def get_meta_analysis_report(self, report_id: uuid.UUID) -> Optional[DBMetaAnalysisReport]:
        """Fetch meta-analysis report by ID."""
        stmt = select(DBMetaAnalysisReport).where(DBMetaAnalysisReport.id == report_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_meta_analyses(self, review_id: uuid.UUID) -> List[DBMetaAnalysisReport]:
        """List all meta-analysis syntheses for a review."""
        stmt = (
            select(DBMetaAnalysisReport)
            .where(DBMetaAnalysisReport.review_id == review_id)
            .order_by(DBMetaAnalysisReport.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_slr_metrics(self) -> Dict[str, Any]:
        """Query platform-wide SLR and meta-analysis statistics."""
        total_reviews = await self.session.scalar(select(func.count(DBLiteratureReview.id))) or 0
        total_candidates = await self.session.scalar(select(func.count(DBSLRStudyCandidate.id))) or 0
        total_included = await self.session.scalar(
            select(func.count(DBSLRStudyCandidate.id)).where(DBSLRStudyCandidate.screening_status == "included")
        ) or 0
        total_meta_analyses = await self.session.scalar(select(func.count(DBMetaAnalysisReport.id))) or 0

        return {
            "total_reviews": total_reviews,
            "total_candidates": total_candidates,
            "total_included_studies": total_included,
            "total_meta_analyses": total_meta_analyses,
            "average_inclusion_rate": round((total_included / max(1, total_candidates)) * 100, 2),
        }
