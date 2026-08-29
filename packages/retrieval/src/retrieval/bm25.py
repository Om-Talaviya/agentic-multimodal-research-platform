"""BM25 lexical search index."""

import math
import re
from typing import Any, Dict, List, Optional, Set
from retrieval.vector_store import SearchResult


def tokenize(text: str) -> List[str]:
    """Tokenize text into normalized alphanumeric terms."""
    if not text:
        return []
    text = text.lower()
    tokens = re.findall(r"\b[a-z0-9_]+\b", text)
    return tokens


class BM25Index:
    """In-memory Okapi BM25 search index."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._doc_ids: List[str] = []
        self._doc_map: Dict[str, Dict[str, Any]] = {}
        self._doc_len: Dict[str, int] = {}
        self._doc_freqs: Dict[str, Dict[str, int]] = {}  # doc_id -> {term: count}
        self._term_doc_count: Dict[str, int] = {}  # term -> count of docs containing term
        self._avg_doc_len: float = 0.0

    def _update_avg_len(self) -> None:
        if not self._doc_len:
            self._avg_doc_len = 0.0
        else:
            self._avg_doc_len = sum(self._doc_len.values()) / len(self._doc_len)

    def add(self, id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add or update a single document in the BM25 index."""
        if id in self._doc_map:
            self.delete([id])

        tokens = tokenize(text)
        term_counts: Dict[str, int] = {}
        for t in tokens:
            term_counts[t] = term_counts.get(t, 0) + 1

        self._doc_ids.append(id)
        self._doc_map[id] = {
            "content": text,
            "metadata": metadata or {},
        }
        self._doc_len[id] = len(tokens)
        self._doc_freqs[id] = term_counts

        for term in term_counts.keys():
            self._term_doc_count[term] = self._term_doc_count.get(term, 0) + 1

        self._update_avg_len()

    def add_batch(self, documents: List[Dict[str, Any]]) -> None:
        """Add multiple documents: each item is {'id': str, 'content': str, 'metadata': dict}."""
        for doc in documents:
            self.add(id=doc["id"], text=doc["content"], metadata=doc.get("metadata"))

    def delete(self, ids: List[str]) -> None:
        """Remove documents from the index."""
        for doc_id in ids:
            if doc_id not in self._doc_map:
                continue

            term_counts = self._doc_freqs.pop(doc_id, {})
            for term in term_counts.keys():
                if term in self._term_doc_count:
                    self._term_doc_count[term] -= 1
                    if self._term_doc_count[term] <= 0:
                        del self._term_doc_count[term]

            self._doc_len.pop(doc_id, None)
            self._doc_map.pop(doc_id, None)
            if doc_id in self._doc_ids:
                self._doc_ids.remove(doc_id)

        self._update_avg_len()

    def clear(self) -> None:
        """Clear the entire index."""
        self._doc_ids.clear()
        self._doc_map.clear()
        self._doc_len.clear()
        self._doc_freqs.clear()
        self._term_doc_count.clear()
        self._avg_doc_len = 0.0

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Score and return top_k matching documents for the query."""
        query_terms = tokenize(query)
        if not query_terms or not self._doc_ids:
            return []

        n_docs = len(self._doc_ids)
        scores: Dict[str, float] = {}

        # Compute BM25 scores
        for term in query_terms:
            doc_count = self._term_doc_count.get(term, 0)
            if doc_count == 0:
                continue

            # Inverse Document Frequency (IDF) with smoothing
            idf = math.log(1.0 + (n_docs - doc_count + 0.5) / (doc_count + 0.5))

            for doc_id in self._doc_ids:
                tf = self._doc_freqs[doc_id].get(term, 0)
                if tf == 0:
                    continue

                d_len = self._doc_len.get(doc_id, 0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (d_len / (self._avg_doc_len or 1.0)))
                term_score = idf * ((tf * (self.k1 + 1.0)) / (denom or 1.0))

                scores[doc_id] = scores.get(doc_id, 0.0) + term_score

        if not scores:
            return []

        # Filter and rank
        scored_results: List[tuple[float, str]] = []
        for doc_id, score in scores.items():
            if score <= 0.0:
                continue
            doc_info = self._doc_map[doc_id]
            if filter:
                match = True
                for k, v in filter.items():
                    if doc_info["metadata"].get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            scored_results.append((score, doc_id))

        scored_results.sort(key=lambda x: (-x[0], x[1]))

        results: List[SearchResult] = []
        for score, doc_id in scored_results[:top_k]:
            doc_info = self._doc_map[doc_id]
            results.append(
                SearchResult(
                    id=doc_id,
                    score=float(score),
                    content=doc_info["content"],
                    metadata=dict(doc_info["metadata"]),
                )
            )

        return results

    def count(self) -> int:
        """Return total indexed documents."""
        return len(self._doc_ids)
