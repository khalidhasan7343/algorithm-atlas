import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b13_support', Path(__file__).resolve().parents[2] / 'support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)

import unicodedata

hmm = s.module('atlas_b11_hmm_for_b13', s.ROOT.parent / 'time-series/hidden-markov-models/python/solution.py')


def sentence(tokens, *, empty=True):
    if not isinstance(tokens, (list, tuple)) or len(tokens) > 64 or (not empty and not tokens):
        raise ValueError('a list of at most64 tokens required; training sentences nonempty')
    result = []
    for token in tokens:
        if not isinstance(token, str) or not token or len(token) > 128:
            raise ValueError('nonempty bounded token strings required')
        token = unicodedata.normalize('NFC', token)
        if s.tokenize(token, lowercase=False) != [token]:
            raise ValueError('each token must be one shared-tokenizer token')
        result.append(token)
    return result


class HMMPOSTagger:
    """Supervised add-alpha POS tables; unchanged B11 owns HMM inference."""
    def __init__(self, *, alpha=1., min_count=1, max_size=16, lowercase=True):
        self.alpha = s.scalar(alpha, 'alpha', 1e-8, 100.)
        self.min_count = s.integer(min_count, 'min_count', 1, 2048)
        self.max_size = s.integer(max_size, 'max_size', 1, 16)
        self.lowercase = s.boolean(lowercase, 'lowercase')

    def fit(self, sentences, tags):
        if not isinstance(sentences, (list, tuple)) or not 1 <= len(sentences) <= 32:
            raise ValueError('fit requires1..32 independent sentences')
        data = [sentence(x, empty=False) for x in sentences]
        if sum(map(len, data)) > 1024:
            raise ValueError('at most1024 training tokens')
        if not isinstance(tags, (list, tuple)) or len(tags) != len(data):
            raise ValueError('one tag sequence per sentence required')
        for words, labels in zip(data, tags):
            if not isinstance(labels, (list, tuple)) or len(labels) != len(words) or any(not isinstance(t, str) or not t or len(t) > 32 for t in labels):
                raise ValueError('bounded nonempty string tags aligned with tokens required')
        names = tuple(sorted({tag for labels in tags for tag in labels}))
        if len(names) > 8:
            raise ValueError('B11 HMM supports at most8 tags')
        index = {tag: i for i, tag in enumerate(names)}
        vocabulary = s.Vocabulary(min_count=self.min_count, max_size=self.max_size, lowercase=self.lowercase).fit_tokens(data)
        k, v = len(names), len(vocabulary)
        initial = np.zeros(k, dtype=np.int64)
        transition = np.zeros((k, k), dtype=np.int64)
        emission = np.zeros((k, v), dtype=np.int64)
        for words, labels in zip(data, tags):
            states = [index[t] for t in labels]
            symbols = vocabulary.encode_tokens(words)
            initial[states[0]] += 1
            for pos, state in enumerate(states):
                emission[state, symbols[pos]] += 1
                if pos:
                    transition[states[pos-1], state] += 1
        smooth = lambda a: (a + self.alpha) / (a.sum(axis=-1, keepdims=True) + self.alpha * a.shape[-1])
        model = hmm.CategoricalHMM(k, v, initial=smooth(initial), transition=smooth(transition), emission=smooth(emission))
        self.vocabulary_, self.tags_, self.tag_index_, self.model_ = vocabulary, names, index, model
        self.initial_counts_, self.transition_counts_, self.emission_counts_ = initial, transition, emission
        self.status_ = 'supervised-estimated'
        return self

    def _observations(self, tokens):
        s.ready(self)
        return self.vocabulary_.encode_tokens(sentence(tokens))

    def decode(self, tokens):
        observations = self._observations(tokens)
        if not len(observations):
            return [], 0.
        path, score = self.model_.decode(observations)
        return [self.tags_[i] for i in path], score

    def tag(self, tokens):
        return self.decode(tokens)[0]

    def tag_text(self, text):
        return self.tag(s.tokenize(text, lowercase=False))

    def score(self, tokens):
        observations = self._observations(tokens)
        return self.model_.score(observations) if len(observations) else 0.

    def posterior(self, tokens):
        observations = self._observations(tokens)
        if not len(observations):
            return np.empty((0, len(self.tags_)))
        return self.model_.infer(observations)['gamma']

    def evaluate(self, sentences, gold):
        s.ready(self, 'model_')
        if not isinstance(sentences, (list, tuple)) or not isinstance(gold, (list, tuple)) or len(sentences) != len(gold) or len(sentences) > 32:
            raise ValueError('aligned bounded sentence and tag lists required')
        correct, total = 0, 0
        for words, labels in zip(sentences, gold):
            predicted = self.tag(words)
            if not isinstance(labels, (list, tuple)) or len(labels) != len(predicted) or any(not isinstance(t, str) or t not in self.tag_index_ for t in labels):
                raise ValueError('known gold tags aligned with tokens required')
            correct += sum(a == b for a, b in zip(predicted, labels))
            total += len(predicted)
        return dict(correct=correct, tokens=total, accuracy=correct/total if total else None)
