"""
ADC Payload-Linker Optimization Engine (Phase 59).
Calculates DAR distributions, bystander killing indices, Cathepsin B cleavability,
and multi-parameter therapeutic indices.
"""
from typing import Any, Dict, List, Optional
import hashlib


class ADCDesignEngine:
    """Simulates ADC payload conjugation, linker stability, and therapeutic index calculation."""

    PAYLOAD_PRESETS = [
        {"name": "DXd (Deruxtecan)", "class": "Topoisomerase I Inhibitor", "linker": "GGFG Tetrapeptide", "dar": 7.8, "bystander": 0.95, "half_life": 192.0},
        {"name": "MMAE (Vedotin)", "class": "Auristatin (Microtubule)", "linker": "Val-Cit PABC", "dar": 3.9, "bystander": 0.88, "half_life": 168.0},
        {"name": "DM1 (Emtansine)", "class": "Maytansinoid", "linker": "MCC Non-Cleavable", "dar": 3.5, "bystander": 0.25, "half_life": 144.0},
        {"name": "PBD Dimer (Tesirine)", "class": "DNA Cross-Linker", "linker": "Val-Ala Cleavable", "dar": 2.0, "bystander": 0.65, "half_life": 120.0},
        {"name": "SN-38 (Govitecan)", "class": "Topoisomerase I Inhibitor", "linker": "CL2A Hydrolysable", "dar": 7.6, "bystander": 0.92, "half_life": 160.0},
    ]

    @classmethod
    def screen_payload_linkers(
        cls,
        antibody_name: str,
        target_antigen: str,
        target_dar: float = 4.0,
    ) -> List[Dict[str, Any]]:
        """Screens payload-linker combinations and scores therapeutic window."""
        seed = int(hashlib.md5(f"{antibody_name}_{target_antigen}".encode()).hexdigest()[:8], 16)
        constructs = []

        for i, p in enumerate(cls.PAYLOAD_PRESETS):
            agg = round(1.2 + ((seed + i) % 15) * 0.1, 1)
            # Therapeutic Index = (Bystander * 4.0) + (HalfLife / 24.0) - (Agg * 0.8) + (DAR match)
            dar_delta = abs(p["dar"] - target_dar)
            ti_score = round(max(3.0, (p["bystander"] * 5.0) + (p["half_life"] / 30.0) - (agg * 0.5) - (dar_delta * 0.3)), 2)
            is_lead = ti_score >= 8.5 or (p["name"].startswith("DXd") and target_dar >= 6.0)

            constructs.append({
                "construct_code": f"{antibody_name[:4].upper()}-{p['name'][:3].upper()}-{i+1:02d}",
                "payload_name": p["name"],
                "payload_class": p["class"],
                "linker_type": p["linker"],
                "measured_dar": p["dar"],
                "bystander_killing_score": p["bystander"],
                "plasma_half_life_hours": p["half_life"],
                "aggregation_propensity_pct": agg,
                "therapeutic_index_score": ti_score,
                "recommended_lead": is_lead,
            })

        return sorted(constructs, key=lambda x: x["therapeutic_index_score"], reverse=True)
