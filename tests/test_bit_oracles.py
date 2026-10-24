"""Keep exact-width and cross-canonical comparisons in the discovered CI suite."""
from scripts.verify_bit_oracles import verify


def test_bit_algorithms_match_independent_and_existing_references():
    result=verify()
    assert result["status"]=="passed"
    assert result["all_32_differing_bits"]=="passed"
    assert len(result["comparisons"])==5
