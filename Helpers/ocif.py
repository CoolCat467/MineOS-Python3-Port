"""Read OCIF files."""

from __future__ import annotations

# Programmed by CoolCat467

OCIF_SIGNATURE = "OCIF"

from typing import TYPE_CHECKING, Generator

import Color as color
import numpy as np

if TYPE_CHECKING:
    import io


class Picture:
    """Picture."""
    __slots__ = ("width", "height", "symbol", "foreground", "background", "alpha")

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

        self.symbol = np.zeros((height, width), dtype=str)
        self.foreground = np.zeros((height, width), dtype=np.int32)
        self.background = np.zeros((height, width), dtype=np.int32)
        self.alpha = np.zeros((height, width), dtype=np.int16)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.width}, {self.height})>"

    def set(
        self, x: int, y: int, symbol: str, background: int, foreground: int, alpha: int,
    ) -> None:
        """Set values for pixel."""
        self.symbol[y, x] = symbol
        self.foreground[y, x] = foreground
        self.background[y, x] = background
        self.alpha[y, x] = alpha

    def get(self, x: int, y: int) -> tuple[str, int, int, int]:
        """Get value at pixel."""
        return (
            self.symbol[y, x],
            self.foreground[y, x],
            self.background[y, x],
            self.alpha[y, x],
        )

    def __iter__(self) -> Generator[str, None, None]:
        for y in range(self.height):
            for x in range(self.width):
                yield self.get(x, y)[0]
            yield "\n"


def bytearr_to_int(arr: bytearray) -> int:
    """Convert bytearray to int."""
    return int.from_bytes(arr)


def int_to_bytearr(number: int, _size: int) -> bytearray:
    """Encode int as bytearray."""
    return number.to_bytes(_size)


def readUTF8(f, count: int) -> str:
    """Read `count` UTF-8 bytes from file `f`, return as unicode."""
    # Assumes UTF-8 data is valid; leaves it up to the `.decode()`
    # call to validate
    res = []
    while count:
        count -= 1
        lead = f.read(1)
        res.append(lead)

        value = ord(lead)
        if 0xBF < value < 0xF5:
            read_count = 1 + (value >= 0xE0) + (value >= 0xF0)
            res.append(f.read(read_count))
    return (b"".join(res)).decode("utf8")


def load_grouped(method: int, file: io.IOBase) -> Picture:
    """Load grouped ocif file."""
    seven = 1 if method >= 7 else 0
    eight = 1 if method >= 8 else 0

    width = file.read(1)[0] + eight
    height = file.read(1)[0] + eight

    picture = Picture(width, height)

    alpha_size = file.read(1)[0] + seven

    for _alpha in range(alpha_size):
        current_alpha = file.read(1)[0]  # / 255

        symbol_size = int.from_bytes(file.read(2)) + seven

        for _symbol in range(symbol_size):
            current_symbol = readUTF8(file, 1)

            background_size = file.read(1)[0]

            for _background in range(background_size + seven):
                current_background = color.to24Bit(file.read(1)[0])
                foreground_size = file.read(1)[0]

                for _foreground in range(foreground_size + seven):
                    current_foreground = color.to24Bit(file.read(1)[0])
                    y_size = file.read(1)[0]

                    for _y in range(y_size + seven):
                        current_y = file.read(1)[0] + eight
                        x_size = file.read(1)[0]

                        for _x in range(x_size + seven):
                            current_x = file.read(1)[0] + eight

                            picture.set(
                                current_x - 1,
                                current_y - 1,
                                current_symbol,
                                current_background,
                                current_foreground,
                                current_alpha,
                            )
    return picture


def load(filename: str) -> Picture:
    """Load picture from file."""
    with open(filename, "rb") as file:
        magic = file.read(4)
        if magic != b"OCIF":
            raise OSError("File header is invalid for OCIF image")
        method = file.read(1)[0]
        print(f"{method = }")
        if method > 5:
            return load_grouped(method, file)
        return None


def run():
    """Run."""
    picture = load("AhsokaTano.pic")
    print(picture)
    print("".join(picture))


if __name__ == "__main__":
    run()
