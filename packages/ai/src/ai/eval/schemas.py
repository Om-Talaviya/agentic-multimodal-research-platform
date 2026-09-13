"""Benchmark datasets and data schemas for automated AI model evaluation."""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from shared.types import JSONDict


class BenchmarkCategory(str, Enum):
    REASONING = "reasoning"
    FACTUAL_RETRIEVAL = "factual_retrieval"
    SYNTHESIS = "synthesis"
    CITATION_ACCURACY = "citation_accuracy"
    CODING = "coding"


class EvaluationMetric(str, Enum):
    FACTUAL_ACCURACY = "factual_accuracy"
    REASONING_DEPTH = "reasoning_depth"
    RETRIEVAL_FAITHFULNESS = "retrieval_faithfulness"
    CITATION_PRECISION = "citation_precision"
    LATENCY_MS = "latency_ms"
    COST_EFFICIENCY = "cost_efficiency"
    OVERALL_SCORE = "overall_score"


class BenchmarkSample(BaseModel):
    """Individual golden ground-truth evaluation case."""
    model_config = ConfigDict(protected_namespaces=())

    id: str
    category: BenchmarkCategory
    prompt: str
    context: Optional[str] = None
    expected_answer: Optional[str] = None
    expected_keywords: List[str] = Field(default_factory=list)
    min_reasoning_steps: int = 1
    required_citations: List[str] = Field(default_factory=list)
    metadata: JSONDict = Field(default_factory=dict)


class BenchmarkDataset(BaseModel):
    """Collection of evaluation samples under a standardized benchmark suite."""
    name: str
    description: str
    version: str = "1.0.0"
    samples: List[BenchmarkSample] = Field(default_factory=list)


# Standard Built-in Golden Benchmark Suite for Research OS
DEFAULT_RESEARCH_BENCHMARK = BenchmarkDataset(
    name="research_core_eval_v1",
    description="Standardized multi-category golden benchmark evaluating reasoning depth, factual precision, and citations.",
    version="1.0.0",
    samples=[
        BenchmarkSample(
            id="eval_sample_1",
            category=BenchmarkCategory.FACTUAL_RETRIEVAL,
            prompt="What is the critical degradation mechanism of PLA bioplastics in marine environments?",
            context="Polylactic acid (PLA) requires industrial composting temperatures (>58°C) for hydrolysis. In ambient marine environments (15-20°C), microbial colonization is slow and abiotic hydrolysis rates are negligible, resulting in prolonged persistence exceeding 3-5 years.",
            expected_keywords=["industrial composting", "58°C", "hydrolysis", "marine", "persistence"],
            required_citations=["doc_marine_pla_section_2"],
        ),
        BenchmarkSample(
            id="eval_sample_2",
            category=BenchmarkCategory.REASONING,
            prompt="Compare solid-state batteries with liquid electrolyte lithium-ion batteries across volumetric energy density, dendrite mitigation, and thermal runaway thresholds.",
            expected_keywords=["solid electrolyte", "volumetric energy density", "dendrite", "thermal runaway", "safety"],
            min_reasoning_steps=3,
        ),
        BenchmarkSample(
            id="eval_sample_3",
            category=BenchmarkCategory.CITATION_ACCURACY,
            prompt="Extract the precise quantitative findings regarding microplastic retention rates from the provided study.",
            context="According to Smith et al. (2025), membrane bioreactors achieved a 99.4% retention efficiency for microplastics >50μm, whereas conventional sand filtration achieved only 68.2% retention.",
            expected_keywords=["99.4%", "membrane bioreactors", "68.2%", "sand filtration"],
            required_citations=["smith_2025_table_3"],
        ),
        BenchmarkSample(
            id="eval_sample_4",
            category=BenchmarkCategory.SYNTHESIS,
            prompt="Synthesize the primary trade-offs between dense neural vector retrieval and sparse BM25 indexing in hybrid RAG systems.",
            expected_keywords=["semantic", "lexical", "exact match", "out of vocabulary", "Reciprocal Rank Fusion", "RRF"],
            min_reasoning_steps=2,
        ),
    ],
)
