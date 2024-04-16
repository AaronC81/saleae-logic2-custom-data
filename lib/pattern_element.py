from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass, field
import copy

@dataclass
class PatternMatchEnvironment:
    captures: Dict[str, bytes] = field(default_factory=lambda: {})

    def add_capture(self, name: str, data: bytes) -> None:
        self.captures[name] = data

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
    def reset(self) -> None:
        """Forget all match state and start again."""
        ...

    @abstractmethod
    def match(self, datum: bytes, env: PatternMatchEnvironment) -> PatternMatchResult:
        """
        Try to match one datum, returning a result based on whether it matched.
        This may be a stateful method if multiple data are required for a match. If so, state
        should be maintained until `reset` is called.

        Capturing pattern elements may modify the `env` *if and only if* the match returns
        `PatternMatchResult.SUCCESS`. Matches shouldn't be modified incrementally, to prevent
        clashes between multiple concurrent match candidates.
        """
        ...

    @abstractmethod
    def start_hint(self) -> Optional[List[bytes]]:
        """
        Get the first matching possibilities for this pattern element.

        This is for optimisation purposes, as it allows possibly relevant patterns to be selected
        more quickly given new data.

        If an item is in the returned list, then the first call to `match` with that item _must_
        return either `PatternMatchResult.SUCCESS` or `PatternMatchResult.NEED_MORE`. Any items not
        in the returned list would cause the first call to `match` to return
        `PatternMatchResult.FAILURE`.

        If `None`, the list of valid input items isn't defined for this pattern.
        """
        ...

    def copy_element(self) -> "PatternElement":
        return copy.deepcopy(self)

@dataclass
class FixedPatternElement(PatternElement):
    """Matches one specific datum."""

    datum: bytes

    def reset(self) -> None:
        # No state, nothing to do!
        pass

    def match(self, datum: bytes, _env: PatternMatchEnvironment) -> PatternMatchResult:
        if self.datum == datum:
            return PatternMatchResult.SUCCESS
        else:
            return PatternMatchResult.FAILURE
        
    def start_hint(self) -> Optional[List[bytes]]:
        return [self.datum]

@dataclass
class SequencePatternElement(PatternElement):
    """Matches a sequence of different patterns, one after the other."""

    pattern_elements: List[PatternElement]

    def __post_init__(self) -> None:
        self.current_pattern_index = 0

        if len(self.pattern_elements) == 0:
            raise ValueError("empty pattern list is not allowed")
        
    def reset(self) -> None:
        # Revert to the first pattern element
        self.current_pattern_index = 0

        # Reset all child elements
        for pe in self.pattern_elements:
            pe.reset()

    def match(self, datum: bytes, env: PatternMatchEnvironment) -> PatternMatchResult:
        result = self.pattern_elements[self.current_pattern_index].match(datum, env)
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
        
        else:
            raise ValueError(f"unknown result: {result}")
        
    def start_hint(self) -> Optional[List[bytes]]:
        return self.pattern_elements[0].start_hint()

@dataclass            
class NamePatternElement(PatternElement):
    """A pattern element which wraps another, assigning a name to it."""

    name: str
    pattern_element: PatternElement

    def reset(self) -> None:
        self.pattern_element.reset()

    def match(self, datum: bytes, env: PatternMatchEnvironment) -> PatternMatchResult:
        return self.pattern_element.match(datum, env)
    
    def start_hint(self) -> Optional[List[bytes]]:
        return self.pattern_element.start_hint()

@dataclass
class WildcardPatternElement(PatternElement):
    """A pattern element which matches any one datum."""

    def reset(self) -> None:
        pass

    def match(self, _datum: bytes, _env: PatternMatchEnvironment) -> PatternMatchResult:
        return PatternMatchResult.SUCCESS
    
    def start_hint(self) -> Optional[List[bytes]]:
        return None

@dataclass
class CapturePatternElement(PatternElement):
    """A pattern element which captures the matched data, for use elsewhere in the pattern."""
    
    name: str
    pattern_element: PatternElement

    def __post_init__(self) -> None:
        self.capture_buffer = bytes()

    def reset(self) -> None:
        self.capture_buffer = bytes()
        self.pattern_element.reset()

    def match(self, datum: bytes, env: PatternMatchEnvironment) -> PatternMatchResult:
        result = self.pattern_element.match(datum, env)

        # Push datum if it didn't cause a failure
        if result == PatternMatchResult.SUCCESS or result == PatternMatchResult.NEED_MORE:
            self.capture_buffer += datum

        # If success, submit capture
        if result == PatternMatchResult.SUCCESS:
            env.add_capture(self.name, self.capture_buffer)

        return result
    
    def start_hint(self) -> Optional[List[bytes]]:
        return self.pattern_element.start_hint()
        