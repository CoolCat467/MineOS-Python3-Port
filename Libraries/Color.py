#!/usr/bin/env python3
# This library is made for color manipulations. It allows you to extrude and pack color channels, convert the RGB color model to HSB and vice versa, perform alpha blending, generate color transitions and convert the color to 8-bit format for the OpenComputers palette.
# -*- coding: utf-8 -*-

from math import floor, inf, modf
from functools import cache, lru_cache

__all__ = ['RGBToInteger', 'integerToRGB', 'RGBToHSB',
           'HSBToRGB', 'integerToHSB', 'HSBToInteger',
           'blend', 'transition', 'to8Bit', 'to24Bit',
           'optimize']
DOCACHE = True

##def _cacheResults(function):
##    """Decorator to cache results for functions that when given arguments return constant results."""
##    def argsToStr(x):
##        return '-'.join((str(i) for i in x))
##    def kwargsToStr(x):
##        return ';'.join((str(k)+'='+str(x[k]) for k in x))
##    cache = {}
##    @wraps(function)
##    def withCache(*args, **kwargs):
##        if DOCACHE:
##            argstr = argsToStr(args)+'/'+kwargsToStr(kwargs)
##            if not argstr in cache:
##                cache[argstr] = function(*args, **kwargs)
##            return cache[argstr]
##        return function(*args, **kwargs)
##    return withCache

##mathHuge = 2**1024 - 1
def mathModf(x):
    """Fix python math.modf ordering for lua code port."""
    fractional, intiger = modf(x)
    return intiger, fractional

palette = (0x000000, 0x000040, 0x000080, 0x0000bf, 0x0000ff, 0x002400,
           0x002440, 0x002480, 0x0024bf, 0x0024ff, 0x004900, 0x004940,
           0x004980, 0x0049bf, 0x0049ff, 0x006d00, 0x006d40, 0x006d80,
           0x006dbf, 0x006dff, 0x009200, 0x009240, 0x009280, 0x0092bf,
           0x0092ff, 0x00b600, 0x00b640, 0x00b680, 0x00b6bf, 0x00b6ff,
           0x00db00, 0x00db40, 0x00db80, 0x00dbbf, 0x00dbff, 0x00ff00,
           0x00ff40, 0x00ff80, 0x00ffbf, 0x00ffff, 0x0f0f0f, 0x1e1e1e,
           0x2d2d2d, 0x330000, 0x330040, 0x330080, 0x3300bf, 0x3300ff,
           0x332400, 0x332440, 0x332480, 0x3324bf, 0x3324ff, 0x334900,
           0x334940, 0x334980, 0x3349bf, 0x3349ff, 0x336d00, 0x336d40,
           0x336d80, 0x336dbf, 0x336dff, 0x339200, 0x339240, 0x339280,
           0x3392bf, 0x3392ff, 0x33b600, 0x33b640, 0x33b680, 0x33b6bf,
           0x33b6ff, 0x33db00, 0x33db40, 0x33db80, 0x33dbbf, 0x33dbff,
           0x33ff00, 0x33ff40, 0x33ff80, 0x33ffbf, 0x33ffff, 0x3c3c3c,
           0x4b4b4b, 0x5a5a5a, 0x660000, 0x660040, 0x660080, 0x6600bf,
           0x6600ff, 0x662400, 0x662440, 0x662480, 0x6624bf, 0x6624ff,
           0x664900, 0x664940, 0x664980, 0x6649bf, 0x6649ff, 0x666d00,
           0x666d40, 0x666d80, 0x666dbf, 0x666dff, 0x669200, 0x669240,
           0x669280, 0x6692bf, 0x6692ff, 0x66b600, 0x66b640, 0x66b680,
           0x66b6bf, 0x66b6ff, 0x66db00, 0x66db40, 0x66db80, 0x66dbbf,
           0x66dbff, 0x66ff00, 0x66ff40, 0x66ff80, 0x66ffbf, 0x66ffff,
           0x696969, 0x787878, 0x878787, 0x969696, 0x990000, 0x990040,
           0x990080, 0x9900bf, 0x9900ff, 0x992400, 0x992440, 0x992480,
           0x9924bf, 0x9924ff, 0x994900, 0x994940, 0x994980, 0x9949bf,
           0x9949ff, 0x996d00, 0x996d40, 0x996d80, 0x996dbf, 0x996dff,
           0x999200, 0x999240, 0x999280, 0x9992bf, 0x9992ff, 0x99b600,
           0x99b640, 0x99b680, 0x99b6bf, 0x99b6ff, 0x99db00, 0x99db40,
           0x99db80, 0x99dbbf, 0x99dbff, 0x99ff00, 0x99ff40, 0x99ff80,
           0x99ffbf, 0x99ffff, 0xa5a5a5, 0xb4b4b4, 0xc3c3c3, 0xcc0000,
           0xcc0040, 0xcc0080, 0xcc00bf, 0xcc00ff, 0xcc2400, 0xcc2440,
           0xcc2480, 0xcc24bf, 0xcc24ff, 0xcc4900, 0xcc4940, 0xcc4980,
           0xcc49bf, 0xcc49ff, 0xcc6d00, 0xcc6d40, 0xcc6d80, 0xcc6dbf,
           0xcc6dff, 0xcc9200, 0xcc9240, 0xcc9280, 0xcc92bf, 0xcc92ff,
           0xccb600, 0xccb640, 0xccb680, 0xccb6bf, 0xccb6ff, 0xccdb00,
           0xccdb40, 0xccdb80, 0xccdbbf, 0xccdbff, 0xccff00, 0xccff40,
           0xccff80, 0xccffbf, 0xccffff, 0xd2d2d2, 0xe1e1e1, 0xf0f0f0,
           0xff0000, 0xff0040, 0xff0080, 0xff00bf, 0xff00ff, 0xff2400,
           0xff2440, 0xff2480, 0xff24bf, 0xff24ff, 0xff4900, 0xff4940,
           0xff4980, 0xff49bf, 0xff49ff, 0xff6d00, 0xff6d40, 0xff6d80,
           0xff6dbf, 0xff6dff, 0xff9200, 0xff9240, 0xff9280, 0xff92bf,
           0xff92ff, 0xffb600, 0xffb640, 0xffb680, 0xffb6bf, 0xffb6ff,
           0xffdb00, 0xffdb40, 0xffdb80, 0xffdbbf, 0xffdbff, 0xffff00,
           0xffff40, 0xffff80, 0xffffbf, 0xffffff)

# Note: Only implemented the more efficiant versions, as python has had
# binary support for a pretty long time now.

def RGBToInteger(r, g, b):
    """Packs three color channels and returns a 24-bit color."""
    return r << 16 | g << 8 | b

def integerToRGB(integerColor):
    """Extrudes three color channels from a 24-bit color."""
    return integerColor >> 16, integerColor >> 8 & 0xff, integerColor & 0xff

def blend(color1, color2, transparency):
    """Mixes two 24 bit colors considering the transparency of the second color."""
    invertedTransparency = 1 - transparency
    r = int(((color2 >> 16) * invertedTransparency + (color1 >> 16) * transparency) // 1) << 16
    g = int(((color2 >> 8 & 0xff) * invertedTransparency + (color1 >> 8 & 0xff) * transparency) // 1) << 8
    b = int(((color2 & 0xff) * invertedTransparency + (color1 & 0xff) * transparency) // 1)
    return r | g | b

def transition(color1, color2, position):
    """Generates a transitive color between first and second ones, based on the transition argument, where the value 0.0 is equivalent to the first color, and 1.0 is the second color."""
    r1, g1, b1 = color1 >> 16, color1 >> 8 & 0xff, color1 & 0xff
    r2, g2, b2 = color2 >> 16, color2 >> 8 & 0xff, color2 & 0xff
    r = int(r1 + ((r2 - r1) * position) // 1) << 16
    g = int(g1 + ((g2 - g1) * position) // 1) << 8
    b = int(b1 + ((b2 - b1) * position) // 1)
    return r | g | b

@cache
def to8Bit(color24Bit):
    """Looks to 256-color OpenComputers palette and returns the color index that most accurately matches given value using the same search method as in gpu.setBackground(value) do."""
    r, g, b = color24Bit >> 16, color24Bit >> 8 & 0xff, color24Bit & 0xff
    closestDelta, closestIndex = inf, 1
    # Moved outside of loop from original
    # See if 24 bit color perfectly matches a palette color
    if color24Bit in palette[1:]:
        # If there is an entry of 24 bit color in palette, return index minus 1 because we skip first entry.
        return palette.index(color24Bit) - 1
    # We ignore first one, so we need to shift palette indexing by one
    for i in range(1, len(palette)-1):
        paletteColor = palette[i]
        
##        if color24Bit == paletteColor:
##            # If color perfectly matches palette color, return palette index.
##            return i - 1
        paletteR, paletteG, paletteB = paletteColor >> 16, paletteColor >> 8 & 0xff, paletteColor & 0xff
        
        delta = (paletteR - r) ** 2 + (paletteG - g) ** 2 + (paletteB - b) ** 2
        if delta < closestDelta:
            closestDelta, closestIndex = delta, i
    return closestIndex - 1

def to24Bit(color8Bit):
    """The method allows you to convert the 8-bit index created by the color.to8Bit method to 24-bit color value."""
    # We ignore first one, so we need to shift palette indexing by one
    return palette[color8Bit + 1]

def RGBToHSB(r, g, b):
    """Converts three color channels of the RGB color model to the HSB color model and returns the corresponding result."""
    maxv, minv = max(r, g, b), min(r, g, b)
    
    if maxv == minv:
        return 0, maxv == 0 and 0 or (1 - minv / maxv), maxv / 255
    elif maxv == r and g >= b:
        return 60 * (g - b) / (maxv - minv), maxv == 0 and 0 or (1 - minv / maxv), maxv / 255
    elif maxv == r and g < b:
        return 60 * (g - b) / (maxv - minv) + 360, maxv == 0 and 0 or (1 - minv / maxv), maxv / 255
    elif maxv == g:
        return 60 * (b - r) / (maxv - minv) + 120, maxv == 0 and 0 or (1 - minv / maxv), maxv / 255
    elif maxv == b:
        return 60 * (r - g) / (maxv - minv) + 240, maxv == 0 and 0 or (1 - minv / maxv), maxv / 255
    return 0, maxv == 0 and 0 or (1 - minv / maxv), maxv / 255

def HSBToRGB(h, s, b):
    """Converts the parameters of the HSB color model into three color channels of the RGB model and returns the corresponding result."""
    integer, fractional = mathModf(h / 60)
    p, q, t = b * (1 - s), b * (1 - s * fractional), b * (1 - (1 - fractional) * s)
    
    if integer == 0:
        return floor(b * 255), floor(t * 255), floor(p * 255)
    elif integer == 1:
        return floor(q * 255), floor(b * 255), floor(p * 255)
    elif integer == 2:
        return floor(p * 255), floor(b * 255), floor(t * 255)
    elif integer == 3:
        return floor(p * 255), floor(q * 255), floor(b * 255)
    elif integer == 4:
        return floor(t * 255), floor(p * 255), floor(b * 255)
    return floor(b * 255), floor(p * 255), floor(q * 255)

def integerToHSB(integerColor):
    """Convert an integer to an RGB value and then that into a HSB value."""
    return RGBToHSB(integerToRGB(integerColor))

def HSBToInteger(h, s, b):
    """Convert an HSB value into an RGB value and that into an integer value."""
    return RGBToInteger(HSBToRGB(h, s, b))

@lru_cache
def optimize(color24Bit):
    """Get a close approximation from the OC Color Palette of given 24 bit color."""
    return to24Bit(to8Bit(color24Bit))
