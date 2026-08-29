"""Hybrid retrieval engine combining dense vector search, BM25 lexical search, and RRF fusion."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from retrieval.bm25 import BM25Index
from retrieval.embedder import Embedder
from retrieval.reranker import Reranker
from retrieval.vector_store import SearchResult, VectorStore
from shared.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GroundedEvidence:
    """Grounded evidence passage retrieved for research synthesis."""

    chunk_id: str
    content: str
    score: float
    document_id: Optional[str] = None
    chunk_index: Optional[int] = None
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    modality: str = "text"
    dense_score: Optional[float] = None
    sparse_score: Optional[float] = None
    rrf_score: Optional[float] = None
    rerank_score: Optional[float] = None
    citation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "score": self.score,
            "modality": self.modality,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "citation": self.citation,
            "dense_score": self.dense_score,
            "sparse_score": self.sparse_score,
            "rrf_score": self.rrf_score,
            "rerank_score": self.rerank_score,
            "metadata": self.metadata,
        }


class HybridRetriever:
    """Hybrid search orchestrating dense embeddings, BM25 sparse search, RRF, and reranking."""

    def __init__(
        self,
        vector_store: VectorStore,
        bm25_index: BM25Index,
        embedder: Embedder,
        reranker: Optional[Reranker] = None,
        rrf_k: int = 60,
    ) -> None:
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.embedder = embedder
        self.reranker = reranker or Reranker()
        self.rrf_k = rrf_k

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        dense_top_k: int = 15,
        sparse_top_k: int = 15,
        filter: Optional[Dict[str, Any]] = None,
        apply_reranker: bool = True,
    ) -> List[GroundedEvidence]:
        """Perform hybrid retrieval with dense + sparse fusion and evidence grounding."""
        if not query.strip():
            return []

        # 1. Dense vector search
        dense_results: List[SearchResult] = []
        try:
            query_vector = await self.embedder.embed_text(query)
            if query_vector:
                dense_results = await self.vector_store.search(
                    query_vector=query_vector,
                    top_k=dense_top_k,
                    filter=filter,
                )
        except Exception as e:
            logger.warning("Dense search failed", error=str(e))

        # 2. Sparse BM25 search
        sparse_results: List[SearchResult] = []
        try:
            sparse_results = self.bm25_index.search(
                query=query,
                top_k=sparse_top_k,
                filter=filter,
            )
        except Exception as e:
            logger.warning("Sparse BM25 search failed", error=str(e))

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        dense_scores_map: Dict[str, float] = {}
        sparse_scores_map: Dict[str, float] = {}
        result_map: Dict[str, SearchResult] = {}

        for rank, res in enumerate(dense_results):
            rrf_scores[res.id] = rrf_scores.get(res.id, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            dense_scores_map[res.id] = res.score
            result_map[res.id] = res

        for rank, res in enumerate(sparse_results):
            rrf_scores[res.id] = rrf_scores.get(res.id, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            sparse_scores_map[res.id] = res.score
            if res.id not in result_map:
                result_map[res.id] = res

        if not rrf_scores:
            return []

        # Rank candidates by RRF score (descending) with doc_id tie-breaking
        sorted_candidates = sorted(
            rrf_scores.keys(),
            key=lambda doc_id: (-rrf_scores[doc_id], doc_id),
        )

        fused_results: List[SearchResult] = []
        for doc_id in sorted_candidates:
            res = result_map[doc_id]
            fused_results.append(
                SearchResult(
                    id=doc_id,
                    score=float(rrf_scores[doc_id]),
                    content=res.content,
                    metadata=dict(res.metadata),
                    embedding=res.embedding,
                )
            )

        # 4. Optional Reranking
        final_results = fused_results
        rerank_scores_map: Dict[str, float] = {}
        if apply_reranker and self.reranker is not None:
            rerank_candidates = fused_results[: max(top_k * 2, 10)]
            reranked = await self.reranker.rerank(query, rerank_candidates, top_k=top_k)
            if reranked:
                for r in reranked:
                    rerank_scores_map[r.id] = r.score
                final_results = reranked

        # 5. Build GroundedEvidence objects
        evidence_list: List[GroundedEvidence] = []
        for res in final_results[:top_k]:
            meta = res.metadata or {}
            doc_id = meta.get("document_id") or meta.get("doc_id")
            chunk_idx = meta.get("chunk_index")
            modality = meta.get("modality") or meta.get("type", "text")

            # Generate formal citation
            citation_parts = []
            if doc_id:
                citation_parts.append(f"Doc: {str(doc_id)[:8]}")
            if chunk_idx is not None:
                citation_parts.append(f"Chunk #{chunk_idx}")
            if meta.get("filename"):
                citation_parts.append(f"File: {meta['filename']}")
            if meta.get("page_number"):
                citation_parts.append(f"Page {meta['page_number']}")

            citation = " | ".join(citation_parts) if citation_parts else f"Chunk: {res.id[:8]}"

            evidence_list.append(
                GroundedEvidence(
                    chunk_id=res.id,
                    content=res.content,
                    score=res.score,
                    document_id=str(doc_id) if doc_id else None,
                    chunk_index=int(chunk_idx) if chunk_idx is not None else None,
                    start_char=meta.get("start_char"),
                    end_char=meta.get("end_char"),
                    modality=str(modality),
                    dense_score=dense_scores_map.get(res.id),
                    sparse_score=sparse_scores_map.get(res.id),
                    rrf_score=rrf_scores.get(res.id),
                    rerank_score=rerank_scores_map.get(res.id),
                    citation=citation,
                    metadata=meta,
                )
            )

        return evidence_list
