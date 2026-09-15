import pytest
from research.patents.prior_art import PatentPriorArtEngine


def test_decompose_claim_limitations():
    claim = (
        "A quantum computing apparatus comprising: "
        "a plurality of superconducting transmon qubits; "
        "a microwave control line coupled to each qubit; "
        "and a digital signal processor configured to execute pulse sequences."
    )
    decomp = PatentPriorArtEngine.decompose_claim_limitations(claim)
    assert decomp["preamble"].startswith("A quantum computing apparatus")
    assert decomp["transition"].lower() == "comprising"
    assert decomp["total_limitations"] >= 3
    assert len(decomp["elements"]) >= 3
    for el in decomp["elements"]:
        assert len(el["keywords"]) > 0


def test_evaluate_prior_art_anticipation_novel():
    target = (
        "A quantum memory system comprising: "
        "a laser-cooled neutral atom array; "
        "a topological optical lattice; "
        "and a zero-noise single photon detector."
    )
    prior_art = [
        "A classical optical switch comprising a fiber optic cable and an LED source."
    ]

    result = PatentPriorArtEngine.evaluate_prior_art_anticipation(target, prior_art)
    assert result["verdict"] in ["distinguishable", "non_infringing"]
    assert result["novelty_score"] >= 0.80
    assert result["overlap_ratio"] <= 0.30
    assert len(result["claim_chart"]) >= 3


def test_evaluate_prior_art_anticipation_anticipated():
    target = (
        "A computing device comprising: "
        "a tensor processing unit; "
        "an asynchronous interconnect fabric; "
        "and a dynamic memory buffer."
    )
    prior_art = [
        "A computing device comprising a tensor processing unit, an asynchronous interconnect fabric, and a dynamic memory buffer for matrix multiplication."
    ]

    result = PatentPriorArtEngine.evaluate_prior_art_anticipation(target, prior_art)
    assert result["verdict"] in ["anticipates_102", "obvious_103"]
    assert result["overlap_ratio"] >= 0.60
    assert result["mitigation_strategy"] is not None


def test_generate_fto_assessment():
    target_claims = [
        "A quantum synthesizer comprising: a topological lattice; and an algorithmic scheduler.",
    ]
    patents = [
        {
            "patent_number": "US-11948201-B2",
            "title": "Quantum Hardware Matrix Acceleration",
            "assignee": "DeepScale",
            "claims": ["A quantum computing apparatus comprising tensor processing cores."],
            "abstract": "Matrix calculations in quantum computing.",
        }
    ]

    fto = PatentPriorArtEngine.generate_fto_assessment(target_claims, patents)
    assert fto["total_examined_patents"] == 1
    assert fto["fto_clearance_percentage"] >= 70.0
    assert len(fto["white_space_opportunities"]) >= 1
    assert len(fto["claim_chart_matrices"]) == 1


def test_synthesize_baseline_corpus():
    corpus = PatentPriorArtEngine.synthesize_baseline_corpus(
        technology_domain="sparse_attention_transformers",
        cpc_classification="G06N 3/08",
        count=3,
    )
    assert len(corpus) == 3
    for p in corpus:
        assert p["patent_number"].startswith(("US-", "EP-", "WO-"))
        assert len(p["claims"]) >= 1
        assert p["assignee"] != ""
