"""Comprehensive automated tests for Unified Research CLI (scripts/research_cli.py)."""

import os
import sys
import subprocess
import pytest

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cli_path = os.path.join(root_dir, "scripts", "research_cli.py")


def test_cli_help():
    """Verify CLI --help runs cleanly."""
    result = subprocess.run([sys.executable, cli_path, "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Agentic Multimodal Research Platform CLI" in result.stdout
    assert "health" in result.stdout
    assert "version" in result.stdout
    assert "factcheck" in result.stdout
    assert "synthesize" in result.stdout


def test_cli_version():
    """Verify CLI version subcommand outputs release information."""
    result = subprocess.run([sys.executable, cli_path, "version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "AI RESEARCH OS" in result.stdout
    assert "125 Completed Active Phases" in result.stdout


def test_cli_health():
    """Verify CLI health subcommand executes."""
    result = subprocess.run([sys.executable, cli_path, "health"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "HEALTH CHECK" in result.stdout


def test_cli_factcheck():
    """Verify CLI factcheck subcommand executes without failure."""
    result = subprocess.run(
        [
            sys.executable,
            cli_path,
            "factcheck",
            "Targeting oncogenic KRAS G12D",
            "--doi",
            "10.1016/sample.doi",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "FACT-CHECK VERDICT" in result.stdout


def test_cli_synthesize():
    """Verify CLI synthesize subcommand executes without failure."""
    result = subprocess.run(
        [
            sys.executable,
            cli_path,
            "synthesize",
            "De-Novo Kinase Inhibitor Discovery",
            "--domain",
            "Chemical Biology",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "SYNTHESIS CAMPAIGN" in result.stdout
    assert "Autonomous State: COMPLETED" in result.stdout
