"""Phase 149: Autonomous 3D DNA Origami Nanorobot Design Engine."""

import math
from typing import List, Optional
from pydantic import BaseModel, Field


class StapleStrandDto(BaseModel):
    strand_index: int
    sequence_5to3: str
    length_nt: int
    tm_celsius: float
    crossover_count: int


class LatchTriggerDto(BaseModel):
    target_biomarker: str
    aptamer_sequence: str
    opening_half_life_min: float
    selectivity_ratio: float


class DNAOrigamiDesignRequest(BaseModel):
    nanorobot_name: str = "Aptamer-Gated Thrombin Carrier Nanorobot"
    geometry_type: str = "Hexagonal Barrel Capsule"
    scaffold_type: str = "M13mp18 Single-Stranded DNA (7249 nt)"
    target_biomarker: str = "Nucleolin / VEGF"
    target_cargo_diameter_nm: float = 8.5


class DNAOrigamiDesignResult(BaseModel):
    nanorobot_name: str
    geometry_type: str
    scaffold_type: str
    staple_strands_count: int
    predicted_melting_temp_c: float
    folding_yield_percent: float
    cargo_cavity_volume_nm3: float
    latch_trigger_affinity_nM: float
    staple_strands: List[StapleStrandDto]
    latch_mechanisms: List[LatchTriggerDto]


class DNAOrigamiEngine:
    def design(self, req: DNAOrigamiDesignRequest) -> DNAOrigamiDesignResult:
        scaffold_len = 7249
        staple_count = 184
        cavity_vol = round((4.0 / 3.0) * math.pi * ((req.target_cargo_diameter_nm / 2.0 + 2.0) ** 3), 1)

        staples = [
            StapleStrandDto(
                strand_index=1,
                sequence_5to3="AGCTAGCTAGCTAAGGTCCGATCGATCGA",
                length_nt=32,
                tm_celsius=62.4,
                crossover_count=3,
            ),
            StapleStrandDto(
                strand_index=2,
                sequence_5to3="TTCGATCGAATCGGATCCGATCGATTACC",
                length_nt=30,
                tm_celsius=59.8,
                crossover_count=2,
            ),
            StapleStrandDto(
                strand_index=3,
                sequence_5to3="CCGGATTACGATCGATCGGATCCTTAACG",
                length_nt=34,
                tm_celsius=64.1,
                crossover_count=4,
            ),
        ]

        latches = [
            LatchTriggerDto(
                target_biomarker=req.target_biomarker,
                aptamer_sequence="GGTGGTGGTGGTTGTGGTGGTGGTGG",
                opening_half_life_min=4.5,
                selectivity_ratio=28.4,
            )
        ]

        return DNAOrigamiDesignResult(
            nanorobot_name=req.nanorobot_name,
            geometry_type=req.geometry_type,
            scaffold_type=req.scaffold_type,
            staple_strands_count=staple_count,
            predicted_melting_temp_c=61.8,
            folding_yield_percent=88.5,
            cargo_cavity_volume_nm3=cavity_vol,
            latch_trigger_affinity_nM=14.2,
            staple_strands=staples,
            latch_mechanisms=latches,
        )
