from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from dataclasses import dataclass
import copy

class PatternMatchResult(Enum):
    # The provided data is not a match for this pattern.
    FAILURE = 0

    # The provided data is a match for this pattern. If there is another pattern subsequent to this
    # one, send future data to that instead.
    SUCCESS = 1

    # This pattern has matched so far, but matching isn't complete. The next datum should be
    # received by this pattern, to work towards determining whether this is a match or not.
    NEED_MORE = 2

class PatternElement(ABC):
    """An abstract class describing how one datum of a packet should be matched."""

    @abstractmethod
    def reset(self):
        """Forget all match state and start again."""
        ...

    @abstractmethod
    def match(self, datum: bytes) -> PatternMatchResult:
        """
        Try to match one datum, returning a result based on whether it matched.
        This may be a stateful method if multiple data are required for a match. If so, state
        should be maintained until `reset` is called.
        """
        ...

    def copy_element(self):
        return copy.deepcopy(self)

@dataclass
class FixedPatternElement(PatternElement):
    """Matches one specific datum."""

    datum: bytes

    def reset(self):
        # No state, nothing to do!
        pass

    def match(self, datum: bytes) -> PatternMatchResult:
        if self.datum == datum:
            return PatternMatchResult.SUCCESS
        else:
            return PatternMatchResult.FAILURE

@dataclass
class SequencePatternElement(PatternElement):
    """Matches a sequence of different patterns, one after the other."""

    pattern_elements: List[PatternElement]

    def __post_init__(self):
        self.current_pattern_index = 0

        if len(self.pattern_elements) == 0:
            raise ValueError("empty pattern list is not allowed")
        
    def reset(self):
        # Revert to the first pattern element
        self.current_pattern_index = 0

        # Reset all child elements
        for pe in self.pattern_elements:
            pe.reset()

    def match(self, datum: bytes) -> PatternMatchResult:
        result = self.pattern_elements[self.current_pattern_index].match(datum)
        if result == PatternMatchResult.SUCCESS:
            # Move onto the next pattern
            self.current_pattern_index += 1

            # If we're now at the end, this is a match overall too!
            if self.current_pattern_index >= len(self.pattern_elements):
                return PatternMatchResult.SUCCESS
            
            return PatternMatchResult.NEED_MORE
        
        elif result == PatternMatchResult.FAILURE:
            # This is a failure too
            return PatternMatchResult.FAILURE
        
        elif result == PatternMatchResult.NEED_MORE:
            # Our current pattern needs more data, so we do too
            return PatternMatchResult.NEED_MORE

@dataclass            
class NamePatternElement(PatternElement):
    """A pattern element which wraps another, assigning a name to it."""

    name: str
    pattern_element: PatternElement

    def reset(self):
        self.pattern_element.reset()

    def match(self, datum: bytes) -> PatternMatchResult:
        return self.pattern_element.match(datum)
