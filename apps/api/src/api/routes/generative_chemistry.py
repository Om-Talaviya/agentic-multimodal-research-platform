"""Generative Chemistry & Antibody Design REST API Routes (Phase 43)."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_current_user
from database.models.user import User as DBUser
from database.repositories.generative_chemistry_repo import GenerativeChemistryRepository
from research.generative_chemistry_engine import GenerativeChemistryEngine

router = APIRouter(prefix="/chemistry", tags=["Generative Chemistry & Biotherapeutics"])

class GenerateMoleculesRequest(BaseModel):
    target_protein: str = Field(..., description="Target protein receptor (e.g. PCSK9, KRAS-G12D, EGFR)")
    lead_scaffold_smiles: Optional[str] = None
    n_candidates: int = Field(5, ge=1, le=20)
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None

class OptimizeAntibodyRequest(BaseModel):
    antigen_target: str = Field(..., description="Antigen target epitope (e.g. PD-L1, CLDN18.2, HER2)")
    base_cdr_h3: str = Field("CARDLLGYYYGMDVW", description="Parent CDR-H3 sequence loop")
    n_mutants: int = Field(3, ge=1, le=10)
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None

class ADMETDTO(BaseModel):
    human_intestinal_absorption: float
    blood_brain_barrier_permeability: float
    cyp3a4_inhibition_risk: bool
    cyp2d6_inhibition_risk: bool
    herg_cardiotoxicity_risk: bool
    plasma_protein_binding: float
    half_life_hours: float

class MoleculeDTO(BaseModel):
    id: str
    name: str
    target_protein: str
    smiles: str
    molecular_weight: float
    log_p: float
    h_bond_donors: int
    h_bond_acceptors: int
    tpsa: float
    qed_score: float
    synthetic_accessibility: float
    predicted_binding_affinity: float
    lipinski_violations: int
    admet_profile: Optional[ADMETDTO] = None
    created_at: str

class AntibodyDTO(BaseModel):
    id: str
    variant_name: str
    antigen_target: str
    cdr_h3_sequence: str
    kd_affinity_nm: float
    melting_temperature_c: float
    humanness_score: float
    sequence_liabilities_count: int
    created_at: str

@router.post("/generate-molecules", response_model=List[MoleculeDTO], status_code=status.HTTP_201_CREATED)
async def generate_small_molecules(
    req: GenerateMoleculesRequest,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = GenerativeChemistryRepository(db)
    engine = GenerativeChemistryEngine()
    
    generated = engine.generate_small_molecules(
        target_protein=req.target_protein,
        lead_scaffold_smiles=req.lead_scaffold_smiles,
        n_candidates=req.n_candidates,
    )

    results = []
    for g in generated:
        mol = await repo.create_molecule(
            name=g["name"],
            target_protein=g["target_protein"],
            smiles=g["smiles"],
            iupac_name=g.get("iupac_name"),
            molecular_weight=g["molecular_weight"],
            log_p=g["log_p"],
            h_bond_donors=g["h_bond_donors"],
            h_bond_acceptors=g["h_bond_acceptors"],
            rotatable_bonds=g["rotatable_bonds"],
            tpsa=g["tpsa"],
            qed_score=g["qed_score"],
            synthetic_accessibility=g["synthetic_accessibility"],
            predicted_binding_affinity=g["predicted_binding_affinity"],
            lipinski_violations=g["lipinski_violations"],
            workspace_id=req.workspace_id,
            project_id=req.project_id,
        )

        admet_data = g["admet"]
        admet_obj = await repo.create_admet_profile(
            molecule_id=mol.id,
            human_intestinal_absorption=admet_data["human_intestinal_absorption"],
            blood_brain_barrier_permeability=admet_data["blood_brain_barrier_permeability"],
            cyp3a4_inhibition_risk=admet_data["cyp3a4_inhibition_risk"],
            cyp2d6_inhibition_risk=admet_data["cyp2d6_inhibition_risk"],
            herg_cardiotoxicity_risk=admet_data["herg_cardiotoxicity_risk"],
            plasma_protein_binding=admet_data["plasma_protein_binding"],
            half_life_hours=admet_data["half_life_hours"],
        )

        results.append(
            MoleculeDTO(
                id=str(mol.id),
                name=mol.name,
                target_protein=mol.target_protein,
                smiles=mol.smiles,
                molecular_weight=mol.molecular_weight,
                log_p=mol.log_p,
                h_bond_donors=mol.h_bond_donors,
                h_bond_acceptors=mol.h_bond_acceptors,
                tpsa=mol.tpsa,
                qed_score=mol.qed_score,
                synthetic_accessibility=mol.synthetic_accessibility,
                predicted_binding_affinity=mol.predicted_binding_affinity,
                lipinski_violations=mol.lipinski_violations,
                admet_profile=ADMETDTO(
                    human_intestinal_absorption=admet_obj.human_intestinal_absorption,
                    blood_brain_barrier_permeability=admet_obj.blood_brain_barrier_permeability,
                    cyp3a4_inhibition_risk=admet_obj.cyp3a4_inhibition_risk,
                    cyp2d6_inhibition_risk=admet_obj.cyp2d6_inhibition_risk,
                    herg_cardiotoxicity_risk=admet_obj.herg_cardiotoxicity_risk,
                    plasma_protein_binding=admet_obj.plasma_protein_binding,
                    half_life_hours=admet_obj.half_life_hours,
                ),
                created_at=mol.created_at.isoformat(),
            )
        )

    return results

@router.post("/optimize-antibody", response_model=List[AntibodyDTO], status_code=status.HTTP_201_CREATED)
async def optimize_antibody_candidate(
    req: OptimizeAntibodyRequest,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = GenerativeChemistryRepository(db)
    engine = GenerativeChemistryEngine()
    
    mutants = engine.optimize_antibody_cdr(
        antigen_target=req.antigen_target,
        base_cdr_h3=req.base_cdr_h3,
        n_mutants=req.n_mutants,
    )

    results = []
    for m in mutants:
        ab = await repo.create_antibody(
            variant_name=m["variant_name"],
            antigen_target=m["antigen_target"],
            heavy_chain_seq=m["heavy_chain_seq"],
            light_chain_seq=m["light_chain_seq"],
            cdr_h3_sequence=m["cdr_h3_sequence"],
            kd_affinity_nm=m["kd_affinity_nm"],
            melting_temperature_c=m["melting_temperature_c"],
            humanness_score=m["humanness_score"],
            sequence_liabilities_count=m["sequence_liabilities_count"],
            workspace_id=req.workspace_id,
            project_id=req.project_id,
        )
        results.append(
            AntibodyDTO(
                id=str(ab.id),
                variant_name=ab.variant_name,
                antigen_target=ab.antigen_target,
                cdr_h3_sequence=ab.cdr_h3_sequence,
                kd_affinity_nm=ab.kd_affinity_nm,
                melting_temperature_c=ab.melting_temperature_c,
                humanness_score=ab.humanness_score,
                sequence_liabilities_count=ab.sequence_liabilities_count,
                created_at=ab.created_at.isoformat(),
            )
        )
    return results

@router.get("/molecules", response_model=List[MoleculeDTO])
async def list_generated_molecules(
    target_protein: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = GenerativeChemistryRepository(db)
    molecules = await repo.list_molecules(target_protein=target_protein, limit=limit, offset=offset)
    
    out = []
    for m in molecules:
        admet = await repo.get_admet_profile(m.id)
        out.append(
            MoleculeDTO(
                id=str(m.id),
                name=m.name,
                target_protein=m.target_protein,
                smiles=m.smiles,
                molecular_weight=m.molecular_weight,
                log_p=m.log_p,
                h_bond_donors=m.h_bond_donors,
                h_bond_acceptors=m.h_bond_acceptors,
                tpsa=m.tpsa,
                qed_score=m.qed_score,
                synthetic_accessibility=m.synthetic_accessibility,
                predicted_binding_affinity=m.predicted_binding_affinity,
                lipinski_violations=m.lipinski_violations,
                admet_profile=ADMETDTO(
                    human_intestinal_absorption=admet.human_intestinal_absorption,
                    blood_brain_barrier_permeability=admet.blood_brain_barrier_permeability,
                    cyp3a4_inhibition_risk=admet.cyp3a4_inhibition_risk,
                    cyp2d6_inhibition_risk=admet.cyp2d6_inhibition_risk,
                    herg_cardiotoxicity_risk=admet.herg_cardiotoxicity_risk,
                    plasma_protein_binding=admet.plasma_protein_binding,
                    half_life_hours=admet.half_life_hours,
                ) if admet else None,
                created_at=m.created_at.isoformat(),
            )
        )
    return out

@router.get("/antibodies", response_model=List[AntibodyDTO])
async def list_antibody_candidates(
    antigen_target: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = GenerativeChemistryRepository(db)
    antibodies = await repo.list_antibodies(antigen_target=antigen_target, limit=limit, offset=offset)
    return [
        AntibodyDTO(
            id=str(a.id),
            variant_name=a.variant_name,
            antigen_target=a.antigen_target,
            cdr_h3_sequence=a.cdr_h3_sequence,
            kd_affinity_nm=a.kd_affinity_nm,
            melting_temperature_c=a.melting_temperature_c,
            humanness_score=a.humanness_score,
            sequence_liabilities_count=a.sequence_liabilities_count,
            created_at=a.created_at.isoformat(),
        )
        for a in antibodies
    ]

@router.delete("/molecules/{molecule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_molecule(
    molecule_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = GenerativeChemistryRepository(db)
    deleted = await repo.delete_molecule(molecule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Molecule not found")
    return None
