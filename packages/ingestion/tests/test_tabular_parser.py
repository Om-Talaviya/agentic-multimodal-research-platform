"""Tests for TabularParser in packages/ingestion."""

import json
import pytest
from ingestion.parsers.tabular import TabularParser
from ingestion.parsers.base import DatasetProfile, ColumnProfile


@pytest.fixture
def tabular_parser() -> TabularParser:
    return TabularParser()


@pytest.mark.asyncio
async def test_tabular_parser_csv_success(tabular_parser: TabularParser):
    csv_content = (
        "Name,Age,Salary,Department\n"
        "Alice,30,75000,Engineering\n"
        "Bob,25,50000,Marketing\n"
        "Charlie,35,90000,Engineering\n"
        "Diana,28,62000,Design\n"
    ).encode("utf-8")

    doc = await tabular_parser.parse(csv_content, filename="employees.csv")

    assert doc.title == "employees.csv"
    assert doc.metadata["row_count"] == 4
    assert doc.metadata["column_count"] == 4
    assert doc.metadata["format"] == "csv"

    profile: DatasetProfile = doc.dataset_profile
    assert profile is not None
    assert profile.row_count == 4
    assert profile.column_count == 4
    assert len(profile.columns) == 4

    # Check Age column statistics
    age_col = next(c for c in profile.columns if c.name == "Age")
    assert age_col.data_type == "numeric"
    assert age_col.min_val == 25
    assert age_col.max_val == 35
    assert age_col.mean == 29.5
    assert age_col.median == 29.0
    assert age_col.null_count == 0

    # Check Department unique values
    dept_col = next(c for c in profile.columns if c.name == "Department")
    assert dept_col.data_type == "string"
    assert "Engineering" in dept_col.unique_values
    assert dept_col.unique_count == 3

    # Check markdown table generation
    assert "| Name | Age | Salary | Department |" in doc.text
    assert "### Dataset Profile Summary" in doc.text


@pytest.mark.asyncio
async def test_tabular_parser_tsv_success(tabular_parser: TabularParser):
    tsv_content = (
        "Year\tRevenue\tProfit\n"
        "2020\t100.5\t20.1\n"
        "2021\t150.0\t35.5\n"
        "2022\t200.2\t50.0\n"
    ).encode("utf-8")

    doc = await tabular_parser.parse(tsv_content, filename="financials.tsv")

    assert doc.metadata["row_count"] == 3
    assert doc.metadata["column_count"] == 3
    assert doc.metadata["delimiter"] == "\t"

    rev_col = next(c for c in doc.dataset_profile.columns if c.name == "Revenue")
    assert rev_col.data_type == "numeric"
    assert rev_col.min_val == 100.5
    assert rev_col.max_val == 200.2


@pytest.mark.asyncio
async def test_tabular_parser_json_records(tabular_parser: TabularParser):
    records = [
        {"product": "Laptop", "price": 1200, "in_stock": True},
        {"product": "Mouse", "price": 25, "in_stock": True},
        {"product": "Monitor", "price": 300, "in_stock": False},
    ]
    json_bytes = json.dumps(records).encode("utf-8")

    doc = await tabular_parser.parse(json_bytes, filename="inventory.json")

    assert doc.metadata["row_count"] == 3
    assert doc.metadata["column_count"] == 3
    assert doc.dataset_profile.columns[0].name == "product"

    price_col = next(c for c in doc.dataset_profile.columns if c.name == "price")
    assert price_col.mean == pytest.approx(508.333, rel=1e-2)
