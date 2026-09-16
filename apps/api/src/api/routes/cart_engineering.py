from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from database.repositories.cart_engineering_repo import CARTRepository
from research.cart.cart_engine import CARTEngine

router = APIRouter(prefix="/cart", tags=["Cell Therapy CAR-T Engineering"])

class ConstructCreateRequest(BaseModel):
    construct_name: str = Field(..., example="Kymriah-Bioequivalent-CD19-41BB")
    target_antigen: str = Field(..., example="CD19")
    scfv_binder_clone: str = Field(default="FMC63", example="FMC63")
    costimulatory_domain: str = Field(default="4-1BB", example="4-1BB")
    hinge_transmembrane: str = Field(default="CD8a", example="CD8a")
    signaling_domain: str = Field(default="CD3zeta", example="CD3zeta")
    vector_type: str = Field(default="Lentiviral", example="Lentiviral")
    full_aa_sequence: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class CytotoxicitySimRequest(BaseModel):
    target_cell_line: str = Field(default="Raji", example="Raji")
    effector_to_target_ratio: float = Field(default=5.0, example=5.0)

class CRSToxicitySimRequest(BaseModel):
    tumor_burden_index: float = Field(default=1.0, example=1.0)

@router.post("/constructs", status_code=status.HTTP_201_CREATED)
async def create_construct(
    req: ConstructCreateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    engine = CARTEngine()
    design = engine.design_car_construct(
        construct_name=req.construct_name,
        target_antigen=req.target_antigen,
        costimulatory_domain=req.costimulatory_domain,
        scfv_clone=req.scfv_binder_clone,
        hinge_transmembrane=req.hinge_transmembrane,
        vector_type=req.vector_type
    )

    repo = CARTRepository(db)
    construct = await repo.create_construct(
        construct_name=design["construct_name"],
        target_antigen=design["target_antigen"],
        scfv_binder_clone=design["scfv_binder_clone"],
        costimulatory_domain=design["costimulatory_domain"],
        hinge_transmembrane=design["hinge_transmembrane"],
        signaling_domain=design["signaling_domain"],
        vector_type=design["vector_type"],
        full_aa_sequence=design["full_aa_sequence"],
        properties={"phenotype": design["phenotype_prediction"], "target_malignancies": design["target_malignancies"]},
    )
    return construct

@router.get("/constructs")
async def list_constructs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session)
):
    repo = CARTRepository(db)
    return await repo.list_constructs(limit=limit)

@router.get("/constructs/{construct_id}")
async def get_construct(
    construct_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    repo = CARTRepository(db)
    construct = await repo.get_construct(construct_id)
    if not construct:
        raise HTTPException(status_code=404, detail=f"CAR-T construct {construct_id} not found")
    return construct

@router.post("/constructs/{construct_id}/simulate-cytotoxicity")
async def simulate_cytotoxicity(
    construct_id: str,
    req: CytotoxicitySimRequest,
    db: AsyncSession = Depends(get_db_session)
):
    repo = CARTRepository(db)
    construct = await repo.get_construct(construct_id)
    if not construct:
        raise HTTPException(status_code=404, detail=f"CAR-T construct {construct_id} not found")

    engine = CARTEngine()
    sim = engine.simulate_cytotoxicity(
        target_antigen=construct.target_antigen,
        costimulatory_domain=construct.costimulatory_domain,
        target_cell_line=req.target_cell_line,
        et_ratio=req.effector_to_target_ratio
    )

    scorecard = await repo.add_cytotoxicity_scorecard(
        construct_id=construct_id,
        target_cell_line=sim["target_cell_line"],
        effector_to_target_ratio=sim["effector_to_target_ratio"],
        specific_lysis_pct=sim["specific_lysis_pct"],
        t_cell_persistence_score=sim["t_cell_persistence_score"],
        exhaustion_pd1_expression_pct=sim["exhaustion_pd1_expression_pct"],
        exhaustion_tim3_expression_pct=sim["exhaustion_tim3_expression_pct"],
        exhaustion_lag3_expression_pct=sim["exhaustion_lag3_expression_pct"],
        cytotoxicity_grade=sim["cytotoxicity_grade"]
    )
    return scorecard

@router.post("/constructs/{construct_id}/predict-crs")
async def predict_crs(
    construct_id: str,
    req: CRSToxicitySimRequest,
    db: AsyncSession = Depends(get_db_session)
):
    repo = CARTRepository(db)
    construct = await repo.get_construct(construct_id)
    if not construct:
        raise HTTPException(status_code=404, detail=f"CAR-T construct {construct_id} not found")

    engine = CARTEngine()
    pred = engine.predict_crs_toxicity(
        target_antigen=construct.target_antigen,
        costimulatory_domain=construct.costimulatory_domain,
        tumor_burden_index=req.tumor_burden_index
    )

    profile = await repo.add_crs_toxicity_profile(
        construct_id=construct_id,
        peak_il6_pg_ml=pred["peak_il6_pg_ml"],
        peak_ifng_pg_ml=pred["peak_ifng_pg_ml"],
        peak_tnfa_pg_ml=pred["peak_tnfa_pg_ml"],
        peak_il1b_pg_ml=pred["peak_il1b_pg_ml"],
        astct_crs_grade_predicted=pred["astct_crs_grade_predicted"],
        icans_neurotoxicity_risk_pct=pred["icans_neurotoxicity_risk_pct"],
        tocilizumab_responsive=pred["tocilizumab_responsive"],
        dexamethasone_recommended=pred["dexamethasone_recommended"],
        safety_summary=pred["safety_summary"]
    )
    return profile
