"""
FastAPI router for Protein-Protein Interaction (PPI) Interactome (Phase 58).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.ppi_interactome_repo import PPIInteractomeRepository
from research.ppi.ppi_engine import PPIInteractomeEngine

router = APIRouter(prefix="/ppi-interactome", tags=["PPI Interactome"])


class CreateNetworkRequest(BaseModel):
    network_name: str = Field(default="KRAS Oncogenic Signalosome")
    seed_gene: str = Field(default="KRAS")
    disease_context: str = Field(default="Pancreatic Ductal Adenocarcinoma")


@router.post("/networks", status_code=status.HTTP_201_CREATED)
async def create_ppi_network(
    request: CreateNetworkRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Constructs a protein-protein interactome network and ranks druggable hub interfaces."""
    repo = PPIInteractomeRepository(db)
    net = await repo.create_network(
        network_name=request.network_name,
        disease_context=request.disease_context,
    )

    graph_data = PPIInteractomeEngine.generate_interactome(
        seed_gene=request.seed_gene,
        disease_context=request.disease_context,
    )

    await repo.add_nodes_and_edges(
        network_id=net.id,
        nodes_data=graph_data["nodes"],
        edges_data=graph_data["edges"],
    )

    return await repo.get_network(net.id)


@router.get("/networks")
async def list_ppi_networks(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists PPI interactome networks."""
    repo = PPIInteractomeRepository(db)
    return await repo.list_networks(limit=limit)


@router.get("/networks/{network_id}")
async def get_ppi_network(
    network_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full interactome network graph with nodes and interaction edges."""
    repo = PPIInteractomeRepository(db)
    net = await repo.get_network(network_id)
    if not net:
        raise HTTPException(status_code=404, detail="PPI interactome network not found")
    return net
