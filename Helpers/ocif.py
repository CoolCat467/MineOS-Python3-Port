"""Read OCIF files."""

from __future__ import annotations

# Programmed by CoolCat467
from typing import TYPE_CHECKING, Final, Generator

import color
import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    import io

    from typing_extensions import Self

OCIF_SIGNATURE: Final = "OCIF"


class Picture:
    """Picture."""

    __slots__ = (
        "width",
        "height",
        "symbol",
        "foreground",
        "background",
        "alpha",
    )

    def __init__(
        self,
        width: int,
        height: int,
        symbols: npt.NDArray[np.unicode_] | None = None,
        foregrounds: npt.NDArray[np.uint32] | None = None,
        backgrounds: npt.NDArray[np.uint32] | None = None,
        alphas: npt.NDArray[np.uint8] | None = None,
    ) -> None:
        """Initialize Picture."""
        self.width = width
        self.height = height

        if symbols is None:
            self.symbol = np.zeros(
                (height, width),
                dtype="<U1",
            )
            self.symbol[:, :] = " "
        else:
            self.symbol = symbols
        self.foreground = (
            np.zeros(
                (height, width),
                dtype=np.uint32,
            )
            if foregrounds is None
            else foregrounds
        )
        self.background = (
            np.zeros(
                (height, width),
                dtype=np.uint32,
            )
            if backgrounds is None
            else backgrounds
        )
        self.alpha = (
            np.zeros(
                (height, width),
                dtype=np.uint8,
            )
            if alphas is None
            else alphas
        )

    @classmethod
    def from_picture(cls, picture: Picture) -> Self:
        """Return instance of this class from Picture object."""
        return cls(
            picture.width,
            picture.height,
            picture.symbol,
            picture.foreground,
            picture.background,
            picture.alpha,
        )

    def __repr__(self) -> str:
        """Return representation of self."""
        return f"<{self.__class__.__name__}({self.width}, {self.height})>"

    def set(
        self,
        x: int,
        y: int,
        symbol: str,
        foreground: np.uint32,
        background: np.uint32,
        alpha: np.uint8,
    ) -> None:
        """Set values for pixel."""
        self.symbol[y, x] = symbol
        self.foreground[y, x] = foreground
        self.background[y, x] = background
        self.alpha[y, x] = alpha

    def get(
        self,
        x: int,
        y: int,
    ) -> tuple[str, np.uint32, np.uint32, np.uint8]:
        """Return (symbol, foreground, background, alpha)."""
        return (
            self.symbol[y, x],
            self.foreground[y, x],
            self.background[y, x],
            self.alpha[y, x],
        )

    def __iter__(self) -> Generator[str, None, None]:
        """Yield symbols."""
        for y in range(self.height):
            for x in range(self.width):
                yield self.get(x, y)[0]
            yield "\n"


def bytearr_to_int(arr: bytearray) -> int:
    """Convert bytearray to int."""
    return int.from_bytes(arr)


def int_to_bytearr(number: int, _size: int) -> bytearray:
    """Encode int as bytearray."""
    return bytearray(number.to_bytes(_size))


def read_utf8(file: io.IOBase, count: int) -> str:
    """Read `count` UTF-8 bytes from file `f`, return as unicode."""
    # Assumes UTF-8 data is valid; leaves it up to the `.decode()`
    # call to validate
    res = []
    while count:
        count -= 1
        lead = file.read(1)
        res.append(lead)

        value = ord(lead)
        if 0xBF < value < 0xF5:
            read_count = 1 + (value >= 0xE0) + (value >= 0xF0)
            res.append(file.read(read_count))
    return (b"".join(res)).decode("utf8")


def load_five(file: io.IOBase) -> Picture:
    """Load OCIF version five file."""
    width = int.from_bytes(file.read(1))
    height = int.from_bytes(file.read(1))

    picture = Picture(width, height)

    for current_y in range(height):
        for current_x in range(width):
            current_background = np.uint32(
                color.to_24_bit(int.from_bytes(file.read(1))),
            )
            current_foreground = np.uint32(
                color.to_24_bit(int.from_bytes(file.read(1))),
            )
            current_alpha = np.uint8(int.from_bytes(file.read(1)))
            current_symbol = read_utf8(file, 1)
            picture.set(
                x=current_x,
                y=current_y,
                symbol=current_symbol,
                foreground=current_foreground,
                background=current_background,
                alpha=current_alpha,
            )
    return picture


def load_grouped(method: int, file: io.IOBase) -> Picture:
    """Load grouped ocif file."""
    seven = 1 if method >= 7 else 0
    eight = 1 if method >= 8 else 0

    width = int.from_bytes(file.read(1)) + eight
    height = int.from_bytes(file.read(1)) + eight

    picture = Picture(width, height)

    alpha_size = int.from_bytes(file.read(1)) + seven

    for _alpha in range(alpha_size):
        current_alpha = np.uint8(int.from_bytes(file.read(1)))  # / 255

        symbol_size = int.from_bytes(file.read(2)) + seven

        for _symbol in range(symbol_size):
            current_symbol = read_utf8(file, 1)

            background_size = int.from_bytes(file.read(1))

            for _background in range(background_size + seven):
                current_background = np.uint32(
                    color.to_24_bit(
                        int.from_bytes(file.read(1)),
                    ),
                )
                foreground_size = int.from_bytes(file.read(1))

                for _foreground in range(foreground_size + seven):
                    current_foreground = np.uint32(
                        color.to_24_bit(
                            int.from_bytes(file.read(1)),
                        ),
                    )
                    y_size = int.from_bytes(file.read(1))

                    for _y in range(y_size + seven):
                        current_y = int.from_bytes(file.read(1)) + eight
                        x_size = int.from_bytes(file.read(1))

                        for _x in range(x_size + seven):
                            current_x = int.from_bytes(file.read(1)) + eight

                            picture.set(
                                x=current_x - 1,
                                y=current_y - 1,
                                symbol=current_symbol,
                                foreground=current_foreground,
                                background=current_background,
                                alpha=current_alpha,
                            )
    return picture


def load(filename: str) -> Picture:
    """Load picture from file."""
    with open(filename, "rb") as file:
        magic = file.read(4)
        if magic != b"OCIF":
            raise OSError("File header is invalid for OCIF image")
        method = int.from_bytes(file.read(1))
        print(f"{method = }")
        if method > 5:
            return load_grouped(method, file)
        if method == 5:
            return load_five(file)
        raise NotImplementedError(f"OCIF method {method!r}")


def run() -> None:
    """Run."""
    picture = load("Pictures/AhsokaTano.pic")
    print(picture)
    print("".join(picture))


if __name__ == "__main__":
    run()
