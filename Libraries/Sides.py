#!/usr/bin/env python3
# Small module for dealing with sides.
# -*- coding: utf-8 -*-

# Programmed by CoolCat467
    
bottom = 0
top    = 1
back   = 2
front  = 3
right  = 4
left   = 5
unknown= 6

sides = {
    bottom:'bottom',
    top:'top',
    back:'back',
    front:'front',
    right:'right',
    left:'left',
    unknown:'unknown'}

down   = bottom
up     = top
north  = back
south  = front
west   = right
east   = left

negy   = down
posy   = up
negz   = north
posz   = south
negx   = west
posx   = east

forward  = front
backward = back
