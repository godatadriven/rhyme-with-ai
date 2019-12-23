from typing import List, Optional

import requests
from rhyme_with_ai.utils import find_last_word


def query_rhyme_words(sentence: str, n_rhymes: Optional[int] = None) -> List[str]:
    """Returns a list of rhyme words for a sentence.

    Parameters
    ----------
    sentence : Sentence that may end with punctuation
    n_rhymes : Maximum number of rhymes to return

    Returns
    -------
        List[str] -- List of words that rhyme with the final word
    """
    last_word = find_last_word(sentence)
    return query_datamuse_api(last_word, n_rhymes)


def query_datamuse_api(word: str, n_rhymes: Optional[int] = None) -> List[str]:
    """Query the DataMuse API.

    Parameters
    ----------
    word : Word to rhyme with
    n_rhymes : Max rhymes to return

    Returns
    -------
    Rhyme words
    """
    out = requests.get(
        "https://api.datamuse.com/words", params={"rel_rhy": word}
    ).json()
    words = [_["word"] for _ in out]
    if n_rhymes is None:
        return words
    return words[:n_rhymes]
