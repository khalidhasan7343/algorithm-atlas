import numpy as np
import pytest
pytestmark=[pytest.mark.ml]


def toy(b13,**kwargs):
    return b13.load('named-entity-recognition').NERTagger(**kwargs).fit([['John','visits','Paris'],['Mary','visits','Rome'],['New','York','shines']], [['B-PER','O','B-LOC'],['B-PER','O','B-LOC'],['B-LOC','I-LOC','O']])


@pytest.mark.oracle
@pytest.mark.parametrize('labels,expected',[([],[]),(['O','O'],[]),(['B-PER'],[('PER',0,1)]),(['B-PER','I-PER'],[('PER',0,2)]),(['B-PER','B-PER'],[('PER',0,1),('PER',1,2)]),(['B-PER','I-PER','O','B-LOC','I-LOC'],[('PER',0,2),('LOC',3,5)]),(['B-X','I-X','B-Y'],[('X',0,2),('Y',2,3)])])
def test_ner_bio_span_hand_oracle(b13,labels,expected):
    assert b13.load('named-entity-recognition').extract_spans(labels)==expected


@pytest.mark.parametrize('labels',[['I-PER'],['O','I-PER'],['B-PER','I-LOC'],['B-'],['X-PER'],['B-!'],[1],['B-_']])
def test_ner_invalid_bio(b13,labels):
    with pytest.raises(ValueError):b13.load('named-entity-recognition').extract_spans(labels)


@pytest.mark.oracle
def test_ner_metrics_exact_spans_differ_from_token_accuracy(b13):
    mod=b13.load('named-entity-recognition')
    info=mod.span_metrics([['B-PER','I-PER','O','B-LOC']],[['B-PER','O','O','B-LOC']])
    assert info==dict(true_positive=1,predicted=2,gold=2,precision=.5,recall=.5,f1=.5,token_accuracy=.75)
    # Identical offsets in a different sentence cannot match an entity.
    info=mod.span_metrics([['B-PER'],['O']],[['O'],['B-PER']]);assert info['true_positive']==0 and info['f1']==0
    info=mod.span_metrics([['O']],[['O']]);assert info['precision']==info['recall']==info['f1']==0 and info['token_accuracy']==1
    assert mod.span_metrics([],[])['token_accuracy'] is None


@pytest.mark.oracle
def test_ner_canonical_crf_reuse_legal_masks_and_feature_hand_oracle(b13):
    m=toy(b13);mod=b13.load('conditional-random-fields')
    assert isinstance(m.model_,mod.LinearChainCRF)
    assert m.labels_==('O','B-LOC','I-LOC','B-PER','I-PER')
    assert not m.model_.allowed_start_[2] and not m.model_.allowed_transitions_[0,2] and m.model_.allowed_transitions_[1,2]
    matrix=m.features(['John']);active={m.feature_names_[i] for i in np.flatnonzero(matrix[0])}
    assert active=={'bias','word=john','suffix=hn','initial_upper'}
    assert 'word=visits' in m.feature_names_ and not any('B-PER' in f for f in m.feature_names_)


def test_ner_tiny_training_unknown_words_no_gold_leak_reproducibility(b13):
    a,b=toy(b13),toy(b13)
    words=['John','visits','Paris'];assert a.predict(words)==['B-PER','O','B-LOC']
    assert a.model_.loss_history_[-1]<a.model_.loss_history_[0]
    assert a.predict(words)==b.predict(words)
    for n in a.model_.parameters_:np.testing.assert_array_equal(a.model_.parameters_[n],b.model_.parameters_[n])
    old=a.feature_names_;predicted=a.predict(['Unseen','visits','Berlin'])
    assert a.feature_names_==old and 'word=unseen' not in old
    b13.load('named-entity-recognition').extract_spans(predicted)
    before=a.predict(words);a.evaluate([words],[['O']*3]);assert a.predict(words)==before
    assert a.evaluate([words],[['B-PER','O','B-LOC']])['f1']==1


def test_ner_empty_unicode_sentence_boundaries_and_raw_tokenization(b13):
    m=toy(b13)
    assert m.predict([])==[] and m.features([]).shape==(0,len(m.feature_names_))
    assert m.predict_text('John visits Paris')['spans']==[('PER',0,1),('LOC',2,3)]
    assert m.predict_text('')['labels']==[]
    one=b13.load('named-entity-recognition').NERTagger(max_iter=5).fit([['Café']],[['B-LOC']])
    assert len(one.predict(['Cafe\u0301']))==1
    no=b13.load('named-entity-recognition').NERTagger().fit([['nothing','special']],[['O','O']]);assert no.predict(['unknown'])==['O']
    matrix=m.features(['John']);matrix[:]=99;assert m.features(['John']).max()==1


@pytest.mark.parametrize('kwargs',[{'max_iter':0},{'max_iter':True},{'learning_rate':0},{'l2':-1},{'l2':float('nan')}])
def test_ner_invalid_hyperparameters(b13,kwargs):
    with pytest.raises(ValueError):b13.load('named-entity-recognition').NERTagger(**kwargs)


@pytest.mark.parametrize('sentences,labels',[([],[]),([[]],[[]]),([['a']],[[]]),([['a']],[['I-X']]),([['a b']],[['O']]),([['a']],[['B-']]),([['a']]*4,[[f'B-{t}'] for t in 'ABCD'])])
def test_ner_invalid_training_atomic(b13,sentences,labels):
    m=toy(b13,max_iter=2);old=m.feature_names_
    with pytest.raises(ValueError):m.fit(sentences,labels)
    assert m.feature_names_==old


@pytest.mark.parametrize('words',[None,'hello',['a b'],[1],['a']*65,['a'*129]])
def test_ner_invalid_queries(b13,words):
    with pytest.raises(ValueError):toy(b13,max_iter=1).predict(words)


def test_ner_unfitted_metrics_validation_and_feature_budget(b13):
    mod=b13.load('named-entity-recognition')
    with pytest.raises(ValueError):mod.NERTagger().predict([])
    with pytest.raises(ValueError):mod.span_metrics([['O']],[[]])
    with pytest.raises(ValueError):mod.span_metrics([['I-X']],[['O']])
    unique=[[f'a{i}z{i}' for i in range(64)],[f'b{i}y{i}' for i in range(64)]]
    with pytest.raises(ValueError):mod.NERTagger().fit(unique,[['O']*64]*2)
