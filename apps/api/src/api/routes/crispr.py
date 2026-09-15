"""Autonomous Synthetic Biology & CRISPR Gene Editing Guide RNA Design API Routes (Phase 40)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.user import User as DBUser
from database.repositories.crispr_repo import CRISPRRepository
from research.crispr_engine import CRISPRGuideDesignEngine
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/crispr", tags=["crispr"])
engine = CRISPRGuideDesignEngine()


# --- Pydantic Request / Response Schemas ---

class CRISPRDesignRequest(BaseModel):
    target_gene: str = Field(..., description="Target gene symbol (e.g. PCSK9, BCL11A, VEGFA)")
    target_sequence: str = Field(..., description="DNA sense strand sequence (min 30 bp)")
    cas_type: str = Field("SpCas9", description="CRISPR nuclease type: SpCas9, Cas12a_Cpf1, xCas9, SaCas9, Cas9_HF1")
    organism: str = Field("Homo sapiens", description="Host organism (e.g. Homo sapiens, Mus musculus)")
    description: Optional[str] = Field(None, description="Optional description of the targeting campaign")
    max_guides: int = Field(15, ge=1, le=50, description="Maximum candidate gRNAs to evaluate and persist")
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


# --- Endpoint Implementations ---

@router.post("/design", status_code=status.HTTP_201_CREATED)
async def design_crispr_guides(
    payload: CRISPRDesignRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute CRISPR candidate guide RNA scanning, on-target Azimuth scoring, off-target CFD calculation, and base editing window profiling."""
    cleaned_seq = payload.target_sequence.upper().strip()
    if len(cleaned_seq) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target DNA sequence must be at least 30 bp in length.",
        )

    result = engine.design_guides(
        target_gene=payload.target_gene,
        target_sequence=cleaned_seq,
        organism=payload.organism,
        cas_enzyme=payload.cas_type,
        max_guides=payload.max_guides,
    )

    repo = CRISPRRepository(session)
    design = await repo.create_design(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        target_gene=result.target_gene,
        genomic_locus=result.genomic_locus,
        organism=result.organism,
        cas_enzyme=result.cas_enzyme,
        pam_motif=result.pam_motif,
        target_strand=result.target_strand,
        editing_modality=result.editing_modality,
        target_sequence_fasta=result.target_sequence_fasta,
        design_summary_json=result.design_summary_json,
    )

    # Persist Guides, Off-Targets, and Base Editing Profiles
    guides_data = [
        {
            "guide_name": g.guide_name,
            "spacer_sequence_20nt": g.spacer_sequence_20nt,
            "pam_sequence": g.pam_sequence,
            "genomic_position": g.genomic_position,
            "strand": g.strand,
            "cut_position_rel": g.cut_position_rel,
            "on_target_efficiency_score": g.on_target_efficiency_score,
            "off_target_cfd_score": g.off_target_cfd_score,
            "gc_content_pct": g.gc_content_pct,
            "secondary_structure_delta_g": g.secondary_structure_delta_g,
            "recommendation_tier": g.recommendation_tier,
            "oligo_forward_top": g.oligo_forward_top,
            "oligo_reverse_bottom": g.oligo_reverse_bottom,
        }
        for g in result.guide_rnas
    ]
    created_guides = await repo.add_guide_rnas(design.id, guides_data)

    guides_response = []
    for g_res, db_g in zip(result.guide_rnas, created_guides):
        # Off-targets
        if g_res.off_target_sites:
            await repo.add_off_target_sites(
                guide_id=db_g.id,
                off_targets_data=[ot.model_dump() for ot in g_res.off_target_sites],
            )

        # Base editing
        if g_res.base_editing_profiles:
            await repo.add_base_editing_profiles(
                guide_id=db_g.id,
                profiles_data=[be.model_dump() for be in g_res.base_editing_profiles],
            )

        guides_response.append({
            "id": str(db_g.id),
            "guide_name": db_g.guide_name,
            "guide_sequence": db_g.spacer_sequence_20nt,
            "pam_sequence": db_g.pam_sequence,
            "strand": db_g.strand,
            "genomic_position": db_g.genomic_position,
            "gc_content": db_g.gc_content_pct,
            "on_target_score": db_g.on_target_efficiency_score,
            "off_target_cfd_score": db_g.off_target_cfd_score,
            "tier": db_g.recommendation_tier,
            "oligo_forward_top": db_g.oligo_forward_top,
            "oligo_reverse_bottom": db_g.oligo_reverse_bottom,
            "off_target_sites_count": len(g_res.off_target_sites),
            "base_editing_profiles_count": len(g_res.base_editing_profiles),
        })

    return {
        "design_id": str(design.id),
        "target_gene": design.target_gene,
        "cas_enzyme": design.cas_enzyme,
        "pam_motif": design.pam_motif,
        "organism": design.organism,
        "total_guides_evaluated": result.total_guides_evaluated,
        "optimal_guides_count": result.optimal_guides_count,
        "guides": guides_response,
        "created_at": design.created_at.isoformat() if design.created_at else None,
    }


@router.get("/designs", status_code=status.HTTP_200_OK)
async def list_crispr_designs(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    target_gene: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """List CRISPR guide RNA design campaigns for the current user."""
    repo = CRISPRRepository(session)
    designs = await repo.list_designs(
        user_id=current_user.id,
        workspace_id=workspace_id,
        project_id=project_id,
        target_gene=target_gene,
        limit=limit,
        offset=offset,
    )

    items = []
    for d in designs:
        items.append({
            "id": str(d.id),
            "user_id": str(d.user_id),
            "workspace_id": str(d.workspace_id) if d.workspace_id else None,
            "project_id": str(d.project_id) if d.project_id else None,
            "target_gene": d.target_gene,
            "genomic_locus": d.genomic_locus,
            "cas_type": d.cas_enzyme,
            "cas_enzyme": d.cas_enzyme,
            "pam_pattern": d.pam_motif,
            "pam_motif": d.pam_motif,
            "organism": d.organism,
            "editing_modality": d.editing_modality,
            "design_summary_json": d.design_summary_json,
            "guides_count": len(d.guide_rnas) if d.guide_rnas else 0,
            "top_guide_efficiency": d.design_summary_json.get("top_on_target_score", 85.0),
            "total_guides_evaluated": d.design_summary_json.get("total_pam_sites_found", len(d.guide_rnas) if d.guide_rnas else 0),
            "created_at": d.created_at.isoformat() if d.created_at else None,
        })

    return {
        "items": items,
        "count": len(items),
        "limit": limit,
        "offset": offset,
    }


@router.get("/designs/{design_id}", status_code=status.HTTP_200_OK)
async def get_crispr_design(
    design_id: uuid.UUID,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve complete CRISPR design campaign with all guide RNAs, off-target loci, and base editing profiles."""
    repo = CRISPRRepository(session)
    d = await repo.get_design(design_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CRISPR design campaign not found")

    guides_data = []
    for g in d.guide_rnas:
        guides_data.append({
            "id": str(g.id),
            "guide_name": g.guide_name,
            "guide_sequence": g.spacer_sequence_20nt,
            "pam_sequence": g.pam_sequence,
            "strand": g.strand,
            "start_pos": g.genomic_position,
            "end_pos": g.genomic_position + len(g.spacer_sequence_20nt) - 1,
            "genomic_position": g.genomic_position,
            "gc_content": g.gc_content_pct,
            "on_target_score": g.on_target_efficiency_score,
            "azimuth_efficiency": g.on_target_efficiency_score,
            "off_target_cfd_score": g.off_target_cfd_score,
            "composite_score": round(g.on_target_efficiency_score * 0.6 + g.off_target_cfd_score * 0.4, 1),
            "tier": "TIER_1" if g.recommendation_tier == "optimal" else "TIER_2" if g.recommendation_tier == "moderate" else "TIER_3",
            "golden_gate_top_oligo": g.oligo_forward_top.replace("5'-", "").replace("-3'", ""),
            "golden_gate_bottom_oligo": g.oligo_reverse_bottom.replace("5'-", "").replace("-3'", ""),
            "oligo_forward_top": g.oligo_forward_top,
            "oligo_reverse_bottom": g.oligo_reverse_bottom,
            "off_targets": [
                {
                    "id": str(ot.id),
                    "locus_name": ot.gene_annotation,
                    "chromosome": ot.chromosome,
                    "target_sequence": ot.mismatched_sequence,
                    "mismatches_count": ot.mismatch_count,
                    "cfd_off_target_score": ot.cfd_cleavage_score * 100.0,
                    "is_exonic": ot.is_exonic,
                    "annotation": ot.gene_annotation,
                }
                for ot in g.off_target_sites
            ],
            "base_editing_profiles": [
                {
                    "id": str(be.id),
                    "editor_type": be.editing_type,
                    "target_nucleotide": be.target_base,
                    "edited_nucleotide": "G" if be.target_base == "A" else "T",
                    "window_start": be.editing_window_start,
                    "window_end": be.editing_window_end,
                    "editing_efficiency": be.activity_score_pct,
                    "bystander_mutation_risk": be.bystander_bases_count > 0,
                }
                for be in g.base_editing_profiles
            ],
        })

    return {
        "id": str(d.id),
        "user_id": str(d.user_id),
        "workspace_id": str(d.workspace_id) if d.workspace_id else None,
        "project_id": str(d.project_id) if d.project_id else None,
        "target_gene": d.target_gene,
        "target_sequence": d.target_sequence_fasta,
        "genomic_locus": d.genomic_locus,
        "cas_type": d.cas_enzyme,
        "cas_enzyme": d.cas_enzyme,
        "pam_pattern": d.pam_motif,
        "pam_motif": d.pam_motif,
        "organism": d.organism,
        "editing_modality": d.editing_modality,
        "total_guides_evaluated": d.design_summary_json.get("total_pam_sites_found", len(d.guide_rnas)),
        "top_guide_efficiency": d.design_summary_json.get("top_on_target_score", 85.0),
        "design_summary_json": d.design_summary_json,
        "guides": guides_data,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


@router.get("/guides/{guide_id}/oligos", status_code=status.HTTP_200_OK)
async def get_guide_oligos(
    guide_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve Golden Gate cloning oligos and protocol order spec for a specific guide RNA."""
    repo = CRISPRRepository(session)
    g = await repo.get_guide(guide_id)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide RNA not found")

    top_clean = g.oligo_forward_top.replace("5'-", "").replace("-3'", "")
    bottom_clean = g.oligo_reverse_bottom.replace("5'-", "").replace("-3'", "")

    return {
        "guide_id": str(g.id),
        "guide_sequence": g.spacer_sequence_20nt,
        "pam_sequence": g.pam_sequence,
        "top_oligo": {
            "name": f"gRNA_Top_{g.spacer_sequence_20nt[:6]}",
            "sequence": top_clean,
            "length": len(top_clean),
            "cloning_overhang_5p": "CACC",
            "purification": "Standard Desalting",
        },
        "bottom_oligo": {
            "name": f"gRNA_Bottom_{g.spacer_sequence_20nt[:6]}",
            "sequence": bottom_clean,
            "length": len(bottom_clean),
            "cloning_overhang_5p": "AAAC",
            "purification": "Standard Desalting",
        },
        "annealing_protocol": {
            "buffer": "1X T4 Ligation Buffer or NEBuffer 2.1",
            "steps": [
                "Mix 10 uL Top Oligo (100 uM) + 10 uL Bottom Oligo (100 uM) + 80 uL Water (10 uM duplex)",
                "Heat to 95°C for 5 minutes in a thermocycler",
                "Ramp down from 95°C to 25°C at -5°C/minute (or let cool slowly to room temp)",
                "Dilute 1:200 in sterile water for Golden Gate ligation into BsmBI/BsaI digested pSpCas9(BB)-2A-Puro (PX459) or similar backbone",
            ],
        },
    }


@router.get("/designs/{design_id}/export-genbank", status_code=status.HTTP_200_OK)
async def export_crispr_genbank(
    design_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Export the targeted sequence and candidate guide RNAs in annotated GenBank (.gb) format."""
    repo = CRISPRRepository(session)
    d = await repo.get_design(design_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CRISPR design campaign not found")

    seq = d.target_sequence_fasta
    seq_len = len(seq)

    gb_lines = [
        f"LOCUS       {d.target_gene[:12]:<12} {seq_len:>8} bp    DNA     linear   SYN 15-SEP-2026",
        f"DEFINITION  Target sequence for CRISPR gene editing ({d.cas_enzyme}) in {d.organism}.",
        f"ACCESSION   {str(d.id)[:8]}",
        f"VERSION     {str(d.id)[:8]}.1",
        f"SOURCE      {d.organism}",
        f"  ORGANISM  {d.organism}",
        "FEATURES             Location/Qualifiers",
        f"     source          1..{seq_len}",
        f'                     /organism="{d.organism}"',
        f'                     /gene="{d.target_gene}"',
    ]

    for idx, g in enumerate(d.guide_rnas, 1):
        end_coord = g.genomic_position + len(g.spacer_sequence_20nt) - 1
        feature_loc = f"{g.genomic_position}..{end_coord}" if g.strand == "+" else f"complement({g.genomic_position}..{end_coord})"
        gb_lines.extend([
            f"     misc_feature    {feature_loc}",
            f'                     /label="{g.guide_name}"',
            f'                     /note="Azimuth: {g.on_target_efficiency_score:.1f}%, CFD: {g.off_target_cfd_score:.1f}, PAM: {g.pam_sequence}"',
            f'                     /guide_seq="{g.spacer_sequence_20nt}"',
        ])

    gb_lines.append("ORIGIN")
    for i in range(0, seq_len, 60):
        chunk = seq[i:i+60].lower()
        sub_chunks = [chunk[j:j+10] for j in range(0, len(chunk), 10)]
        gb_lines.append(f"{i+1:>9} " + " ".join(sub_chunks))
    gb_lines.append("//\n")

    content = "\n".join(gb_lines)
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{d.target_gene}_CRISPR_Guides.gb"'},
    )


@router.delete("/designs/{design_id}", status_code=status.HTTP_200_OK)
async def delete_crispr_design(
    design_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete a CRISPR design campaign."""
    repo = CRISPRRepository(session)
    success = await repo.delete_design(design_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CRISPR design campaign not found")
    return {"status": "deleted", "design_id": str(design_id)}
