import numpy as np


class TokenWeighter:
    def __init__(self, tokenizer):
        self.tokenizer_ = tokenizer
        self.proba = self.get_token_proba()

    def get_token_proba(self):
        valid_token_mask = self._filter_short_partial(self.tokenizer_.vocab)
        return valid_token_mask

    def _filter_short_partial(self, vocab):
        valid_token_ids = [v for k, v in vocab.items() if len(k) > 1 and "#" not in k]
        is_valid = np.zeros(len(vocab.keys()))
        is_valid[valid_token_ids] = 1
        return is_valid
