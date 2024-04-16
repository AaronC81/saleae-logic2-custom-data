from enum import Enum
from saleae.analyzers import AnalyzerFrame
from typing import Optional
from .errors import CustomException

class InputAnalyzerType(str, Enum):
    """The user-selectable type of the input analyzer, to dictate how data is read from it.
    Each enum value is a friendly name."""

    ASYNC_SERIAL = "Async Serial"
    SPI_MOSI = "SPI (use MOSI)"
    SPI_MISO = "SPI (use MISO)"

def extract_datum_from_frame(ty: str, frame: AnalyzerFrame) -> Optional[bytes]:
    """Extract relevant datum given a frame, based on the given type.
    Returns `None` if this frame is valid but contains no data."""

    try:
        if ty == InputAnalyzerType.ASYNC_SERIAL.value:
            return frame.data["data"]
        elif ty == InputAnalyzerType.SPI_MOSI.value:
            if frame.type == "result":
                return frame.data["mosi"]
        elif ty == InputAnalyzerType.SPI_MISO.value:
            if frame.type == "result":
                return frame.data["miso"]
        else:
            raise ValueError(f"unknown input type '{ty}'")
    except KeyError as e:
        raise CustomException.from_analyzer_data_error(e, frame.data, ty)
