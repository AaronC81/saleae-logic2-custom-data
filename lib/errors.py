from dataclasses import dataclass
from .pattern_tokens import Token

class UnexpectedEndError(Exception): pass

@dataclass
class UnexpectedCharacterError(Exception):
    char: str
    position: int

class UnterminatedQuotedStringError(Exception): pass

@dataclass
class UnexpectedTokenError(Exception):
    token: Token

@dataclass
class InvalidDatumError(Exception):
    reason: str
