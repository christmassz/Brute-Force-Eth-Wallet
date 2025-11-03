"""Combination generator for Trial 3.

Given:
- scrambled_words: list with 9 items; exactly one item is the empty string "".
- replacement_pool: list of 30 candidate words.

For each candidate replacement word, insert it into the blank slot, then
yield all permutations of the resulting 9-word list **excluding** the blank.

This is memory-efficient: permutations are streamed, not stored.
"""
from typing import Iterator, List
import itertools

BLANK_TOKEN = ""

def generate_trial3_word_sets(scrambled_words: List[str], replacement_pool: List[str]) -> Iterator[List[str]]:
    """Yield permutations for Trial 3.

    Args:
        scrambled_words: List[str] – 9 items; one item is "" marking the wrong index.
        replacement_pool: List[str] – 30 candidate words.

    Yields:
        List[str]: A permutation (length 9) ready for position 1-9 of mnemonic.
    """
    if len(scrambled_words) != 9:
        raise ValueError("scrambled_words must have length 9")
    if BLANK_TOKEN not in scrambled_words:
        raise ValueError('scrambled_words must contain exactly one blank ""')
    blank_count = scrambled_words.count(BLANK_TOKEN)
    if blank_count != 1:
        raise ValueError("scrambled_words must contain exactly one blank token")

    base_words = [w for w in scrambled_words if w != BLANK_TOKEN]
    if len(base_words) != 8:
        raise ValueError("Expected 8 known scrambled words after removing blank")

    for candidate in replacement_pool:
        candidate = candidate.lower().strip()
        words_9 = base_words + [candidate]
        for perm in itertools.permutations(words_9):
            yield list(perm)
