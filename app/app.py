import copy

import streamlit as st
from rhyme_with_ai.rhyme import query_rhyme_words
from rhyme_with_ai.rhyme_generator import RhymeGenerator
from rhyme_with_ai.utils import color_new_words, sanitize
from transformers import BertTokenizer, TFBertForMaskedLM

DEFAULT_QUERY = "Machines will take over the world soon"
N_RHYMES = 10
ITER_FACTOR = 5
MODEL_PATH = "./data/bert-large-cased-whole-word-masking"


def main():
    st.title("Rhyme with AI")
    query = get_query()
    if not query:
        query = DEFAULT_QUERY
    rhyme_words_options = query_rhyme_words(query)
    if rhyme_words_options:
        start_rhyming(query, rhyme_words_options)
    else:
        st.write("No rhyme words found")


def get_query():
    q = sanitize(
        st.text_input("Write your first line and press ENTER to rhyme:", DEFAULT_QUERY)
    )
    if not q:
        return DEFAULT_QUERY
    return q


def start_rhyming(query, rhyme_words_options):
    st.markdown("## My Suggestions:")

    progress_bar = st.progress(0)
    status_text = st.empty()
    max_iter = len(query.split()) * ITER_FACTOR

    rhyme_words = rhyme_words_options[:N_RHYMES]

    model, tokenizer = load_model(MODEL_PATH)
    sentence_generator = RhymeGenerator(model, tokenizer)
    sentence_generator.start(query, rhyme_words)

    current_sentences = [" " for _ in range(N_RHYMES)]
    for i in range(max_iter):
        progress_bar.progress(i / (max_iter + 1))
        previous_sentences = copy.deepcopy(current_sentences)
        current_sentences = sentence_generator.mutate()
        display_output(status_text, query, current_sentences, previous_sentences)
    st.balloons()


@st.cache(allow_output_mutation=True)
def load_model(model_path):
    return (
        TFBertForMaskedLM.from_pretrained(model_path),
        BertTokenizer.from_pretrained(model_path),
    )


def display_output(status_text, query, current_sentences, previous_sentences):
    print_sentences = []
    for new, old in zip(current_sentences, previous_sentences):
        formatted = color_new_words(new, old)
        after_comma = "<li>" + formatted.split(",")[1][:-2] + "</li>"
        print_sentences.append(after_comma)
    status_text.markdown(
        query + ",<br>" + "".join(print_sentences), unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
