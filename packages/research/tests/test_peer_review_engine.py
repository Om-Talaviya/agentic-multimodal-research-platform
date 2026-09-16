"""
Tests for Phase 64: Peer Review Engine.
"""
from research.peer_review.peer_review_engine import ScientificPeerReviewEngine


def test_evaluate_manuscript():
    res = ScientificPeerReviewEngine.evaluate_manuscript(
        title="Test Title",
        abstract="Test Abstract",
    )
    assert "reviews" in res
    assert "overall_score" in res
    assert len(res["reviews"]) == 3
    assert res["overall_score"] > 0
