"""Mitochondrial OXPHOS Bioenergetics & ROS Dynamics Engine (Phase 144)."""

import math
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class BioenergeticsSimulationRequest(BaseModel):
    cell_line: str
    substrate_type: str = "Pyruvate/Malate"  # Pyruvate/Malate, Succinate, Palmitoyl-CoA
    uncoupler_fccp_concentration_um: float = Field(default=0.5, ge=0.0, le=5.0)
    complex_i_inhibition_pct: float = Field(default=0.0, ge=0.0, le=100.0)


class ETCComplexStatus(BaseModel):
    complex_id: str
    activity_pct: float
    atp_yield_ratio: float


class BioenergeticsSimulationResult(BaseModel):
    cell_line: str
    basal_ocr_pmol_min: float
    atp_linked_respiration: float
    proton_leak: float
    maximal_respiratory_capacity: float
    spare_respiratory_capacity: float
    superoxide_emission_rate: float
    delta_psi_mv: float
    etc_complexes: List[ETCComplexStatus]
    status: str = "COMPLETED"


class MitochondrialBioenergeticsEngine:
    """Simulates chemiosmotic OXPHOS ATP synthesis, proton leak, and ROS generation."""

    def simulate(self, req: BioenergeticsSimulationRequest) -> BioenergeticsSimulationResult:
        i_factor = 1.0 - (req.complex_i_inhibition_pct / 100.0)
        basal = round(220.0 * i_factor, 1)
        atp_linked = round(165.0 * i_factor, 1)
        leak = round(25.0 + 10.0 * (req.uncoupler_fccp_concentration_um / 2.0), 1)
        maximal = round((380.0 + 120.0 * min(2.0, req.uncoupler_fccp_concentration_um)) * i_factor, 1)
        spare = round(max(0.0, maximal - basal), 1)

        ros = round(max(0.01, 0.035 * (1.0 + (req.complex_i_inhibition_pct / 40.0))), 3)
        delta_psi = round(-170.0 + 15.0 * (req.uncoupler_fccp_concentration_um / 1.0), 1)

        complexes = [
            ETCComplexStatus(complex_id="Complex I (NADH Dehydrogenase)", activity_pct=round(100.0 * i_factor, 1), atp_yield_ratio=2.5),
            ETCComplexStatus(complex_id="Complex II (Succinate Dehydrogenase)", activity_pct=100.0, atp_yield_ratio=1.5),
            ETCComplexStatus(complex_id="Complex III (Cytochrome bc1)", activity_pct=98.5, atp_yield_ratio=2.0),
            ETCComplexStatus(complex_id="Complex IV (Cytochrome c Oxidase)", activity_pct=99.0, atp_yield_ratio=1.0),
            ETCComplexStatus(complex_id="Complex V (ATP Synthase)", activity_pct=round(95.0 * i_factor, 1), atp_yield_ratio=1.0),
        ]

        return BioenergeticsSimulationResult(
            cell_line=req.cell_line,
            basal_ocr_pmol_min=basal,
            atp_linked_respiration=atp_linked,
            proton_leak=leak,
            maximal_respiratory_capacity=maximal,
            spare_respiratory_capacity=spare,
            superoxide_emission_rate=ros,
            delta_psi_mv=delta_psi,
            etc_complexes=complexes,
        )
