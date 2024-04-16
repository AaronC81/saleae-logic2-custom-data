from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Token(ABC):
    position: range

    @abstractmethod
    def explain(self) -> str:
        """Produce a human-readable description of this token."""
        ...

@dataclass
class DatumToken(Token):
    contents: str

    def explain(self) -> str:
        return self.contents

@dataclass
class QuotedStringToken(Token):
    contents: str

    def explain(self) -> str:
        return self.contents
    
# Fancy metaclass shenanigans to avoid taking up loads of space with tiny `explain` implementations
class CharTokenMeta(type(Token)):
    def __new__(cls, name, bases, dct, /, char = None):
        klass = super().__new__(cls, name, bases, dct)
        klass.explain = lambda _: char
        return klass
class CharToken(Token, metaclass=CharTokenMeta): pass

class SemicolonToken(CharToken, char=";"): pass
class EqualsToken(CharToken, char="="): pass
class DotToken(CharToken, char="."): pass
class ColonToken(CharToken, char=":"): pass
class LParenToken(CharToken, char="("): pass
class RParenToken(CharToken, char=")"): pass
