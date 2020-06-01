import copy

import streamlit as st
from rhyme_with_ai.rhyme import query_rhyme_words
from rhyme_with_ai.rhyme_generator import RhymeGenerator
from rhyme_with_ai.utils import color_new_words, sanitize
from transformers import BertTokenizer, TFBertForMaskedLM

DEFAULT_QUERY = "Machines will take over the world soon"
N_RHYMES = 10
ITER_FACTOR = 5


LANGUAGE = st.sidebar.radio("Language",["english","dutch"],0)
if LANGUAGE == "english":
    MODEL_PATH = "./data/bert-large-cased-whole-word-masking-finetuned-squad"
elif LANGUAGE == "dutch":
    MODEL_PATH = "./data/wietsedv/bert-base-dutch-cased"
else:
    raise NotImplementedError(f"Unsupported language ({LANGUAGE}) expected 'english' or 'dutch'.")

def main():
    st.markdown(
        "<sup>Created with "
        "[Datamuse](https://www.datamuse.com/api/), "
        "[Mick's rijmwoordenboek](https://rijmwoordenboek.nl)"
        "[Hugging Face](https://huggingface.co/), "
        "[Streamlit](https://streamlit.io/) and "
        "[App Engine](https://cloud.google.com/appengine/)."
        " Read our [blog](https://blog.godatadriven.com/rhyme-with-ai) "
        "or check the "
        "[source](https://github.com/godatadriven/rhyme-with-ai).</sup>",
        unsafe_allow_html=True,
    )
    st.title("Rhyme with AI")
    query = get_query()
    if not query:
        query = DEFAULT_QUERY
    rhyme_words_options = query_rhyme_words(query, n_rhymes=N_RHYMES,language=LANGUAGE)
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
        previous_sentences = copy.deepcopy(current_sentences)
        current_sentences = sentence_generator.mutate()
        display_output(status_text, query, current_sentences, previous_sentences)
        progress_bar.progress(i / (max_iter - 1))
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
