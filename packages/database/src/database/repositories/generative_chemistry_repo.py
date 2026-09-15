"""Generative Chemistry & Antibody Design Repository (Phase 43)."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.generative_chemistry import (
    DBGenerativeMolecule,
    DBADMETProfile,
    DBAntibodyCandidate,
)

class GenerativeChemistryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_molecule(
        self,
        name: str,
        target_protein: str,
        smiles: str,
        molecular_weight: float,
        log_p: float,
        iupac_name: Optional[str] = None,
        h_bond_donors: int = 2,
        h_bond_acceptors: int = 5,
        rotatable_bonds: int = 4,
        tpsa: float = 75.0,
        qed_score: float = 0.85,
        synthetic_accessibility: float = 2.8,
        predicted_binding_affinity: float = -9.4,
        lipinski_violations: int = 0,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        meta_info: Optional[Dict[str, Any]] = None,
    ) -> DBGenerativeMolecule:
        mol = DBGenerativeMolecule(
            name=name,
            target_protein=target_protein,
            smiles=smiles,
            iupac_name=iupac_name,
            molecular_weight=molecular_weight,
            log_p=log_p,
            h_bond_donors=h_bond_donors,
            h_bond_acceptors=h_bond_acceptors,
            rotatable_bonds=rotatable_bonds,
            tpsa=tpsa,
            qed_score=qed_score,
            synthetic_accessibility=synthetic_accessibility,
            predicted_binding_affinity=predicted_binding_affinity,
            lipinski_violations=lipinski_violations,
            workspace_id=workspace_id,
            project_id=project_id,
            meta_info=meta_info or {},
        )
        self.session.add(mol)
        await self.session.commit()
        await self.session.refresh(mol)
        return mol

    async def get_molecule(self, molecule_id: str) -> Optional[DBGenerativeMolecule]:
        stmt = select(DBGenerativeMolecule).where(DBGenerativeMolecule.id == molecule_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_molecules(
        self,
        target_protein: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBGenerativeMolecule]:
        stmt = select(DBGenerativeMolecule)
        if target_protein:
            stmt = stmt.where(DBGenerativeMolecule.target_protein.ilike(f"%{target_protein}%"))
        if workspace_id:
            stmt = stmt.where(DBGenerativeMolecule.workspace_id == workspace_id)
        stmt = stmt.order_by(DBGenerativeMolecule.predicted_binding_affinity.asc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_admet_profile(
        self,
        molecule_id: str,
        human_intestinal_absorption: float = 92.5,
        blood_brain_barrier_permeability: float = 0.45,
        cyp3a4_inhibition_risk: bool = False,
        cyp2d6_inhibition_risk: bool = False,
        herg_cardiotoxicity_risk: bool = False,
        plasma_protein_binding: float = 88.0,
        half_life_hours: float = 6.5,
        meta_info: Optional[Dict[str, Any]] = None,
    ) -> DBADMETProfile:
        admet = DBADMETProfile(
            molecule_id=molecule_id,
            human_intestinal_absorption=human_intestinal_absorption,
            blood_brain_barrier_permeability=blood_brain_barrier_permeability,
            cyp3a4_inhibition_risk=cyp3a4_inhibition_risk,
            cyp2d6_inhibition_risk=cyp2d6_inhibition_risk,
            herg_cardiotoxicity_risk=herg_cardiotoxicity_risk,
            plasma_protein_binding=plasma_protein_binding,
            half_life_hours=half_life_hours,
            meta_info=meta_info or {},
        )
        self.session.add(admet)
        await self.session.commit()
        await self.session.refresh(admet)
        return admet

    async def get_admet_profile(self, molecule_id: str) -> Optional[DBADMETProfile]:
        stmt = select(DBADMETProfile).where(DBADMETProfile.molecule_id == molecule_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_antibody(
        self,
        variant_name: str,
        antigen_target: str,
        heavy_chain_seq: str,
        light_chain_seq: str,
        cdr_h3_sequence: str,
        kd_affinity_nm: float,
        melting_temperature_c: float = 74.5,
        humanness_score: float = 0.92,
        sequence_liabilities_count: int = 0,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        meta_info: Optional[Dict[str, Any]] = None,
    ) -> DBAntibodyCandidate:
        ab = DBAntibodyCandidate(
            variant_name=variant_name,
            antigen_target=antigen_target,
            heavy_chain_seq=heavy_chain_seq,
            light_chain_seq=light_chain_seq,
            cdr_h3_sequence=cdr_h3_sequence,
            kd_affinity_nm=kd_affinity_nm,
            melting_temperature_c=melting_temperature_c,
            humanness_score=humanness_score,
            sequence_liabilities_count=sequence_liabilities_count,
            workspace_id=workspace_id,
            project_id=project_id,
            meta_info=meta_info or {},
        )
        self.session.add(ab)
        await self.session.commit()
        await self.session.refresh(ab)
        return ab

    async def get_antibody(self, antibody_id: str) -> Optional[DBAntibodyCandidate]:
        stmt = select(DBAntibodyCandidate).where(DBAntibodyCandidate.id == antibody_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_antibodies(
        self,
        antigen_target: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBAntibodyCandidate]:
        stmt = select(DBAntibodyCandidate)
        if antigen_target:
            stmt = stmt.where(DBAntibodyCandidate.antigen_target.ilike(f"%{antigen_target}%"))
        if workspace_id:
            stmt = stmt.where(DBAntibodyCandidate.workspace_id == workspace_id)
        stmt = stmt.order_by(DBAntibodyCandidate.kd_affinity_nm.asc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_molecule(self, molecule_id: str) -> bool:
        mol = await self.get_molecule(molecule_id)
        if not mol:
            return False
        await self.session.delete(mol)
        await self.session.commit()
        return True
