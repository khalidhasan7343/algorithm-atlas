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


def tokens(sequence, *, empty=True):
    if not isinstance(sequence, (list, tuple)) or len(sequence) > 64 or (not empty and not sequence):
        raise ValueError('bounded token list required; training sentences nonempty')
    result = []
    for word in sequence:
        if not isinstance(word, str) or not word or len(word) > 128:
            raise ValueError('nonempty token strings required')
        word = unicodedata.normalize('NFC', word)
        if s.tokenize(word, lowercase=False) != [word]:
            raise ValueError('tokens must follow the shared tokenizer boundary convention')
        result.append(word)
    return result


def extract_spans(labels):
    """Strict BIO/IOB2 -> (entity_type,start,end), half-open token offsets."""
    if not isinstance(labels, (list, tuple)) or len(labels) > 64:
        raise ValueError('bounded BIO label list required')
    spans, active, start = [], None, 0
    for i, label in enumerate([*labels, 'O']):
        if not isinstance(label, str) or (label != 'O' and (len(label) < 3 or label[:2] not in ('B-', 'I-') or not label[2:].isascii() or not label[2:].replace('_', '').isalnum() or len(label) > 24)):
            raise ValueError('labels must be O,B-TYPE or I-TYPE with bounded ASCII type')
        prefix, kind = ('O', None) if label == 'O' else (label[0], label[2:])
        if prefix == 'I' and active != kind:
            raise ValueError('I-TYPE requires preceding B/I of same type')
        if prefix != 'I':
            if active is not None:
                spans.append((active, start, i))
            active = kind if prefix == 'B' else None
            start = i
    return spans


def span_metrics(gold, predicted):
    if not isinstance(gold, (list, tuple)) or not isinstance(predicted, (list, tuple)) or len(gold) != len(predicted) or len(gold) > 32:
        raise ValueError('aligned lists of at most32 BIO sentences required')
    actual, guesses, correct_tokens, total = set(), set(), 0, 0
    for sid, (a, b) in enumerate(zip(gold, predicted)):
        if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)) or len(a) != len(b):
            raise ValueError('aligned BIO labels required')
        actual.update((sid, *span) for span in extract_spans(a))
        guesses.update((sid, *span) for span in extract_spans(b))
        correct_tokens += sum(x == y for x, y in zip(a, b))
        total += len(a)
    true_positive = len(actual & guesses)
    precision = true_positive/len(guesses) if guesses else 0.
    recall = true_positive/len(actual) if actual else 0.
    return dict(true_positive=true_positive, predicted=len(guesses), gold=len(actual), precision=precision, recall=recall,
                f1=2*precision*recall/(precision+recall) if precision+recall else 0., token_accuracy=correct_tokens/total if total else None)


def _features(word):
    lower = word.casefold()
    result = {'bias', 'word='+lower, 'suffix='+lower[-2:]}
    if word[0].isupper(): result.add('initial_upper')
    if word.isupper(): result.add('all_upper')
    if word.isdigit(): result.add('digit')
    return result


class NERTagger:
    """Explicit BIO feature-CRF baseline, not a universal NER algorithm."""
    def __init__(self, *, max_iter=100, learning_rate=.5, l2=.01):
        self.max_iter = s.integer(max_iter, 'max_iter', 1, 200)
        self.learning_rate = s.scalar(learning_rate, 'learning_rate', 1e-8, 1.)
        self.l2 = s.scalar(l2, 'l2', 0., 10.)

    def fit(self, sentences, labels):
        if not isinstance(sentences, (list, tuple)) or not 1 <= len(sentences) <= 32 or not isinstance(labels, (list, tuple)) or len(labels) != len(sentences):
            raise ValueError('aligned lists of1..32 token/BIO sentences required')
        data = [tokens(words, empty=False) for words in sentences]
        if sum(map(len, data)) > 1024:
            raise ValueError('at most1024 training tokens')
        entity_types = set()
        for words, path in zip(data, labels):
            if not isinstance(path, (list, tuple)) or len(path) != len(words):
                raise ValueError('one BIO label per token required')
            entity_types.update(kind for kind, _, _ in extract_spans(path))
        if len(entity_types) > 3:
            raise ValueError('at most3 entity types (7 BIO labels) supported')
        names = ('O', *(label for kind in sorted(entity_types) for label in ('B-'+kind, 'I-'+kind)))
        features = tuple(sorted({name for words in data for word in words for name in _features(word)}))
        if len(features) > 128:
            raise ValueError('feature vocabulary exceeds128 training-only columns')
        index = {name: i for i, name in enumerate(features)}
        matrices = [self._matrix(words, index) for words in data]
        allowed = np.ones((len(names), len(names)), dtype=bool)
        starts = np.array([not label.startswith('I-') for label in names])
        for i, before in enumerate(names):
            for j, after in enumerate(names):
                if after.startswith('I-'):
                    allowed[i, j] = before in ('B-'+after[2:], after)
        model = s.load('conditional-random-fields').LinearChainCRF(names, len(features), max_iter=self.max_iter, learning_rate=self.learning_rate, l2=self.l2, allowed_transitions=allowed, allowed_start=starts)
        model.fit(matrices, labels)
        self.feature_names_, self.feature_index_, self.model_, self.labels_ = features, index, model, names
        self.status_ = model.status_
        return self

    @staticmethod
    def _matrix(words, index):
        out = np.zeros((len(words), len(index)))
        for row, word in enumerate(words):
            for name in _features(word):
                if name in index:
                    out[row, index[name]] = 1.
        return out

    def features(self, words):
        s.ready(self, 'model_')
        return self._matrix(tokens(words), self.feature_index_)

    def predict(self, words):
        s.ready(self, 'model_')
        words = tokens(words)
        return self.model_.predict(self._matrix(words, self.feature_index_)) if words else []

    def predict_text(self, text):
        words = s.tokenize(text, lowercase=False)
        labels = self.predict(words)
        return dict(tokens=words, labels=labels, spans=extract_spans(labels))

    def evaluate(self, sentences, gold):
        s.ready(self, 'model_')
        if not isinstance(sentences, (list, tuple)) or len(sentences) > 32:
            raise ValueError('bounded sentence list required')
        return span_metrics(gold, [self.predict(words) for words in sentences])
