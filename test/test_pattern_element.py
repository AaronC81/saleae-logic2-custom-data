from ..lib.pattern_element import *

def test_fixed():
    assert FixedPatternElement(b"\x12").match(b"\x12", env()) == PatternMatchResult.SUCCESS
    assert FixedPatternElement(b"\x12").match(b"\xAB", env()) == PatternMatchResult.FAILURE

def test_sequence():
    seq = SequencePatternElement([
        FixedPatternElement(b"\x01"),
        SequencePatternElement([
            FixedPatternElement(b"\x02"),
            FixedPatternElement(b"\x03"),
        ]),
        FixedPatternElement(b"\x04"),
    ])

    assert seq.match(b"\x01", env()) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x03", env()) == PatternMatchResult.FAILURE
    seq.reset()

    assert seq.match(b"\x01", env()) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x02", env()) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x03", env()) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x04", env()) == PatternMatchResult.SUCCESS

def test_wildcard():
    seq = SequencePatternElement([
        FixedPatternElement(b"\x01"),
        WildcardPatternElement(),
        WildcardPatternElement(),
        FixedPatternElement(b"\x04"),
    ])

    assert seq.match(b"\x01", env()) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x02", env()) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x03", env()) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x04", env()) == PatternMatchResult.SUCCESS

def test_capture():
    seq = SequencePatternElement([
        FixedPatternElement(b"\x01"),
        CapturePatternElement("x", SequencePatternElement([
            WildcardPatternElement(),
            WildcardPatternElement(),
        ])),
        FixedPatternElement(b"\x04"),
    ])

    e = env()
    assert seq.match(b"\x01", e) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x02", e) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x03", e) == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x04", e) == PatternMatchResult.SUCCESS

    assert e.captures == { "x": b"\x02\x03" }

def env() -> PatternMatchEnvironment:
    return PatternMatchEnvironment()
