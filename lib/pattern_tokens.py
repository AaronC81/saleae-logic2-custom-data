from dataclasses import dataclass

@dataclass
class Token:
    position: range

@dataclass
class DatumToken(Token):
    contents: str

@dataclass
class QuotedStringToken(Token):
    contents: str

class SemicolonToken(Token): pass
class EqualsToken(Token): pass
class DotToken(Token): pass
class ColonToken(Token): pass
class LParenToken(Token): pass
class RParenToken(Token): pass
