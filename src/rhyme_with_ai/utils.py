import itertools
import string


def color_new_words(new: str, old: str, color: str = "#eefa66") -> str:
    """Color new words in strings with a span."""

    def find_diff(new_, old_):
        return [ii for ii, (n, o) in enumerate(zip(new_, old_)) if n != o]

    new_words = new.split()
    old_words = old.split()
    forward = find_diff(new_words, old_words)
    backward = find_diff(new_words[::-1], old_words[::-1])

    if not forward or not backward:
        # No difference
        return new

    start, end = forward[0], len(new_words) - backward[0]
    return (
        " ".join(new_words[:start])
        + " "
        + f'<span style="background-color: {color}">'
        + " ".join(new_words[start:end])
        + "</span>"
        + " "
        + " ".join(new_words[end:])
    )


def find_last_word(s):
    """Find the last word in a string."""
    # Note: will break on \n, \r, etc.
    alpha_only_sentence = "".join([c for c in s if (c.isalpha() or (c == " "))]).strip()
    return alpha_only_sentence.split()[-1]


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    # https://stackoverflow.com/questions/5434891/iterate-a-list-as-pair-current-next-in-python
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def sanitize(s):
    """Remove punctuation from a string."""
    return s.translate(str.maketrans("", "", string.punctuation))
