from ..lib.pattern_parser import *
from ..lib.pattern_element import *
from ..lib.errors import InvalidDatumError
import pytest

def test_parse_sequence():
    assert parse("xAB xCD") == [
        SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            FixedPatternElement(b"\xCD"),
        ]),
    ]

def test_parse_named():
    assert parse("\"foo\" = xAB xCD") == [
        NamePatternElement("foo", SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            FixedPatternElement(b"\xCD"),
        ])),
    ]

def test_parse_multiple():
    assert parse("\"foo\" = xAB xCD ; \"bar\" = xDE x12;") == [
        NamePatternElement("foo", SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            FixedPatternElement(b"\xCD"),
        ])),
        NamePatternElement("bar", SequencePatternElement([
            FixedPatternElement(b"\xDE"),
            FixedPatternElement(b"\x12"),
        ])),
    ]

def test_parse_wildcard():
    assert parse("xAB .. xCD") == [
        SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            WildcardPatternElement(),
            WildcardPatternElement(),
            FixedPatternElement(b"\xCD"),
        ]),
    ]

def test_parse_capture():
    assert parse("xAB x:. y:. xCD") == [
        SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            CapturePatternElement("x", WildcardPatternElement()),
            CapturePatternElement("y", WildcardPatternElement()),
            FixedPatternElement(b"\xCD"),
        ]),
    ]

def test_parse_subpattern():
    assert parse("xAB x:(..) xCD") == [
        SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            CapturePatternElement("x", SequencePatternElement([
                WildcardPatternElement(),
                WildcardPatternElement(),
            ])),
            FixedPatternElement(b"\xCD"),
        ]),
    ]

def test_parse_number_styles():
    # Hex
    assert parse("xAB")  == [SequencePatternElement([FixedPatternElement(b"\xAB")])]
    assert parse("0xAB") == [SequencePatternElement([FixedPatternElement(b"\xAB")])]
    assert parse("ABx")  == [SequencePatternElement([FixedPatternElement(b"\xAB")])]

    # Decimal
    assert parse("d16")  == [SequencePatternElement([FixedPatternElement(b"\x10")])]
    assert parse("0d16") == [SequencePatternElement([FixedPatternElement(b"\x10")])]
    assert parse("16d")  == [SequencePatternElement([FixedPatternElement(b"\x10")])]

    # Binary
    assert parse("b100")  == [SequencePatternElement([FixedPatternElement(b"\x04")])]
    assert parse("0b100") == [SequencePatternElement([FixedPatternElement(b"\x04")])]
    assert parse("100b")  == [SequencePatternElement([FixedPatternElement(b"\x04")])]

    # Special case - zero doesn't need a base
    assert parse("0") == [SequencePatternElement([FixedPatternElement(b"\0")])]

    # But other numbers do
    with pytest.raises(InvalidDatumError):
        parse("4")

def parse(input: str):
    return Parser(Tokenizer(input).tokenize()).parse()
