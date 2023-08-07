#!/usr/bin/env python3
# Fake component module for OpenComputers in Python3.
# -*- coding: utf-8 -*-

# Programmed by CoolCat467

WARNING = True

import random

import Proxy as _Proxy

##import os, math, random
##from io import IOBase as _IOBASE

##LIBRARIES = os.path.split(__file__)[0]
##MINEOS = os.path.split(LIBRARIES)[0]
##OPENCOMPUTERS = os.path.split(MINEOS)[0]

BOOT_PROXY = None
PRIMARYS = {}

import computer


def get(abbreviatedAddress):
    """Returns full address from an abbreviated address."""
    leng = len(abbreviatedAddress)
    for addr in _Proxy.COMPONENTS:
        if addr[:leng] == abbreviatedAddress:
            return addr


def isAvailable(componentName):
    """Return True if component of name componentName is available."""
    componentTypes = list(_Proxy.COMPONENTS.keys())
    return componentName in componentTypes


def getPrimary(componentName):
    """Return the primary component of componentName."""
    if componentName in PRIMARYS:
        return proxy(PRIMARYS[componentName])
    raise RuntimeError(f'No primary component of type "{componentName}"')


def list(type_):
    return _Proxy.COMPONENTS.copy()


def proxy(address):
    if address in _Proxy.COMPONENTS:
        return _Proxy.Proxy(address)
    raise ValueError("Address is invalid.")


def newRandomAddress():
    """Return a new random address."""
    parts = (8, 4, 4, 4, 12)

    def getRandom(num):
        lst = []
        for i in range(num):
            lst.append(random.randint(0x0, 0xF))
        return "".join((hex(i)[2:] for i in lst))

    # (getRandom(8), getRandom(4), getRandom(4), getRandom(4), getRandom(12))
    return "-".join((getRandom(i) for i in parts))


def addComponent(name, address):
    """Add a component to the dictionary."""
    _Proxy.COMPONENTS[address] = name


addComponent("computer", _Proxy.MINEOS)
BOOT_PROXY = proxy(_Proxy.MINEOS)
