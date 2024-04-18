from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import no_type_check

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
    
class SemicolonToken(Token):
    def explain(self) -> str: return ";"
class EqualsToken(Token):
    def explain(self) -> str: return "="
class DotToken(Token):
    def explain(self) -> str: return "."
class ColonToken(Token):
    def explain(self) -> str: return ":"
class StarToken(Token):
    def explain(self) -> str: return "*"
class LParenToken(Token):
    def explain(self) -> str: return "("
class RParenToken(Token):
    def explain(self) -> str: return ")"
