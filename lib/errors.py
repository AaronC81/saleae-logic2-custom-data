from dataclasses import dataclass
from typing import Optional
from .pattern_tokens import Token

from abc import ABC, abstractmethod

@dataclass
class SourceError(ABC, Exception):
    """An error with an associated position in the input source."""
    position: Optional[range] # `None` means end-of-file

    @abstractmethod
    def explain(self) -> str:
        """Produce a human-readable description of this error."""
        ...

class UnexpectedEndError(SourceError):
    def explain(self) -> str:
        return "unexpected end of input"

@dataclass
class UnexpectedCharacterError(SourceError):
    char: str

    def explain(self) -> str:
        return f"unexpected character '{self.char}' while tokenizing input"

class UnterminatedQuotedStringError(SourceError):
    def explain(self) -> str:
        return "quoted string is not closed"

@dataclass
class UnexpectedTokenError(SourceError):
    token: Token

    def explain(self) -> str:
        return f"unexpected token '{self.token.explain()}'"

@dataclass
class InvalidDatumError(SourceError):
    reason: str

    def explain(self) -> str:
        return self.reason


@dataclass
class CustomException(Exception):
    """A hacky `Exception` subclass which overrides __str__ and __repr__, to better show a custom
    message in the Saleae window's popup."""

    message: str

    @staticmethod
    def from_syntax_error(error: SourceError, input_name: str, input: str) -> "CustomException":
        """Converts a `SourceError` into an annotated `CustomException`."""

        if error.position is None:
            position_desc = "at end of file"
        else:
            # Find the line which contains our start position
            current_pos = 0
            line_number = 1
            for line in input.splitlines(True):
                if current_pos < error.position.start < (current_pos + len(line)):
                    break
                line_number += 1
                current_pos += len(line)
            else:
                position_desc = "at unknown position"
            index_into_line = error.position.start - current_pos + 1

            position_desc = f"at line {line_number} col {index_into_line}"

        message = f"Syntax error in pattern {input_name} {position_desc} - {error.explain()}"

        return CustomException(message)

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return self.message
