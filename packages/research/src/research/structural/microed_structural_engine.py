"""
Autonomous Engine for Phase 166: Micro-Crystal Electron Diffraction (MicroED) Structural Engine.
"""

import math
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class DiffractionFrameResult(BaseModel):
    frame_number: int
    tilt_angle_deg: float
    reflections_count: int
    i_over_sigma: float


class AtomicRefinementResult(BaseModel):
    cycle: int
    ramachandran_favored: float
    clashscore: float
    electrostatic_potential_peak: float


class MicroEDRefinementResult(BaseModel):
    sample_name: str
    crystal_system: str
    electron_voltage_kv: float
    rotation_range_deg: float
    resolution_angstrom: float
    completeness_percent: float
    r_work: float
    r_free: float
    frames: List[DiffractionFrameResult]
    refinements: List[AtomicRefinementResult]
    recommendations: List[str]


class MicroEDStructuralEngine:
    def __init__(self):
        self.canonical_crystals = {
            "Bovine Trypsin": {"res": 0.85, "r_work": 0.142, "r_free": 0.168, "sym": "Orthorhombic P212121"},
            "Lysozyme Sub-micron": {"res": 0.92, "r_work": 0.138, "r_free": 0.162, "sym": "Tetragonal P43212"},
            "Tau Protofibril Peptide": {"res": 1.05, "r_work": 0.155, "r_free": 0.185, "sym": "Monoclinic P21"},
        }

    def simulate_microed_refinement(
        self,
        sample_name: str,
        voltage_kv: float = 200.0,
        rotation_range: float = 120.0,
        frames_count: int = 5,
    ) -> MicroEDRefinementResult:
        preset = self.canonical_crystals.get(
            sample_name,
            {"res": 0.88, "r_work": 0.145, "r_free": 0.172, "sym": "Orthorhombic P212121"},
        )

        frames: List[DiffractionFrameResult] = []
        step_angle = rotation_range / max(frames_count, 1)

        for i in range(frames_count):
            tilt = round(- (rotation_range / 2.0) + (i * step_angle), 1)
            refl = int(450 + 80 * math.cos(math.radians(tilt)))
            i_sig = round(16.5 - abs(tilt) * 0.08, 1)
            frames.append(
                DiffractionFrameResult(
                    frame_number=i + 1,
                    tilt_angle_deg=tilt,
                    reflections_count=refl,
                    i_over_sigma=i_sig,
                )
            )

        refinements = [
            AtomicRefinementResult(
                cycle=1,
                ramachandran_favored=96.5,
                clashscore=2.8,
                electrostatic_potential_peak=14.2,
            ),
            AtomicRefinementResult(
                cycle=2,
                ramachandran_favored=98.4,
                clashscore=1.4,
                electrostatic_potential_peak=18.6,
            ),
            AtomicRefinementResult(
                cycle=3,
                ramachandran_favored=99.2,
                clashscore=0.9,
                electrostatic_potential_peak=22.1,
            ),
        ]

        recommendations = [
            f"Sub-Ångström MicroED electrostatic Coulomb potential map resolved at {preset['res']} Å resolution.",
            f"Continuous rotation data integration yielded {98.5}% reciprocal space completeness.",
            f"Final refinement converged with R-work = {preset['r_work']} / R-free = {preset['r_free']}.",
        ]

        return MicroEDRefinementResult(
            sample_name=sample_name,
            crystal_system=preset["sym"],
            electron_voltage_kv=voltage_kv,
            rotation_range_deg=rotation_range,
            resolution_angstrom=preset["res"],
            completeness_percent=98.5,
            r_work=preset["r_work"],
            r_free=preset["r_free"],
            frames=frames,
            refinements=refinements,
            recommendations=recommendations,
        )
