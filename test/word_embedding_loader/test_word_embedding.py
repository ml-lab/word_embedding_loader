# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import StringIO
from collections import OrderedDict

import pytest
import numpy as np
from numpy.testing import assert_array_equal

from word_embedding_loader import word_embedding
from word_embedding_loader import loader


def test__get_two_lines():
    f = StringIO.StringIO(u"""2 3
</s> 0.080054 0.088388 -0.07660
the -1.420859 1.156857 0.744776""")
    l0, l1 = word_embedding._get_two_lines(f)
    assert l0 == u"2 3\n"
    assert l1 == u"</s> 0.080054 0.088388 -0.07660\n"


class TestClassifyFormat:
    def test__classify_format_glove(self, glove_file):
        assert word_embedding._classify_format(glove_file) == word_embedding._glove

    def test__classify_format_word2vec_bin(self, word2vec_bin_file):
        assert word_embedding._classify_format(word2vec_bin_file) == word_embedding._word2vec_bin

    def test__classify_format_word2vec_text(self, word2vec_text_file):
        assert word_embedding._classify_format(word2vec_text_file) == word_embedding._word2vec_text


def test_WordEmbedding___init__():
    obj = word_embedding.WordEmbedding(
        np.zeros((123, 49), dtype=np.float32),
        dict.fromkeys(range(123), 0)
    )
    assert len(obj) == 123
    assert obj.size == 49

    # Check no assertion raised with OrderedDict
    word_embedding.WordEmbedding(
        np.zeros((2, 3), dtype=np.float32),
        OrderedDict.fromkeys(range(2), 0)
    )


@pytest.mark.parametrize("keep_order", [True, False])
def test_WordEmbedding___load__(glove_file, keep_order):
    """ Check one instance of loading; we assume that each loader is tested
    thoroughly in other unit test.
    """
    obj = word_embedding.WordEmbedding.load(
        glove_file.name, keep_order=keep_order)
    vocab = obj.vocab
    arr = obj.vectors
    assert u'the' in vocab
    assert u',' in vocab
    assert u'日本語' in vocab
    assert len(obj) == 3
    assert arr.dtype == np.float32

    assert obj._load_cond.mod == word_embedding._glove
    assert obj._load_cond.encoding == 'utf-8'
    assert obj._load_cond.unicode_errors == 'strict'

    assert_array_equal(arr[vocab[u'the']],
                       np.array([0.418, 0.24968, -0.41242, 0.1217],
                                dtype=np.float32))
    assert_array_equal(arr[vocab[u',']],
                       np.array([0.013441, 0.23682, -0.16899, 0.40951],
                                dtype=np.float32))
    assert_array_equal(arr[vocab[u'日本語']],
                       np.array([0.15164, 0.30177, -0.16763, 0.17684],
                                dtype=np.float32))


def test_WordEmbedding___save__(word_embedding_data, tmpdir):
    arr_input, vocab_input = word_embedding_data
    obj = word_embedding.WordEmbedding(arr_input, vocab_input)
    tmp_path = tmpdir.join('WordEmbedding__save.txt').strpath
    obj.save(tmp_path, format="word2vec", binary=True)
    with open(tmp_path, 'r') as f:
        arr, vocab = loader.word2vec_bin.load(f, dtype=np.float32)
    assert_array_equal(arr, arr_input)
    assert vocab_input == vocab
