import functools
import random
from typing import List, Optional

import requests
from gazpacho import Soup, get

from rhyme_with_ai.utils import find_last_word


def query_rhyme_words(sentence: str, n_rhymes: int, language:str="english") -> List[str]:
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
    if language == "english":
       return query_datamuse_api(last_word, n_rhymes)
    elif language == "dutch":
        return mick_rijmwoordenboek(last_word, n_rhymes)
    else:
        raise NotImplementedError(f"Unsupported language ({language}) expected 'english' or 'dutch'.")


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


@functools.lru_cache(maxsize=128, typed=False)
def mick_rijmwoordenboek(word: str, n_words: int):
    url = f"https://rijmwoordenboek.nl/rijm/{word}"
    html = get(url)
    soup = Soup(html)

    results = soup.find("div", {"id": "rhymeResultsWords"}).html.split("<br />")

    # clean up
    results = [r.replace("\n", "").replace(" ", "") for r in results]

    # filter html and empty strings
    results = [r for r in results if ("<" not in r) and (len(r) > 0)]

    return random.sample(results, min(len(results), n_words))
