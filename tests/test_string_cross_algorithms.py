"""Keep the semantic Phase 9 comparison matrix in the discovered CI suite."""
from scripts.verify_string_cross_algorithms import verify


def test_string_algorithms_share_exact_byte_semantics():
    result = verify()
    assert result["status"] == "passed"
    assert len(result["comparisons"]) == 9
    assert set(result["comparisons"].values()) == {120}
