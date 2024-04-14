from dataclasses import dataclass
from typing import List

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

class UnexpectedEndError(Exception): pass

@dataclass
class UnexpectedCharacterError(Exception):
    char: str
    position: int

class UnterminatedQuotedStringError(Exception): pass


class Tokenizer:
    def __init__(self, input: str):
        self.input = input
        self.current_position = 0

    def tokenize(self) -> List[Token]:
        tokens = []

        while not self.is_at_end():
            # Skip whitespace
            self.skip_whitespace()
            if self.is_at_end(): break

            start_pos = self.current_position

            if self.take_if(";"):
                tokens.append(SemicolonToken(position=self.range_to_here_from(start_pos)))
            elif self.take_if("="):
                tokens.append(EqualsToken(position=self.range_to_here_from(start_pos)))
            elif self.take_if("."):
                tokens.append(DotToken(position=self.range_to_here_from(start_pos)))
            elif self.take_if(":"):
                tokens.append(ColonToken(position=self.range_to_here_from(start_pos)))

            elif self.here().isalnum():
                buffer = ""
                while not self.is_at_end() and (self.here().isalnum() or self.here() == '_'):
                    buffer += self.take()
                tokens.append(DatumToken(contents=buffer, position=self.range_to_here_from(start_pos)))

            elif self.take_if("\""):
                buffer = ""
                while not self.is_at_end() and self.here() != "\"":
                    buffer += self.take()

                # Consume closing quote
                if self.is_at_end():
                    raise UnterminatedQuotedStringError()
                self.take() 

                tokens.append(QuotedStringToken(contents=buffer, position=self.range_to_here_from(start_pos)))

            else:
                raise UnexpectedCharacterError(char=self.here(), position=self.current_position)
            
        return tokens

    def skip_whitespace(self):
        while not self.is_at_end() and self.here().isspace():
            self.take()

    def is_at_end(self) -> bool:
        return self.current_position >= len(self.input)

    def take(self) -> str:
        """Consume one character from the input, and return it."""

        char = self.here()
        self.current_position += 1
        return char
    
    def take_if(self, expected: str) -> bool:
        """If the next character from the input matches a given one, consume it and return True."""

        char = self.here()
        if char == expected:
            self.take()
            return True
        return False

    def here(self) -> str:
        """Return the current character from the input, without changing it."""

        if self.is_at_end():
            raise UnexpectedEndError()
    
        return self.input[self.current_position]

    def range_to_here_from(self, start_pos) -> range:
        return range(start_pos, self.current_position)
