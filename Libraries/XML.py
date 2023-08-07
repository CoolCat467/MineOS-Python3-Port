#!/usr/bin/env python3
# XML API, for dealing with XML strings
# -*- coding: utf-8 -*-

__all__ = ["parseargs", "collect"]

"<users>\n\t<user>\n\t\t<id>1</id>\n\t\t<name>Fred</name>\n\t\t<salary>500000</salary>\n\t</user>\n\t<user>\n\t\t<id>1</id>\n\t\t<name>ScienceCat</name>\n\t\t<salary>500000</salary>\n\t</user>\n\t<user>\n\t\t<id>1</id>\n\t\t<name>Bob</name>\n\t\t<salary>500000</salary>\n\t</user>\n</users>"
xmlex = "<users>\n<user>\n<id>1</id>\n<name>Fred</name>\n<salary>500000</salary>\n</user>\n<user>\n<id>1</id>\n<name>ScienceCat</name>\n<salary>500000</salary>\n</user>\n<user>\n<id>1</id>\n<name>Bob</name>\n<salary>500000</salary>\n</user>\n</users>"
argex = 'cats="True and Sand" true=\'Cats two\' sand="graval"'

##import re
##import xml.etree.cElementTree as xml


def parseargs(string: str):
    """Split a given string into individual arguments, seperated into key:arg for <key>=(' or ")<arg>(same char as start)"""
    arg = {}
    # ([%-%w]+)=([\"'])(.-)%2
    # '([\w]+)=([\"\'])(.*)'
    # '([-\w]+)=([\"\']*)'
    ##    pattern = re.compile('([\w]+)=([\"\'])(.*)')
    ##    print(pattern)
    ##    for match in re.findall(pattern, string):
    ##        print(match)

    parts = string.split(" ")
    bkey = ""
    buffer = ""
    end = '"'
    for part in parts:
        if "=" in part:
            key, vp = part.split("=")
            if vp[0] in ('"', "'"):
                end = vp[0]
            if vp.endswith(end):
                arg[key] = vp[1:-1]
            else:
                bkey = key
                buffer += vp
        elif part.endswith(end):
            buffer += " " + part
            arg[bkey] = buffer[1:-1]
            bkey, buffer = "", ""
        else:
            buffer += " " + part
    return arg


def collect(string: str):
    stack = []
    top = []
    stack.append(top)
    i, j = 0, 0

    class elementTag:
        def __init__(self, label, xargs, empty=0):
            self.label = label
            self.xargs = xargs
            self.empty = empty

    while True:
        ni
        h
        c
        lable
        xarg
        emtpy
        if not ni:
            break
        text = string[i : ni - 1]
        if not text.find("^ "):
            top.append(text)
        if empty == "/":  # empty element tag
            top.append(elementTag(label, parseargs(xarg), 1))
        elif c == "":  # start tag
            top = [elementTag(label, parseargs(xarg))]
            stack.append(top)
        else:
            toclose = stack
            if len(stack) < 1:
                error(f"Nothing to close with {label}.")
            elif toclose.label == label:
                pass
