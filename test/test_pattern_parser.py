from ..lib.pattern_parser import *
from ..lib.pattern_element import *

def test_parse_sequence():
    assert parse("ab cd") == [
        SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            FixedPatternElement(b"\xCD"),
        ]),
    ]

def test_parse_named():
    assert parse("\"foo\" = ab cd") == [
        NamePatternElement("foo", SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            FixedPatternElement(b"\xCD"),
        ])),
    ]

def test_parse_multiple():
    assert parse("\"foo\" = ab cd ; \"bar\" = de 12;") == [
        NamePatternElement("foo", SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            FixedPatternElement(b"\xCD"),
        ])),
        NamePatternElement("bar", SequencePatternElement([
            FixedPatternElement(b"\xDE"),
            FixedPatternElement(b"\x12"),
        ])),
    ]

def parse(input: str):
    return Parser(Tokenizer(input).tokenize()).parse()
