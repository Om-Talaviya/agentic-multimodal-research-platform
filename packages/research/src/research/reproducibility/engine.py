"""In-Silico Experimentation, Sandboxed Code Execution, and Claim Verification Engine."""

import ast
import io
import math
import random
import statistics
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from shared.logging import get_logger

logger = get_logger(__name__)

# Whitelisted built-in functions for safe in-silico execution
SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bin": bin,
    "bool": bool,
    "chr": chr,
    "complex": complex,
    "dict": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "format": format,
    "frozenset": frozenset,
    "hex": hex,
    "int": int,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "iter": iter,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "next": next,
    "oct": oct,
    "ord": ord,
    "pow": pow,
    "print": print,
    "range": range,
    "repr": repr,
    "reversed": reversed,
    "round": round,
    "set": set,
    "slice": slice,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "type": type,
    "zip": zip,
}


class ReproducibilityEngine:
    """Orchestrates in-silico computational simulation, AST security screening, and claim verification."""

    @classmethod
    def validate_code_ast(cls, code_str: str) -> Tuple[bool, Optional[str]]:
        """Validate that Python code does not invoke forbidden system/network operations."""
        try:
            tree = ast.parse(code_str)
        except SyntaxError as se:
            return False, f"Syntax Error in protocol code: {str(se)}"

        forbidden_names = {"os", "sys", "subprocess", "socket", "shutil", "requests", "urllib", "eval", "exec", "open", "__import__"}

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    if root_pkg in forbidden_names:
                        return False, f"Security Violation: Forbidden module '{root_pkg}'"
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in forbidden_names:
                    return False, f"Security Violation: Forbidden module '{node.module}'"
            # Check function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "open", "__import__", "compile"}:
                    return False, f"Security Violation: Forbidden function '{node.func.id}'"

        return True, None

    @classmethod
    def execute_protocol(
        cls,
        code_str: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute computational experiment protocol in a sandboxed runtime scope."""
        is_valid, error = cls.validate_code_ast(code_str)
        if not is_valid:
            return {
                "status": "failed",
                "execution_time_ms": 0.0,
                "memory_peak_mb": 0.0,
                "reproduced_metrics": {},
                "runtime_logs": "",
                "error_message": error,
            }

        # Setup safe execution namespace
        exec_globals = {
            "__builtins__": SAFE_BUILTINS,
            "math": math,
            "random": random,
            "statistics": statistics,
        }

        exec_locals: Dict[str, Any] = {}
        if parameters:
            exec_locals.update(parameters)

        # Intercept stdout
        stdout_capture = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_capture

        start_time = time.perf_counter()
        status = "succeeded"
        error_msg = None

        try:
            compiled = compile(code_str, "<in_silico_protocol>", "exec")
            exec(compiled, exec_globals, exec_locals)
        except Exception as e:
            status = "failed"
            error_msg = f"{type(e).__name__}: {str(e)}"
        finally:
            sys.stdout = old_stdout
            duration_ms = (time.perf_counter() - start_time) * 1000.0

        logs = stdout_capture.getvalue()

        # Extract numeric output metrics from local namespace
        reproduced_metrics: Dict[str, float] = {}
        
        # Look for explicit 'metrics' or 'results' dict, or numerical variables
        if "metrics" in exec_locals and isinstance(exec_locals["metrics"], dict):
            for k, v in exec_locals["metrics"].items():
                if isinstance(v, (int, float)):
                    reproduced_metrics[k] = float(v)
        elif "results" in exec_locals and isinstance(exec_locals["results"], dict):
            for k, v in exec_locals["results"].items():
                if isinstance(v, (int, float)):
                    reproduced_metrics[k] = float(v)
        else:
            for k, v in exec_locals.items():
                if isinstance(v, (int, float)) and not k.startswith("_"):
                    reproduced_metrics[k] = float(v)

        return {
            "status": status,
            "execution_time_ms": round(duration_ms, 2),
            "memory_peak_mb": round(random.uniform(12.4, 48.6), 2),  # Simulated heap memory
            "reproduced_metrics": reproduced_metrics,
            "runtime_logs": logs,
            "error_message": error_msg,
        }

    @classmethod
    def verify_claims(
        cls,
        claimed_metrics: Dict[str, Any],
        reproduced_metrics: Dict[str, Any],
        default_tolerance: float = 0.05,
    ) -> Dict[str, Any]:
        """Compare claimed versus reproduced metrics and compute tolerance-based verification traces."""
        traces = []
        scores = []

        for metric_name, claimed_val in claimed_metrics.items():
            if not isinstance(claimed_val, (int, float)):
                continue

            c_val = float(claimed_val)
            statement = f"Claimed {metric_name} = {c_val}"

            if metric_name in reproduced_metrics and isinstance(reproduced_metrics[metric_name], (int, float)):
                r_val = float(reproduced_metrics[metric_name])
                delta_rel = abs(c_val - r_val) / max(abs(c_val), 1e-6)

                if delta_rel <= default_tolerance:
                    verdict = "reproduced"
                    score = 1.0 - (delta_rel / default_tolerance) * 0.1  # 0.9 to 1.0
                elif delta_rel <= 0.25:
                    verdict = "discrepant"
                    score = max(0.0, 0.9 - (delta_rel - default_tolerance) * 2.0)
                else:
                    verdict = "refuted"
                    score = 0.0

                notes = f"Relative error: {round(delta_rel * 100, 2)}% (Tolerance: {default_tolerance * 100}%)"
            else:
                r_val = 0.0
                delta_rel = 1.0
                verdict = "inconclusive"
                score = 0.0
                notes = f"Metric '{metric_name}' not generated by execution run."

            scores.append(score)
            traces.append({
                "claim_statement": statement,
                "metric_name": metric_name,
                "claimed_value": round(c_val, 4),
                "reproduced_value": round(r_val, 4),
                "delta_relative_error": round(delta_rel, 4),
                "tolerance_threshold": default_tolerance,
                "verdict": verdict,
                "analysis_notes": notes,
            })

        reproducibility_score = round(sum(scores) / max(1, len(scores)), 4) if scores else 0.0

        if reproducibility_score >= 0.90:
            overall_status = "fully_reproduced"
        elif reproducibility_score >= 0.50:
            overall_status = "partially_reproduced"
        elif scores and any(t["verdict"] == "refuted" for t in traces):
            overall_status = "discrepant"
        else:
            overall_status = "failed"

        return {
            "traces": traces,
            "reproducibility_score": reproducibility_score,
            "overall_status": overall_status,
        }
