#!/usr/bin/env python3
# Bitwise functions for 32 bit numbers.
# -*- coding: utf-8 -*-

__all__ = [
    "arshift",
    "band",
    "bnot",
    "bor",
    "btest",
    "bxor",
    "extract",
    "replace",
    "lshift",
    "rshift",
    "rrotate",
    "lrotate",
]


def fold(init, op, *args):
    """Apply operator function op on all arguments and return sum result. Very strange and confusing."""
    result = init
    for arg in args:
        result = op(result, arg)
    return result


def trim(n):
    """Return the bitwise and of n and 0xffffffff."""
    return n & 0xFFFFFFFF


def mask(w):
    """Return the inverse (~) of 0xffffffff bitshifted to the right by w."""
    return ~(0xFFFFFFFF << w)


def arshift(x, disp):
    """Return x floor div (//) of two to the power of <disp>."""
    return x // (2**disp)


def band(*args):
    """Return the combined bitwise and of all arguments and 0xffffffff."""
    res = 0xFFFFFFFF
    for arg in args:
        res &= arg
    return res


def bnot(x):
    """Return the bitwise inverse (~) of x."""
    return ~x


def bor(*args):
    """Return the bitwise or of all arguments."""
    res = 0
    for arg in args:
        res |= arg
    return res


def btest(*args):
    """Return if bitwise and of all arguments is not equal to zero."""
    # Lua ~= is apparently negation of equality, or != in Python.
    return band(*args) != 0


def bxor(*args):
    """Return the bitwise xor of all arguments."""
    res = 0
    for arg in args:
        res ^= arg
    return res


def fieldargs(field, width):
    """Ensure that the arguments of a function cannot go out of bounds."""
    w = width or 1
    assert field >= 0, "Field cannot be negative."
    assert w > 0, "Width must be positive."
    assert field + w <= 32, "Bits accessed exceed 32."
    return field, w


def extract(n, field, width):
    """Perform n bitwise shifted right by field, bitwise anded with a mask of width."""
    f, w = fieldargs(field, width)
    return (n >> f) & mask(w)


def replace(n, v, field, width):
    """Perform n bitwise anded with the inverse of mask of width rightsifted by field, bitwise ored with the bitwise and of v and a mask of width rightshifted by field.
    (n & ~(mask(width) << f)) | ((v & mask(width)) << f).
    """
    f, w = fieldargs(field, width)
    m = mask(w)
    return (n & ~(m << f)) | ((v & m) << f)


def lshift(x, disp):
    """Return x leftshifted by disp trimmed to 32 bits."""
    return trim(x << disp)


def rshift(x, disp):
    """Return x rightshifted by disp trimmed to 32 bits."""
    return trim(x >> disp)


def rrotate(x, disp):
    """Rotate x's bits to the right by disp."""
    if disp == 0:
        return x
    elif disp < 0:
        return lrotate(x, -disp)
    disp &= 31
    x = trim(x)
    return trim((x >> disp) | (x << (32 - disp)))


def lrotate(x, disp):
    """Rotate x's bits to the left by disp."""
    if disp == 0:
        return x
    elif disp < 0:
        return rrotate(x, -disp)
    disp &= 31
    x = trim(x)
    return trim((x << disp) | (x >> (32 - disp)))
