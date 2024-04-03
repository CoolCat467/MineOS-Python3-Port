#!/usr/bin/env python3
# Fake computer module for OpenComputers in Python3.
# -*- coding: utf-8 -*-

# Programmed by CoolCat467

__all__ = [
    "HZ",
    "addUser",
    "address",
    "beep",
    "crash",
    "energy",
    "freeMemory",
    "getArchitecture",
    "getBootAddress",
    "getDeviceInfo",
    "isRobot",
    "isRunning",
    "math",
    "maxEnergy",
    "pullSignal",
    "pushSignal",
    "removeUser",
    "runlevel",
    "setBootAddress",
    "shutdown",
    "start",
    "stop",
    "tmpAddress",
    "totalMemory",
    "uptime",
    "users",
]

import math
import os
import struct
import time
from collections import deque
from threading import Lock as _Lock, Thread as _Thread

_ADDRESS = "a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"
_TMPFS = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
_START = math.floor(time.time())
_RUNNING = False
_SHUTTINGDOWN = False
_REBOOT = False

_SIGNALS = deque()

_PITCHSTANDARD = 440
HZ = lambda semitones: _PITCHSTANDARD * (2 ** (1 / 12)) ** semitones
_SAMPLERATE = 44100
_BEEPS = {}
_NEXTBEEP = 0
_NEWBEEP = _Lock()


def start():
    """Tries to start the computer. Returns True on success, False otherwise. Note that this will also return false if the computer was already running. If the computer is currently shutting down, this will cause the computer to reboot instead."""
    if _RUNNING:
        if _SHUTTINGDOWN:
            _REBOOT = True
        return False
    else:
        _RUNNING = True
        _START = math.floor(time.time())
        return True


def stop():
    """Tries to stop the computer. Returns true on success, false otherwise. Also returns false if the computer is already stopped."""
    if _RUNNING:
        _SHUTTINGDOWN = True
        return True
    return False


def isRunning():
    """Returns whether the computer is currently running."""
    return _RUNNING


def crash(reason):
    """Attempts to crash the computer for the specified reason."""


def getArchitecture():
    """Returns the computer's current architecture."""
    return f"Python {os.sys.version.split(' ')[0]}"


def isRobot():
    """Returns whether or not the computer is, in fact, a robot."""
    return False


def address():
    """Returns the component address of computer."""
    return _ADDRESS


def tmpAddress():
    """The component address of the computer's temporary file system (if any), used for mounting it on startup."""
    return _TMPFS


def freeMemory():
    """The amount of memory currently unused, in bytes."""
    return int


def totalMemory():
    """The total amount of memory installed in this computer, in bytes."""
    return int


def energy():
    """The amount of energy currently available in the network the computer is in. For a robot this is the robot's own energy / fuel level."""
    return int


def maxEnergy():
    """The maximum amount of energy that can be stored in the network the computer is in. For a robot this is the size of the robot's internal buffer (what you se in the robot's GUI)."""
    return int


def uptime():
    """The time in real world seconds this computer has been running, measured based on the world time that passed since it was started - meaning this will not increase while the game is paused, for example."""
    return math.floor(time.time()) - _START


def shutdown(reboot=False):
    """Shuts down the computer. Optionally reboots the computer, if reboot is true, i.e. shuts down, then starts it again automatically. This function never returns."""


def getBootAddress():
    """Get the address of the filesystem component from which to try to boot first."""
    return str


def setBootAddress(address=None):
    """Set the address of the filesystem component from which to try to boot first. Call with nil / no arguments to clear."""


def runlevel():
    """Returns the current runlevel the computer is in.

    Current Runlevels in OpenOS are:
    S: Single-User mode, no components or filesystems initialized yet
    1: Single-User mode, filesystems and components initialized - OpenOS finished booting
    """
    return "S"


def users():
    """A list of all users registered on this computer, as a tuple."""
    return tuple()


def addUser(name):
    """Registers a new user with this computer. Returns true if the user was successfully added. Returns None and an error message otherwise."""
    return None, "Not implemented."


def removeUser(name):
    """Unregisters a user from this computer. Returns true if the user was removed, false if they weren't registered in the first place.
    The user will lose all access to this computer. When the last user is removed from the user list, the computer becomes accessible to all players.
    """
    return False


class _Signal:
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __repr__(self):
        args = " ,".join(self.args)
        return f"_Signal({self.name}, {args})"


def pushSignal(name, *args):
    """Pushes a new signal into the queue. _Signals are processed in a FIFO order. The signal has to at least have a name. Arguments to pass along with it are optional. Note that the types supported as signal parameters are limited to the basic types nil, boolean, number, string, and tables. Yes tables are supported (keep reading). Threads and functions are not supported.
    Note that only tables of the supported types are supported. That is, tables must compose types supported, such as other strings and numbers, or even sub tables. But not of functions or threads.
    """
    _SIGNALS.append(_Signal(name, *args))


def pullSignal(timeout=math.inf):
    """Tries to pull a signal from the queue, waiting up to the specified amount of time before failing and returning nil. If no timeout is specified waits forever.
    The first returned result is the signal name, following results correspond to what was pushed in push_Signal, for example. These vary based on the event type. Generally it is more convenient to use event.pull from the event library. The return value is the very same, but the event library provides some more options.
    """
    start = math.floor(time.time())
    while math.floor(time.time()) - start < timeout:
        if _SIGNALS:
            signal = _SIGNALS.popleft()
            return signal.name, *signal.args
    ##            return signalName, *signalargs
    return None


def _beeps_threads_cleanup():
    """Hidden function to clean up dead beep threads."""
    global _BEEPS, _NEXTBEEP
    for bid in list(_BEEPS):
        if not _BEEPS[bid].is_alive():
            del _BEEPS[bid]
    # maybe dangerous, but keep memory down if people are playing songs or something
    if _BEEPS:
        _NEXTBEEP = max(_BEEPS) + 1
    else:
        _NEXTBEEP = 0


def beep(frequency, duration):
    """Causes the computer to produce a beep sound at frequency Hz for duration seconds. This method is overloaded taking a single string parameter as a pattern of dots . and dashes - for short and long beeps respectively.

    Plays a tone, useful to alert users via audible feedback. Supports frequencies from 20 to 2000Hz, with a duration of up to 5 seconds.
    """
    global _NEWBEEP, _BEEPS, _NEXTBEEP

    def square(x):
        if math.sin(x) > 0:
            return 1
        return -1

    def save(data, filename):
        file = open(filename, "wb")
        file.write(struct.pack(str(len(data)) + "f", *data))

    def play(filename):
        # f32le = 32 bit float encoding in Little-endian byte order
        os.system(
            "ffplay -autoexit -showmode 0 -f f32le -ar %f %s"
            % (_SAMPLERATE, filename),
        )

    def _beepSound(beepId):
        if isinstance(frequency, str):
            # morris code mode, ignore duration.
            raise NotImplementedError
        else:
            if frequency < 20 or frequency > 2000:
                return
            hz = frequency
            step = (hz * 2 * math.pi) / _SAMPLERATE
            f = square
            output = [f(i * step) for i in range(int(_SAMPLERATE * duration))]
            file = f"beep{beepId}.bin"
            save(output, file)
            play(file)
            os.remove(file)

    # Get beep lock
    _NEWBEEP.acquire()
    # Quick delete dead _BEEPS since we have the lock
    _beeps_threads_cleanup()
    # Make new beep thread
    beepThread = _Thread(target=_beepSound, args=str(_NEXTBEEP))
    # Keep track of it in the _BEEPS dictionary
    _BEEPS[_NEXTBEEP] = beepThread
    # Increment the beep id by one
    _NEXTBEEP += 1
    # Release the lock
    _NEWBEEP.release()
    # Start playing sound
    beepThread.start()


def getDeviceInfo():
    """Returns a table of information about installed devices in the computer."""
    return dict
