"""Keep both categories' mathematical and pointer relationships in CI."""
from scripts.verify_number_window_oracles import verify


def test_number_theory_relationships():
    assert verify('number-theory')['status']=='passed'


def test_pointer_window_relationships():
    assert verify('two-pointers-sliding-window')['status']=='passed'
