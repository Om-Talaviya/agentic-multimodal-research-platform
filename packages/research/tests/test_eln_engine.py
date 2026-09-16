"""Unit tests for ElectronicLabNotebookEngine (Phase 53)."""
import pytest
from research.eln.eln_engine import ElectronicLabNotebookEngine


def test_eln_engine_block_validation():
    engine = ElectronicLabNotebookEngine()

    # 1. Protocol Block
    proto = engine.validate_block_content(
        block_type="PROTOCOL_STEP",
        content={"step_number": 1, "title": "PCR Amplification", "parameters": {"cycles": 35}}
    )
    assert proto["step_number"] == 1
    assert proto["parameters"]["cycles"] == 35

    # 2. SMILES Block
    smiles_block = engine.validate_block_content(
        block_type="MOLECULAR_SMILES",
        content={"smiles": "CC(=O)Oc1ccccc1C(=O)O"}
    )
    assert smiles_block["smiles"] == "CC(=O)Oc1ccccc1C(=O)O"

    # Invalid SMILES character error
    with pytest.raises(ValueError):
        engine.validate_block_content(
            block_type="MOLECULAR_SMILES",
            content={"smiles": "INVALID_$$$_SMILES"}
        )

    # 3. Audit Trail Chain Verification
    valid_entries = [
        {"cryptographic_hash": "a" * 64, "diff_payload": {}},
        {"cryptographic_hash": "b" * 64, "diff_payload": {}},
    ]
    assert engine.verify_audit_trail_chain(valid_entries) is True

    invalid_entries = [
        {"cryptographic_hash": "tampered_short_hash", "diff_payload": {}}
    ]
    assert engine.verify_audit_trail_chain(invalid_entries) is False
