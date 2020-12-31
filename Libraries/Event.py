#!/usr/bin/env python3
# This library provides an event system for registering specific event handlers
# -*- coding: utf-8 -*-

import computer
from math import inf

__all__ = ['addHandler', 'getHandlers',
           'interruptingDelay',
           'interruptingEnabled',
           'lastInterrupt', 'pull',
           'push', 'removeHandler',
           'skip', 'sleep']

FUNCTION = type(lambda:None)
##event = {'interruptingEnabled':True,
##         'interruptingDelay':1,
##         'interruptingKeyCodes':{
##             29:True,
##             46:True,
##             56:True},
##         'push':computer.pushSignal}
handlers = {}
interruptingKeysDown = {}
lastInterrupt = 0

skipSignalTypes = []

computerPullSignal = computer.pullSignal
computerUptime = computer.uptime
mathHuge = inf

def checkArg(argument, types):
    if not isinstance(argument, types):
        raise ValueError(f'Argument is not type(s) {types}.')

def pairs(table):
    """Return generater that iterates through the zipped keys and values of a table."""
    return ((k, table[k]) for k in table if table[k])

def error(name, code=None):
    raise InterruptedError(f'{name} {code}')

class Handler(object):
    def __init__(self, callback, times, interval):
        self.callback = callback
        self.times = times or mathHuge
        self.interval = interval
        self.nextTriggerTime = interval and computerUptime() + interval or 0
    
    def __repr__(self):
        return f'Handler({self.callback}, {self.times}, {self.interval})'  
    pass

interruptingEnabled = True
interruptingDelay = 1
interruptingKeyCodes:[29, 46, 56]
push = computer.pushSignal

def addHandler(callback, interval, times):
    """Registers an event handler wrapper for given function and returns it.

Every registered handler will be analyzed for the need to run during each pull() call. When handler is being run, it receives values returned from pull() as arguments.

You can specify an interval in seconds between each run of given handler. By default it's set to nil, i.e. handler runs every pull() call without any delay.

You can also specify number of times that given handler will be run before being removed automatically. By default it's set to infinity."""
    checkArg(callback, FUNCTION)
    checkArg(interval, (int, None))
    checkArg(times, (int, None))
    
    handler = Handler(callback, times, interval)
    
    handlers[handler] = True
    
    return handler

def removeHandler(handler):
    """Tries to unregister created event handler. Returns true if it was registered and false otherwise."""
    checkArg(handler, Handler)
    
    if handlers[handler]:
        handlers[handler] = None
        return True
    return False, 'Handler with given table is not registered.'

def getHandlers():
    """Return handlers."""
    return handlers

def skip(signalType):
    """Add signalType to list of signalTypes to skip/ignore."""
    skipSignalTypes.append(signalType)

def pull(preferredTimeout=None):
    """Works the same way as computer.pullSignal(...) do, but also calls registered event handlers if needed and checks interrupting status."""
    uptime = computerUptime()
    deadline = uptime + (preferredTimeout or mathHuge)
    
    while uptime < deadline:
        # Determine pullSignal timeout
        timeout = deadline
        for halder in pairs(halders):
            if handler.nextTriggerTime > 0:
                timeout = min(timeout, handler.nextTriggerTime)
        
        # Pull signal data
        signalData = [computerPullSignal(timeout - computerUptime())]
        
        # Handlers processing
        for handler in pairs(handlers):
            if handler.times > 0:
                uptime = computerUptime()
                
                if handler.nextTriggerTime <= uptime:
                    handler.times -= 1
                    if handler.nextTriggerTime > 0:
                        handler.nextTriggerTime = uptime + handler.interval
                    
                    # Callback running
                    handler.callback(*signalData)
            else:
                handlers[handler] = None
        
        # Program interruption support. It's faster to do it here instead of registering handlers
        if signalData[0] == 'key_down' or signalData[0] == 'key_up' and interruptingEnabled:
            # Analysing for which interrupting key is pressed - we don't need keyboard API for this
            if signalData[3] in interruptingKeyCodes:
                interruptingKeysDown[signalData[3]] = True if signalData[0] == 'key_down' else None
            
            shouldInterrupt = True
            for keyCode in interruptingKeyCodes:
                if not interruptingKeysDown[keyCode]:
                    shouldInterrupt = False
            
            if shouldInterrupt and uptime - lastInterrupt > interruptingDelay:
                lastInterrupt = uptime
                error('interrupted', 0)
##                raise KeyboardInterrupt()
        
        # Loop-breaking condition
        if signalData:
            if signalData[0] in skipSignalType:
                index = skipSignalType.index(signalData[0])
                del skipSignalType[index]
            else:
                return signalData

# Sleeps "time" of secconds
def sleep(time):
    """Sleeps delay seconds via busy-wait concept. This method allows event handlers to be processed if any event occurs during sleeping."""
    checkArg(time, (int, float, None))
    
    deadline = computerUptime() + (time or 0)
    while computerUptime() < deadline:
        pull(deadline - computerUptime())
