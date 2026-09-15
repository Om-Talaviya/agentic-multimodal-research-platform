import pytest
from research.datasets.synthesizer import InstructionDatasetSynthesizer


def test_calculate_quality_metrics():
    metrics = InstructionDatasetSynthesizer.calculate_quality_metrics(
        instruction="Derive the asymptotic convergence bound for linear transformer attention.",
        response="### Proof\n\nLinear attention replaces quadratic softmax with kernel product decomposition:\n$$\\mathcal{O}(N D^2)$$\n\nThis guarantees strictly linear compute scaling in sequence length $N$.",
    )
    assert metrics["quality_score"] >= 0.85
    assert metrics["toxicity_score"] <= 0.05
    assert metrics["hallucination_risk"] <= 0.10
    assert len(metrics["dedup_hash"]) == 64


def test_evolve_instruction_strategies():
    inst = "Implement flash attention."
    resp = "Flash attention uses SRAM tiling to optimize memory I/O."

    # Test in_depth_expansion
    evolved_depth = InstructionDatasetSynthesizer.evolve_instruction(inst, resp, "in_depth_expansion")
    assert "Specifically, provide a formal mathematical derivation" in evolved_depth["instruction"]
    assert evolved_depth["cot_reasoning_trace"] is not None

    # Test constraint_hardening
    evolved_hard = InstructionDatasetSynthesizer.evolve_instruction(inst, resp, "constraint_hardening")
    assert "zero third-party dependencies" in evolved_hard["instruction"]

    # Test adversarial_redteaming
    evolved_adv = InstructionDatasetSynthesizer.evolve_instruction(inst, resp, "adversarial_redteaming")
    assert "security vulnerability" in evolved_adv["instruction"]


def test_synthesize_from_research_findings_alpaca():
    findings = [
        {"claim": "Kernel caching reduces latency by 45%", "detail": "Empirical tests on H100 GPU cluster."},
        {"claim": "Quantization retains 99.8% precision", "detail": "Evaluated on MMLU-Pro benchmark."},
    ]
    samples = InstructionDatasetSynthesizer.synthesize_from_research_findings(
        title="Inference Optimization",
        topic="Low-Latency LLM Serving",
        findings=findings,
        dataset_format="alpaca_sft",
        sample_count=4,
    )
    assert len(samples) == 4
    for s in samples:
        assert s["quality_score"] > 0.80
        assert s["curation_verdict"] == "accepted"
        assert s["instruction"] != ""
        assert s["chosen_response"] != ""


def test_synthesize_dpo_preference_pairs():
    findings = [
        {"claim": "Reciprocal rank fusion outperforms single dense retrieval", "detail": "MRR@10 improved by 14.2%."},
    ]
    samples = InstructionDatasetSynthesizer.synthesize_from_research_findings(
        title="Hybrid Retrieval",
        topic="Dense-Sparse RAG",
        findings=findings,
        dataset_format="dpo_preference",
        sample_count=2,
    )
    assert len(samples) == 2
    for s in samples:
        assert s["rejected_response"] is not None
        assert len(s["rejected_response"]) > 0


def test_format_dataset_all_formats():
    raw_samples = [
        {
            "instruction": "Explain quantum entanglement.",
            "input_context": "Physics 101",
            "chosen_response": "Quantum entanglement is a physical phenomenon...",
            "rejected_response": "It's spooky action at a distance.",
            "cot_reasoning_trace": "Step 1: Define state superposition.\nStep 2: Tensor product state.",
            "system_prompt": "You are a physicist.",
        }
    ]

    # 1. Alpaca
    alpaca = InstructionDatasetSynthesizer.format_dataset(raw_samples, "alpaca_sft")
    assert "instruction" in alpaca[0]
    assert "input" in alpaca[0]
    assert "output" in alpaca[0]

    # 2. ShareGPT
    sharegpt = InstructionDatasetSynthesizer.format_dataset(raw_samples, "sharegpt")
    assert "conversations" in sharegpt[0]
    assert len(sharegpt[0]["conversations"]) >= 2

    # 3. DPO
    dpo = InstructionDatasetSynthesizer.format_dataset(raw_samples, "dpo_preference")
    assert "prompt" in dpo[0]
    assert "chosen" in dpo[0]
    assert "rejected" in dpo[0]

    # 4. CoT
    cot = InstructionDatasetSynthesizer.format_dataset(raw_samples, "cot_reasoning")
    assert "thought" in cot[0]
    assert "solution" in cot[0]
