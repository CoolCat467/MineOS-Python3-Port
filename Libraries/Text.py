#!/usr/bin/env python3
# TITLE DESCRIPTION
# -*- coding: utf-8 -*-

from math import inf, modf


def serialize(
    table,
    prettyLook=False,
    indentator="  ",
    recursionStackLimit=inf,
):
    equalsSymbol = prettyLook and " = " or "="

    def serialize_(t, currentIndentationSymbol, currentRecursionStack):
        result = ""
        nextIndentationSymbol = currentIndentationSymbol + indentator

        if prettyLook:
            result += "\n"

        for key, value in ((k, t[k]) for k in t):
            if prettyLook:
                result += nextIndentationSymbol

            if isinstance(key, (int, float)):
                result += f"[{key}]{equalsSymbol}"
            elif isinstance(key, str):
                # In short, if the type begins with a letter, as well as if it is an alphanumeric work
                if prettyLook and key.isascii() and key.isalnum():
                    result += key
                else:
                    result += f'["{key}"]'

                result += equalsSymbol

            if isinstance(value, (int, float, bool, type(None))):
                result += str(value)
            elif isinstance(value, (str, type(lambda x: None))):
                result += f'"{value!s}"'
            elif isinstance(value, dict):
                if currentRecursionStack < recursionStackLimit:
                    result += "".join(
                        serialize_(
                            value,
                            nextIndentationSymbol,
                            currentRecursionStack + 1,
                        ),
                    )
                else:
                    result += '"…"'  # ..."'

            result += ","

            if prettyLook:
                result += "\n"
        # Remove the comma
        if prettyLook:
            if len(result) > 2:
                result = result[:-2]
            result += currentIndentationSymbol
        elif len(result) > 1:
            result = result[:-1]

        result += "}"

        return result

    return "".join(serialize_(table, "", 0))


def deserialize(string):
    return dict


def brailleChar(a, b, c, d, e, f, g, h):
    return chr(
        10240 + 128 * h + 64 * g + 32 * f + 16 * d + 8 * b + 4 * e + 2 * c + a,
    )


def unicodeFind(string, pattern, init, plain):
    if init is not None:
        if init < 0:
            init = -len(string[init:])
        elif init > 0:
            init = len(string[:init]) + 1

    a = string.find(pattern, init, plain)
    b = len(string) - a + len(pattern)

    if a != -1:
        ap, bp = string[: a - 1], string[a:b]
        a = len(ap)
        b = a + len(bp)

        return a, b
    else:
        return a, None


def limit(string, limit, mode=None, noDots=False):
    length = len(string)

    if length <= limit:
        return string
    elif mode == "left":
        if noDots:
            return string[length - limit :]
        else:
            return "…" + string[length - limit + 1 :]
    elif mode == "center":
        # Python's modf has the numbers flipped
        fractional, integer = modf(limit / 2)
        integer = int(integer)
        if fractional == 0:
            return string[:integer] + "…" + string[-integer + 1 :]
        return string[:integer] + "…" + string[-integer:]
    if noDots:
        return string[:limit]
    else:
        return string[: limit - 1] + "…"


def wrap(data, limit):
    if isinstance(data, str):
        data = [data]

    wrappedLines = {}

    # Duplicate the table of rows, so as not to skew to carry transfers
    for i in range(len(data)):
        wrappedLines[i] = data[i]

    # Trim carriage return
    i = 0
    while i < len(wrappedLines) - 1:
        position = wrappedLines[i].find("\n")
        if position != -1:
            ##            wrappedLines[i+1] += wrappedLines[i][position:]
            wrappedLines[i] = wrappedLines[i][:position]

        i += 1

    # The transfer itself
    i = 0
    while i < len(wrappedLines) - 1:
        result = ""

        for word in wrappedLines[i].split():
            preResult = result + word

            if len(preResult) > limit:
                if len(word) > limit:
                    ##                    wrappedLines[i+1] += wrappedLines[i][limit+1:]
                    result = wrappedLines[:limit]
                ##                else:
                ##                    wrappedLines[i+1] += wrappedLines[i][len(result):]
                break
            else:
                result = preResult + " "

        wrappedLines[i] = result  # .replace('$', '').replace('', '')

        i += 1
    return list(wrappedLines.values())
