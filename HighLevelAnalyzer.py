# Logic2 doesn't re-import libraries when using the "Reload Extension" button.
# Force that to happen manually.
import lib.pattern_element
import importlib 
importlib.reload(lib.pattern_element)

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
from lib.pattern_element import *

class Hla(HighLevelAnalyzer):
    pattern_setting = StringSetting()

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        "named": {
            "format": "{{data.text}}"
        },

        "unnamed": {
            "format": "(unnamed)"
        },
    }

    def __init__(self):
        self.pattern_templates = [
            NamePatternElement("Get Version",
                SequencePatternElement([
                    FixedPatternElement(b"\x01"),
                    FixedPatternElement(b"\xFE"),
                ])
            ),
            NamePatternElement("Get Chip ID",
                SequencePatternElement([
                    FixedPatternElement(b"\x02"),
                    FixedPatternElement(b"\xFD"),
                ])
            ),
        ]
        self.candidates = []

    pattern_templates: List[PatternElement]
    candidates: List[Tuple[PatternElement, object]]

    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''

        # Create a new candidate for each pattern template
        self.candidates.extend((p.copy_element(), frame.start_time) for p in self.pattern_templates)

        # Pipe datum into each candidate
        matches = []
        for candidate in [*self.candidates]:
            (pattern, start_time) = candidate

            match_result = pattern.match(frame.data['data'])
            if match_result == PatternMatchResult.SUCCESS:
                # This matched - store it in the list of matches so we can possibly make it into
                # a frame later
                matches.append((pattern, start_time))

                self.candidates.remove(candidate)
            elif match_result == PatternMatchResult.FAILURE:
                # No match - remove it
                self.candidates.remove(candidate)
            elif match_result == PatternMatchResult.NEED_MORE:
                # Could still match, we don't know yet. Keep it around
                pass

        if any(matches):
            # Find the "longest" match, and create a frame for that one.
            # (Discard the other matches, if they existed.)
            # TODO: more control over what to do?
            matching_pattern, matching_start_time = min(matches, key=lambda match: match[1])

            if isinstance(matching_pattern, NamePatternElement):
                ty, data = "named", { "text": matching_pattern.name }
            else:
                ty, data = "unnamed", {}

            return AnalyzerFrame(ty, matching_start_time, frame.end_time, data)
