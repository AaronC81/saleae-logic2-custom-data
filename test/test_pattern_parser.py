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

def test_parse_wildcard():
    assert parse("ab .. cd") == [
        SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            WildcardPatternElement(),
            WildcardPatternElement(),
            FixedPatternElement(b"\xCD"),
        ]),
    ]

def test_parse_capture():
    assert parse("ab x:. y:. cd") == [
        SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            CapturePatternElement("x", WildcardPatternElement()),
            CapturePatternElement("y", WildcardPatternElement()),
            FixedPatternElement(b"\xCD"),
        ]),
    ]

def test_parse_subpattern():
    assert parse("ab x:(..) cd") == [
        SequencePatternElement([
            FixedPatternElement(b"\xAB"),
            CapturePatternElement("x", SequencePatternElement([
                WildcardPatternElement(),
                WildcardPatternElement(),
            ])),
            FixedPatternElement(b"\xCD"),
        ]),
    ]


def parse(input: str):
    return Parser(Tokenizer(input).tokenize()).parse()
