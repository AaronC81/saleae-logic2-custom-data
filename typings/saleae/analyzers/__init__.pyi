from ..data import SaleaeTime
from typing import Dict, Mapping, Optional, List, Union

class AnalyzerFrame:
    type: str
    start_time: SaleaeTime
    end_time: SaleaeTime
    data: Dict[str, object]

    def __init__(self, type: str, start_time: SaleaeTime, end_time: SaleaeTime, data: Mapping[str, object]): ...

class HighLevelAnalyzer:
    def decode(self, frame: AnalyzerFrame) -> Optional[Union[AnalyzerFrame, List[AnalyzerFrame]]]: ...

class Setting:
    label: Optional[str]

    def __init__(self, /, label: Optional[str] = None): ...

class StringSetting(Setting):
    def __init__(self, /, label: Optional[str] = None): ...

class NumberSetting(Setting):
    min_value: Optional[float]
    max_value: Optional[float]

    def __init__(self, /,
                 label: Optional[str] = None,
                 min_value: Optional[float] = None,
                 max_value: Optional[float] = None,
                 ): ...

class ChoicesSetting(Setting):
    choices: List[str]

    def __init__(self, /,
                 choices: List[str],
                 label: Optional[str] = None,
                 ): ...