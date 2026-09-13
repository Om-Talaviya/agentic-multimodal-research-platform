"""Tests for DataAnalysisTool and DeterministicMathTool in packages/tools."""

import pytest
from tools.definitions.data_analysis import DataAnalysisTool, DeterministicMathTool


@pytest.fixture
def data_tool() -> DataAnalysisTool:
    return DataAnalysisTool()


@pytest.fixture
def math_tool() -> DeterministicMathTool:
    return DeterministicMathTool()


@pytest.mark.asyncio
async def test_data_analysis_describe(data_tool: DataAnalysisTool):
    sample_data = [
        {"x": 10, "y": 100, "cat": "A"},
        {"x": 20, "y": 200, "cat": "B"},
        {"x": 30, "y": 300, "cat": "A"},
        {"x": 40, "y": 400, "cat": "C"},
        {"x": 50, "y": 500, "cat": "B"},
    ]

    res = await data_tool.execute(operation="describe", data=sample_data)
    assert res.success is True
    assert res.data["row_count"] == 5
    assert "x" in res.data["statistics"]
    assert res.data["statistics"]["x"]["mean"] == 30.0
    assert res.data["statistics"]["x"]["min"] == 10
    assert res.data["statistics"]["x"]["max"] == 50
    assert res.data["statistics"]["cat"]["type"] == "categorical"
    assert res.data["statistics"]["cat"]["unique_count"] == 3


@pytest.mark.asyncio
async def test_data_analysis_aggregate(data_tool: DataAnalysisTool):
    sample_data = [
        {"dept": "Sales", "revenue": 100},
        {"dept": "Sales", "revenue": 200},
        {"dept": "Engineering", "revenue": 300},
        {"dept": "Engineering", "revenue": 400},
    ]

    res = await data_tool.execute(
        operation="aggregate",
        data=sample_data,
        columns=["revenue"],
        group_by="dept",
        agg_func="sum"
    )
    assert res.success is True
    assert res.data["Sales"]["revenue"] == 300
    assert res.data["Engineering"]["revenue"] == 700


@pytest.mark.asyncio
async def test_data_analysis_correlation_and_regression(data_tool: DataAnalysisTool):
    sample_data = [
        {"ad_spend": 10, "sales": 25},
        {"ad_spend": 20, "sales": 45},
        {"ad_spend": 30, "sales": 65},
        {"ad_spend": 40, "sales": 85},
        {"ad_spend": 50, "sales": 105},
    ]

    # Correlation
    corr_res = await data_tool.execute(
        operation="correlation",
        data=sample_data,
        col_x="ad_spend",
        col_y="sales"
    )
    assert corr_res.success is True
    assert corr_res.data["pearson_r"] == pytest.approx(1.0, rel=1e-3)

    # Linear Regression
    reg_res = await data_tool.execute(
        operation="linear_regression",
        data=sample_data,
        col_x="ad_spend",
        col_y="sales"
    )
    assert reg_res.success is True
    assert reg_res.data["slope"] == pytest.approx(2.0, rel=1e-3)
    assert reg_res.data["intercept"] == pytest.approx(5.0, rel=1e-3)
    assert reg_res.data["r_squared"] == pytest.approx(1.0, rel=1e-3)


@pytest.mark.asyncio
async def test_deterministic_math_eval(math_tool: DeterministicMathTool):
    res = await math_tool.execute(expression="(1250 * 1.08) - (450 / 3) + 2**4")
    assert res.success is True
    expected = (1250 * 1.08) - (450 / 3) + 2**4
    assert res.data["result"] == pytest.approx(expected)

    # Safe math function call
    res_func = await math_tool.execute(expression="sqrt(144) + log10(1000) * sin(0)")
    assert res_func.success is True
    assert res_func.data["result"] == 12.0

    # Test safety against disallowed builtins
    res_unsafe = await math_tool.execute(expression="__import__('os').system('ls')")
    assert res_unsafe.success is False
    assert "Disallowed AST node or function" in res_unsafe.error
