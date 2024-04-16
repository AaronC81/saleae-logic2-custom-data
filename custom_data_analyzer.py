# Logic2 doesn't re-import libraries when using the "Reload Extension" button.
# Force that to happen manually.
import lib.pattern_tokens 
import lib.errors
import lib.pattern_element
import lib.pattern_tokenizer
import lib.pattern_parser
import lib.byte_formatter
import lib.data_extractor
import importlib
importlib.reload(lib.pattern_tokens)
importlib.reload(lib.errors)
importlib.reload(lib.pattern_element)
importlib.reload(lib.pattern_tokenizer)
importlib.reload(lib.pattern_parser)
importlib.reload(lib.byte_formatter)
importlib.reload(lib.data_extractor)

from typing import cast, Dict, List, Optional
from dataclasses import dataclass

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
from saleae.data import SaleaeTime

from lib.pattern_element import *
from lib.pattern_tokenizer import Tokenizer
from lib.pattern_parser import Parser
from lib.byte_formatter import ByteFormatter
from lib.errors import SourceError, CustomException
from lib.data_extractor import InputAnalyzerType, extract_datum_from_frame

@dataclass
class PatternMatchCandidate:
    pattern: PatternElement
    env: PatternMatchEnvironment
    start_time: SaleaeTime

class CustomDataAnalyzer(HighLevelAnalyzer):
    input_analyzer_type = ChoicesSetting(label="Input Analyzer Type", choices=[t.value for t in InputAnalyzerType])
    source_setting = ChoicesSetting(label="Pattern Source", choices=["Text", "File"])
    pattern_setting = StringSetting(label="Pattern or File Path")

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        "named": {
            "format": "{{data.text}}"
        },

        "unnamed": {
            "format": "(unnamed)"
        },
    }

    def __init__(self) -> None:
        source_setting = cast(str, self.source_setting)
        pattern_setting = cast(str, self.pattern_setting)

        if source_setting == "Text":
            source_name = "<text>"
            pattern = pattern_setting
        elif source_setting == "File":
            source_name = pattern_setting
            with open(pattern_setting, "r") as f:
                pattern = f.read()
        else:
            raise ValueError(f"unknown source: {source_setting}")

        # Parse input patterns
        try:
            tokens = Tokenizer(pattern).tokenize()
            patterns = Parser(tokens).parse()
        except SourceError as e:
            # Throw another exception with the info presented nicely
            raise CustomException.from_syntax_error(e, source_name, pattern)

        # Set up state
        self.candidates = []

        # Set up lookup tables for creating patterns
        self.pattern_templates_by_start_hint = {}
        self.pattern_templates_without_start_hint = []
        for pat in patterns:
            hints = pat.start_hint()
            if hints is None:
                self.pattern_templates_without_start_hint.append(pat)
            else:
                for hint in hints:
                    if hint not in self.pattern_templates_by_start_hint:
                        self.pattern_templates_by_start_hint[hint] = []
                    self.pattern_templates_by_start_hint[hint].append(pat)

    pattern_templates: List[PatternElement]
    candidates: List[PatternMatchCandidate]

    pattern_templates_by_start_hint: Dict[bytes, List[PatternElement]]
    pattern_templates_without_start_hint: List[PatternElement]

    def decode(self, frame: AnalyzerFrame) -> Optional[AnalyzerFrame | List[AnalyzerFrame]]:
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''

        # Find datum
        datum = extract_datum_from_frame(cast(str, self.input_analyzer_type), frame)
        if datum is None:
            return None
        
        # Create a new candidate for each pattern template
        self.candidates.extend(
            PatternMatchCandidate(pattern=p.copy_element(), env=PatternMatchEnvironment(), start_time=frame.start_time)
            for p in self.pattern_templates_by_start_hint.get(datum, []) + self.pattern_templates_without_start_hint
        )

        # Pipe datum into each candidate
        matches = []
        for candidate in [*self.candidates]:
            match_result = candidate.pattern.match(datum, candidate.env)
            if match_result == PatternMatchResult.SUCCESS:
                # This matched - store it in the list of matches so we can possibly make it into
                # a frame later
                matches.append(candidate)
                self.candidates.remove(candidate)
            elif match_result == PatternMatchResult.FAILURE:
                # No match - remove it
                self.candidates.remove(candidate)
            elif match_result == PatternMatchResult.NEED_MORE:
                # Could still match, we don't know yet. Keep it around
                pass

        if any(matches):
            # Find the "longest" match
            # TODO: more control over what to do?
            matching_candidate = min(matches, key=lambda match: match.start_time)

            # Discard other candidates.
            # The one we just matched is marked with ~, others with -.
            # None of these are allowed:
            #  
            #      |~~~~|           |~~~~|          |~~~~|
            #        |---         |-------               |
            #
            # This isn't possible (because the match just ended, so we'd have to time-travel)
            #
            #      |~~~~|
            #   |-----|
            #
            # That covers all possibilities, so empty the candidate list.
            self.candidates.clear()

            # Create our frame with a formatted message
            if isinstance(matching_candidate.pattern, NamePatternElement):
                format_captures = { k: ByteFormatter(data=v) for k, v in matching_candidate.env.captures.items() }
                text = matching_candidate.pattern.name.format(**format_captures)
                ty, data = "named", { "text": text }
            else:
                ty, data = "unnamed", {}

            return AnalyzerFrame(ty, matching_candidate.start_time, frame.end_time, data)
        
        return None


    