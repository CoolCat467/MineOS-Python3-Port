"""Library for color manipulations.

It allows you to extrude and pack color channels, convert
the RGB color model to HSB and vice versa, perform alpha blending,
generate color transitions and convert the color to 8-bit format for
the OpenComputers PALETTE.
"""

from __future__ import annotations

from functools import cache, lru_cache
from math import floor, inf, modf

__all__ = [
    "blend",
    "hsb_to_integer",
    "hsb_to_rgb",
    "integer_to_hsb",
    "integer_to_rgb",
    "optimize",
    "rgb_to_hsb",
    "rgb_to_integer",
    "to_8_bit",
    "to_24_bit",
    "transition",
]


# fmt: off
PALETTE = (
    0x000000, 0x000040, 0x000080, 0x0000BF, 0x0000FF, 0x002400, 0x002440, 0x002480,
    0x0024BF, 0x0024FF, 0x004900, 0x004940, 0x004980, 0x0049BF, 0x0049FF, 0x006D00,
    0x006D40, 0x006D80, 0x006DBF, 0x006DFF, 0x009200, 0x009240, 0x009280, 0x0092BF,
    0x0092FF, 0x00B600, 0x00B640, 0x00B680, 0x00B6BF, 0x00B6FF, 0x00DB00, 0x00DB40,
    0x00DB80, 0x00DBBF, 0x00DBFF, 0x00FF00, 0x00FF40, 0x00FF80, 0x00FFBF, 0x00FFFF,
    0x0F0F0F, 0x1E1E1E, 0x2D2D2D, 0x330000, 0x330040, 0x330080, 0x3300BF, 0x3300FF,
    0x332400, 0x332440, 0x332480, 0x3324BF, 0x3324FF, 0x334900, 0x334940, 0x334980,
    0x3349BF, 0x3349FF, 0x336D00, 0x336D40, 0x336D80, 0x336DBF, 0x336DFF, 0x339200,
    0x339240, 0x339280, 0x3392BF, 0x3392FF, 0x33B600, 0x33B640, 0x33B680, 0x33B6BF,
    0x33B6FF, 0x33DB00, 0x33DB40, 0x33DB80, 0x33DBBF, 0x33DBFF, 0x33FF00, 0x33FF40,
    0x33FF80, 0x33FFBF, 0x33FFFF, 0x3C3C3C, 0x4B4B4B, 0x5A5A5A, 0x660000, 0x660040,
    0x660080, 0x6600BF, 0x6600FF, 0x662400, 0x662440, 0x662480, 0x6624BF, 0x6624FF,
    0x664900, 0x664940, 0x664980, 0x6649BF, 0x6649FF, 0x666D00, 0x666D40, 0x666D80,
    0x666DBF, 0x666DFF, 0x669200, 0x669240, 0x669280, 0x6692BF, 0x6692FF, 0x66B600,
    0x66B640, 0x66B680, 0x66B6BF, 0x66B6FF, 0x66DB00, 0x66DB40, 0x66DB80, 0x66DBBF,
    0x66DBFF, 0x66FF00, 0x66FF40, 0x66FF80, 0x66FFBF, 0x66FFFF, 0x696969, 0x787878,
    0x878787, 0x969696, 0x990000, 0x990040, 0x990080, 0x9900BF, 0x9900FF, 0x992400,
    0x992440, 0x992480, 0x9924BF, 0x9924FF, 0x994900, 0x994940, 0x994980, 0x9949BF,
    0x9949FF, 0x996D00, 0x996D40, 0x996D80, 0x996DBF, 0x996DFF, 0x999200, 0x999240,
    0x999280, 0x9992BF, 0x9992FF, 0x99B600, 0x99B640, 0x99B680, 0x99B6BF, 0x99B6FF,
    0x99DB00, 0x99DB40, 0x99DB80, 0x99DBBF, 0x99DBFF, 0x99FF00, 0x99FF40, 0x99FF80,
    0x99FFBF, 0x99FFFF, 0xA5A5A5, 0xB4B4B4, 0xC3C3C3, 0xCC0000, 0xCC0040, 0xCC0080,
    0xCC00BF, 0xCC00FF, 0xCC2400, 0xCC2440, 0xCC2480, 0xCC24BF, 0xCC24FF, 0xCC4900,
    0xCC4940, 0xCC4980, 0xCC49BF, 0xCC49FF, 0xCC6D00, 0xCC6D40, 0xCC6D80, 0xCC6DBF,
    0xCC6DFF, 0xCC9200, 0xCC9240, 0xCC9280, 0xCC92BF, 0xCC92FF, 0xCCB600, 0xCCB640,
    0xCCB680, 0xCCB6BF, 0xCCB6FF, 0xCCDB00, 0xCCDB40, 0xCCDB80, 0xCCDBBF, 0xCCDBFF,
    0xCCFF00, 0xCCFF40, 0xCCFF80, 0xCCFFBF, 0xCCFFFF, 0xD2D2D2, 0xE1E1E1, 0xF0F0F0,
    0xFF0000, 0xFF0040, 0xFF0080, 0xFF00BF, 0xFF00FF, 0xFF2400, 0xFF2440, 0xFF2480,
    0xFF24BF, 0xFF24FF, 0xFF4900, 0xFF4940, 0xFF4980, 0xFF49BF, 0xFF49FF, 0xFF6D00,
    0xFF6D40, 0xFF6D80, 0xFF6DBF, 0xFF6DFF, 0xFF9200, 0xFF9240, 0xFF9280, 0xFF92BF,
    0xFF92FF, 0xFFB600, 0xFFB640, 0xFFB680, 0xFFB6BF, 0xFFB6FF, 0xFFDB00, 0xFFDB40,
    0xFFDB80, 0xFFDBBF, 0xFFDBFF, 0xFFFF00, 0xFFFF40, 0xFFFF80, 0xFFFFBF, 0xFFFFFF,
)
# fmt: on


def rgb_to_integer(r: int, g: int, b: int) -> int:
    """Packs three color channels and returns a 24-bit color."""
    return r << 16 | g << 8 | b


def integer_to_rgb(color: int) -> tuple[int, int, int]:
    """Extrudes three color channels from a 24-bit color."""
    return color >> 16, color >> 8 & 0xFF, color & 0xFF


def blend(color1: int, color2: int, transparency: float) -> int:
    """Mixes two 24 bit colors considering the transparency of the second color."""
    inverted_transparency = 1 - transparency
    r = (
        int(
            (
                (color2 >> 16) * inverted_transparency
                + (color1 >> 16) * transparency
            )
            // 1,
        )
        << 16
    )
    g = (
        int(
            (
                (color2 >> 8 & 0xFF) * inverted_transparency
                + (color1 >> 8 & 0xFF) * transparency
            )
            // 1,
        )
        << 8
    )
    b = int(
        (
            (color2 & 0xFF) * inverted_transparency
            + (color1 & 0xFF) * transparency
        )
        // 1,
    )
    return r | g | b


def transition(color1: int, color2: int, position: float) -> int:
    """Generate a transitive color between first and second ones, based on the transition argument, where the value 0.0 is equivalent to the first color, and 1.0 is the second color."""
    r1, g1, b1 = color1 >> 16, color1 >> 8 & 0xFF, color1 & 0xFF
    r2, g2, b2 = color2 >> 16, color2 >> 8 & 0xFF, color2 & 0xFF
    r = int(r1 + ((r2 - r1) * position) // 1) << 16
    g = int(g1 + ((g2 - g1) * position) // 1) << 8
    b = int(b1 + ((b2 - b1) * position) // 1)
    return r | g | b


@cache
def to_8_bit(color_24_bit: int) -> int:
    """Look at 256-color OpenComputers PALETTE and return the color index that most accurately matches given value using the same search method as in gpu.setBackground(value) does."""
    r, g, b = color_24_bit >> 16, color_24_bit >> 8 & 0xFF, color_24_bit & 0xFF
    closest_delta, closest_index = inf, 1
    # Moved outside of loop from original
    # See if 24 bit color perfectly matches a PALETTE color
    if color_24_bit in PALETTE[1:]:
        # If there is an entry of 24 bit color in PALETTE, return index minus 1 because we skip first entry.
        return PALETTE.index(color_24_bit) - 1
    # We ignore first one, so we need to shift PALETTE indexing by one
    for i in range(1, len(PALETTE) - 1):
        palette_color = PALETTE[i]

        p_r, p_g, p_b = (
            palette_color >> 16,
            palette_color >> 8 & 0xFF,
            palette_color & 0xFF,
        )

        delta = (p_r - r) ** 2 + (p_g - g) ** 2 + (p_b - b) ** 2
        if delta < closest_delta:
            closest_delta, closest_index = delta, i
    return closest_index - 1


def to_24_bit(color_8_bit: int) -> int:
    """Convert the 8-bit index created by the color.to_8_bit method to 24-bit color value."""
    return PALETTE[color_8_bit]


def rgb_to_hsb(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert three color channels of the RGB color model to the HSB color model and returns the corresponding result."""
    maxv, minv = max(r, g, b), min(r, g, b)

    if maxv == minv:
        return 0, (maxv == 0 and 0) or (1 - minv / maxv), maxv / 255
    if maxv == r and g >= b:
        return (
            60 * (g - b) / (maxv - minv),
            (maxv == 0 and 0) or (1 - minv / maxv),
            maxv / 255,
        )
    if maxv == r and g < b:
        return (
            60 * (g - b) / (maxv - minv) + 360,
            (maxv == 0 and 0) or (1 - minv / maxv),
            maxv / 255,
        )
    if maxv == g:
        return (
            60 * (b - r) / (maxv - minv) + 120,
            (maxv == 0 and 0) or (1 - minv / maxv),
            maxv / 255,
        )
    if maxv == b:
        return (
            60 * (r - g) / (maxv - minv) + 240,
            (maxv == 0 and 0) or (1 - minv / maxv),
            maxv / 255,
        )
    return 0, (maxv == 0 and 0) or (1 - minv / maxv), maxv / 255


def hsb_to_rgb(h: float, s: float, b: float) -> tuple[int, int, int]:
    """Convert the parameters of the HSB color model into three color channels of the RGB model and returns the corresponding result."""
    fractional, integer = modf(h / 60)
    p = b * (1 - s)
    q = b * (1 - s * fractional)
    t = b * (1 - (1 - fractional) * s)

    if integer == 0:
        return floor(b * 255), floor(t * 255), floor(p * 255)
    if integer == 1:
        return floor(q * 255), floor(b * 255), floor(p * 255)
    if integer == 2:
        return floor(p * 255), floor(b * 255), floor(t * 255)
    if integer == 3:
        return floor(p * 255), floor(q * 255), floor(b * 255)
    if integer == 4:
        return floor(t * 255), floor(p * 255), floor(b * 255)
    return floor(b * 255), floor(p * 255), floor(q * 255)


def integer_to_hsb(color: int) -> tuple[float, float, float]:
    """Convert an integer to an RGB value and then that into a HSB value."""
    return rgb_to_hsb(*integer_to_rgb(color))


def hsb_to_integer(h: int, s: int, b: int) -> int:
    """Convert an HSB value into an RGB value and that into an integer value."""
    return rgb_to_integer(*hsb_to_rgb(h, s, b))


@lru_cache
def optimize(color_24_bit: int) -> int:
    """Get a close approximation from the OC Color Palette of given 24 bit color."""
    return to_24_bit(to_8_bit(color_24_bit))
