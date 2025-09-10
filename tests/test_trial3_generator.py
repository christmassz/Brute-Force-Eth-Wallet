import pytest
from src.trial3_generator import generate_trial3_word_sets, BLANK_TOKEN
import itertools
import math


def test_invalid_length():
    scrambled = ["a", "b", "c", "d", "e", "f", "g", "h"]  # only 8
    pool = ["x"] * 30
    with pytest.raises(ValueError):
        list(generate_trial3_word_sets(scrambled, pool))


def test_missing_blank():
    scrambled = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    pool = ["x"] * 30
    with pytest.raises(ValueError):
        list(generate_trial3_word_sets(scrambled, pool))


def test_generator_yields_correct_length():
    scrambled = ["w1", BLANK_TOKEN, "w2", "w3", "w4", "w5", "w6", "w7", "w8"]
    pool = ["rep1", "rep2"]  # small pool for test
    gen = generate_trial3_word_sets(scrambled, pool)
    first_perm = next(gen)
    assert len(first_perm) == 9
    # verify all original eight words present and one replacement word appears
    assert set(first_perm).issuperset({"w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8"})


def test_generator_total_count_small_case():
    # Use 2 replacement words and scramble of 9 (1 blank, 8 fixed) => 9! * 2 outputs.
    scrambled = ["w1", BLANK_TOKEN, "w2", "w3", "w4", "w5", "w6", "w7", "w8"]
    pool = ["rep1", "rep2"]
    expected = math.factorial(9) * len(pool)
    total = sum(1 for _ in generate_trial3_word_sets(scrambled, pool))
    assert total == expected
