# type: ignore

import pytest
from ..lib.pattern_tokenizer import *

def test_tokenize_data():
    assert Tokenizer("ab 12 34 5").tokenize() == [
        DatumToken(contents="ab", position=range(0, 2)),
        DatumToken(contents="12", position=range(3, 5)),
        DatumToken(contents="34", position=range(6, 8)),
        DatumToken(contents="5",  position=range(9, 10)),
    ]

def test_tokenize_symbols():
    assert Tokenizer("\"ABC\" = ab ;").tokenize() == [
        QuotedStringToken(contents="ABC", position=range(0, 5)),
        EqualsToken(                      position=range(6, 7)),
        DatumToken(contents="ab",         position=range(8, 10)),
        SemicolonToken(                   position=range(11, 12)),
    ]

def test_unknown():
    with pytest.raises(UnexpectedCharacterError):
        Tokenizer("?").tokenize()

def test_unterminated_string():
    with pytest.raises(UnterminatedQuotedStringError):
        Tokenizer("\"ABC = ab ;").tokenize()
