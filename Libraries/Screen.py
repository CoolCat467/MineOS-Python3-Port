#!/usr/bin/env python3
# This is library for efficient usage of GPU resources and rendering data on screen as fast as possible. MineOS, it's software and internal interface libraries are based on screen library.
# -*- coding: utf-8 -*-


import Color as color

colorBlend = color.blend


##__all__ = ['getIndex', 'setDrawLimit', 'resetDrawLimit',
##           'getDrawLimit', 'flush', 'setResolution',
##           'bind', 'setGPUProxy', 'getGPUProxy',
##           'getScaledResolution', 'getResolution',
##           'getWidth', 'getHeight', 'getCurrentFrameTables',
##           'getNewFrameTables',
##           'rawSet', 'rawGet', 'get', 'set', 'clear', 'copy',
##           'paste', 'rasterizeLine', 'rasterizeEllipse',
##           'semiPixelRawSet', 'semiPixelSet', 'update',
##           'drawRectangle', 'drawLine', 'drawEllipse',
##           'drawText', 'drawImage', 'drawFrame',
##           'drawSemiPixelRectangle', 'drawSemiPixelLine',
##           'drawSemiPixelEllipse', 'drawSemiPixelCurve']


bufferWidth = 0
bufferHeight = 0

currentFrameBackgrounds: dict[int, int] = {}
currentFrameForegrounds: dict[int, int] = {}
currentFrameSymbols: dict[int, str] = {}

newFrameBackgrounds: dict[int, int] = {}
newFrameForegrounds: dict[int, int] = {}
newFrameSymbols: dict[int, str] = {}

drawLimitX1 = 1
drawLimitY1 = 1
drawLimitX2 = bufferWidth
drawLimitY2 = bufferHeight

##GPUProxy
GPUProxyGetResolution = lambda: 0, 0
GPUProxySetResolution = lambda: None
GPUProxyGetBackground = lambda: 0x000000
GPUProxyGetForeground = lambda: 0x000000
GPUProxySetBackground = lambda: None
GPUProxySetForeground = lambda: None
GPUProxyGet = lambda: None
GPUProxySet = lambda: None
GPUProxyFill = lambda: None


def tableInsert(table: dict, value: object) -> None:
    """Add a value to a table at given position. -1 is adding to the end. Only works if dictionary keys are intigers."""
    pos = max(table.keys()) + 1
    table[pos] = value


def updateGPUProxyMethods(GPUProxy: object) -> None:
    """Update the GPU Proxy methods."""
    global GPUProxyGetResolution, GPUProxyGetBackground, GPUProxyGetForeground
    global GPUProxySet, GPUProxySetResolution, GPUProxySetBackground, GPUProxySetForeground
    global GPUProxyFill
    GPUProxyGet = GPUProxy.get
    GPUProxyGetResolution = GPUProxy.getResolution
    GPUProxyGetBackground = GPUProxy.getBackground
    GPUProxyGetForeground = GPUProxy.getForeground

    GPUProxySet = GPUProxy.set
    GPUProxySetResolution = GPUProxy.setResolution
    GPUProxySetBackground = GPUProxy.setBackground
    GPUProxySetForeground = GPUProxy.setForeground

    GPUProxyFill = GPUProxy.fill


def getIndex(x: int, y: int) -> int:
    """Return the buffer index of a given choordinate."""
    return bufferWidth * (y - 1) + x


def getCurrentFrameFromTables() -> (
    tuple[dict[int, int], dict[int, int], dict[int, str]]
):
    """Return the current frame backgrounds, foregrounds, and symbols."""
    return (
        currentFrameBackgrounds,
        currentFrameForegrounds,
        currentFrameSymbols,
    )


def getNewFrameTables() -> (
    tuple[dict[int, int], dict[int, int], dict[int, str]]
):
    """Return new frame tables for backgrounds, foregrounds, and symbols."""
    return newFrameBackgrounds, newFrameForegrounds, newFrameSymbols


def resetDrawLimit() -> None:
    """Reset the draw limit to defaults."""
    global drawLimitX1, drawLimitY1, drawLimitX2, drawLimitY2
    drawLimitX1, drawLimitY1, drawLimitX2, drawLimitY2 = (
        1,
        1,
        bufferWidth,
        bufferHeight,
    )


def setDrawLimit(x1: int, y1: int, x2: int, y2: int) -> None:
    """Set the draw limit to given arguments."""
    global drawLimitX1, drawLimitY1, drawLimitX2, drawLimitY2
    drawLimitX1, drawLimitY1, drawLimitX2, drawLimitY2 = x1, y1, x2, y2


def getDrawLimit() -> tuple[int, int, int, int]:
    """Return the draw limit."""
    return drawLimitX1, drawLimitY1, drawLimitX2, drawLimitY2


def flush(width: int | None = None, height: int | None = None) -> None:
    """Flush the screen; Reset it to blank. If either arguments are None, use GPU Proxy resolution."""
    global currentFrameBackgrounds, currentFrameForegrounds, currentFrameSymbols, newFrameBackgrounds, newFrameForegrounds, newFrameSymbols
    global bufferWidth, bufferHeight

    if not width or not height:
        width, height = GPUProxySetResolution()

    (
        currentFrameBackgrounds,
        currentFrameForegrounds,
        currentFrameSymbols,
        newFrameBackgrounds,
        newFrameForegrounds,
        newFrameSymbols,
    ) = ({}, {}, {}, {}, {}, {})
    bufferWidth = width
    bufferHeight = height
    resetDrawLimit()

    for y in range(1, bufferHeight):
        for x in range(1, bufferWidth):
            tableInsert(currentFrameBackgrounds, 0x010101)
            tableInsert(currentFrameForegrounds, 0xFEFEFE)
            tableInsert(currentFrameSymbols, " ")

            tableInsert(newFrameBackgrounds, 0x010101)
            tableInsert(newFrameForegrounds, 0xFEFEFE)
            tableInsert(newFrameSymbols, " ")


def setResolution(width: int, height: int) -> None:
    """Set the resolution on the GPU Proxy and flush the frame buffers."""
    GPUProxySetResolution(width, height)
    flush(width, height)


def getResolution() -> tuple[int, int]:
    """Return the current screen resolution."""
    return bufferWidth, bufferHeight


def setGPUProxy(proxy: str) -> None:
    """Set the GPU Proxy."""
    global GPUProxy
    GPUProxy = proxy
    updateGPUProxyMethods()
    flush()


def getGPUProxy() -> str:
    """Return the GPU Proxy."""
    return GPUProxy
