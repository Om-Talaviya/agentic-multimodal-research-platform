"""CTC Engine (Phase 111)."""
from typing import Dict, Any

class CTCTrajectoryEngine:
    ORGANS = ["Hepatic (Liver)", "Pulmonary (Lung)", "Osseous (Bone)", "Cerebral (Brain)"]

    def analyze_ctc_trajectory(self, patient_id: str, primary_tumor: str, ctc_count: int,
                               epcam_expression: float, vimentin_expression: float) -> Dict[str, Any]:
        emt_score = round(vimentin_expression / (epcam_expression + vimentin_expression + 1e-6), 3)
        risk_tier = "HIGH" if ctc_count >= 10 and emt_score >= 0.6 else "INTERMEDIATE" if ctc_count >= 5 else "LOW"
        sites = []
        for org in self.ORGANS:
            prob = round(0.4 + (0.5 * emt_score * (ctc_count / (ctc_count + 10))), 3)
            seed_soil = round(70.0 + (prob * 25.0), 1)
            sites.append({
                "target_organ": org,
                "colonization_probability": min(0.98, prob),
                "seed_soil_compatibility": seed_soil,
                "chemokine_gradient": round(0.7 + (prob * 0.25), 2),
            })
        sites.sort(key=lambda x: x["colonization_probability"], reverse=True)
        return {
            "patient_id": patient_id,
            "primary_tumor_type": primary_tumor,
            "ctc_enumeration_per_7_5ml": ctc_count,
            "emt_hybrid_score": emt_score,
            "risk_tier": risk_tier,
            "dominant_tropism": sites[0]["target_organ"],
            "colonization_sites": sites,
            "summary": f"Identified {ctc_count} CTCs with EMT score {emt_score}."
        }
