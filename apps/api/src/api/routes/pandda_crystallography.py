"""
Phase 129: Autonomous High-Throughput Crystallography Fragment Screening & PanDDA API Routes.
"""
from typing import Dict, Any, Optional, List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.pandda_crystallography_repo import PanDDACrystallographyRepository
from research.structural.pandda_engine import PanDDACrystallographyEngine

router = APIRouter(prefix="/pandda-crystallography", tags=["Phase 129: PanDDA Fragment Crystallography"])


class RunPanDDAScreenRequest(BaseModel):
    campaign_name: str = Field(..., example="SARS_CoV_2_Mpro_XChem_PanDDA")
    target_protein: str = Field("Main Protease (Mpro)", example="Main Protease (Mpro)")
    total_crystals_soaked: int = Field(320, ge=20, le=2000)
    crystal_space_group: str = Field("P 21 21 21", example="P 21 21 21")
    project_id: Optional[str] = Field(None)


@router.post("/screen", status_code=status.HTTP_201_CREATED)
async def screen_crystallography_fragments(
    req: RunPanDDAScreenRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Executes PanDDA ensemble statistical ground-state background density modeling and fragment hit detection.
    """
    engine = PanDDACrystallographyEngine()
    pipeline_res = engine.simulate_fragment_screen(
        campaign_name=req.campaign_name,
        target_protein=req.target_protein,
        total_crystals=req.total_crystals_soaked,
    )

    repo = PanDDACrystallographyRepository(db)
    screen = await repo.create_screen(
        campaign_name=req.campaign_name,
        target_protein=req.target_protein,
        crystal_space_group=req.crystal_space_group,
        high_resolution_cutoff_angstrom=1.45,
        total_crystals_soaked=req.total_crystals_soaked,
        pandda_events_detected=pipeline_res["summary"]["events_detected"],
        background_model_r_free=0.185,
        metadata_json={"summary": pipeline_res["summary"]},
        project_id=req.project_id,
    )

    # Persist density map
    await repo.add_density_map(
        screen_id=screen.id,
        map_id="PanDDA_Ground_State_Statistical_Map_01",
        resolution_angstrom=1.45,
        statistical_outlier_noise_sigma=pipeline_res["background_model"]["sigma"],
        mean_density_value=pipeline_res["background_model"]["mean_density"],
    )

    # Persist fragment hits
    for hit in pipeline_res["fragment_hits"]:
        await repo.add_fragment_hit(
            screen_id=screen.id,
            hit_id=hit["hit_id"],
            fragment_smiles=hit["smiles"],
            binding_site_name=hit["site"],
            event_b_factor=hit["event"]["event_b_factor"],
            event_occupancy=hit["event"]["estimated_occupancy"],
            z_peak_score=hit["event"]["z_peak_score"],
            ligand_efficiency_le=hit["event"]["ligand_efficiency_le"],
        )

    saved = await repo.get_screen(screen.id)
    return {
        "status": "success",
        "screen_id": str(screen.id),
        "campaign_name": screen.campaign_name,
        "hits_count": len(saved.hits) if saved else 0,
        "density_maps_count": len(saved.density_maps) if saved else 0,
        "summary": pipeline_res["summary"],
    }


@router.get("/screens", status_code=status.HTTP_200_OK)
async def list_pandda_screens(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List PanDDA crystallography fragment screens."""
    repo = PanDDACrystallographyRepository(db)
    screens = await repo.list_screens(limit=limit)
    return [
        {
            "id": str(s.id),
            "campaign_name": s.campaign_name,
            "target_protein": s.target_protein,
            "space_group": s.crystal_space_group,
            "resolution_angstrom": s.high_resolution_cutoff_angstrom,
            "crystals_soaked": s.total_crystals_soaked,
            "events_detected": s.pandda_events_detected,
            "hits_count": len(s.hits),
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in screens
    ]


@router.get("/screens/{screen_id}", status_code=status.HTTP_200_OK)
async def get_pandda_screen(
    screen_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get single PanDDA crystallography fragment screen details."""
    repo = PanDDACrystallographyRepository(db)
    screen = await repo.get_screen(screen_id)
    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screen {screen_id} not found",
        )
    return {
        "id": str(screen.id),
        "campaign_name": screen.campaign_name,
        "target_protein": screen.target_protein,
        "space_group": screen.crystal_space_group,
        "resolution": screen.high_resolution_cutoff_angstrom,
        "hits": [
            {
                "hit_id": h.hit_id,
                "smiles": h.fragment_smiles,
                "site": h.binding_site_name,
                "b_factor": h.event_b_factor,
                "occupancy": h.event_occupancy,
                "z_peak": h.z_peak_score,
                "le": h.ligand_efficiency_le,
            }
            for h in screen.hits
        ],
        "density_maps": [
            {
                "map_id": d.map_id,
                "resolution": d.resolution_angstrom,
                "sigma": d.statistical_outlier_noise_sigma,
                "mean_density": d.mean_density_value,
            }
            for d in screen.density_maps
        ],
    }
