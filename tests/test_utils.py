import pytest
from rhyme_with_ai.utils import color_new_words, find_last_word, pairwise, sanitize


@pytest.mark.parametrize(
    "new,old,expected",
    [
        (
            "word up",
            "word down",
            'word <span style="background-color: #eefa66">up</span> ',
        ),
        (
            "word up dog",
            "word down dog",
            'word <span style="background-color: #eefa66">up</span> dog',
        ),
        (
            "word up ye dog",
            "word up dog",
            'word up <span style="background-color: #eefa66">ye</span> dog',
        ),
    ],
)
def test_color_new_words(new, old, expected):
    assert color_new_words(new, old) == expected


@pytest.mark.parametrize(
    "s,expected_last", [("word up", "up"), ("word up!", "up"), ("gg!", "gg")]
)
def test_find_last_word(s, expected_last):
    assert find_last_word(s) == expected_last


def test_pairwise():
    assert list(pairwise([0, 1, 2])) == [(0, 1), (1, 2)]


@pytest.mark.parametrize(
    "s,expected",
    [("hai!!!!!", "hai"), ("hello", "hello"), ("??!!&&wha$$dup**", "whadup")],
)
def test_sanitize(s, expected):
    assert sanitize(s) == expected
