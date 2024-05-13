#!/usr/bin/env python3
# This library is made for Image manipulations
# -*- coding: utf-8 -*-

# load('/MineOS/Pictures/AhsokaTano.pic')

import math
import random

import Bit32 as bit32
import Color as color
import computer
import Filesystem as filesystem

__all__ = [
    "blend",
    "copy",
    "create",
    "crop",
    "encodingMethodsLoad",
    "encodingMethodsSave",
    "expand",
    "flipHorizontally",
    "flipVertically",
    "fromString",
    "get",
    "getHeight",
    "getIndex",
    "getSize",
    "getWidth",
    "group",
    "load",
    "save",
    "set",
    "toString",
    "transform",
]

OCIFSignature = "OCIF"
encodingMethodsLoad = {}
encodingMethodsSave = {}


class Picture:
    def __init__(self, data):
        self.data = data

    ##        if (len(self.data)-2) % 4 > 0:
    ##            raise TypeError('Image data is invalid!')

    def __str__(self):
        return self.getStr()

    def getStr(self):
        w, h = getSize(self.data)
        ##        for bg, fg, al, ch in self.data[2:]:
        ##            print(ch)
        ##            chars.append(ch)
        pixels = len(self.data) // 4
        realh = pixels // w
        ##        print(w, h)
        print(w, realh)
        chars = []
        for y in range(1, realh + 1):
            for x in range(1, w + 1):
                try:
                    data = get(self.data, x, y)[3]
                    ##                    if not isinstance(data, str):
                    ##                        raise ValueError
                    chars.append(data)
                ##                    chars.append(self.data[(4 * ((y * w) + x) + 2) + 3])
                except BaseException:
                    ##                    chars.append('�')
                    chars.append(" ")
        ##        chars = [self.data[2+i*4+3] for i in range(pixels)]
        # (len(self.data)-2) // w-4
        lines = ["".join(chars[i * w : (i + 1) * w]) for i in range(realh)]
        ##        chars = [''.join(chars[i*w:(i+1)*w]) for i in range()]
        return "\n".join(lines)

    def __repr__(self):
        return self.getStr()


##def readOutput(output):
##    "Return True, output, None if output does not have error reason, and False, output, reason if it does."
##    try:
##


def group(picture, compressColors=False):
    """Simplify a picture into a gigantic table."""
    groupedPicture = {}
    x, y = 1, 1
    ##    print((2, len(picture), 4))

    for i in range(2, len(picture), 4):
        if compressColors:
            background, foreground = color.to8Bit(picture[i]), color.to8Bit(
                picture[i + 1],
            )
            ##            # Skipping because it's very strange.
            if i % 603 == 0:
                # Handle signals for zero seconds? What?
                # If it's computer's pullSignal, we are making event
                # module not process signals. Interesting.
                computer.pullSignal(0)
        else:
            background, foreground = picture[i], picture[i + 1]
        alpha, char = picture[i + 2], picture[i + 3]

        if alpha not in groupedPicture:
            groupedPicture[alpha] = {}
        if char not in groupedPicture[alpha]:
            groupedPicture[alpha][char] = {}
        if background not in groupedPicture[alpha][char]:
            groupedPicture[alpha][char][background] = {}
        if foreground not in groupedPicture[alpha][char][background]:
            groupedPicture[alpha][char][background][foreground] = {}
        if y not in groupedPicture[alpha][char][background][foreground]:
            groupedPicture[alpha][char][background][foreground][y] = []

        groupedPicture[alpha][char][background][foreground][y].append(x)

        x += 1
        if x > picture[0]:
            x = 1
            y += 1
    return groupedPicture


def encMethodSave5(file, picture):
    """Save an picture to a file."""
    file.writeBytes(bit32.rshift(picture[0], 8), bit32.band(picture[1], 0xFF))

    for i in range(2, len(picture), 4):
        file.writeBytes(
            color.to8Bit(picture[i]),
            color.to8Bit(picture[i + 1]),
            math.floor(picture[i + 2] * 255),
        )

        file.write(picture[i + 3])
    return True, None


encodingMethodsSave[5] = encMethodSave5


def encMethodLoad5(file, picture):
    """Load a picture from a file."""
    picture[0] = file.readBytes(2)
    picture[1] = file.readBytes(2)

    for i in range(math.ceil(getWidth(picture) * picture[1])):
        picture[i] = color.to24Bit(file.readBytes(1))
        picture[i + 1] = color.to24Bit(file.readBytes(1))
        picture[i + 2] = file.readBytes(1) / 255
        picture[i + 3] = file.readUnicodeChar()
    return None, None


encodingMethodsLoad[5] = encMethodLoad5


def encMethodSave6(file, picture):
    """Save groups of the same objects."""
    # Grouping an image by it's alphas, symbols, and colors
    groupedPicture = group(picture, True)

    # Write 2 bytes for image width and height
    file.writeBytes(picture[0], picture[1])

    # Write one byte for alphas array size
    file.writeBytes(len(groupedPicture))

    for alpha in groupedPicture:
        symbolsSize = len(groupedPicture[alpha])

        # Write one byte for alpha value
        # Write two bytes for symbols array size
        file.writeBytes(
            math.floor(alpha * 255),
            bit32.rshift(symbolsSize, 8),
            bit32.band(symbolsSize, 0xFF),
        )

        for symbol in groupedPicture[alpha]:
            # Write current unicode symbol value
            file.write(symbol)
            # Write one byte for backgrounds array size
            file.writeBytes(len(groupedPicture[alpha][symbol]))

            for background in groupedPicture[alpha][symbol]:
                # Write one byte for background color value (compressed by color)
                # Write one byte for foregrounds array size
                file.writeBytes(
                    background,
                    len(groupedPicture[alpha][symbol][background]),
                )

                for foreground in groupedPicture[alpha][symbol][background]:
                    # Write one byte for foreground color value (compressed by color
                    # Write one byte for y array size
                    file.writeBytes(
                        foreground,
                        len(
                            groupedPicture[alpha][symbol][background][
                                foreground
                            ],
                        ),
                    )

                    for y in groupedPicture[alpha][symbol][background][
                        foreground
                    ]:
                        # Write one byte for current y value
                        # Write one byte for x array size
                        file.writeBytes(
                            y,
                            len(
                                groupedPicture[alpha][symbol][background][
                                    foreground
                                ][y],
                            ),
                        )

                        for x in groupedPicture[alpha][symbol][background][
                            foreground
                        ][y]:
                            file.writeBytes(x)
    return True, None


encodingMethodsSave[6] = encMethodSave6


def encMethodLoad6(file, picture, mode=0):
    """Very efficiant."""
    picture[0] = file.readBytes(1)
    picture[1] = file.readBytes(1)

    alphaSize = file.readBytes(1) + mode

    for alpha in range(alphaSize):
        currentAlpha = file.readBytes(1) / 255
        symbolSize = file.readBytes(2) + mode

        for symbol in range(symbolSize):
            print(symbolSize)
            currentSymbol = file.readUnicodeChar()
            print(currentSymbol)
            backgroundSize = file.readBytes(1)

            for background in range(backgroundSize + mode):
                currentBackground = color.to24Bit(file.readBytes(1))
                foregroundSize = file.readBytes(1)

                for foreground in range(foregroundSize + mode):
                    currentForeground = color.to24Bit(file.readBytes(1))
                    ySize = file.readBytes(1)

                    for y in range(ySize + mode):
                        currently = file.readBytes(1)
                        xSize = file.readBytes(1)

                        for x in range(xSize + mode):
                            currentX = file.readBytes(1)

                            if currentX is None:
                                print(
                                    currentX,
                                    currently,
                                    f"{currentBackground:06x}",
                                    f"{currentForeground:06x}",
                                    currentAlpha,
                                    currentSymbol,
                                )
                                print(
                                    f"{x}/{xSize} {y}/{ySize} {background}/{backgroundSize} {foreground}/{foregroundSize} {alpha}/{alphaSize} {symbol}/{symbolSize}",
                                )
                                return None, None
                            index = getIndex(currentX, currently, picture[0])
                            if index < 2:
                                ##                                print('Low index!')
                                ##                                print(currentX, currently)
                                continue
                            (
                                picture[index],
                                picture[index + 1],
                                picture[index + 2],
                                picture[index + 3],
                            ) = (
                                currentBackground,
                                currentForeground,
                                currentAlpha,
                                currentSymbol,
                            )
    ##                            set_(picture, currentX, currently, currentBackground, currentForeground, currentAlpha, currentSymbol)
    return None, None


encodingMethodsLoad[6] = encMethodLoad6


def getSize(picture):
    """Return the size of a given picture."""
    return picture[0], picture[1]


def getWidth(picture) -> int:
    """Return the width of a given picture."""
    return picture[0]


def getHeight(picture) -> int:
    """Return the height of a given picture."""
    return picture[1]


def getIndex(x: int, y: int, width: int) -> int:
    """Return the internal picture index of a given pixel, given xy position and the width of the image. Indexing starts at 1, 1."""
    # Original
    # return 4 * (width * (y - 1) + x) - 1
    # Fixed python indexing
    return 4 * (width * (y - 1) + x) - 2


##    return 4 * (width * (y - 1) + x) - 1


def set_(picture, x, y, background, foreground, alpha, symbol):
    """Set the data of the pixel at given xy choordinates in a given image."""
    index = getIndex(x, y, picture[0])
    (
        picture[index],
        picture[index + 1],
        picture[index + 2],
        picture[index + 3],
    ) = (
        background,
        foreground,
        alpha,
        symbol,
    )

    return picture


def get(picture, x, y):
    """Return the background, foreground, alpha, and symbol at the pixel at given xy choordinates in given image."""
    index = getIndex(x, y, picture[0])
    return (
        picture[index],
        picture[index + 1],
        picture[index + 2],
        picture[index + 3],
    )


def _pictLstToDict(lst):
    """Convert picture from list to dictionary."""
    return {i: lst[i] for i in range(len(lst))}


def create(
    width=160,
    height=50,
    background=0x0,
    foreground=0x0,
    alpha=0x0,
    symbol=" ",
    random_=False,
):
    """Create a new picture with given arguments."""
    picture = [width, height]

    for _ in range(math.ceil(width * height)):
        if random_:
            picture.append(random.randint(0x0, 0xFFFFFF))
            picture.append(random.randint(0x0, 0xFFFFFF))
        else:
            picture.append(background)
            picture.append(foreground)
        picture.append(alpha)
        if random_:
            picture.append(chr(random.randint(65, 90)))
        else:
            picture.append(symbol)
    return _pictLstToDict(picture)


def copy(picture):
    """Return a copy of given picture."""
    v = list(picture.values())
    return _pictLstToDict(v)


def save(path, picture, encodingMethod=6):
    """Save a given picture to a file at path, using given encoding method."""
    file, reason = filesystem.open(path, "wb")
    if file:
        if encodingMethodsSave[encodingMethod]:
            file.write(OCIFSignature, string.byte(encodingMethod))

            result, reason = encodingMethodsSave[encodingMethod](file, picture)

            file.close()

            if result:
                return True, None
            return False, f"Failed to save OCIF image: {reason}"
        file.close()
        return (
            False,
            f'Failed to save OCIF image: encoding method "{encodingMethod}" is not supported.',
        )
    return False, f"Failed to open file for writing: {reason}"


def load(path):
    """Load an image from given path. Automatically de-compresses."""
    file, reason = filesystem.open(path, "rb")
    if file:
        print(f"Length: {file.proxy.size(path)[0]}")
        readSignature = string.char(file.readString(len(OCIFSignature)))
        if readSignature == OCIFSignature:
            encodingMethod = file.readBytes(1)
            if encodingMethod in encodingMethodsLoad:
                picture = {}
                result, reason = encodingMethodsLoad[encodingMethod](
                    file,
                    picture,
                )

                print(f"End position: {file.position}")

                file.close()

                if reason is None:
                    return picture, None
                return False, f"Failed to load OCIF image: {reason}"
            file.close()
            return (
                False,
                f'Failed to load OCIF image: encoding method "{encodingMethod}" is not supported.',
            )
        file.close()
        return (
            False,
            f'Failed to load OCIF image: binary signature "{readSignature}" is not valid.',
        )
    return False, f'Failed to open file "{path}" for reading: {reason}'


def toString(picture):
    """Convert an image into a string and return the string."""
    charArray = [f"{picture[0]:02X}", f"{picture[1]:02X}"]

    for i in range(2, len(picture), 4):
        charArray.append(f"{color.to8Bit(picture[i]):02X}")
        charArray.append(f"{color.to8Bit(picture[i + 1]):02X}")
        charArray.append(f"{math.floor(picture[i + 2] * 255):02X}")
        charArray.append(picture[i + 3])

        if i % 603 == 0:
            computer.pullSignal(0)

    return "".join(charArray)


def fromString(pictureString):
    """Convert an picture string back into a picture again."""

    def hfstr(string):
        return int("0x" + string.lower(), 16)

    picture = [hfstr(pictureString[0:2]), hfstr(pictureString[2:4])]

    for i in range(4, len(pictureString), 7):
        picture.append(color.to24Bit(hfstr(pictureString[i : i + 2])))
        picture.append(color.to24Bit(hfstr(pictureString[i + 2 : i + 4])))
        picture.append(hfstr(pictureString[i + 4 : i + 6]) / 255)
        picture.append(pictureString[i + 6])

    return _pictLstToDict(picture)


def transform(picture, newWidth: int, newHeight: int):
    """Scale picture to a new size."""
    newPicture = [newWidth, newHeight]
    stepWidth, stepHeight = picture[0] / newWidth, picture[1] / newHeight

    x, y = 1, 1
    for _j in range(1, newHeight + 1):
        for _i in range(1, newWidth + 1):
            bg, fg, al, sy = get(picture, math.floor(x), math.floor(y))
            newPicture.append(bg)
            newPicture.append(fg)
            newPicture.append(al)
            newPicture.append(sy)

            x += stepWidth
        x = 1
        y += stepHeight
    return _pictLstToDict(newPicture)


def crop(picture, fromX, fromY, width, height):
    """Return picture cropped to size width, height, starting at fromX, fromY, returns cropped, None on success, False, Error of failure."""
    # toX, toY = fromX + width - 1, fromY + height - 1
    toX, toY = fromX + width, fromY + height
    if (
        fromX >= 1
        and fromY >= 1
        and toX - 1 <= picture[0]
        and toY - 1 <= picture[1]
    ):
        newPicture = [width, height]

        for y in range(fromY, toY):
            for x in range(fromX, toX):
                bg, fg, al, sy = get(picture, x, y)
                newPicture.append(bg)
                newPicture.append(fg)
                newPicture.append(al)
                newPicture.append(sy)
    else:
        return (
            False,
            "Failed to crop image: target coordinates are out of range.",
        )

    return _pictLstToDict(newPicture), None


def flipHorizontally(picture):
    """Return the picture mirrored on the X axes."""
    newPicture = [picture[0], picture[1]]

    for y in range(1, picture[1] + 1):
        for x in range(picture[0], 0, -1):
            bg, fg, al, sy = get(picture, x, y)
            newPicture.append(bg)
            newPicture.append(fg)
            newPicture.append(al)
            newPicture.append(sy)

    return _pictLstToDict(newPicture)


def flipVertically(picture):
    """Return the picture mirrored on the X axes."""
    newPicture = [picture[0], picture[1]]

    for y in range(picture[1], 0, -1):
        for x in range(1, picture[0] + 1):
            bg, fg, al, sy = get(picture, x, y)
            newPicture.append(bg)
            newPicture.append(fg)
            newPicture.append(al)
            newPicture.append(sy)

    return _pictLstToDict(newPicture)


def expand(
    picture,
    fromTop,
    fromBottom,
    fromLeft,
    fromRight,
    background=0x000000,
    foreground=0x000000,
    alpha=0,
    symbol=" ",
):
    """Expand a picture in all four directions, with new pixels defined with background, foreground, alpha, and symbol arguments. No random."""
    newWidth = picture[0] + fromRight + fromLeft
    newHeight = picture[1] + fromTop + fromBottom
    # Create new picture filled with new pixels from arguments
    newPicture = create(
        newWidth,
        newHeight,
        background,
        foreground,
        alpha,
        symbol,
    )

    # Copy pixels from original pixel, overwriting new ones.
    for y in range(1, picture[1] + 1):
        for x in range(1, picture[0] + 1):
            set_(newPicture, x + fromLeft, y + fromTop, *get(picture, x, y))

    return newPicture


def blend(picture, blendColor, transparency):
    """Blend the background and foreground with blendColor by transparency for every pixel in picture. Usually is, but has to be in 24 bit color mode."""
    newPicture = [picture[0], picture[1]]

    for i in range(2, len(picture), 4):
        newPicture.append(color.blend(picture[i], blendColor, transparency))
        newPicture.append(
            color.blend(picture[i + 1], blendColor, transparency),
        )
        newPicture.append(picture[i + 2])
        newPicture.append(picture[i + 3])

    return _pictLstToDict(newPicture)


##set = set_
