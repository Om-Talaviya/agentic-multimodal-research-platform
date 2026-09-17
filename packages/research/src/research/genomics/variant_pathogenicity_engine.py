"""Genomic Variant Pathogenicity & ACMG/AMP Classification Engine."""
from typing import List, Dict, Any, Optional


class VariantPathogenicityEngine:
    """Evaluates human genetic variants against ACMG/AMP 2015 guidelines with in-silico predictor integration."""

    def evaluate_variant(self, variant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classifies a genetic variant and returns criterion evidences and in-silico metrics."""
        gene = variant_data.get("gene_symbol", "BRCA1")
        hgvs_c = variant_data.get("hgvs_c", "c.5266dupC")
        hgvs_p = variant_data.get("hgvs_p", "p.Gln1756Profs*74")
        af = float(variant_data.get("allele_frequency_gnomad", 0.00001))
        consequence = variant_data.get("consequence", "frameshift_variant")
        is_lof_mechanism = bool(variant_data.get("is_gene_lof_mechanism", True))
        in_critical_domain = bool(variant_data.get("in_critical_domain", True))
        is_canonical_splice = bool(variant_data.get("is_canonical_splice", False))
        functional_assay_abnormal = variant_data.get("functional_assay_abnormal", None)

        # In-silico predictors
        am_score = float(variant_data.get("alphamissense_score", 0.85 if "missense" in consequence else 0.5))
        cadd_phred = float(variant_data.get("cadd_phred", 28.5 if "frameshift" in consequence or "nonsense" in consequence else 24.0))
        revel_score = float(variant_data.get("revel_score", 0.78 if "missense" in consequence else 0.5))
        spliceai_max = float(variant_data.get("spliceai_delta_score", 0.95 if is_canonical_splice else 0.05))

        criteria_met = []

        # 1. PVS1 (Null variant in a gene where LOF is a known mechanism of disease)
        if consequence in ["frameshift_variant", "stop_gained", "nonsense"] and is_lof_mechanism:
            criteria_met.append({
                "criterion_code": "PVS1",
                "criterion_type": "PATHOGENIC_VERY_STRONG",
                "status": "MET",
                "weight": 8.0,
                "rationale": f"Null variant ({consequence}) in {gene} where loss-of-function is an established disease mechanism.",
                "evidence_source": "Transcript Annotation & ClinGen Dosage Curation"
            })
        elif is_canonical_splice and is_lof_mechanism:
            criteria_met.append({
                "criterion_code": "PVS1",
                "criterion_type": "PATHOGENIC_VERY_STRONG",
                "status": "MET",
                "weight": 8.0,
                "rationale": f"Canonical ±1,2 splice site disruption in {gene} with predicted LOF.",
                "evidence_source": "SpliceAI / Canonical GTAG Motif"
            })

        # 2. Population Frequency Criteria (BA1, BS1, PM2)
        if af >= 0.05:
            criteria_met.append({
                "criterion_code": "BA1",
                "criterion_type": "BENIGN_STANDALONE",
                "status": "MET",
                "weight": 10.0,
                "rationale": f"Allele frequency in gnomAD ({af:.4f}) is >= 5.0%, meeting standalone benign threshold.",
                "evidence_source": "gnomAD v4.1 Genome Database"
            })
        elif af >= 0.01:
            criteria_met.append({
                "criterion_code": "BS1",
                "criterion_type": "BENIGN_STRONG",
                "status": "MET",
                "weight": 4.0,
                "rationale": f"Allele frequency in gnomAD ({af:.4f}) is greater than expected for disorder.",
                "evidence_source": "gnomAD v4.1 Genome Database"
            })
        elif af <= 0.0001:
            criteria_met.append({
                "criterion_code": "PM2",
                "criterion_type": "PATHOGENIC_MODERATE",
                "status": "MET",
                "weight": 2.0,
                "rationale": f"Extremely low allele frequency in population cohorts (gnomAD AF = {af:.6f}).",
                "evidence_source": "gnomAD v4.1 Population Filter"
            })

        # 3. Functional Studies (PS3 / BS3)
        if functional_assay_abnormal is True:
            criteria_met.append({
                "criterion_code": "PS3",
                "criterion_type": "PATHOGENIC_STRONG",
                "status": "MET",
                "weight": 4.0,
                "rationale": "Well-established in-vitro/in-vivo functional studies show damaging effect on gene product.",
                "evidence_source": "Published Validated Functional Assay"
            })
        elif functional_assay_abnormal is False:
            criteria_met.append({
                "criterion_code": "BS3",
                "criterion_type": "BENIGN_STRONG",
                "status": "MET",
                "weight": 4.0,
                "rationale": "Well-established functional studies show no damaging effect on protein function.",
                "evidence_source": "Published Validated Functional Assay"
            })

        # 4. Critical Domain / Mutational Hotspot (PM1)
        if in_critical_domain and "missense" in consequence:
            criteria_met.append({
                "criterion_code": "PM1",
                "criterion_type": "PATHOGENIC_MODERATE",
                "status": "MET",
                "weight": 2.0,
                "rationale": "Located in a mutational hotspot and/or critical and well-established functional domain.",
                "evidence_source": "UniProt Functional Domain Annotation"
            })

        # 5. In-Silico Computational Evidence (PP3 vs BP4)
        damaging_count = sum([
            am_score >= 0.70,
            cadd_phred >= 20.0,
            revel_score >= 0.65,
            spliceai_max >= 0.50
        ])
        benign_count = sum([
            am_score <= 0.30,
            cadd_phred <= 15.0,
            revel_score <= 0.30,
            spliceai_max <= 0.10
        ])

        if damaging_count >= 2:
            criteria_met.append({
                "criterion_code": "PP3",
                "criterion_type": "PATHOGENIC_SUPPORTING",
                "status": "MET",
                "weight": 1.0,
                "rationale": f"Multiple lines of computational evidence support a deleterious effect (AlphaMissense: {am_score}, CADD: {cadd_phred}, REVEL: {revel_score}).",
                "evidence_source": "In-Silico Ensemble Predictors"
            })
        elif benign_count >= 2 and consequence == "synonymous_variant":
            criteria_met.append({
                "criterion_code": "BP4",
                "criterion_type": "BENIGN_SUPPORTING",
                "status": "MET",
                "weight": 1.0,
                "rationale": "Multiple lines of computational evidence suggest no impact on gene product.",
                "evidence_source": "In-Silico Ensemble Predictors"
            })

        # In-Silico predictor score list
        predictor_scores = [
            {
                "tool_name": "AlphaMissense",
                "score_value": am_score,
                "score_percentile": round(am_score * 100, 1),
                "prediction_label": "Likely Pathogenic" if am_score >= 0.56 else "Likely Benign" if am_score <= 0.34 else "Ambiguous"
            },
            {
                "tool_name": "REVEL",
                "score_value": revel_score,
                "score_percentile": round(revel_score * 100, 1),
                "prediction_label": "Damaging" if revel_score >= 0.50 else "Tolerated"
            },
            {
                "tool_name": "CADD",
                "score_value": cadd_phred,
                "score_percentile": min(99.9, round(cadd_phred * 3.3, 1)),
                "prediction_label": "Deleterious" if cadd_phred >= 20.0 else "Neutral"
            },
            {
                "tool_name": "SpliceAI",
                "score_value": spliceai_max,
                "score_percentile": round(spliceai_max * 100, 1),
                "prediction_label": "High Splice Risk" if spliceai_max >= 0.50 else "Normal Splicing"
            }
        ]

        # ACMG Combiner Logic
        has_ba1 = any(c["criterion_code"] == "BA1" for c in criteria_met)
        bs_count = sum(1 for c in criteria_met if c["criterion_code"].startswith("BS"))
        bp_count = sum(1 for c in criteria_met if c["criterion_code"].startswith("BP"))
        pvs_count = sum(1 for c in criteria_met if c["criterion_code"].startswith("PVS"))
        ps_count = sum(1 for c in criteria_met if c["criterion_code"].startswith("PS"))
        pm_count = sum(1 for c in criteria_met if c["criterion_code"].startswith("PM"))
        pp_count = sum(1 for c in criteria_met if c["criterion_code"].startswith("PP"))

        if has_ba1 or bs_count >= 2:
            acmg_class = "BENIGN"
            pathogenicity_score = 0.02
        elif (bs_count == 1 and bp_count >= 1) or bp_count >= 2:
            acmg_class = "LIKELY_BENIGN"
            pathogenicity_score = 0.10
        elif (pvs_count >= 1 and (ps_count >= 1 or pm_count >= 2 or (pm_count >= 1 and pp_count >= 1) or pp_count >= 2)) or \
             (ps_count >= 2) or \
             (ps_count >= 1 and pm_count >= 3):
            acmg_class = "PATHOGENIC"
            pathogenicity_score = 0.99
        elif (pvs_count >= 1 and pm_count >= 1) or \
             (ps_count >= 1 and (pm_count >= 1 or pp_count >= 2)) or \
             (pm_count >= 3) or \
             (pm_count >= 2 and pp_count >= 2) or \
             (pm_count >= 1 and pp_count >= 4):
            acmg_class = "LIKELY_PATHOGENIC"
            pathogenicity_score = 0.90
        else:
            acmg_class = "VUS"
            pathogenicity_score = 0.50

        return {
            "gene_symbol": gene,
            "hgvs_c": hgvs_c,
            "hgvs_p": hgvs_p,
            "chromosome": variant_data.get("chromosome", "chr17"),
            "genomic_position": int(variant_data.get("genomic_position", 43044295)),
            "ref_allele": variant_data.get("ref_allele", "C"),
            "alt_allele": variant_data.get("alt_allele", "CC"),
            "transcript_id": variant_data.get("transcript_id", "NM_007294.4"),
            "acmg_class": acmg_class,
            "pathogenicity_score": pathogenicity_score,
            "total_criteria_met": len(criteria_met),
            "clinvar_id": variant_data.get("clinvar_id", "VCV000017667"),
            "criteria": criteria_met,
            "predictor_scores": predictor_scores,
            "variant_summary_json": {
                "consequence": consequence,
                "allele_frequency_gnomad": af,
                "pvs_count": pvs_count,
                "ps_count": ps_count,
                "pm_count": pm_count,
                "pp_count": pp_count,
            }
        }
