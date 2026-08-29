"""Reranker service for scoring and re-ordering retrieval candidates."""

import re
from typing import List, Optional
from ai.providers.base import RerankerProvider
from ai.providers.router import ModelRouter
from ai.schemas import RerankRequest
from retrieval.vector_store import SearchResult
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)


def lexical_overlap_score(query: str, text: str) -> float:
    """Compute normalized token overlap score between query and text."""
    if not query or not text:
        return 0.0
    q_tokens = set(re.findall(r"\b[a-z0-9_]+\b", query.lower()))
    t_tokens = set(re.findall(r"\b[a-z0-9_]+\b", text.lower()))
    if not q_tokens or not t_tokens:
        return 0.0
    intersection = q_tokens.intersection(t_tokens)
    return len(intersection) / len(q_tokens)


class Reranker:
    """Reranks candidate search results using neural cross-encoders or fallback heuristic scoring."""

    def __init__(
        self,
        model_router: Optional[ModelRouter] = None,
        provider: Optional[RerankerProvider] = None,
        default_model: Optional[str] = None,
    ) -> None:
        self.router = model_router
        self.provider = provider
        self.default_model = default_model or settings.default_reranker_model

    def _get_provider(self) -> Optional[RerankerProvider]:
        if self.provider is not None:
            return self.provider
        if self.router is not None:
            try:
                return self.router.select_reranker()
            except Exception:
                return None
        return None

    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: int = 5,
    ) -> List[SearchResult]:
        """Rerank search results given a query."""
        if not results or not query:
            return results[:top_k]

        provider = self._get_provider()
        if provider is not None:
            try:
                documents = [r.content for r in results]
                req = RerankRequest(
                    query=query,
                    documents=documents,
                    model=self.default_model,
                    top_k=top_k,
                )
                resp = await provider.rerank(req)
                if resp.results:
                    reranked: List[SearchResult] = []
                    for item in resp.results:
                        idx = item.get("index", 0)
                        score = float(item.get("score", 0.0))
                        if 0 <= idx < len(results):
                            orig = results[idx]
                            reranked.append(
                                SearchResult(
                                    id=orig.id,
                                    score=score,
                                    content=orig.content,
                                    metadata=dict(orig.metadata),
                                    embedding=orig.embedding,
                                )
                            )
                    if reranked:
                        return reranked[:top_k]
            except Exception as e:
                logger.warning("Neural reranking failed, falling back to heuristic scoring", error=str(e))

        # Fallback: Combine original score with lexical overlap bonus
        scored_candidates: List[tuple[float, SearchResult]] = []
        for r in results:
            overlap = lexical_overlap_score(query, r.content)
            # 70% original score + 30% lexical overlap boost
            combined_score = float(r.score * 0.7 + overlap * 0.3)
            scored_candidates.append((
                combined_score,
                SearchResult(
                    id=r.id,
                    score=combined_score,
                    content=r.content,
                    metadata=dict(r.metadata),
                    embedding=r.embedding,
                ),
            ))

        scored_candidates.sort(key=lambda x: (-x[0], x[1].id))
        return [item[1] for item in scored_candidates[:top_k]]
