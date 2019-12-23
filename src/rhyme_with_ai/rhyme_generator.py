import logging
from typing import List

import numpy as np
import tensorflow as tf
from transformers.modeling_tf_bert import TFBertForPreTraining
from transformers.tokenization_bert import PreTrainedTokenizer

from rhyme_with_ai.utils import pairwise
from rhyme_with_ai.token_weighter import TokenWeighter


class RhymeGenerator:
    def __init__(
        self,
        model: TFBertForPreTraining,
        tokenizer: PreTrainedTokenizer,
        token_weighter: TokenWeighter = None,
    ):
        """Generate rhymes.

        Parameters
        ----------
        model : Model for masked language modelling
        tokenizer : Tokenizer for model
        token_weighter : Class that weighs tokens
        """

        self.model = model
        self.tokenizer = tokenizer
        if token_weighter is None:
            token_weighter = TokenWeighter(tokenizer)
        self.token_weighter = token_weighter
        self._logger = logging.getLogger(__name__)

        self.tokenized_rhymes_ = None
        self.position_probas_ = None

        # Easy access.
        self.comma_token_id = self.tokenizer.encode(",", add_special_tokens=False)[0]
        self.period_token_id = self.tokenizer.encode(".", add_special_tokens=False)[0]
        self.mask_token_id = self.tokenizer.mask_token_id

    def start(self, query: str, rhyme_words: List[str]) -> None:
        """Start the sentence generator.

        Parameters
        ----------
        query : Seed sentence
        rhyme_words : Rhyme words for next sentence
        """
        # TODO: What if no content?
        self._logger.info("Got sentence %s", query)
        tokenized_rhymes = [
            self._initialize_rhymes(query, rhyme_word) for rhyme_word in rhyme_words
        ]
        # Make same length.
        self.tokenized_rhymes_ = tf.keras.preprocessing.sequence.pad_sequences(
            tokenized_rhymes, padding="post", value=self.tokenizer.pad_token_id
        )
        p = self.tokenized_rhymes_ == self.tokenizer.mask_token_id
        self.position_probas_ = p / p.sum(1).reshape(-1, 1)

    def _initialize_rhymes(self, query: str, rhyme_word: str) -> List[int]:
        """Initialize the rhymes.

        * Tokenize input
        * Append a comma if the sentence does not end in it (might add better predictions as it
            shows the two sentence parts are related)
        * Make second line as long as the original
        * Add a period

        Parameters
        ----------
        query : First line
        rhyme_word : Last word for second line

        Returns
        -------
        Tokenized rhyme lines
        """

        query_token_ids = self.tokenizer.encode(query, add_special_tokens=False)
        rhyme_word_token_ids = self.tokenizer.encode(
            rhyme_word, add_special_tokens=False
        )

        if query_token_ids[-1] != self.comma_token_id:
            query_token_ids.append(self.comma_token_id)

        magic_correction = len(rhyme_word_token_ids) + 1  # 1 for comma
        return (
            query_token_ids
            + [self.tokenizer.mask_token_id] * (len(query_token_ids) - magic_correction)
            + rhyme_word_token_ids
            + [self.period_token_id]
        )

    def mutate(self):
        """Mutate the current rhymes.

        Returns
        -------
        Mutated rhymes
        """
        self.tokenized_rhymes_ = self._mutate(
            self.tokenized_rhymes_, self.position_probas_, self.token_weighter.proba
        )

        rhymes = []
        for i in range(len(self.tokenized_rhymes_)):
            rhymes.append(
                self.tokenizer.convert_tokens_to_string(
                    self.tokenizer.convert_ids_to_tokens(
                        self.tokenized_rhymes_[i], skip_special_tokens=True
                    )
                )
            )
        self._logger.info(rhymes)
        return rhymes

    def _mutate(
        self,
        tokenized_rhymes: np.ndarray,
        position_probas: np.ndarray,
        token_id_probas: np.ndarray,
    ) -> np.ndarray:

        replacements = []
        for i in range(tokenized_rhymes.shape[0]):
            mask_idx, masked_token_ids = self._mask_token(
                tokenized_rhymes[i], position_probas[i]
            )
            tokenized_rhymes[i] = masked_token_ids
            replacements.append(mask_idx)

        predictions = self._predict_masked_tokens(tokenized_rhymes)

        for i, token_ids in enumerate(tokenized_rhymes):
            replace_ix = replacements[i]
            token_ids[replace_ix] = self._draw_replacement(
                predictions[i], token_id_probas, replace_ix
            )
            tokenized_rhymes[i] = token_ids

        return tokenized_rhymes

    def _mask_token(self, token_ids, position_probas):
        """Mask line and return index to update."""
        token_ids = self._mask_repeats(token_ids, position_probas)
        ix = self._locate_mask(token_ids, position_probas)
        token_ids[ix] = self.mask_token_id
        return ix, token_ids

    def _locate_mask(self, token_ids, position_probas):
        """Update masks or a random token."""
        if self.mask_token_id in token_ids:
            # Already masks present, just return the last.
            # We used to return thee first but this returns worse predictions.
            return np.where(token_ids == self.tokenizer.mask_token_id)[0][-1]
        return np.random.choice(range(len(position_probas)), p=position_probas)

    def _mask_repeats(self, token_ids, position_probas):
        """Repeated tokens are generally of less quality."""
        repeats = [
            ii for ii, ids in enumerate(pairwise(token_ids[:-2])) if ids[0] == ids[1]
        ]
        for ii in repeats:
            if position_probas[ii] > 0:
                token_ids[ii] = self.mask_token_id
            if position_probas[ii + 1] > 0:
                token_ids[ii + 1] = self.mask_token_id
        return token_ids

    def _predict_masked_tokens(self, tokenized_rhymes):
        return self.model(tf.constant(tokenized_rhymes))[0]

    def _draw_replacement(self, predictions, token_probas, replace_ix):
        """Get probability, weigh and draw."""
        # TODO (HG): Can't we softmax when calling the model?
        probas = tf.nn.softmax(predictions[replace_ix]).numpy() * token_probas
        probas /= probas.sum()
        return np.random.choice(range(len(probas)), p=probas)
