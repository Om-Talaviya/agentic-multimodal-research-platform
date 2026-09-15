"""Unit tests for KnowledgeGraphRepository."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.connection import Base
from database.repositories.graph_repo import KnowledgeGraphRepository
from database.models.graph import DBKnowledgeEntity, DBKnowledgeRelation


@pytest.fixture
async def async_session():
    """Create isolated in-memory SQLite async session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_entity_lifecycle_and_canonicalization(async_session):
    """Test entity creation, alias resolution, canonical name lookup, and updates."""
    repo = KnowledgeGraphRepository(async_session)
    user_id = uuid.uuid4()

    # 1. Create Entity
    entity = await repo.create_entity(
        name="Polylactic Acid",
        entity_type="MATERIAL",
        user_id=user_id,
        description="A biodegradable thermoplastic polyester.",
        aliases=["PLA", "poly(lactic acid)"],
        properties={"melting_point": "150-160C"},
    )
    assert entity.id is not None
    assert entity.canonical_name == "polylactic acid"
    assert entity.entity_type == "MATERIAL"
    assert "PLA" in entity.aliases

    # 2. Find by alias
    found_by_alias = await repo.find_entity_by_name("PLA", user_id=user_id)
    assert found_by_alias is not None
    assert found_by_alias.id == entity.id

    # 3. Find or create (should match existing)
    existing = await repo.find_or_create_entity(
        name="polylactic acid",
        entity_type="MATERIAL",
        user_id=user_id,
        aliases=["corn plastic"],
    )
    assert existing.id == entity.id
    assert "corn plastic" in existing.aliases

    # 4. List and count
    listed = await repo.list_entities(user_id=user_id, entity_type="MATERIAL")
    assert len(listed) == 1
    assert listed[0].name == "Polylactic Acid"

    count = await repo.count_entities(user_id=user_id)
    assert count == 1

    # 5. Update
    updated = await repo.update_entity(entity.id, description="Updated definition.")
    assert updated.description == "Updated definition."

    # 6. Delete
    deleted = await repo.delete_entity(entity.id)
    assert deleted is True
    assert await repo.get_entity_by_id(entity.id) is None


@pytest.mark.asyncio
async def test_relations_and_k_hop_subgraph_traversal(async_session):
    """Test directed relation creation, k-hop subgraph traversal, and shortest path finding."""
    repo = KnowledgeGraphRepository(async_session)
    user_id = uuid.uuid4()

    # Create network of nodes: PLA -> Seawater -> Microorganisms -> Enzymatic Cleavage
    pla = await repo.find_or_create_entity("PLA", "MATERIAL", user_id=user_id)
    seawater = await repo.find_or_create_entity("Seawater", "ENVIRONMENT", user_id=user_id)
    microbes = await repo.find_or_create_entity("Marine Microbes", "BIOLOGY", user_id=user_id)
    enzymes = await repo.find_or_create_entity("Protease K", "ENZYME", user_id=user_id)

    # Add relations
    r1 = await repo.create_relation(
        source_id=pla.id,
        target_id=seawater.id,
        relation_type="EXPOSED_TO",
        user_id=user_id,
        description="PLA submerged in ambient seawater",
    )
    r2 = await repo.create_relation(
        source_id=seawater.id,
        target_id=microbes.id,
        relation_type="HOSTS",
        user_id=user_id,
        description="Seawater hosts indigenous marine microbial communities",
    )
    r3 = await repo.create_relation(
        source_id=microbes.id,
        target_id=enzymes.id,
        relation_type="SECRETES",
        user_id=user_id,
        description="Microbes secrete digestive enzymes",
    )

    # 1-Hop Subgraph around PLA
    subgraph_1 = await repo.get_k_hop_subgraph(pla.id, max_hops=1)
    node_names_1 = [n["name"] for n in subgraph_1["nodes"]]
    assert "PLA" in node_names_1
    assert "Seawater" in node_names_1
    assert "Marine Microbes" not in node_names_1
    assert len(subgraph_1["edges"]) == 1

    # 2-Hop Subgraph around PLA
    subgraph_2 = await repo.get_k_hop_subgraph(pla.id, max_hops=2)
    node_names_2 = [n["name"] for n in subgraph_2["nodes"]]
    assert "PLA" in node_names_2
    assert "Seawater" in node_names_2
    assert "Marine Microbes" in node_names_2
    assert len(subgraph_2["edges"]) == 2

    # Shortest Path Finding: PLA -> Protease K (3 hops)
    path = await repo.find_shortest_path(pla.id, enzymes.id, max_depth=4)
    assert path is not None
    assert len(path) == 3
    assert path[0]["relation_type"] == "EXPOSED_TO"
    assert path[1]["relation_type"] == "HOSTS"
    assert path[2]["relation_type"] == "SECRETES"


@pytest.mark.asyncio
async def test_batch_upsert_triplets(async_session):
    """Test batch extraction triplet ingestion with automatic entity creation and edge linking."""
    repo = KnowledgeGraphRepository(async_session)
    user_id = uuid.uuid4()

    triplets = [
        {
            "source": "Graphene Oxide",
            "source_type": "MATERIAL",
            "relation": "ENHANCES",
            "target": "Tensile Strength",
            "target_type": "METRIC",
            "description": "Addition of 0.5 wt% GO increases tensile strength by 42%",
            "confidence": 0.96,
        },
        {
            "source": "Graphene Oxide",
            "source_type": "MATERIAL",
            "relation": "SYNTHESIZED_VIA",
            "target": "Hummer's Method",
            "target_type": "METHODOLOGY",
            "description": "Standard chemical oxidation protocol",
            "confidence": 0.99,
        },
    ]

    entities, relations = await repo.batch_upsert_triplets(triplets, user_id=user_id)
    assert len(entities) == 3  # Graphene Oxide, Tensile Strength, Hummer's Method
    assert len(relations) == 2

    # Verify query
    go = await repo.find_entity_by_name("Graphene Oxide", user_id=user_id)
    assert go is not None

    go_relations = await repo.list_relations(user_id=user_id, entity_id=go.id)
    assert len(go_relations) == 2
