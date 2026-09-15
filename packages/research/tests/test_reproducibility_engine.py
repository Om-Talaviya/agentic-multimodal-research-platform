"""Unit tests for ReproducibilityEngine AST safety and in-silico simulation."""

import pytest
from research.reproducibility.engine import ReproducibilityEngine


def test_ast_safety_validation():
    """Verify that safe scientific code passes and malicious code is blocked."""
    safe_code = """
import math
import statistics

data = [1.0, 2.0, 3.0, 4.0, 5.0]
mean_val = statistics.mean(data)
std_val = statistics.stdev(data)
metrics = {"mean": mean_val, "std": std_val}
"""
    valid, err = ReproducibilityEngine.validate_code_ast(safe_code)
    assert valid is True
    assert err is None

    malicious_code_1 = "import os; os.system('echo hacked')"
    valid_m1, err_m1 = ReproducibilityEngine.validate_code_ast(malicious_code_1)
    assert valid_m1 is False
    assert "Forbidden module 'os'" in err_m1

    malicious_code_2 = "eval('1 + 1')"
    valid_m2, err_m2 = ReproducibilityEngine.validate_code_ast(malicious_code_2)
    assert valid_m2 is False
    assert "Forbidden function 'eval'" in err_m2


def test_in_silico_execution():
    """Verify execution in sandbox and output extraction."""
    code = """
import math
x = 5.0
y = 12.0
hypot = math.sqrt(x**2 + y**2)
metrics = {"hypotenuse": hypot, "perimeter": x + y + hypot}
print("Calculated triangle properties successfully.")
"""
    result = ReproducibilityEngine.execute_protocol(code)
    assert result["status"] == "succeeded"
    assert result["execution_time_ms"] >= 0
    assert result["reproduced_metrics"]["hypotenuse"] == 13.0
    assert result["reproduced_metrics"]["perimeter"] == 30.0
    assert "Calculated triangle properties" in result["runtime_logs"]


def test_claim_verification():
    """Verify tolerance comparisons and discrepancy verdict categorization."""
    claimed = {
        "accuracy": 0.950,
        "latency_ms": 12.0,
        "divergent_metric": 100.0,
    }
    reproduced = {
        "accuracy": 0.948,       # delta = 0.2% -> reproduced
        "latency_ms": 14.0,       # delta = 16.6% -> discrepant
        "divergent_metric": 20.0, # delta = 80.0% -> refuted
    }

    verification = ReproducibilityEngine.verify_claims(claimed, reproduced, default_tolerance=0.05)
    traces = {t["metric_name"]: t for t in verification["traces"]}

    assert traces["accuracy"]["verdict"] == "reproduced"
    assert traces["latency_ms"]["verdict"] == "discrepant"
    assert traces["divergent_metric"]["verdict"] == "refuted"
    assert verification["reproducibility_score"] > 0.0
    assert verification["overall_status"] == "discrepant"
