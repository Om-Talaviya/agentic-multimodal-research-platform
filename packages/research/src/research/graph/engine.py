"""Knowledge Graph Engine orchestrating extraction, entity resolution, and GraphRAG reasoning."""

import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID
from database.repositories.graph_repo import KnowledgeGraphRepository
from research.graph.models import (
    EntityType,
    GraphData,
    GraphExtractionResult,
    GraphPathResult,
    GraphPathStep,
    GraphTriplet,
    RelationType,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class KnowledgeGraphEngine:
    """Core research knowledge graph engine managing extraction, canonicalization, and GraphRAG."""

    def __init__(self, repo: KnowledgeGraphRepository) -> None:
        self.repo = repo

    async def extract_triplets_from_text(
        self,
        text: str,
        user_id: Optional[UUID] = None,
        job_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        confidence_threshold: float = 0.5,
    ) -> GraphExtractionResult:
        """Extract entity-relation triplets from text and persist to graph repository.

        Uses deterministic rule-based pattern extraction for standard academic/technical relations
        (e.g., 'X degrades in Y', 'X developed by Y', 'X enhances Y', 'X contradicts Y', 'X uses Y').
        """
        if not text or not text.strip():
            return GraphExtractionResult(entities_count=0, relations_count=0)

        triplets: List[GraphTriplet] = []
        extracted_entities: Set[str] = set()

        # Regular expression patterns for key academic and domain relations
        patterns = [
            # X enhances / increases / reduces Y
            (
                r"(?P<source>[A-Z][A-Za-z0-9\s\-]{2,30}?)\s+(?:significantly\s+)?(?P<rel>enhances?|increases?|improves?|reduces?|decreases?)\s+(?P<target>[a-z0-9\s\-]{3,40}?)(?:\.|\,|$|\s+by)",
                "ENHANCES",
                "METRIC",
            ),
            # X degrades in / exposed to Y
            (
                r"(?P<source>[A-Z][A-Za-z0-9\s\-]{2,30}?)\s+(?:degrades?|biodegrades?)\s+in\s+(?P<target>[A-Za-z0-9\s\-]{3,40}?)(?:\.|\,|$|\s+at|\s+within)",
                "DEGRADES_IN",
                "ENVIRONMENT",
            ),
            # X developed by / synthesized by / authored by Y
            (
                r"(?P<source>[A-Z][A-Za-z0-9\s\-]{2,30}?)\s+(?:was\s+)?(?:developed|synthesized|authored|proposed)\s+by\s+(?P<target>[A-Z][A-Za-z0-9\s\-]{2,40}?)(?:\.|\,|$|\s+in)",
                "DEVELOPED_BY",
                "ORGANIZATION",
            ),
            # X uses / utilizes / applies Y
            (
                r"(?P<source>[A-Z][A-Za-z0-9\s\-]{2,30}?)\s+(?:uses?|utilizes?|applies?|employs?)\s+(?P<target>[A-Za-z0-9\s\-]{3,40}?)(?:\.|\,|$|\s+to|\s+for)",
                "USES_MATERIAL",
                "TECHNOLOGY",
            ),
            # X contradicts / conflicts with Y
            (
                r"(?P<source>[A-Z][A-Za-z0-9\s\-]{2,30}?)\s+(?:contradicts?|conflicts\s+with)\s+(?P<target>[A-Za-z0-9\s\-]{3,40}?)(?:\.|\,|$)",
                "CONTRADICTS",
                "CONCEPT",
            ),
            # X correlates with Y
            (
                r"(?P<source>[A-Z][A-Za-z0-9\s\-]{2,30}?)\s+(?:positively\s+|negatively\s+)?correlates\s+with\s+(?P<target>[A-Za-z0-9\s\-]{3,40}?)(?:\.|\,|$)",
                "CORRELATES_WITH",
                "METRIC",
            ),
        ]

        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            s_clean = sentence.strip()
            if not s_clean:
                continue

            for pat, default_rel, default_target_type in patterns:
                for match in re.finditer(pat, s_clean, re.IGNORECASE):
                    src = match.group("source").strip()
                    tgt = match.group("target").strip()
                    rel = default_rel

                    # Filter noise
                    if len(src) < 2 or len(tgt) < 2 or src.lower() == tgt.lower():
                        continue
                    if src.lower() in ("the", "this", "these", "it", "there", "which", "such"):
                        continue
                    if tgt.lower() in ("the", "this", "these", "it", "there", "which", "such"):
                        continue

                    # Determine basic entity type heuristics
                    src_type = "CONCEPT"
                    if any(w in src.lower() for w in ("acid", "polymer", "oxide", "film", "pha", "pla", "metal", "composite")):
                        src_type = "MATERIAL"
                    elif any(w in src.lower() for w in ("algorithm", "model", "network", "system", "method", "parser")):
                        src_type = "TECHNOLOGY"
                    elif any(w in src.lower() for w in ("paper", "study", "report", "article")):
                        src_type = "PAPER"

                    tgt_type = default_target_type
                    if any(w in tgt.lower() for w in ("strength", "rate", "temperature", "score", "percentage", "loss")):
                        tgt_type = "METRIC"
                    elif any(w in tgt.lower() for w in ("seawater", "compost", "water", "air", "soil")):
                        tgt_type = "ENVIRONMENT"

                    triplet = GraphTriplet(
                        source=src,
                        source_type=src_type,
                        relation=rel,
                        target=tgt,
                        target_type=tgt_type,
                        description=s_clean,
                        confidence=0.9,
                        weight=1.0,
                    )
                    triplets.append(triplet)
                    extracted_entities.add(src)
                    extracted_entities.add(tgt)

        # Batch upsert extracted triplets
        if triplets:
            raw_dicts = [t.model_dump() for t in triplets]
            entities, relations = await self.repo.batch_upsert_triplets(
                raw_dicts, user_id=user_id, job_id=job_id, project_id=project_id
            )
            logger.info(
                "Extracted and persisted knowledge graph triplets",
                triplet_count=len(triplets),
                entities_count=len(entities),
                relations_count=len(relations),
            )
            return GraphExtractionResult(
                entities_count=len(entities),
                relations_count=len(relations),
                triplets=triplets,
                extracted_entities=list(extracted_entities),
            )

        return GraphExtractionResult(entities_count=0, relations_count=0)

    async def extract_from_report(
        self,
        report_data: Dict[str, Any],
        user_id: Optional[UUID] = None,
        job_id: Optional[UUID] = None,
    ) -> GraphExtractionResult:
        """Extract entities and relations from a synthesized ResearchReport."""
        text_blocks = []

        # Executive summary
        if "summary" in report_data and report_data["summary"]:
            text_blocks.append(str(report_data["summary"]))
        if "executive_summary" in report_data and report_data["executive_summary"]:
            text_blocks.append(str(report_data["executive_summary"]))

        # Key findings
        findings = report_data.get("findings", [])
        for f in findings:
            if isinstance(f, dict):
                content = f.get("content") or f.get("claim") or f.get("summary") or ""
                text_blocks.append(str(content))
            elif isinstance(f, str):
                text_blocks.append(f)

        combined_text = "\n\n".join(text_blocks)
        return await self.extract_triplets_from_text(combined_text, user_id=user_id, job_id=job_id)

    async def get_graph_augmented_context(
        self,
        query: str,
        user_id: Optional[UUID] = None,
        max_hops: int = 1,
        limit_entities: int = 5,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Graph-Augmented RAG (GraphRAG):
        Extracts matched entities from the query, traverses their k-hop relations, and formats
        a structured Markdown graph context for LLM agents.
        """
        if not query or not query.strip():
            return "", []

        # Find matching entities in graph repository
        matching_entities = await self.repo.list_entities(
            user_id=user_id, search=query, limit=limit_entities
        )
        if not matching_entities:
            # Token search fallback
            words = [w for w in re.findall(r"\b[A-Za-z0-9\-]{3,}\b", query) if len(w) >= 3]
            for word in words[:3]:
                found = await self.repo.find_entity_by_name(word, user_id=user_id)
                if found and found not in matching_entities:
                    matching_entities.append(found)

        if not matching_entities:
            return "", []

        collected_subgraphs: List[Dict[str, Any]] = []
        markdown_lines = ["### 🕸️ Knowledge Graph Relational Context:"]

        for entity in matching_entities[:limit_entities]:
            subgraph = await self.repo.get_k_hop_subgraph(
                entity.id, max_hops=max_hops, limit_nodes=10, limit_edges=15
            )
            collected_subgraphs.append(subgraph)

            markdown_lines.append(f"- **Entity**: `{entity.name}` ({entity.entity_type})")
            if entity.description:
                markdown_lines.append(f"  - *Definition*: {entity.description}")
            if entity.aliases:
                markdown_lines.append(f"  - *Aliases*: {', '.join(entity.aliases)}")

            # Relations
            edges = subgraph.get("edges", [])
            if edges:
                markdown_lines.append("  - *Relationships*:")
                for edge in edges[:5]:
                    src = edge.get("source_name") or edge.get("source_id")
                    tgt = edge.get("target_name") or edge.get("target_id")
                    rel = edge.get("relation_type", "RELATES_TO")
                    desc = edge.get("description")
                    if desc:
                        markdown_lines.append(f"    • `{src}` ──[{rel}]──> `{tgt}` ({desc})")
                    else:
                        markdown_lines.append(f"    • `{src}` ──[{rel}]──> `{tgt}`")

        formatted_context = "\n".join(markdown_lines)
        return formatted_context, collected_subgraphs

    async def find_path_between_entities(
        self,
        source_name: str,
        target_name: str,
        user_id: Optional[UUID] = None,
        max_depth: int = 4,
    ) -> GraphPathResult:
        """Find multi-hop relational path connecting two entities by name."""
        src_entity = await self.repo.find_entity_by_name(source_name, user_id=user_id)
        tgt_entity = await self.repo.find_entity_by_name(target_name, user_id=user_id)

        if not src_entity or not tgt_entity:
            return GraphPathResult(
                source_entity=source_name,
                target_entity=target_name,
                path_found=False,
                summary=f"One or both entities not found in knowledge graph (Source: {bool(src_entity)}, Target: {bool(tgt_entity)}).",
            )

        raw_path = await self.repo.find_shortest_path(
            src_entity.id, tgt_entity.id, max_depth=max_depth
        )
        if not raw_path:
            return GraphPathResult(
                source_entity=src_entity.name,
                target_entity=tgt_entity.name,
                path_found=False,
                summary=f"No relational path found between '{src_entity.name}' and '{tgt_entity.name}' within {max_depth} hops.",
            )

        steps: List[GraphPathStep] = []
        step_descriptions: List[str] = []

        for step in raw_path:
            p_step = GraphPathStep(
                from_id=step["from_id"],
                to_id=step["to_id"],
                relation_id=step["relation_id"],
                relation_type=step["relation_type"],
                description=step.get("description"),
                direction=step.get("direction", "OUTGOING"),
            )
            steps.append(p_step)

            from_ent = await self.repo.get_entity_by_id(step["from_id"])
            to_ent = await self.repo.get_entity_by_id(step["to_id"])
            fn = from_ent.name if from_ent else step["from_id"]
            tn = to_ent.name if to_ent else step["to_id"]
            step_descriptions.append(f"`{fn}` ──[{step['relation_type']}]──> `{tn}`")

        summary_text = " ➔ ".join(step_descriptions)

        return GraphPathResult(
            source_entity=src_entity.name,
            target_entity=tgt_entity.name,
            path_found=True,
            hop_count=len(steps),
            steps=steps,
            summary=summary_text,
        )
