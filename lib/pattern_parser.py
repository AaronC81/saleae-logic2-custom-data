from .pattern_tokenizer import *
from .pattern_element import PatternElement, SequencePatternElement, NamePatternElement, FixedPatternElement, WildcardPatternElement, CapturePatternElement
from dataclasses import dataclass
from typing import List
from .errors import *
from .pattern_tokens import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.input = tokens
        self.current_position = 0

    def parse(self) -> List[PatternElement]:
        elements = []

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
                raise UnexpectedTokenError(token=token, position=self.current_position)
        
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

    def parse_body(self, end_delimiter) -> SequencePatternElement:
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
            raise UnexpectedTokenError(token=token, position=self.current_position)
    
    def datum_contents_to_bytes(self, token: DatumToken) -> bytes:
        try:
            numeric = int(token.contents, 16)
        except ValueError:
            raise InvalidDatumError(reason=f"data values must be hexadecimal strings, not `{token.contents}`", position=token.position)
        
        if numeric < 0 or numeric > 0xFF:
            raise InvalidDatumError(reason=f"data values must be bytes (00-ff), `{token.contents}` is out-of-range", position=token.position)
        
        return bytes([numeric])

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
