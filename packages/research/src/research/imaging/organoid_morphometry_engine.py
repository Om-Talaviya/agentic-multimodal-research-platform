"""Phase 147: Autonomous 3D Tumor Organoid High-Content Morphometry Engine."""

import math
from typing import List, Optional
from pydantic import BaseModel, Field


class ZStackSliceDto(BaseModel):
    depth_um: float
    area_um2: float
    circularity: float
    fluorescence_intensity: float
    live_dead_ratio: float


class DrugDoseDto(BaseModel):
    compound_name: str
    dose_uM: float
    viability_pct: float
    invasion_inhibition_pct: float
    computed_ic50_uM: float


class OrganoidAnalysisRequest(BaseModel):
    study_name: str = "Patient Spheroid High-Content Screen"
    tumor_type: str = "Glioblastoma Multiforme"
    z_slices_count: int = 5
    primary_compound: str = "Temozolomide"
    compound_dose_uM: float = 10.0


class OrganoidAnalysisResult(BaseModel):
    study_name: str
    tumor_type: str
    mean_diameter_um: float
    mean_volume_um3: float
    sphericity_index: float
    necrotic_core_ratio: float
    hypoxia_gradient_slope: float
    z_slices: List[ZStackSliceDto]
    dose_responses: List[DrugDoseDto]


class OrganoidMorphometryEngine:
    def analyze(self, req: OrganoidAnalysisRequest) -> OrganoidAnalysisResult:
        z_slices: List[ZStackSliceDto] = []
        base_area = 150000.0
        depth_step = 50.0

        for i in range(req.z_slices_count):
            depth = i * depth_step
            # Gaussian-like slice profile
            norm = math.exp(-((i - (req.z_slices_count - 1) / 2.0) ** 2) / 1.5)
            area = base_area * norm + 20000.0
            circ = round(0.88 + 0.08 * norm, 3)
            intensity = round(500.0 + 350.0 * norm, 1)
            ld_ratio = round(max(1.2, 6.0 * norm), 2)
            z_slices.append(
                ZStackSliceDto(
                    depth_um=depth,
                    area_um2=round(area, 1),
                    circularity=circ,
                    fluorescence_intensity=intensity,
                    live_dead_ratio=ld_ratio,
                )
            )

        # Trapezoidal volume integration
        vol = 0.0
        for j in range(len(z_slices) - 1):
            dz = abs(z_slices[j+1].depth_um - z_slices[j].depth_um)
            vol += ((z_slices[j].area_um2 + z_slices[j+1].area_um2) / 2.0) * dz

        max_area = max(s.area_um2 for s in z_slices)
        radius = math.sqrt(max_area / math.pi)
        diameter = round(radius * 2.0, 2)
        sphericity = round(sum(s.circularity for s in z_slices) / len(z_slices), 3)

        min_ld = min(s.live_dead_ratio for s in z_slices)
        necrotic_ratio = round(max(0.08, min(0.45, (5.0 - min_ld) / 10.0 + 0.05)), 3)
        hypoxia_slope = round(-0.0003 * (diameter / 100.0), 5)

        # Compound response
        ic50 = 12.5 if req.primary_compound == "Temozolomide" else 3.5
        viab = round(100.0 / (1.0 + (req.compound_dose_uM / ic50) ** 1.4), 2)
        inhibit = round(100.0 - viab * 0.82, 2)

        dose_responses = [
            DrugDoseDto(
                compound_name=req.primary_compound,
                dose_uM=req.compound_dose_uM,
                viability_pct=viab,
                invasion_inhibition_pct=inhibit,
                computed_ic50_uM=ic50,
            )
        ]

        return OrganoidAnalysisResult(
            study_name=req.study_name,
            tumor_type=req.tumor_type,
            mean_diameter_um=diameter,
            mean_volume_um3=round(vol, 1),
            sphericity_index=sphericity,
            necrotic_core_ratio=necrotic_ratio,
            hypoxia_gradient_slope=hypoxia_slope,
            z_slices=z_slices,
            dose_responses=dose_responses,
        )
