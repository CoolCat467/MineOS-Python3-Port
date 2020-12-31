#!/usr/bin/env python3
# This library provides most commonly used MineOS system and user paths.
# -*- coding: utf-8 -*-

__all__ = ['system', 'user', 'getUser', 'updateUser', 'create']

# System is re-defined below
system = None
user = None

class _System:
    libraries = '/Libraries/'
    applications = '/Applications/'
    icons = '/Icons/'
    localizations = '/Localizations/'
    extensions = '/Extensions/'
    mounts = '/Mounts/'
    temporary = '/Temporary/'
    pictures = '/Pictures/'
    screensavers = '/Screensavers/'
    users = '/Users/'
    versions = '/Versions.cfg'
    
    applicationSample = applications + 'Sample.app/'
    applicationAppMarket = applications + 'App Market.app/Main.py'
    applicationMineCodeIDE = applications + 'MineCode IDE.app/Main.py'
    applicationFinder = applications + 'Finder.app/Main.py'
    applicationPictureEdit = applications + 'Picture Edit.app/Main.py'
    applicationSettings = applications + 'Settings.app/Main.py'
    applicationPrint3D = applications + '3D Print.app/Main.py'
    
    @classmethod
    def __repr__(cls):
        return str(cls.__dict__)
    pass

system = _System()

class _User:
    def __init__(self, name):
        global system
        self.name = name
        self.home = system.users + name + '/'
        self.applicationData = self.home + 'Application data/'
        self.desktop = self.home + 'Desktop/'
        self.libraries = self.home + 'Libraries/'
        self.applications = self.home + 'Applications/'
        self.pictures = self.home + 'Pictures/'
        self.screensavers = self.home + 'Screensavers/'
        self.trash = self.home + 'Trash/'
        self.settings = self.home + 'Settings.cfg'
        self.versions = self.home + 'Versions.cfg'
    
    def __repr__(self):
        return str(self.__dict__)
    pass

def pairs(table):
    """Return generater that iterates through the zipped keys and values of a table."""
    return ((k, table[k]) for k in table if table[k])
    
def create(what=()):
    """Create a new directory(s) by using the filesystem module."""
##    for _, path in pairs(what):
    if isinstance(what, dict):
        what = list(what.values())
    for path in what:
        if path[-1] == '/':
            import Filesystem as filesystem
            filesystem.makeDirectory(path)
            del filesystem

def getUser(name):
    """Returns user paths table created based on given userName."""
    return _User(name)

def updateUser(name):
    """Updates current user table in paths.user by give userName."""
    global user
    user = getUser(name)
