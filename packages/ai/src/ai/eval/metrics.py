"""Deterministic evaluation metrics for AI models and research pipelines."""
import re
from typing import Dict, List, Optional
from ai.eval.schemas import BenchmarkSample, EvaluationMetric


class EvaluationMetricsEngine:
    """Calculates quantitative benchmark evaluation metrics across multiple dimensions."""

    @staticmethod
    def calculate_factual_accuracy(response_text: str, sample: BenchmarkSample) -> float:
        """Calculate factual keyword coverage and phrase precision [0.0 - 1.0]."""
        if not sample.expected_keywords:
            return 1.0

        text_lower = response_text.lower()
        matched = sum(1 for kw in sample.expected_keywords if kw.lower() in text_lower)
        return round(matched / len(sample.expected_keywords), 4)

    @staticmethod
    def calculate_reasoning_depth(response_text: str, sample: BenchmarkSample) -> float:
        """Assess logical reasoning structure, multi-step explanations, and step markers."""
        score = 0.5  # Base score for coherent text

        # Check for sequential step markers (1., 2., Step 1, First, Therefore, Because, However)
        reasoning_markers = [
            r"\b(first|second|third|finally)\b",
            r"\b(therefore|consequently|as a result|furthermore)\b",
            r"\b(because|since|due to|whereas)\b",
            r"\b(step \d+|\d+\.)\b",
            r"\b(trade-off|comparison|contrast|advantage|limitation)\b",
        ]

        found_markers = 0
        text_lower = response_text.lower()
        for pattern in reasoning_markers:
            if re.search(pattern, text_lower):
                found_markers += 1

        marker_bonus = min(found_markers * 0.1, 0.4)
        score += marker_bonus

        # Length / substantive elaboration bonus
        word_count = len(response_text.split())
        if word_count >= 100:
            score += 0.1
        elif word_count < 30:
            score -= 0.2

        return min(max(round(score, 4), 0.0), 1.0)

    @staticmethod
    def calculate_retrieval_faithfulness(response_text: str, sample: BenchmarkSample) -> float:
        """Evaluate whether response claims are strictly grounded in provided context."""
        if not sample.context:
            return 1.0  # Open-domain prompt without strict context constraints

        context_words = set(re.findall(r"\w+", sample.context.lower()))
        response_words = re.findall(r"\w+", response_text.lower())
        
        # Filter stopwords
        stopwords = {"the", "a", "an", "is", "are", "and", "or", "in", "of", "to", "for", "with", "that", "this", "it"}
        content_response_words = [w for w in response_words if len(w) > 3 and w not in stopwords]

        if not content_response_words:
            return 0.5

        grounded_count = sum(1 for w in content_response_words if w in context_words)
        ratio = grounded_count / len(content_response_words)
        
        # Scaling: standard factual responses typically share 40-70% vocabulary with ground truth context
        scaled = min(ratio * 1.5, 1.0)
        return round(scaled, 4)

    @staticmethod
    def calculate_citation_precision(response_text: str, sample: BenchmarkSample) -> float:
        """Check presence of required citations or source coordinates."""
        if not sample.required_citations:
            return 1.0

        text_lower = response_text.lower()
        matched = sum(1 for cite in sample.required_citations if cite.lower() in text_lower)
        return round(matched / len(sample.required_citations), 4)

    @classmethod
    def evaluate_sample(
        cls,
        response_text: str,
        sample: BenchmarkSample,
        latency_ms: int,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
    ) -> Dict[str, float]:
        """Compute all evaluation metrics for a single sample."""
        acc = cls.calculate_factual_accuracy(response_text, sample)
        reasoning = cls.calculate_reasoning_depth(response_text, sample)
        faithfulness = cls.calculate_retrieval_faithfulness(response_text, sample)
        citations = cls.calculate_citation_precision(response_text, sample)

        # Overall composite score
        overall = round((acc * 0.35) + (reasoning * 0.30) + (faithfulness * 0.20) + (citations * 0.15), 4)

        return {
            EvaluationMetric.FACTUAL_ACCURACY.value: acc,
            EvaluationMetric.REASONING_DEPTH.value: reasoning,
            EvaluationMetric.RETRIEVAL_FAITHFULNESS.value: faithfulness,
            EvaluationMetric.CITATION_PRECISION.value: citations,
            EvaluationMetric.LATENCY_MS.value: float(latency_ms),
            EvaluationMetric.COST_EFFICIENCY.value: float(cost_usd),
            EvaluationMetric.OVERALL_SCORE.value: overall,
        }
