#!/usr/bin/env python3
# OpenComputers Proxy
# -*- coding: utf-8 -*-

# Programmed by CoolCat467

__all__ = ['WARNING', 'LIBRARIES', 'MINEOS',
           'OPENCOMPUTERS', 'COMPONENTS', 'Proxy']

WARNING = True

import os as _os
from math import ceil as _ceil
from io import IOBase as _IOBASE

LIBRARIES = _os.path.split(__file__)[0]
MINEOS = _os.path.split(LIBRARIES)[0]
OPENCOMPUTERS = _os.path.split(MINEOS)[0]

COMPONENTS = {}

def _isStream(stream):
    """Return wether stream argument is an instance of io.IOBase."""
    return isinstance(stream, _IOBASE)

def _realPath(fakePath):
    """Return the real path of a given open computers path."""
    return _os.path.join(OPENCOMPUTERS, fakePath[1:])

def _fakePath(realPath):
    """Return the open computers path of a real path."""
    return realPath.split(OPENCOMPUTERS)[1]

class Proxy:
    def __init__(self, address):
        self.address = address
        self.type = COMPONENTS[self.address]
    
    def __repr__(self):
        return '<component Proxy object>'
    
    def exists(self, path):
        """Checks if file or directory exists on given path."""
        return _os.path.exists(_realPath(path))
    
    def size(self, path):
        """Tries to get file size by given path in bytes. Returns size on success, False and reason message otherwise."""
##        return False, 'File does not exist.'#success int or False, message
        if self.exists(path):
            try:
                size = _os.path.getsize(_realPath(path))
            except OSError:
                return False, 'File/Directory is inaccessible.'
            return size, None
        return False, 'File/Directory does not exist.'
    
    def isDirectory(self, path):
        """Checks if given path is a directory or a file."""
        return _os.path.isdir(_realPath(path))
    
    def makeDirectory(self, path):
        """Tries to create directory with all sub-paths by given path. Returns True on success, False and reason message otherwise."""
        try:
            _os.mkdir(_realPath(path), 664)
        except OSError:
            return False, 'Cannot create directory.'
        return True, None
    
    def lastModified(self, path):
        """Tries to get real world timestamp when file or directory by given path was modified. For directories this is usually the time of their creation. Returns timestamp on success, False and reason message otherwise."""
        if self.exists(path):
            time = _os.path.getmtime(_realPath(path))
##            return math.ceil(time), None
            return _ceil(time), None
        return False, 'File does not exist.'
    
    def remove(self, path):
        """Tries to remove file or directory by given path. Returns True on success, False and reason message otherwise."""
        if WARNING:
            ok = input(f'WARNING: Removing file {_realPath(path)}. Ok? (y/N) : ').lower()
            if ok == '':
                ok == 'n'
            if ok != 'y':
                return False, 'Access Denied.'
        _os.remove(_realPath(path))
        return False, 'File does not exist.'
    
    def list(self, path):
        """Tries to get list of files and directories from given path. Returns table with list on success, False and reason message otherwise."""
        if self.exists(path):
            if self.isDirectory(path):
                return _os.listdir(_realPath(path)), None
            name = _os.path.basename(_realPath(path))
            return False, f'"{name}" is not a directory.'
        return False, 'Directory does not exist.'
    
    def seek(self, stream, position='cur', offset=0):
        """If seek is successful, returns the new absolute position, None, measured in bytes from the beginning of the file. Otherwise it returns None and string reason."""
##        return False, 'Stream is invalid.'
        if _isStream(stream):
            if stream.seekable():
                if position in ('set', 'cur', 'end'):
                    whence = {'set':0, 'cur':1, 'end':2}[position]
                    if isinstance(offset, int):
                        return stream.seek(offset, whence), None
                    return False, 'Invalid offset.'
                return False, 'Invalid position.'
            return False, 'Stream is not seekable.'
        return False, f'"{stream}" is not a stream object.'
    
    def close(self, stream):
        """Close file stream."""
        if _isStream(stream):
            stream.close()
    
    def read(self, stream, buffer_size=-1):
        """Read exactly buffer_size or less from a file stream."""
        if _isStream(stream):
            if stream.readable():
                return stream.read(buffer_size), None
            return False, 'Stream is not readable.'
        return False, f'"{stream}" is not a stream object.'
    
    def write(self, stream, data):
        """Write data to stream.
           Returns the number of characters written (which is always equal to the length of the string)"""
        if _isStream(stream):
            if stream.writable():
                written = stream.write(data)
                return True, written
            return False, 'Stream is not writable.'
        return False, f'"{stream}" is not a stream object.'
    
    def open(self, path, mode):
        """Opens a file at the specified path for reading or writing with specified string mode. By default, mode is r. Possible modes are: r, rb, w, wb, a and ab"""
        if mode in ('r', 'rb', 'w', 'wb', 'a', 'ab'):
            readAdd = mode in ('r', 'rb', 'a', 'ab')
            if (readAdd and self.exists(path)) or (not readAdd):
                if not self.isDirectory(path):
                    try:
                        return open(_realPath(path), mode=mode), None
                    except BaseException:
                        return False, 'Cannot open file stream.'
                name = _os.path.split(_os.path.dirname(_realPath(path)))[1]
                return False, f'"{name}" is a directory.'
            return False, 'File does not exist.'
        return False, f'Mode "{mode}" is invalid.'
    
    def rename(self, fromPath, toPath):
        """Tries to rename file or directory from first path to second one. Returns True on success, False and reason message otherwise."""
        if self.exists(fromPath):
            try:
                _os.rename(_realPath(fromPath), _realPath(toPath))
            except OSError:
                return False, 'Cannot rename file/directory'
            return True, None
        return False, 'File does not exist.'
    pass
