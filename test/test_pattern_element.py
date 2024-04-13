from ..lib.pattern_element import PatternMatchResult, FixedPatternElement, SequencePatternElement, WildcardPatternElement

def test_fixed():
    assert FixedPatternElement(b"\x12").match(b"\x12") == PatternMatchResult.SUCCESS
    assert FixedPatternElement(b"\x12").match(b"\xAB") == PatternMatchResult.FAILURE

def test_sequence():
    seq = SequencePatternElement([
        FixedPatternElement(b"\x01"),
        SequencePatternElement([
            FixedPatternElement(b"\x02"),
            FixedPatternElement(b"\x03"),
        ]),
        FixedPatternElement(b"\x04"),
    ])

    assert seq.match(b"\x01") == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x03") == PatternMatchResult.FAILURE
    seq.reset()

    assert seq.match(b"\x01") == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x02") == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x03") == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x04") == PatternMatchResult.SUCCESS

def test_wildcard():
    seq = SequencePatternElement([
        FixedPatternElement(b"\x01"),
        WildcardPatternElement(),
        WildcardPatternElement(),
        FixedPatternElement(b"\x04"),
    ])

    assert seq.match(b"\x01") == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x02") == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x03") == PatternMatchResult.NEED_MORE
    assert seq.match(b"\x04") == PatternMatchResult.SUCCESS
