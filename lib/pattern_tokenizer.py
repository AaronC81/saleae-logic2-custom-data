from dataclasses import dataclass
from typing import List
from .pattern_tokens import *
from .errors import *

class Tokenizer:
    def __init__(self, input: str):
        self.input = input
        self.current_position = 0

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

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
            elif self.take_if("*"):
                tokens.append(StarToken(position=self.range_to_here_from(start_pos)))
            elif self.take_if("("):
                tokens.append(LParenToken(position=self.range_to_here_from(start_pos)))
            elif self.take_if(")"):
                tokens.append(RParenToken(position=self.range_to_here_from(start_pos)))


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
                    raise UnterminatedQuotedStringError(position=None)
                self.take() 

                tokens.append(QuotedStringToken(contents=buffer, position=self.range_to_here_from(start_pos)))

            else:
                raise UnexpectedCharacterError(char=self.here(), position=self.range_to_here_from(start_pos))
            
        return tokens

    def skip_whitespace(self) -> None:
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
            raise UnexpectedEndError(position=None)
    
        return self.input[self.current_position]

    def range_to_here_from(self, start_pos: int) -> range:
        return range(start_pos, self.current_position)
