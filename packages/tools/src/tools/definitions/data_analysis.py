"""Deterministic computational tools for tabular data analysis and mathematical verification."""

import ast
import math
import operator
import statistics
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from tools.base import Permission, Tool, ToolParameter, ToolSchema
from shared.logging import get_logger

logger = get_logger(__name__)


# Supported operators for safe AST evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_MATH_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
    "mean": statistics.mean,
    "median": statistics.median,
    "stdev": statistics.stdev,
    "variance": statistics.variance,
}


def safe_eval_ast(node: ast.AST) -> Any:
    """Recursively evaluate an AST expression safely without arbitrary code execution."""
    if isinstance(node, ast.Expression):
        return safe_eval_ast(node.body)
    elif isinstance(node, ast.Constant):  # Python 3.8+ numbers/strings/booleans
        return node.value
    elif isinstance(node, ast.Num):  # Fallback for older AST
        return node.n
    elif isinstance(node, ast.BinOp):
        left = safe_eval_ast(node.left)
        right = safe_eval_ast(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval_ast(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in SAFE_MATH_FUNCTIONS:
                args = [safe_eval_ast(arg) for arg in node.args]
                return SAFE_MATH_FUNCTIONS[func_name](*args)
            raise ValueError(f"Math function '{func_name}' is not allowed in safe sandbox")
        raise ValueError("Dynamic or nested function calls are forbidden")
    elif isinstance(node, ast.List):
        return [safe_eval_ast(elem) for elem in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(safe_eval_ast(elem) for elem in node.elts)
    raise ValueError(f"Unsupported AST expression node type: {type(node).__name__}")


class DeterministicMathTool(Tool):
    """Safely evaluates mathematical and statistical formulas using AST parsing."""

    schema = ToolSchema(
        name="deterministic_math",
        description=(
            "Calculates exact mathematical and statistical formulas with 100% precision. "
            "Prevents LLM arithmetic hallucinations by executing calculations deterministically in Python."
        ),
        parameters=[
            ToolParameter(
                name="expression",
                type="string",
                description="Mathematical expression or function call (e.g. 'sqrt(144) + 25 * 4', 'mean([10, 20, 30, 40, 50])', 'stdev([12.5, 14.2, 19.8])')",
                required=True,
            ),
        ],
        returns="dict with expression, result, type, and formatted_result",
        permissions=[Permission.CODE_EXECUTION],
    )

    async def execute(self, expression: str, **kwargs: Any) -> Dict[str, Any]:
        expr_str = expression.strip()
        try:
            parsed = ast.parse(expr_str, mode="eval")
            result = safe_eval_ast(parsed)
            formatted = f"{result:.6f}".rstrip("0").rstrip(".") if isinstance(result, float) else str(result)
            return {
                "success": True,
                "expression": expr_str,
                "result": result,
                "formatted_result": formatted,
                "type": type(result).__name__,
            }
        except Exception as e:
            logger.warning("Deterministic math evaluation failed", expression=expr_str, error=str(e))
            return {
                "success": False,
                "expression": expr_str,
                "error": str(e),
            }


class DataAnalysisTool(Tool):
    """Performs deterministic statistical profiling, aggregations, correlation, and regression on tabular data."""

    schema = ToolSchema(
        name="data_analysis",
        description=(
            "Executes deterministic statistical and quantitative operations on tabular data: "
            "descriptive statistics, grouped aggregations, Pearson correlations, linear regression, and filtering."
        ),
        parameters=[
            ToolParameter(
                name="operation",
                type="string",
                description="Analysis operation to execute: 'describe', 'aggregate', 'correlation', 'linear_regression', 'filter'",
                required=True,
                enum=["describe", "aggregate", "correlation", "linear_regression", "filter"],
            ),
            ToolParameter(
                name="data",
                type="array",
                description="List of row dictionaries (e.g. [{'x': 1, 'y': 10}, {'x': 2, 'y': 20}]) or a list of numbers",
                required=True,
            ),
            ToolParameter(
                name="column",
                type="string",
                description="Target column name for univariate operations (describe, filter)",
                required=False,
            ),
            ToolParameter(
                name="column_y",
                type="string",
                description="Second column name for bivariate operations (correlation, linear_regression)",
                required=False,
            ),
            ToolParameter(
                name="groupby_column",
                type="string",
                description="Column to group by for aggregation",
                required=False,
            ),
            ToolParameter(
                name="agg_function",
                type="string",
                description="Aggregation function: 'sum', 'mean', 'min', 'max', 'count', 'median'",
                required=False,
                enum=["sum", "mean", "min", "max", "count", "median"],
                default="mean",
            ),
            ToolParameter(
                name="filter_condition",
                type="string",
                description="Filter expression e.g. '> 50', '== Sales', '<= 100.5'",
                required=False,
            ),
        ],
        returns="dict with structured numerical results, metrics, and markdown table",
        permissions=[Permission.CODE_EXECUTION],
    )

    async def execute(
        self,
        operation: str,
        data: List[Any],
        column: Optional[str] = None,
        column_y: Optional[str] = None,
        groupby_column: Optional[str] = None,
        agg_function: str = "mean",
        filter_condition: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if not data:
            return {"success": False, "error": "No data records provided"}

        try:
            if operation == "describe":
                return self._describe(data, column)
            elif operation == "aggregate":
                return self._aggregate(data, groupby_column, column, agg_function)
            elif operation == "correlation":
                return self._correlation(data, column, column_y)
            elif operation == "linear_regression":
                return self._linear_regression(data, column, column_y)
            elif operation == "filter":
                return self._filter(data, column, filter_condition)
            else:
                return {"success": False, "error": f"Unsupported operation: {operation}"}
        except Exception as e:
            logger.warning("Data analysis tool execution failed", operation=operation, error=str(e))
            return {"success": False, "operation": operation, "error": str(e)}

    def _extract_numeric_series(self, data: List[Any], col: Optional[str]) -> List[float]:
        """Extract a clean float list from rows or raw array."""
        values: List[float] = []
        for item in data:
            val = item.get(col) if isinstance(item, dict) and col else item
            if val is not None and str(val).strip() != "":
                try:
                    f = float(str(val).replace(",", "").strip())
                    if not math.isnan(f) and not math.isinf(f):
                        values.append(f)
                except (ValueError, TypeError):
                    continue
        return values

    def _describe(self, data: List[Any], column: Optional[str]) -> Dict[str, Any]:
        """Compute univariate descriptive statistics."""
        values = self._extract_numeric_series(data, column)
        if not values:
            return {"success": False, "error": f"No valid numeric data found in column '{column}'"}

        n = len(values)
        s_min = min(values)
        s_max = max(values)
        s_mean = statistics.mean(values)
        s_median = statistics.median(values)
        s_stdev = statistics.stdev(values) if n > 1 else 0.0
        s_variance = statistics.variance(values) if n > 1 else 0.0
        s_sum = sum(values)

        # Quantiles
        sorted_vals = sorted(values)
        q25 = sorted_vals[int(n * 0.25)]
        q50 = s_median
        q75 = sorted_vals[min(int(n * 0.75), n - 1)]
        iqr = q75 - q25

        summary_md = (
            f"**Descriptive Statistics for `{column or 'series'}` (N={n})**\n"
            f"- **Mean**: {s_mean:.4f} | **Std Dev**: {s_stdev:.4f}\n"
            f"- **Median**: {s_median:.4f} | **IQR**: {iqr:.4f}\n"
            f"- **Min**: {s_min:.4f} | **Max**: {s_max:.4f}\n"
            f"- **Q1 (25%)**: {q25:.4f} | **Q3 (75%)**: {q75:.4f} | **Sum**: {s_sum:.4f}"
        )

        return {
            "success": True,
            "operation": "describe",
            "column": column,
            "count": n,
            "mean": s_mean,
            "median": s_median,
            "std_dev": s_stdev,
            "variance": s_variance,
            "min": s_min,
            "max": s_max,
            "sum": s_sum,
            "q25": q25,
            "q50": q50,
            "q75": q75,
            "iqr": iqr,
            "summary_markdown": summary_md,
        }

    def _aggregate(
        self,
        data: List[Any],
        groupby_col: Optional[str],
        target_col: Optional[str],
        agg_func: str,
    ) -> Dict[str, Any]:
        """Compute grouped aggregations."""
        if not groupby_col or not target_col:
            return {"success": False, "error": "Both groupby_column and column must be specified"}

        groups: Dict[str, List[float]] = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            g_key = str(item.get(groupby_col, "Unknown"))
            t_val = item.get(target_col)
            if t_val is not None:
                try:
                    f = float(str(t_val).replace(",", "").strip())
                    groups.setdefault(g_key, []).append(f)
                except (ValueError, TypeError):
                    continue

        results: Dict[str, float] = {}
        for g_name, vals in groups.items():
            if not vals:
                continue
            if agg_func == "sum":
                results[g_name] = sum(vals)
            elif agg_func == "min":
                results[g_name] = min(vals)
            elif agg_func == "max":
                results[g_name] = max(vals)
            elif agg_func == "count":
                results[g_name] = float(len(vals))
            elif agg_func == "median":
                results[g_name] = statistics.median(vals)
            else:  # default mean
                results[g_name] = statistics.mean(vals)

        # Build Markdown Table
        table_lines = [
            f"| `{groupby_col}` | `{target_col}` ({agg_func}) | Count |",
            "|---|---|---|",
        ]
        for k, v in sorted(results.items(), key=lambda x: -x[1]):
            table_lines.append(f"| {k} | {v:.4f} | {len(groups[k])} |")

        return {
            "success": True,
            "operation": "aggregate",
            "groupby_column": groupby_col,
            "target_column": target_col,
            "agg_function": agg_func,
            "results": results,
            "summary_markdown": "\n".join(table_lines),
        }

    def _correlation(self, data: List[Any], col_x: Optional[str], col_y: Optional[str]) -> Dict[str, Any]:
        """Compute Pearson correlation coefficient between two numeric columns."""
        if not col_x or not col_y:
            return {"success": False, "error": "Both column and column_y are required for correlation"}

        paired: List[Tuple[float, float]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            vx, vy = item.get(col_x), item.get(col_y)
            if vx is not None and vy is not None:
                try:
                    fx = float(str(vx).replace(",", "").strip())
                    fy = float(str(vy).replace(",", "").strip())
                    if not (math.isnan(fx) or math.isnan(fy) or math.isinf(fx) or math.isinf(fy)):
                        paired.append((fx, fy))
                except (ValueError, TypeError):
                    continue

        if len(paired) < 2:
            return {"success": False, "error": "Need at least 2 valid paired records for correlation"}

        n = len(paired)
        xs = [p[0] for p in paired]
        ys = [p[1] for p in paired]

        mean_x = statistics.mean(xs)
        mean_y = statistics.mean(ys)

        numerator = sum((x - mean_x) * (y - mean_y) for x, y in paired)
        denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
        denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))

        if denom_x == 0 or denom_y == 0:
            r = 0.0
        else:
            r = numerator / (denom_x * denom_y)

        r = max(-1.0, min(1.0, r))

        strength = "very strong" if abs(r) >= 0.8 else "moderate" if abs(r) >= 0.5 else "weak" if abs(r) >= 0.2 else "negligible"
        direction = "positive" if r > 0 else "negative" if r < 0 else "none"

        return {
            "success": True,
            "operation": "correlation",
            "column_x": col_x,
            "column_y": col_y,
            "n_pairs": n,
            "pearson_r": r,
            "r_squared": r ** 2,
            "relationship": f"{strength} {direction} correlation",
            "summary_markdown": f"**Correlation between `{col_x}` and `{col_y}`**: $r = {r:.4f}$ ($R^2 = {r**2:.4f}$, {strength} {direction} correlation, N={n})",
        }

    def _linear_regression(self, data: List[Any], col_x: Optional[str], col_y: Optional[str]) -> Dict[str, Any]:
        """Compute ordinary least squares linear regression."""
        if not col_x or not col_y:
            return {"success": False, "error": "Both column and column_y are required for linear regression"}

        paired: List[Tuple[float, float]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            vx, vy = item.get(col_x), item.get(col_y)
            if vx is not None and vy is not None:
                try:
                    fx = float(str(vx).replace(",", "").strip())
                    fy = float(str(vy).replace(",", "").strip())
                    paired.append((fx, fy))
                except (ValueError, TypeError):
                    continue

        if len(paired) < 2:
            return {"success": False, "error": "Need at least 2 valid paired data points for regression"}

        n = len(paired)
        xs = [p[0] for p in paired]
        ys = [p[1] for p in paired]

        mean_x = statistics.mean(xs)
        mean_y = statistics.mean(ys)

        var_x = sum((x - mean_x) ** 2 for x in xs)
        if var_x == 0:
            return {"success": False, "error": "Variance of independent variable X is zero"}

        cov_xy = sum((x - mean_x) * (y - mean_y) for x, y in paired)
        slope = cov_xy / var_x
        intercept = mean_y - slope * mean_x

        # R-squared
        y_pred = [slope * x + intercept for x in xs]
        ss_tot = sum((y - mean_y) ** 2 for y in ys)
        ss_res = sum((y - y_p) ** 2 for y, y_p in zip(ys, y_pred))
        r_sq = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

        eq = f"y = {slope:.4f}x + {intercept:.4f}" if intercept >= 0 else f"y = {slope:.4f}x - {abs(intercept):.4f}"

        return {
            "success": True,
            "operation": "linear_regression",
            "independent_var": col_x,
            "dependent_var": col_y,
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_sq,
            "equation": eq,
            "summary_markdown": f"**Linear Regression (`{col_y}` on `{col_x}`)**: `{eq}` ($R^2 = {r_sq:.4f}$, N={n})",
        }

    def _filter(self, data: List[Any], column: Optional[str], condition_str: Optional[str]) -> Dict[str, Any]:
        """Filter dataset rows by logical condition."""
        if not column or not condition_str:
            return {"success": False, "error": "Both column and filter_condition are required"}

        cond = condition_str.strip()
        matched: List[Any] = []

        # Parse operator and target
        op = "=="
        target_raw = cond
        for op_sym in [">=", "<=", "!=", ">", "<", "=="]:
            if cond.startswith(op_sym):
                op = op_sym
                target_raw = cond[len(op_sym):].strip()
                break

        # Check if numeric target
        target_num = None
        try:
            target_num = float(target_raw)
        except ValueError:
            target_num = None

        for item in data:
            if not isinstance(item, dict):
                continue
            val = item.get(column)
            if val is None:
                continue

            match = False
            if target_num is not None:
                try:
                    val_num = float(str(val).replace(",", "").strip())
                    if op == ">":
                        match = val_num > target_num
                    elif op == ">=":
                        match = val_num >= target_num
                    elif op == "<":
                        match = val_num < target_num
                    elif op == "<=":
                        match = val_num <= target_num
                    elif op == "==":
                        match = val_num == target_num
                    elif op == "!=":
                        match = val_num != target_num
                except (ValueError, TypeError):
                    match = False
            else:
                str_val = str(val).lower()
                target_str = target_raw.lower()
                if op == "==":
                    match = str_val == target_str
                elif op == "!=":
                    match = str_val != target_str

            if match:
                matched.append(item)

        return {
            "success": True,
            "operation": "filter",
            "column": column,
            "condition": condition_str,
            "total_records": len(data),
            "matched_count": len(matched),
            "matched_percentage": (len(matched) / len(data)) * 100 if data else 0,
            "sample_matches": matched[:5],
            "summary_markdown": f"Filtered by `{column} {condition_str}`: Matched **{len(matched)}** / {len(data)} rows ({(len(matched)/len(data)*100):.1f}%)",
        }
