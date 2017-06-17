# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
import StringIO
import pytest
from numpy.testing import assert_array_equal

import word_embedding_loader.loader as loader
import word_embedding_loader.saver as saver


@pytest.mark.parametrize("mod", [
    (saver.glove, loader.glove),
    (saver.word2vec_bin, loader.word2vec_bin),
    (saver.word2vec_text, loader.word2vec_text)
])
def test_load(word_embedding, mod, tmpdir):
    _saver, _loader = mod
    arr_input, vocab_input = word_embedding

    with open(tmpdir.join('output.txt').strpath, 'a+') as f:
        _saver.save(f, arr_input, vocab_input)
        f.seek(0)
        arr, vocab = _loader.load(f, dtype=np.float32, keep_order=True)
    assert_array_equal(arr, arr_input)
    assert vocab_input == vocab