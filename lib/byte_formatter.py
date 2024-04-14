from dataclasses import dataclass

@dataclass
class ByteFormatter:
    """Wraps a `bytes` instance to provide in-depth formatting control."""

    data: bytes

    def __format__(self, spec):
        # Convention here is that lowercase options change formatting, while uppercase options
        # change how the data is actually interpreted.

        if spec == "":
            # By default, render as a "packed" hexadecimal sequence:
            #   abcdef1234
            return self.data.hex()

        elif spec == "s":
            # Render the string with *s*pacing
            #   ab cd ef 12 34
            return self.data.hex(" ")
        
        elif spec == "L":
            # Interpret the string as a *l*ittle-endian integer
            return str(int.from_bytes(self.data, byteorder="little"))
        
        elif spec == "B":
            # Interpret the string as a *b*ittle-endian integer
            return str(int.from_bytes(self.data, byteorder="big"))

        else:
            raise ValueError(f"unknown string format spec: {spec}")
        