from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.neoepitope_vaccine_repo import NeoepitopeVaccineRepository
from research.vaccine.neoepitope_engine import ProteogenomicNeoepitopeEngine

router = APIRouter(prefix="/api/v1/cancer-vaccines", tags=["Cancer Vaccines & Neoepitopes"])

class NeoepitopeMutationInput(BaseModel):
    mutated_gene: str = Field(..., example="KRAS")
    mutation_type: str = Field("SNV", example="SNV")
    peptide_mt: str = Field(..., example="KLVVVGADGV")
    peptide_wt: str = Field(..., example="KLVVVGAGGV")
    hla_allele: str = Field("HLA-A*02:01", example="HLA-A*02:01")
    vaf_pct: float = Field(35.5, example=35.5)
    expression_tpm: float = Field(120.4, example=120.4)

class CancerVaccineDesignRequest(BaseModel):
    patient_id: str = Field(..., example="PT-MEL-8842")
    tumor_type: str = Field("Melanoma", example="Melanoma")
    hla_alleles: List[str] = Field(default_factory=lambda: ["HLA-A*02:01", "HLA-A*24:02"])
    mutations: List[NeoepitopeMutationInput]
    polyepitope_linker: str = Field("AAY", example="AAY")
    adjuvant_type: str = Field("Poly-ICLC", example="Poly-ICLC")

class CancerVaccineResponse(BaseModel):
    id: str
    patient_id: str
    tumor_type: str
    hla_alleles: List[str]
    mrna_construct_sequence: Optional[str]
    polyepitope_junction_cleavability_score: float
    predicted_immunogenicity_index: float
    neoepitopes_count: int
    created_at: str

@router.post("/design", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def design_cancer_vaccine(
    request: CancerVaccineDesignRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Autonomous Proteogenomic Neoepitope Discovery & Personalized mRNA Cancer Vaccine Designer.
    """
    engine = ProteogenomicNeoepitopeEngine()
    repo = NeoepitopeVaccineRepository(db)

    # 1. Score all candidate mutations
    scored_neoepitopes = []
    for mut in request.mutations:
        scored = engine.score_neoepitope(
            mutated_gene=mut.mutated_gene,
            peptide_mt=mut.peptide_mt,
            peptide_wt=mut.peptide_wt,
            hla_allele=mut.hla_allele,
            vaf_pct=mut.vaf_pct,
            expression_tpm=mut.expression_tpm,
        )
        scored["mutation_type"] = mut.mutation_type
        scored_neoepitopes.append(scored)

    # 2. Assemble mRNA polyepitope
    assembly_result = engine.assemble_mrna_polyepitope(
        scored_neoepitopes,
        top_k=min(15, len(scored_neoepitopes)),
        linker=request.polyepitope_linker,
    )

    # 3. Persist vaccine design in DB
    vaccine = await repo.create_vaccine_design(
        patient_id=request.patient_id,
        tumor_type=request.tumor_type,
        hla_alleles=request.hla_alleles,
        mrna_construct_sequence=assembly_result["full_engineered_construct"],
        polyepitope_junction_cleavability_score=assembly_result["polyepitope_junction_cleavability_score"],
        predicted_immunogenicity_index=assembly_result["mean_predicted_immunogenicity"],
        properties={"linker": request.polyepitope_linker},
    )

    # 4. Persist individual neoepitopes
    for ep in scored_neoepitopes:
        await repo.add_candidate_neoepitope(
            vaccine_id=vaccine.id,
            mutated_gene=ep["mutated_gene"],
            mutation_type=ep["mutation_type"],
            peptide_sequence=ep["peptide_sequence"],
            wildtype_sequence=ep["wildtype_sequence"],
            hla_restriction=ep["hla_restriction"],
            mhc_binding_affinity_ic50_nm=ep["mt_affinity_ic50_nm"],
            clonality_vaf_pct=ep["clonality_vaf_pct"],
            expression_tpm=ep["expression_tpm"],
            immunogenicity_rank_score=ep["immunogenicity_rank_score"],
            is_selected_for_vaccine=ep in assembly_result["selected_epitopes"],
        )

    # 5. Persist Adjuvant Schedule
    await repo.add_adjuvant_schedule(
        vaccine_id=vaccine.id,
        adjuvant_type=request.adjuvant_type,
        dose_schedule_days=[0, 3, 7, 14, 28, 56],
        booster_frequency_weeks=4,
        predicted_cd8_tcell_response_pct=round(70.0 + assembly_result["mean_predicted_immunogenicity"] * 25.0, 1),
    )

    hydrated_vaccine = await repo.get_vaccine_design_by_id(vaccine.id)

    return {
        "status": "SUCCESS",
        "vaccine_id": hydrated_vaccine.id,
        "patient_id": hydrated_vaccine.patient_id,
        "tumor_type": hydrated_vaccine.tumor_type,
        "polyepitope_junction_cleavability_score": hydrated_vaccine.polyepitope_junction_cleavability_score,
        "predicted_immunogenicity_index": hydrated_vaccine.predicted_immunogenicity_index,
        "mrna_construct_sequence": hydrated_vaccine.mrna_construct_sequence,
        "neoepitopes_count": len(hydrated_vaccine.neoepitopes),
        "selected_epitopes": [
            {
                "mutated_gene": ep.mutated_gene,
                "peptide_sequence": ep.peptide_sequence,
                "hla_restriction": ep.hla_restriction,
                "mhc_affinity_ic50_nm": ep.mhc_binding_affinity_ic50_nm,
                "immunogenicity_rank_score": ep.immunogenicity_rank_score,
            }
            for ep in hydrated_vaccine.neoepitopes if ep.is_selected_for_vaccine
        ],
    }

@router.get("/designs", response_model=List[Dict[str, Any]])
async def list_cancer_vaccine_designs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = NeoepitopeVaccineRepository(db)
    designs = await repo.list_vaccine_designs(limit=limit)
    return [
        {
            "id": d.id,
            "patient_id": d.patient_id,
            "tumor_type": d.tumor_type,
            "hla_alleles": d.hla_alleles,
            "mrna_construct_sequence": d.mrna_construct_sequence,
            "polyepitope_junction_cleavability_score": d.polyepitope_junction_cleavability_score,
            "predicted_immunogenicity_index": d.predicted_immunogenicity_index,
            "neoepitopes_count": len(d.neoepitopes),
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in designs
    ]

@router.get("/designs/{vaccine_id}", response_model=Dict[str, Any])
async def get_cancer_vaccine_design(
    vaccine_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = NeoepitopeVaccineRepository(db)
    d = await repo.get_vaccine_design_by_id(vaccine_id)
    if not d:
        raise HTTPException(status_code=404, detail="Cancer vaccine design not found")
    return {
        "id": d.id,
        "patient_id": d.patient_id,
        "tumor_type": d.tumor_type,
        "hla_alleles": d.hla_alleles,
        "mrna_construct_sequence": d.mrna_construct_sequence,
        "polyepitope_junction_cleavability_score": d.polyepitope_junction_cleavability_score,
        "predicted_immunogenicity_index": d.predicted_immunogenicity_index,
        "neoepitopes": [
            {
                "id": ep.id,
                "mutated_gene": ep.mutated_gene,
                "mutation_type": ep.mutation_type,
                "peptide_sequence": ep.peptide_sequence,
                "wildtype_sequence": ep.wildtype_sequence,
                "hla_restriction": ep.hla_restriction,
                "mhc_binding_affinity_ic50_nm": ep.mhc_binding_affinity_ic50_nm,
                "clonality_vaf_pct": ep.clonality_vaf_pct,
                "expression_tpm": ep.expression_tpm,
                "immunogenicity_rank_score": ep.immunogenicity_rank_score,
                "is_selected_for_vaccine": ep.is_selected_for_vaccine,
            }
            for ep in d.neoepitopes
        ],
        "schedules": [
            {
                "id": s.id,
                "adjuvant_type": s.adjuvant_type,
                "dose_schedule_days": s.dose_schedule_days,
                "booster_frequency_weeks": s.booster_frequency_weeks,
                "predicted_cd8_tcell_response_pct": s.predicted_cd8_tcell_response_pct,
            }
            for s in d.schedules
        ],
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }
