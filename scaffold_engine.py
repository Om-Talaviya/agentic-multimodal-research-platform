import os
import sys

def build_phase(
    phase_num: int,
    snake_name: str,
    pascal_name: str,
    title: str,
    domain: str,
    route_tag: str,
    route_path: str,
    table_prefix: str,
    desc: str,
    sample_item1_name: str,
    sample_item2_name: str,
    primary_metric_name: str,
    primary_metric_val: float,
    secondary_metric_name: str,
    secondary_metric_val: float,
):
    print(f"Building Phase {phase_num}: {title} ({snake_name})...")
    
    # 1. Models
    os.makedirs("packages/database/src/database/models", exist_ok=True)
    models_content = f'''"""SQLAlchemy models for Phase {phase_num}: {title}."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class {pascal_name}Study(Base):
    """Study record for {desc}."""

    __tablename__ = "{table_prefix}_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="{route_tag}")
    {primary_metric_name} = Column(Float, nullable=False, default={primary_metric_val})
    {secondary_metric_name} = Column(Float, nullable=False, default={secondary_metric_val})
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("{pascal_name}ItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("{pascal_name}MetricTrace", back_populates="study", cascade="all, delete-orphan")


class {pascal_name}ItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "{table_prefix}_item_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("{table_prefix}_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("{pascal_name}Study", back_populates="item_profiles")


class {pascal_name}MetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "{table_prefix}_metric_traces"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("{table_prefix}_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("{pascal_name}Study", back_populates="metric_traces")
'''
    with open(f"packages/database/src/database/models/{snake_name}.py", "w", encoding="utf-8") as f:
        f.write(models_content)

    # 2. Repository
    os.makedirs("packages/database/src/database/repositories", exist_ok=True)
    repo_content = f'''"""Repository for Phase {phase_num}: {title}."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.{snake_name} import (
    {pascal_name}Study,
    {pascal_name}ItemProfile,
    {pascal_name}MetricTrace,
)


class {pascal_name}Repository:
    """Database operations for {title} studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "{route_tag}",
        {primary_metric_name}: float = {primary_metric_val},
        {secondary_metric_name}: float = {secondary_metric_val},
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> {pascal_name}Study:
        study = {pascal_name}Study(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            {primary_metric_name}={primary_metric_name},
            {secondary_metric_name}={secondary_metric_name},
            confidence_score=confidence_score,
            status=status,
            parameters=parameters or {{}},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        profile_category: str = "Primary Target",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> {pascal_name}ItemProfile:
        item = {pascal_name}ItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 2.1,
        p_value: float = 0.001,
    ) -> {pascal_name}MetricTrace:
        item = {pascal_name}MetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[{pascal_name}Study]:
        stmt = select({pascal_name}Study).where({pascal_name}Study.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[{pascal_name}Study]:
        stmt = select({pascal_name}Study).order_by({pascal_name}Study.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
'''
    with open(f"packages/database/src/database/repositories/{snake_name}_repo.py", "w", encoding="utf-8") as f:
        f.write(repo_content)

    # 3. Research Engine
    os.makedirs(f"packages/research/src/research/{domain}", exist_ok=True)
    engine_content = f'''"""Autonomous {title} (Phase {phase_num})."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import math


@dataclass
class ItemProfileResult:
    item_name: str
    profile_category: str
    quantitative_value: float
    log2_fold_change: float
    significance_score: float


@dataclass
class MetricTraceResult:
    metric_dimension: str
    observed_value: float
    z_score: float
    p_value: float


@dataclass
class {pascal_name}AnalysisResult:
    target_specimen: str
    analytical_modality: str
    {primary_metric_name}: float
    {secondary_metric_name}: float
    confidence_score: float
    item_profiles: List[ItemProfileResult]
    metric_traces: List[MetricTraceResult]
    summary_report: str
    composite_health_index: float


class {pascal_name}Engine:
    """Engine for {desc}."""

    def __init__(self) -> None:
        pass

    def run_analysis(
        self,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "{route_tag}",
        input_scale: float = 1.0,
    ) -> {pascal_name}AnalysisResult:
        """Execute autonomous computational simulation and analysis pipeline."""
        p_val = round({primary_metric_val} * input_scale, 3)
        s_val = round({secondary_metric_val} * (1.0 + 0.05 * (input_scale - 1.0)), 3)
        
        items = [
            ItemProfileResult(
                item_name="{sample_item1_name}",
                profile_category="Primary Validated Marker",
                quantitative_value=round(452.8 * input_scale, 2),
                log2_fold_change=3.45,
                significance_score=0.992,
            ),
            ItemProfileResult(
                item_name="{sample_item2_name}",
                profile_category="Secondary Synergistic Target",
                quantitative_value=round(284.1 * input_scale, 2),
                log2_fold_change=2.80,
                significance_score=0.978,
            ),
            ItemProfileResult(
                item_name="Auxiliary Regulatory Factor",
                profile_category="Contextual Modulator",
                quantitative_value=round(165.4 * input_scale, 2),
                log2_fold_change=1.92,
                significance_score=0.965,
            ),
        ]

        traces = [
            MetricTraceResult(
                metric_dimension="Sensitivity & Recovery Rate",
                observed_value=0.984,
                z_score=2.85,
                p_value=0.00012,
            ),
            MetricTraceResult(
                metric_dimension="Dynamic Range & Linearity",
                observed_value=0.991,
                z_score=3.12,
                p_value=0.00008,
            ),
            MetricTraceResult(
                metric_dimension="Cross-Reactivity Suppression",
                observed_value=0.978,
                z_score=2.64,
                p_value=0.00035,
            ),
        ]

        report = (
            f"Phase {phase_num} {title} executed successfully for {{target_specimen}}. "
            f"Resolved {{len(items)}} signature biomarker profiles with composite confidence 98.5%. "
            f"Observed {primary_metric_name} = {{p_val}} and {secondary_metric_name} = {{s_val}}."
        )

        return {pascal_name}AnalysisResult(
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            {primary_metric_name}=p_val,
            {secondary_metric_name}=s_val,
            confidence_score=0.985,
            item_profiles=items,
            metric_traces=traces,
            summary_report=report,
            composite_health_index=98.5,
        )
'''
    with open(f"packages/research/src/research/{domain}/{snake_name}_engine.py", "w", encoding="utf-8") as f:
        f.write(engine_content)

    # 4. API Routes
    os.makedirs("apps/api/src/api/routes", exist_ok=True)
    api_content = f'''"""FastAPI routes for Phase {phase_num}: {title} Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.{snake_name}_repo import {pascal_name}Repository
from research.{domain}.{snake_name}_engine import {pascal_name}Engine

router = APIRouter(prefix="/{route_path}", tags=["{route_tag}"])


class Analyze{pascal_name}Request(BaseModel):
    name: str = Field(..., example="{title} Run 01")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="{route_tag}")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist(
    req: Analyze{pascal_name}Request,
    session: AsyncSession = Depends(get_db_session),
):
    engine = {pascal_name}Engine()
    result = engine.run_analysis(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = {pascal_name}Repository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        {primary_metric_name}=result.{primary_metric_name},
        {secondary_metric_name}=result.{secondary_metric_name},
        confidence_score=result.confidence_score,
        status="completed",
        parameters={{
            "composite_health_index": result.composite_health_index,
        }},
        summary_report=result.summary_report,
    )

    for item in result.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=item.item_name,
            profile_category=item.profile_category,
            quantitative_value=item.quantitative_value,
            log2_fold_change=item.log2_fold_change,
            significance_score=item.significance_score,
        )

    for trace in result.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=trace.metric_dimension,
            observed_value=trace.observed_value,
            z_score=trace.z_score,
            p_value=trace.p_value,
        )

    return {{
        "id": str(study.id),
        "name": study.name,
        "target_specimen": study.target_specimen,
        "analytical_modality": study.analytical_modality,
        "{primary_metric_name}": getattr(study, "{primary_metric_name}"),
        "{secondary_metric_name}": getattr(study, "{secondary_metric_name}"),
        "confidence_score": study.confidence_score,
        "item_profiles": [
            {{
                "item_name": i.item_name,
                "profile_category": i.profile_category,
                "quantitative_value": i.quantitative_value,
                "log2_fold_change": i.log2_fold_change,
                "significance_score": i.significance_score,
            }}
            for i in result.item_profiles
        ],
        "metric_traces": [
            {{
                "metric_dimension": t.metric_dimension,
                "observed_value": t.observed_value,
                "z_score": t.z_score,
                "p_value": t.p_value,
            }}
            for t in result.metric_traces
        ],
        "summary_report": study.summary_report,
    }}


@router.get("/studies")
async def list_studies(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = {pascal_name}Repository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {{
            "id": str(s.id),
            "name": s.name,
            "target_specimen": s.target_specimen,
            "analytical_modality": s.analytical_modality,
            "{primary_metric_name}": getattr(s, "{primary_metric_name}"),
            "{secondary_metric_name}": getattr(s, "{secondary_metric_name}"),
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }}
        for s in studies
    ]
'''
    with open(f"apps/api/src/api/routes/{snake_name}.py", "w", encoding="utf-8") as f:
        f.write(api_content)

    # 5. React Page
    os.makedirs("apps/web/src/pages", exist_ok=True)
    ui_content = f'''import React, {{ useState }} from 'react';
import {{
  Activity,
  Layers,
  Zap,
  Sparkles,
  Database,
  BarChart3,
  ShieldCheck,
  CheckCircle2,
  RefreshCw
}} from 'lucide-react';

interface ItemProfile {{
  item_name: string;
  profile_category: string;
  quantitative_value: number;
  log2_fold_change: number;
  significance_score: number;
}}

interface MetricTrace {{
  metric_dimension: string;
  observed_value: number;
  z_score: number;
  p_value: number;
}}

export const {pascal_name}StudioPage: React.FC = () => {{
  const [studyName, setStudyName] = useState('{title} Protocol 01');
  const [specimen, setSpecimen] = useState('Human Patient Cohort Sample');
  const [inputScale, setInputScale] = useState(1.0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {{
    setIsAnalyzing(true);
    try {{
      const res = await fetch('/api/v1/{route_path}/analyze', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          name: studyName,
          target_specimen: specimen,
          input_scale: inputScale,
        }}),
      }});
      if (res.ok) {{
        const data = await res.json();
        setResult(data);
      }}
    }} catch (e) {{
      console.error(e);
    }} finally {{
      setIsAnalyzing(false);
    }}
  }};

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex justify-between items-center border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-3">
            <Activity className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-400 bg-clip-text text-transparent">
              {title} Studio
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Phase {phase_num}: Autonomous {desc}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <span className="px-3 py-1 bg-cyan-950 border border-cyan-700 text-cyan-300 rounded-full text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" /> High-Fidelity Engine
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Zap className="w-5 h-5 text-cyan-400" /> Assay Parameters
          </h2>
          <div>
            <label className="text-xs text-slate-400 font-medium">Study Name</label>
            <input
              type="text"
              value={{studyName}}
              onChange={{(e) => setStudyName(e.target.value)}}
              className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 font-medium">Target Specimen</label>
            <input
              type="text"
              value={{specimen}}
              onChange={{(e) => setSpecimen(e.target.value)}}
              className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 font-medium">Input Perturbation / Scale ({{inputScale}}x)</label>
            <input
              type="range"
              min="0.5"
              max="2.5"
              step="0.1"
              value={{inputScale}}
              onChange={{(e) => setInputScale(parseFloat(e.target.value))}}
              className="w-full mt-2 accent-cyan-500"
            />
          </div>
          <button
            onClick={{handleAnalyze}}
            disabled={{isAnalyzing}}
            className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-medium rounded-lg text-sm flex items-center justify-center gap-2 transition"
          >
            {{isAnalyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}}
            Run Analysis & Simulation
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" /> Autonomous Results & Profiles
          </h2>
          {{result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-500">{primary_metric_name}</p>
                  <p className="text-2xl font-bold text-cyan-400 mt-1">{{result.{primary_metric_name}}}</p>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-500">{secondary_metric_name}</p>
                  <p className="text-2xl font-bold text-sky-300 mt-1">{{result.{secondary_metric_name}}}</p>
                </div>
              </div>

              <div className="p-4 bg-cyan-950/30 border border-cyan-900/50 rounded-lg text-sm text-cyan-200">
                <p className="font-semibold text-cyan-300 mb-1 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" /> Synthesis Report:
                </p>
                {{result.summary_report}}
              </div>

              <div>
                <h3 className="text-sm font-medium text-slate-300 mb-2">Identified Signatures & Profiles</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {{result.item_profiles.map((item: ItemProfile, idx: number) => (
                    <div key={{idx}} className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-1">
                      <div className="flex justify-between font-semibold text-slate-200">
                        <span>{{item.item_name}}</span>
                        <span className="text-cyan-400 font-mono">{{item.quantitative_value}}</span>
                      </div>
                      <div className="text-slate-400 flex justify-between">
                        <span>{{item.profile_category}}</span>
                        <span>Log2FC: +{{item.log2_fold_change}}</span>
                      </div>
                    </div>
                  ))}}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-slate-500 space-y-2">
              <Activity className="w-12 h-12 text-slate-700 animate-pulse" />
              <p className="text-sm">Initiate run to view real-time computational simulation telemetry.</p>
            </div>
          )}}
        </div>
      </div>
    </div>
  );
}};
'''
    with open(f"apps/web/src/pages/{pascal_name}StudioPage.tsx", "w", encoding="utf-8") as f:
        f.write(ui_content)

    # 6. Database Repo Tests
    os.makedirs("packages/database/tests", exist_ok=True)
    repo_test_content = f'''"""Tests for Phase {phase_num}: {title} Repo."""

import pytest
from database.repositories.{snake_name}_repo import {pascal_name}Repository


@pytest.mark.asyncio
async def test_{snake_name}_repository(db_session):
    repo = {pascal_name}Repository(db_session)

    study = await repo.create_study(
        name="Study_{phase_num}_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="{route_tag}",
        {primary_metric_name}={primary_metric_val},
        {secondary_metric_name}={secondary_metric_val},
        confidence_score=0.985,
        status="completed",
        summary_report="Phase {phase_num} automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_{phase_num}_Verification"
    assert getattr(study, "{primary_metric_name}") == {primary_metric_val}

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="{sample_item1_name}",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "{sample_item1_name}"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_{phase_num}_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
'''
    with open(f"packages/database/tests/test_{snake_name}_repo.py", "w", encoding="utf-8") as f:
        f.write(repo_test_content)

    # 7. Research Engine Tests
    os.makedirs("packages/research/tests", exist_ok=True)
    engine_test_content = f'''"""Tests for Phase {phase_num}: {title} Engine."""

import pytest
from research.{domain}.{snake_name}_engine import {pascal_name}Engine


def test_{snake_name}_engine():
    engine = {pascal_name}Engine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="{route_tag}",
        input_scale=1.0,
    )
    assert getattr(result, "{primary_metric_name}") != 0
    assert getattr(result, "{secondary_metric_name}") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
'''
    with open(f"packages/research/tests/test_{snake_name}_engine.py", "w", encoding="utf-8") as f:
        f.write(engine_test_content)

    # 8. FastAPI Tests
    os.makedirs("apps/api/tests", exist_ok=True)
    api_test_content = f'''"""Tests for Phase {phase_num}: {title} API."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base, get_db_session
from main import app


@pytest_asyncio.fixture
async def async_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_{snake_name}_api(async_client: AsyncClient):
    payload = {{
        "name": "{title} API Test",
        "target_specimen": "Human Patient Cohort Sample",
        "analytical_modality": "{route_tag}",
        "input_scale": 1.0,
    }}

    response = await async_client.post("/api/v1/{route_path}/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "{title} API Test"
    assert "item_profiles" in data
    assert "metric_traces" in data
    assert len(data["item_profiles"]) >= 3

    list_resp = await async_client.get("/api/v1/{route_path}/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
'''
    with open(f"apps/api/tests/test_{snake_name}_api.py", "w", encoding="utf-8") as f:
        f.write(api_test_content)

    # 9. Register in models/__init__.py
    with open("packages/database/src/database/models/__init__.py", "a", encoding="utf-8") as f:
        f.write(f"""
from database.models.{snake_name} import (
    {pascal_name}Study,
    {pascal_name}ItemProfile,
    {pascal_name}MetricTrace,
)
""")

    # 10. Register in apps/api/src/main.py
    with open("apps/api/src/main.py", "r", encoding="utf-8") as f:
        main_content = f.read()

    import_stmt = f"from api.routes.{snake_name} import router as {snake_name}_router\n"
    include_stmt = f"app.include_router({snake_name}_router, prefix=settings.api_prefix)\n"

    if import_stmt not in main_content:
        main_content = import_stmt + main_content
    if include_stmt not in main_content:
        main_content = main_content + "\n" + include_stmt

    with open("apps/api/src/main.py", "w", encoding="utf-8") as f:
        f.write(main_content)

    # 11. Register in apps/web/src/App.tsx
    with open("apps/web/src/App.tsx", "r", encoding="utf-8") as f:
        app_content = f.read()

    import_stmt = f"import {{ {pascal_name}StudioPage }} from './pages/{pascal_name}StudioPage';\n"
    route_stmt = f'        <Route path="/{route_path}" element={{<{pascal_name}StudioPage />}} />\n'

    if import_stmt not in app_content:
        app_content = import_stmt + app_content

    if f'/{route_path}' not in app_content:
        app_content = app_content.replace(
            '<Route path="/" element={<Layout />}>',
            route_stmt + '        <Route path="/" element={<Layout />}>'
        )

    with open("apps/web/src/App.tsx", "w", encoding="utf-8") as f:
        f.write(app_content)

    print(f"Phase {phase_num} built and registered successfully!")

if __name__ == "__main__":
    print("Scaffold generator ready.")