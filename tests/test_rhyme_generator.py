import pytest
from rhyme_with_ai.rhyme_generator import RhymeGenerator
from transformers import TFBertForMaskedLM, BertTokenizer


@pytest.fixture
def sentence_generator():
    model_path = "./data/bert-large-cased-whole-word-masking"
    model = TFBertForMaskedLM.from_pretrained(model_path)
    tokenizer = BertTokenizer.from_pretrained(model_path)
    return RhymeGenerator(model, tokenizer)


@pytest.mark.parametrize(
    "query,rhyme_word", [("I like cheese", "peace"), ("I like cheese, ", "peace")]
)
def test_preprocess(sentence_generator, query, rhyme_word):
    # GIVEN
    i_like_cheese_tokens = [178, 1176, 9553]
    peace_token = 3519
    comma_token = 117
    period_token = 119
    mask_token = 103

    # WHEN
    actual = sentence_generator._initialize_rhymes(query, rhyme_word)

    # THEN
    expected = (
        i_like_cheese_tokens
        + [comma_token]
        + [mask_token] * (len(i_like_cheese_tokens) - 1)
        + [peace_token]
        + [period_token]
    )
    assert actual == expected
