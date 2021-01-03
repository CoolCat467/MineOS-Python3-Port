#!/usr/bin/env python3
# This library is made for Image manipulations
# -*- coding: utf-8 -*-

# load('/MineOS/Pictures/AhsokaTano.pic')

import computer
import Color as color
import Filesystem as filesystem
import Bit32 as bit32
import math, random

OCIFSignature = 'OCIF'
encodingMethodsLoad = {}
encodingMethodsSave = {}

class string:
    def char(bytes_):
        """Decode bytes and return string."""
        if len(bytes_) == 1:
            return ord(bytes_)
        if isinstance(bytes_, bytes):
            return bytes_.decode('utf-8')
        elif isinstance(bytes_, str):
            return bytes_
        print(bytes_)
        raise ValueError
    
    def byte(string_):
        """Encode string and return bytes."""
        if isinstance(string_, str):
            return string_.encode('utf-8')
        elif isinstance(string_, int):
            return chr(string_)
        elif isinstance(string_, bytes):
            return string_
        raise ValueError
    pass

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
##        print(w, realh)
        chars = []
        for y in range(realh):
            for x in range(w):
                try:
                    chars.append(self.data[getIndex(x, y, w)+3])
                except KeyError:
                    chars.append(' ')
        for i in reversed(range(len(chars))):
            if isinstance(chars[i], int):
               chars[i] = ' '
##        chars = [self.data[2+i*4+3] for i in range(pixels)]
        #(len(self.data)-2) // w-4
        lines = [''.join(chars[i*w:(i+1)*w]) for i in range(realh)]
##        chars = [''.join(chars[i*w:(i+1)*w]) for i in range()]
        return '\n'.join(lines)
    
    def __repr__(self):
        return self.getStr()

##def readOutput(output):
##    """Return True, output, None if output does not have error reason, and False, output, reason if it does."""
##    try:
##        

def group(picture, compressColors=False):
    """Simplify a picture into a gigantic table."""
    groupedPicture = {}
    x, y = 1, 1
    # Make code smaller
    p = picture
##    print((2, len(p), 4))
    
    for i in range(2, len(p), 4):
##        index = i*4 + 2
        if compressColors:
##            print(i)
##            print([p[i], p[i+1]])
            background, foreground = color.to8Bit(p[i]), color.to8Bit(p[i + 1])
##            background, foreground = color.to8Bit(p[index]), color.to8Bit(p[index + 1])
            # Skipping because it's very strange.
##            if i % 603 == 0:
##                # Handle signals for zero secconds? What?
##                # If it's computer's pullSignal, we are making event
##                # module not process signals. Interesting.
##                computer.pullSignal(0)
        else:
            background, foreground = p[i], p[i+1]
##            background, foreground = p[index], p[index+1]
        alpha, char = p[i+2], p[i+3]
##        alpha, char = p[index+2], p[index+3]
        
        if not alpha in groupedPicture:
            groupedPicture[alpha] = {}
        if not char in groupedPicture[alpha]:
            groupedPicture[alpha][char] = {}
        if not background in groupedPicture[alpha][char]:
            groupedPicture[alpha][char][background] = {}
        if not foreground in groupedPicture[alpha][char][background]:
            groupedPicture[alpha][char][background][foreground] = {}
        if not y in groupedPicture[alpha][char][background][foreground]:
            groupedPicture[alpha][char][background][foreground][y] = []
        
        groupedPicture[alpha][char][background][foreground][y].append(x)
        
        x += 1
        if x > p[0]:
            x = 0
            y += 1
##    print(p[0], p[1])
##    print(x, y)
    return groupedPicture
            
def encMethodSave5(file, picture):
    """Save an picture to a file."""
    file.writeBytes(bit32.rshift(picture[0], 8),
                    bit32.band(picture[1], 0xff))
    
    for i in range(2, len(picture), 4):
        file.writeBytes(color.to8Bit(picture[i]), color.to8Bit(picture[i+1]), math.floor(picture[i + 2] * 255))
        
        file.write(picture[i + 3])
    return True, None

encodingMethodsSave[5] = encMethodSave5

def encMethodLoad5(file, picture):
    """Load a picture from a file."""
    picture[0] = file.readBytes(2)
    picture[1] = file.readBytes(2)
    
    for i in range(math.ceil(getWidth(picture) * picture[1])):
        picture[i] = color.to24Bit(file.readBytes(1))
        picture[i+1] = color.to24Bit(file.readBytes(1))
        picture[i+2] = file.readBytes(1) / 255
        picture[i+3] = file.readUnicodeChar()
##        picture.append(color.to24Bit(file.readBytes(1)))
##        picture.append(color.to24Bit(file.readBytes(1)))
##        picture.append(file.readBytes(1) / 255)
##        picture.append(file.readUnicodeChar())
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
        file.writeBytes(math.floor(alpha * 255), bit32.rshift(symbolsSize, 8), bit32.band(symbolsSize, 0xff))
        
        for symbol in groupedPicture[alpha]:
            # Write current unicode symbol value
            file.write(symbol)
            # Write one byte for backgrounds array size
            file.writeBytes(len(groupedPicture[alpha][symbol]))
            
            for background in groupedPicture[alpha][symbol]:
                # Write one byte for background color value (compressed by color)
                # Write one byte for foregrounds array size
                file.writeBytes(background, len(groupedPicture[alpha][symbol][background]))
                
                for foreground in groupedPicture[alpha][symbol][background]:
                    # Write one byte for foreground color value (compressed by color
                    # Write one byte for y array size
                    file.writeBytes(foreground, len(groupedPicture[alpha][symbol][background][foreground]))
                    
                    for y in groupedPicture[alpha][symbol][background][foreground]:
                        # Write one byte for current y value
                        # Write one byte for x array size
                        file.writeBytes(y, len(groupedPicture[alpha][symbol][background][foreground][y]))
                        
                        for x in groupedPicture[alpha][symbol][background][foreground][y]:
                            file.writeBytes(x)
    return True, None

encodingMethodsSave[6] = encMethodSave6

def encMethodLoad6(file, picture):
    """Very efficiant."""
    global PIC
    PIC = picture
    def readBytes(num=1):
        read = file.readBytes(num)
        if not read is None:
            return read
        else:
            print(xSize, ySize)
            print(x, y)
##            print(currentY, read)
        return read
##    picture.append(file.readBytes(1))
##    picture.append(file.readBytes(1))
    picture[0] = file.readBytes(1)
    picture[1] = file.readBytes(1)
    
    alphaSize = file.readBytes(1)
    
    for alpha in range(alphaSize):
        currentAlpha = file.readBytes(1) / 255
        symbolSize = file.readBytes(2)
        
        for symbol in range(symbolSize):
            currentSymbol = file.readUnicodeChar()
            backgroundSize = file.readBytes(1)
            
            for background in range(backgroundSize):
                currentBackground = color.to24Bit(file.readBytes(1))
                foregroundSize = file.readBytes(1)
                
                for foreground in range(foregroundSize):
                    currentForeground = color.to24Bit(file.readBytes(1))
                    ySize = file.readBytes(1)
                    
                    for y in range(ySize):
                        currentY = file.readBytes(1)
                        xSize = file.readBytes(1)
                        
                        for x in range(xSize):
                            currentX = file.readBytes(1)
                            if currentX is None:
                                print('EOF error averted.')
                                print(currentX, currentY, currentBackground, currentForeground, currentAlpha, currentSymbol)
##                                print(x, y, background, foreground, alpha, symbol)
##                                print(xSize, ySize, backgroundSize, foregroundSize, alphaSize, symbolSize)
                                print(f'{x}/{xSize} {y}/{ySize} {background}/{backgroundSize} {foreground}/{foregroundSize} {alpha}/{alphaSize} {symbol}/{symbolSize}')
                                return None, None
##                            index = getIndex(currentX+1, currentY+1, picture[0])-1
                            index = getIndex(currentX, currentY, picture[0])
                            if index <= 2:
                                print(index)
##                            index = getIndex(readBytes(1), currentY, picture[0])
##                            index = getIndex(currentX, currentY, picture[0])
                            picture[index], picture[index+1], picture[index+2], picture[index+3] = currentBackground, currentForeground, currentAlpha, currentSymbol
##                            set_(picture, currentX, currentY, currentBackground, currentForeground, currentAlpha, currentSymbol)
##                            print(index)
##                            raise RuntimeError
    return None, None

encodingMethodsLoad[6] = encMethodLoad6

def getSize(picture):
    """Return the size of a given picture."""
    return picture[0], picture[1]

def getWidth(picture):
    """Return the width of a given picture."""
    return picture[0]

def getHeight(picture):
    """Return the height of a given picture."""
    return picture[1]

def getIndex(x:int, y:int, width:int):
    """Return the internal picture index of a given pixel, given xy position and the width of the image. Indexing starts at 1, 1."""
##    return 4 * (width * (y - 1) + x) - 1
    return 4 * (width * y + x - 1) + 2# - 1

def set_(picture, x, y, background, foreground, alpha, symbol):
    """Set the data of the pixel at given xy choordinates in a given image."""
    index = getIndex(x, y, picture[0])
##    data = [picture, x, y, background, foreground, alpha, symbol]
##    for i in data:
##        picture.append(i)
    picture[index], picture[index+1], picture[index+2], picture[index+3] = background, foreground, alpha, symbol
##    return picture

def get(picture, x, y):
    """Return the background, foreground, alpha, and symol at the pixel at given xy choordinates in given image."""
    index = getIndex(x, y, picture[0])
    return picture[index], picture[index+1], picture[index+2], picture[index+3]
##    return picture[index:index+4]

def create(width:int, height:int, background=0x0, foreground=0x0, alpha=0x0, symbol=' ', random_=False):
    """Create a new picture with given arguments."""
    picture = {0:width, 1:height}
    
    for y in range(picture[1]):
        for x in range(picture[0]):
            i = 4 * ((y * picture[0]) + x) + 2
##    for _ in range(math.ceil(width * height)):
            if random_:
##                picture.append(random.randint(0x0, 0xffffff))
##                picture.append(random.randint(0x0, 0xffffff))
                picture[i] = random.randint(0x0, 0xffffff)
                picture[i+1] = random.randint(0x0, 0xffffff)
            else:
##                picture.append(background)
##                picture.append(foreground)
                picture[i] = background
                picture[i+1] = foreground
##            picture.append(alpha)
            picture[i+2] = alpha
            if random_:
##                picture.append(chr(random.randint(65, 90)))
                picture[i+3] = chr(random.randint(65, 90))
            else:
##                picture.append(symbol)
                picture[i+3] = symbol
    return picture

def copy(picture):
    """Return a copy of given picture."""
    return [i for i in picture]

def save(path, picture, encodingMethod=6):
    """Save a given picture to a file at path, using given encoding method."""
    file, reason = filesystem.open(path, 'wb')
    if file:
        if encodingMethodsSave[encodingMethod]:
            file.write(OCIFSignature, string.byte(encodingMethod))
            
            result, reason = encodingMethodsSave[encodingMethod](file, picture)
            
            file.close()
            
            if result:
                return True, None
##            else:
            return False, f'Failed to save OCIF image: {reason}'
##        else:
        file.close()
        return False, f'Failed to save OCIF image: encoding method "{encodingMethod}" is not supported.'
    return False, f'Failed to open file for writing: {reason}'

def load(path):
    """Load an image from given path. Automatically de-compresses."""
    file, reason = filesystem.open(path, 'rb')
    if file:
        readSignature = string.char(file.readString(len(OCIFSignature)))
        if readSignature == OCIFSignature:
            encodingMethod = file.readBytes(1)
            if encodingMethod in encodingMethodsLoad:
                picture = {}
                result, reason = encodingMethodsLoad[encodingMethod](file, picture)
                
                file.close()
                
                if reason is None:
                    return picture, None
                return False, f'Failed to load OCIF image: {reason}'
            file.close()
            return False, f'Failed to load OCIF image: encoding method "{encodingMethod}" is not supported.'
        file.close()
        return False, f'Failed to load OCIF image: binary signature "{readSignature}" is not valid.'
    return False, f'Failed to open file "{path}" for reading: {reason}'

def toString(picture):
    pass
                
    

set = set_
