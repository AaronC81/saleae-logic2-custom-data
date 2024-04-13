from .pattern_tokenizer import *
from .pattern_element import PatternElement, SequencePatternElement, NamePatternElement, FixedPatternElement, WildcardPatternElement
from dataclasses import dataclass
from typing import List

class UnexpectedEndError(Exception): pass

@dataclass
class UnexpectedTokenError(Exception):
    token: Token

@dataclass
class InvalidDatumError(Exception):
    reason: str


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
                elements.append(self.parse_body())

            else:
                raise UnexpectedTokenError(token)
        
        return elements
    
    def parse_named(self) -> NamePatternElement:
        name = self.take()
        if not isinstance(name, QuotedStringToken):
            return UnexpectedTokenError(name)
        
        eq = self.take()
        if not isinstance(eq, EqualsToken):
            return UnexpectedTokenError(eq)
        
        body = self.parse_body()

        return NamePatternElement(name=name.contents, pattern_element=body)

    def parse_body(self) -> SequencePatternElement:
        elements = []

        while not self.is_at_end():
            token = self.here()

            if isinstance(token, SemicolonToken):
                # Bail - this sequence is over
                break

            elif isinstance(token, DatumToken):
                elements.append(FixedPatternElement(datum=self.datum_contents_to_bytes(token.contents)))
                self.take()

            elif isinstance(token, DotToken):
                elements.append(WildcardPatternElement())
                self.take()

            else:
                raise UnexpectedTokenError(token)
            
        return SequencePatternElement(elements)
    
    def datum_contents_to_bytes(self, contents: str) -> bytes:
        try:
            numeric = int(contents, 16)
        except ValueError:
            raise InvalidDatumError(reason=f"data values must be hexadecimal strings, not `{contents}`")
        
        if numeric < 0 or numeric > 0xFF:
            raise InvalidDatumError(reason=f"data values must be bytes (00-ff), `{contents}` is out-of-range")
        
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
            raise UnexpectedEndError()
    
        return self.input[self.current_position]
