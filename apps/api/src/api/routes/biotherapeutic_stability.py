from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.biotherapeutic_stability_repo import BiotherapeuticStabilityRepository
from research.stability.stability_engine import BiotherapeuticStabilityEngine

router = APIRouter(prefix="/api/v1/biotherapeutic-stability", tags=["Biotherapeutic Stability & Developability"])

class StabilityAnalyzeRequest(BaseModel):
    construct_name: str = Field(..., example="Trastuzumab-Biosimilar-V2")
    modality: str = Field("mAb", example="mAb")
    heavy_chain_sequence: str = Field(..., example="EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSC")
    light_chain_sequence: Optional[str] = Field(None, example="DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVDNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC")
    buffer_type: str = Field("Histidine", example="Histidine")
    ph: float = Field(6.0, example=6.0)
    surfactant: str = Field("Polysorbate 80", example="Polysorbate 80")
    tonicity_agent: str = Field("Sucrose", example="Sucrose")

@router.post("/analyze", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def analyze_biotherapeutic_stability(
    request: StabilityAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Autonomous Biotherapeutic Stability & Spatial Aggregation Propensity Forecaster.
    """
    engine = BiotherapeuticStabilityEngine()
    repo = BiotherapeuticStabilityRepository(db)

    # 1. Compute SAP score and thermal parameters
    metrics = engine.compute_spatial_aggregation_propensity(
        heavy_chain=request.heavy_chain_sequence,
        light_chain=request.light_chain_sequence,
    )

    # 2. Compute formulation excipient screening
    formulation = engine.optimize_formulation_buffer(
        sap_score=metrics["aggregation_propensity_score"],
        buffer_type=request.buffer_type,
        ph=request.ph,
        surfactant=request.surfactant,
        tonicity_agent=request.tonicity_agent,
    )

    # 3. Persist construct in DB
    construct = await repo.create_construct(
        construct_name=request.construct_name,
        modality=request.modality,
        heavy_chain_sequence=request.heavy_chain_sequence,
        light_chain_sequence=request.light_chain_sequence,
        melting_temp_tm1_celsius=metrics["melting_temp_tm1_celsius"],
        melting_temp_tm2_celsius=metrics["melting_temp_tm2_celsius"],
        aggregation_propensity_score=metrics["aggregation_propensity_score"],
        colloidal_stability_kd=metrics["colloidal_stability_kd"],
        diffusion_interaction_parameter_b22=metrics["diffusion_interaction_parameter_b22"],
        shelf_life_months_at_4c=metrics["shelf_life_months_at_4c"],
    )

    # 4. Persist Hydrophobic Patches
    for patch in metrics["hydrophobic_patches"]:
        await repo.add_hydrophobic_patch(
            construct_id=construct.id,
            patch_identifier=patch["patch_identifier"],
            surface_area_angstrom2=patch["surface_area_angstrom2"],
            average_hydrophobicity_score=patch["average_hydrophobicity_score"],
            residue_span=patch["residue_span"],
            aggregation_risk_level=patch["aggregation_risk_level"],
        )

    # 5. Persist Formulation Screen
    await repo.add_excipient_screen(
        construct_id=construct.id,
        buffer_type=formulation["buffer_type"],
        ph=formulation["ph"],
        surfactant=formulation["surfactant"],
        tonicity_agent=formulation["tonicity_agent"],
        monomer_retention_pct_at_40c=formulation["monomer_retention_pct_at_40c"],
    )

    hydrated = await repo.get_construct_by_id(construct.id)

    return {
        "status": "SUCCESS",
        "construct_id": hydrated.id,
        "construct_name": hydrated.construct_name,
        "modality": hydrated.modality,
        "aggregation_propensity_score": hydrated.aggregation_propensity_score,
        "melting_temp_tm1_celsius": hydrated.melting_temp_tm1_celsius,
        "melting_temp_tm2_celsius": hydrated.melting_temp_tm2_celsius,
        "colloidal_stability_kd": hydrated.colloidal_stability_kd,
        "shelf_life_months_at_4c": hydrated.shelf_life_months_at_4c,
        "monomer_retention_pct_at_40c": formulation["monomer_retention_pct_at_40c"],
        "formulation_stability_grade": formulation["formulation_stability_grade"],
        "hydrophobic_patches": [
            {
                "patch_identifier": p.patch_identifier,
                "surface_area_angstrom2": p.surface_area_angstrom2,
                "average_hydrophobicity_score": p.average_hydrophobicity_score,
                "residue_span": p.residue_span,
                "aggregation_risk_level": p.aggregation_risk_level,
            }
            for p in hydrated.hydrophobic_patches
        ],
    }

@router.get("/constructs", response_model=List[Dict[str, Any]])
async def list_biotherapeutic_constructs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = BiotherapeuticStabilityRepository(db)
    constructs = await repo.list_constructs(limit=limit)
    return [
        {
            "id": c.id,
            "construct_name": c.construct_name,
            "modality": c.modality,
            "aggregation_propensity_score": c.aggregation_propensity_score,
            "melting_temp_tm1_celsius": c.melting_temp_tm1_celsius,
            "shelf_life_months_at_4c": c.shelf_life_months_at_4c,
            "patches_count": len(c.hydrophobic_patches),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in constructs
    ]

@router.get("/constructs/{construct_id}", response_model=Dict[str, Any])
async def get_biotherapeutic_construct(
    construct_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = BiotherapeuticStabilityRepository(db)
    c = await repo.get_construct_by_id(construct_id)
    if not c:
        raise HTTPException(status_code=404, detail="Biotherapeutic construct not found")
    return {
        "id": c.id,
        "construct_name": c.construct_name,
        "modality": c.modality,
        "heavy_chain_sequence": c.heavy_chain_sequence,
        "light_chain_sequence": c.light_chain_sequence,
        "melting_temp_tm1_celsius": c.melting_temp_tm1_celsius,
        "melting_temp_tm2_celsius": c.melting_temp_tm2_celsius,
        "aggregation_propensity_score": c.aggregation_propensity_score,
        "colloidal_stability_kd": c.colloidal_stability_kd,
        "diffusion_interaction_parameter_b22": c.diffusion_interaction_parameter_b22,
        "shelf_life_months_at_4c": c.shelf_life_months_at_4c,
        "hydrophobic_patches": [
            {
                "id": p.id,
                "patch_identifier": p.patch_identifier,
                "surface_area_angstrom2": p.surface_area_angstrom2,
                "average_hydrophobicity_score": p.average_hydrophobicity_score,
                "residue_span": p.residue_span,
                "aggregation_risk_level": p.aggregation_risk_level,
            }
            for p in c.hydrophobic_patches
        ],
        "excipient_screens": [
            {
                "id": s.id,
                "buffer_type": s.buffer_type,
                "ph": s.ph,
                "surfactant": s.surfactant,
                "tonicity_agent": s.tonicity_agent,
                "monomer_retention_pct_at_40c": s.monomer_retention_pct_at_40c,
            }
            for s in c.excipient_screens
        ],
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
