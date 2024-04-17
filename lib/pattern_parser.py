from .pattern_tokenizer import *
from .pattern_element import PatternElement, SequencePatternElement, NamePatternElement, FixedPatternElement, WildcardPatternElement, CapturePatternElement
from dataclasses import dataclass
from typing import List, Tuple
from .errors import *
from .pattern_tokens import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.input = tokens
        self.current_position = 0

    def parse(self) -> List[PatternElement]:
        elements: List[PatternElement] = []

        while not self.is_at_end():
            token = self.here()

            if isinstance(token, SemicolonToken):
                # Skip - child parsers can use this as an indication to stop
                self.take()

            elif isinstance(token, QuotedStringToken):
                elements.append(self.parse_named())

            elif isinstance(token, DatumToken):
                elements.append(self.parse_body(end_delimiter=SemicolonToken))

            else:
                raise UnexpectedTokenError(token=token, position=token.position)
        
        return elements
    
    def parse_named(self) -> NamePatternElement:
        name = self.take()
        if not isinstance(name, QuotedStringToken):
            raise UnexpectedTokenError(token=name, position=name.position)
        
        eq = self.take()
        if not isinstance(eq, EqualsToken):
            raise UnexpectedTokenError(token=eq, position=eq.position)
        
        body = self.parse_body(end_delimiter=SemicolonToken)

        return NamePatternElement(name=name.contents, pattern_element=body)

    def parse_body(self, end_delimiter: type) -> SequencePatternElement:
        elements = []

        while not self.is_at_end():
            token = self.here()

            if isinstance(token, end_delimiter):
                # Bail - this sequence is over
                break
            else:
                elements.append(self.parse_single_element())
            
        return SequencePatternElement(elements)
    
    def parse_single_element(self) -> PatternElement:
        token = self.here()

        if isinstance(token, DatumToken):
            self.take()

            # This might be a capture, if it's of the form `x:...` rather than just `x`
            if not self.is_at_end() and isinstance(self.here(), ColonToken):
                self.take()
                captured_pattern = self.parse_single_element()
                return CapturePatternElement(token.contents, captured_pattern)

            return FixedPatternElement(datum=self.datum_contents_to_bytes(token))

        elif isinstance(token, DotToken):
            self.take()
            return WildcardPatternElement()
        
        elif isinstance(token, LParenToken):
            self.take()
            body = self.parse_body(end_delimiter=RParenToken)
            if not self.is_at_end():
                self.take() # Consume RParen
            return body
        
        else:
            raise UnexpectedTokenError(token=token, position=token.position)
    
    def datum_contents_to_bytes(self, token: DatumToken) -> bytes:
        """Converts a `DatumToken` into the bytes which that datum should match."""

        base, value = self.datum_extract_base_and_value(token)

        try:
            numeric = int(value, base)
        except ValueError:
            raise InvalidDatumError(reason=f"data value expected to be in base {base}, but `{value}` is not", position=token.position)
        
        if numeric < 0 or numeric > 0xFF:
            raise InvalidDatumError(reason=f"data values must be bytes, `{token.contents}` is out-of-range", position=token.position)
        
        return bytes([numeric])
    
    def datum_extract_base_and_value(self, token: DatumToken) -> Tuple[int, str]:
        """
        Gets the base and value for a `DatumToken`.
        For example, "0x1A" gives `(16, "1A")`.

        Throws an `InvalidDatumError` if the token's contents do not match any of the expected
        formats or bases.
        """

        contents = token.contents

        # If this is just zeroes, return now
        if all(c == '0' for c in contents):
            return (10, "0")

        # Trim off any leading 0 to remove `0x00` from being something we need to explicitly
        # consider. (It'll become the same as `x00`.)
        if contents[0] == '0':
            contents = contents[1:]

        # Find a base at the start or end
        bases = { "x": 16, "d": 10, "b": 2 }
        if contents[0] in bases:
            return (bases[contents[0]], contents[1:])
        elif contents[-1] in bases:
            return (bases[contents[-1]], contents[:-1])
        else:
            raise InvalidDatumError(reason=f"cannot find base specifier (`x`, `b`, or `d`) on data value `{token.contents}`", position=token.position)

    def is_at_end(self) -> bool:
        return self.current_position >= len(self.input)

    def take(self) -> Token:
        """Consume one token from the input, and return it."""

        char = self.here()
        self.current_position += 1
        return char

    def here(self) -> Token:
        """Return the current token from the input, without changing it."""

        if self.is_at_end():
            raise UnexpectedEndError(position=None)
    
        return self.input[self.current_position]
