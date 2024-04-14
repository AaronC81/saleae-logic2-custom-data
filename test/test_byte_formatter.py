from ..lib.byte_formatter import ByteFormatter

def test_default_format():
    assert "{}".format(ByteFormatter(bytes([1, 2, 0xa]))) == "01020a"

def test_spaced_format():
    assert "{:s}".format(ByteFormatter(bytes([1, 2, 0xa]))) == "01 02 0a"

def test_integer_conversion():
    assert "{:B}".format(ByteFormatter(bytes([1, 2, 0xa]))) == "66058"
    assert "{:L}".format(ByteFormatter(bytes([1, 2, 0xa]))) == "655873"
