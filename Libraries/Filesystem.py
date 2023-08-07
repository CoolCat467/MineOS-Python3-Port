#!/usr/bin/env python3
# This library allows developer to interact with filesystem components, to mount them on virtual directories, to perform buffered I/O operations and to process string paths for extraction of their parts.
# -*- coding: utf-8 -*-

__all__ = [
    "address",
    "append",
    "copy",
    "doFile",
    "exists",
    "extension",
    "get",
    "getProxy",
    "hideExtension",
    "isDirectory",
    "isHidden",
    "lastModified",
    "lines",
    "list",
    "loadfile",
    "makeDirectory",
    "mount",
    "mounts",
    "name",
    "open",
    "path",
    "read",
    "readLines",
    "readTable",
    "remove",
    "removeSlashes",
    "rename",
    "setProxy",
    "size",
    "unmount",
    "write",
    "writeTable",
]

import math

import Bit32 as bit32
import component
import computer
import Event as event
import Paths as paths

BUFFER_SIZE = 1024
BOOT_PROXY = None  #'12512'
mountedProxies = []  # {}

SORTING_NAME = 1
SORTING_TYPE = 2
SORTING_DATE = 3


class string:
    def char(bytes_):
        "Decode bytes and return string."
        if len(bytes_) == 1:
            return ord(bytes_)
        if isinstance(bytes_, bytes):
            return bytes_.decode("utf-8")
        elif isinstance(bytes_, str):
            return bytes_
        print(bytes_)
        raise ValueError

    def byte(string_):
        "Encode string and return bytes."
        if isinstance(string_, str):
            return string_.encode("utf-8")
        elif isinstance(string_, int):
            return chr(string_)
        elif isinstance(string_, bytes):
            return string_
        raise ValueError

    pass


def pairs(table):
    "Return generater that iterates through the zipped keys and values of a table."
    return ((k, table[k]) for k in table if table[k])


def error(name, code=1):
    raise InterruptedError(f"{name} {code}")


class _mountProxy:
    def __init__(self, path, proxy):
        self.path = path
        self.proxy = proxy

    pass


def path(path_):
    "Returns parent path from given path."
    return "/".join(path_.split("/")[:-1]) + "/"


def name(path_):
    "Returns file name from given path. Keeps end slash if any."
    add = ""
    if path_.endswith("/"):
        path_ = path_[:-1]
        add = "/"
    return path_.split("/")[-1] + add


def extension(path_):
    "Returns extension from given path. Skips end slash if any."
    if path_.endswith("/"):
        path_ = path_[:-1]
    filename = path_.split("/")[-1]
    if not "." in filename:
        return None
    return "." + filename.split(".")[1]


def hideExtension(path_):
    "Returns given path without it's extension"
    spPath = path_.split("/")
    spPath[-1] = spPath[-1].split(".")[0]
    return "/".join(spPath)


def isHidden(path_):
    "Hidden files are files which names starts of dot symbol. This method returns True if file is hidden or False otherwise."
    return path_[0] == "."


def removeSlashes(path_):
    "Remove slashes from path_."
    return "/".join([i for i in path_.split("/") if i != ""])


def mount(proxy, path_):
    "Mounts passed filesystem component proxy table to specified path."
    for mp in mountedProxies:
        if mp.path == path_:
            return False, "Mount path has been taken by another mounted filesystem."
        elif mp.proxy == proxy:
            return False, "Proxy is already mounted."

    mountedProxies.append(_mountProxy(path_, proxy))
    return True, None


def unmount(proxy):
    "Unmounts passed filesystem component proxy table or it's string address from mounted path."
    if isinstance(proxy, (dict, list, tuple)):
        for i in range(len(mountedProxies)):
            if mountedProxies[i].proxy == proxy:
                del mountedProxies[i]
                return True, None
        return False, "Specified proxy is not mounted."
    elif isinstance(proxy, str):
        for i in range(len(mountedProxies)):
            if mountedProxies[i].address == proxy:
                del mountedProxies[i]
                return True, None
        return False, "Specified proxy address is not mounted."
    ##    else:
    error(f"Bad argument (filesystem proxy or mounted path expected, got {proxy}).")


def get(path_):
    "Determines correct filesystem component proxy from given path and returns it with rest path part."
    if not isinstance(path_, str):
        print(path_)
        error("Invalid argument.")
    for mp in mountedProxies:
        if path_[: len(mp.path)] == mp.path:
            return mp.proxy, path[len(mp.path) :]
    return BOOT_PROXY, path_


def mounts():
    "Returns an iterator function for listing of mounted filesystems."
    return ((mp.proxy, mp.path) for mp in mountedProxies if mp)


def exists(path):
    "Checks if file or directory exists on given path."
    proxy, proxyPath = get(path)
    return proxy.exists(proxyPath)


def size(path_):
    "Tries to get file size by given path in bytes. Returns size on success, False and reason message otherwise."
    proxy, proxyPath = get(path_)
    return proxy.size(proxyPath)


def isDirectory(path_):
    "Checks if given path is a directory or a file."
    proxy, proxyPath = get(path_)
    return proxy.isDirectory(proxyPath)


def makeDirectory(path_):
    "Tries to create directory with all sub-paths by given path. Returns True on success, False and reason message otherwise."
    proxy, proxyPath = get(path_)
    return proxy.makeDirectory(proxyPath)


def lastModified(path_):
    "Tries to get real world timestamp when file or directory by given path was modified. For directories this is usually the time of their creation. Returns timestamp on success, False and reason message otherwise."
    proxy, proxyPath = get(path_)
    return proxy.lastModified(proxyPath)


def remove(path_):
    "Tries to remove file or directory by given path. Returns True on success, False and reason message otherwise."
    proxy, proxyPath = get(path_)
    return proxy.remove(proxyPath)


def list_(path_, sortingMethod=SORTING_NAME):
    "Tries to get list of files and directories from given path. Returns table with list on success, False and reason message otherwise."
    proxy, proxyPath = get(path_)

    list__, reason = proxy.list(proxyPath)
    ##    list_, reason = ['computer.py', 'Event.py', 'py', 'Screen.py', 'Color.py', '__pycache__', 'Paths.py'], None

    if not reason and list__:
        # Fullfill list with mounted paths if needed
        for mp in mountedProxies:
            if path_ == path(mp.path):
                list__.append(name(mp.path))

        # Apply sorting methods
        if sortingMethod == SORTING_NAME:
            list__.sort(lambda a, b: a.lower() < b.lower())
            return list__, None
        elif sortingMethod == SORTING_DATE:
            list__.sort(lambda a, b: lastModified(path_ + a) > lastModified(path_ + b))
            return list__, None
        elif sortingMethod == SORTING_TYPE:
            # Create a map with "extention" structure
            map_ = {}
            for file in list__:
                if not "." in file and isDirectory(path_ + file):
                    extention_ = "."
                else:
                    extention_ = extension(file) or "Z"

                if not extention_ in map_:
                    map_[extention_] = []
                map_[extention_].append(file)

            # Sort lists for each extention
            extentions = {}
            for key, value in pairs(map_):
                value.sort(lambda a, b: a.lower() < b.lower())

                extentions[key] = value

            # Sort extentions
            keys = list(extentions.keys())
            keys.sort(lambda a, b: a.lower() < b.lower())

            # Create final list:
            list__ = []
            for key in keys:
                for value in extentions[key]:
                    list__.append(value)

            return list__, None
        ##        else:
        reason = "No sorting method given."
    return list__, reason


# I/O methods


def _getForMode(string_, mode):
    "Get the proper string for given mode."
    if "b" in mode:
        return string.byte(string_)
    return string.char(string_)


##        return bytes(string_, 'utf-8')
##    return str(string_)


class _Handle:
    def __init__(self, proxy, stream, mode="r"):
        self.proxy = proxy
        self.stream = stream
        self.mode = mode
        self.position = 0
        self.buffer = ""
        if "b" in self.mode:
            self.buffer = b""

    def seek(self, position="cur", offset=0):
        """Sets or gets the handle position, measured from the beginning of the file, to the position given by offset plus a base specified by the string whence, as follows:

            set: base is position 0 (beginning of the file)
            cur: base is current position
            end: base is end of file

        The default value for whence is "cur", and for offset is 0. If seek was successful, returns the final file position, measured in bytes from the beginning of the file. Otherwise it returns nil and string reason.
        """
        if position == "set":
            result, reason = self.proxy.seek(self.stream, "set", offset)
        elif position == "cur":
            result, reason = self.proxy.seek(self.stream, "set", self.position + offset)
        elif position == "end":
            result, reason = self.proxy.seek(self.stream, "end", offset)
        else:
            error(f"Bad argument #2 ('set', 'cur', or 'end' expected, got {position})")
        if reason is None:
            self.position = result
            self.buffer = ""
            return result  # , reason
        error(f"{reason}")

    def close(self):
        "Closes file stream, flushes internal buffer and releases the handle."
        if "w" in self.mode and len(self.buffer) > 0:
            self.proxy.write(self.stream, self.buffer)

        self.proxy.close(self.stream)

    def readString(self, count):
        "Reads string with length of given count of bytes. Returns string value or None if EOF has reached."
        # If current buffer content is a "part" of "count data" we need to read
        if count > len(self.buffer):
            data = self.buffer

            while len(data) < count:
                chunk, error_ = self.proxy.read(self.stream, BUFFER_SIZE)
                if error_:
                    error(error_)

                if chunk:
                    data += chunk
                else:
                    self.position = self.seek("end", 0)

                    # EOF at start
                    ##                    if len(data) == 0:
                    if data == "":
                        print("EOF")
                        return None
                    # EOF after read
                    return data

            self.buffer = data[count:]  # -1
            chunk = data[:count]
            self.position += len(chunk)

            return chunk
        data = self.buffer[:count]
        self.buffer = self.buffer[count:]
        self.position += count

        return data

    def readLine(self):
        "Reads next line from file without \n character. Returns string line or None if EOF has reached."
        data = _getForMode("", self.mode)

        linebreak = _getForMode("\n", self.mode)
        while True:
            if len(self.buffer) > 0:
                eofidx = self.buffer.find(linebreak)
                if eofidx >= 0:
                    chunk = self.buffer[:eofidx]
                    self.buffer = self.buffer[eofidx:]
                    self.position += len(chunck)

                    ##                    return data + chunck
                    return string.char(data + chunck)
                else:
                    data += self.buffer

            chunk, error_ = self.proxy.read(self.stream, BUFFER_SIZE)
            if error_:
                error(error_)
            if chunk:
                self.buffer = chunk
                self.position += len(chunk)
            else:  # EOF
                data = self.buffer
                self.position = self.seek("end", 0)

                ##                return len(data) > 0 and data or None
                return len(data) > 0 and string.char(data) or None

    def lines(self):
        "Return a generator object that will return lines, and on EOF close self."

        def lineGen():
            while True:
                line = self.readLine()
                if line:
                    yield line
                else:
                    break
            self.close()
            raise StopIteration

        ##            return None
        return lineGen

    def readAll(self):
        "Reads whole file as string. Returns string data if reading operation was successful, None and reason message otherwise."
        data = _getForMode("", self.mode)
        while True:
            chunk, error_ = self.proxy.read(self.stream, BUFFER_SIZE)
            if error_:
                error(error_)

            if chunk:
                data += chunk
            else:
                self.position = self.seek("end", 0)
                break
        ##        return data
        return string.char(data)

    def readBytes(self, count, littleEndian=False):
        "Reads number represented by count of bytes in big endian format by default or little endian if desired. Returns int value or None if EOF has reached."
        if count == 1:
            data = self.readString(1)
            if data:
                return ord(data)
            return None
        else:
            lst = lambda x: [i for i in x]
            bytes_ = lst(string.byte(self.readString(count))[:8]) or b"\x00"
            result = 0

            if littleEndian:
                for i in range(len(bytes_) - 1, -1, -1):
                    result = bit32.bor(bit32.lshift(result, 8), bytes_[i])
            else:
                for i in range(len(bytes_)):
                    result = bit32.bor(bit32.lshift(result, 8), bytes_[i])
            return result

    def readUnicodeChar(self):
        "Reads next bytes (up to 6 from current position) as char in UTF-8 encoding. Returns string value or nil if EOF has reached."
        byteArray = [
            string.byte(self.readString(1))
        ]  # bytearray(bytes(self.readString(1)))

        nullBitPos = 0
        for i in range(1, 7):
            # Added indexing zeroth to zero.
            if bit32.band(bit32.rshift(byteArray[0][0], 7 - i), 0x1) == 0x0:
                nullBitPos = i
                break

        for i in range(1, nullBitPos - 2):
            byte = string.byte(self.readString(1))
            byteArray.append(byte)  # bytes(self.readString(1)))

        fullbytes = b"".join(byteArray)

        return "".join([chr(int(i)) for i in fullbytes])

    def read(self, format_, bytesSize=1):
        "Read from this handle in a given format."
        if isinstance(format_, int):
            return self.readString(format_)
        elif isinstance(format_, str):
            format_ = format_.replace("^%*", "").lower()

            if format_ == "a":
                return self.readAll()
            elif format_ == "l":
                return self.readLine()
            elif format_ == "b":
                return self.readBytes(1)
            elif format_ == "bs":
                return self.readBytes(bytesSize)
            elif format_ == "u":
                return self.readUnicodeChar()
            else:
                error(
                    f"Bad argument #2 ('a' (whole file), 'l' (line), 'u' (unicode char), 'b' (byte as number) or 'bs' (sequence of n bytes as number) expected, got {type(_format)})"
                )
        error(f"Bad argument #1 (int or str expected, got {type(format_)}).")

    def write(self, *write_):
        "Writes passed arguments to file. Returns True, None on success, False and reason message otherwise. Arguments may have str, int, or bool type."
        blank = _getForMode("", self.mode)
        data = blank.join((_getForMode(thing, self.mode) for thing in write_))

        # If data is small enough to fit in a buffer
        if len(data) < (BUFFER_SIZE - len(self.buffer)):
            self.buffer += data
            # Ok to exit because close writes additional data.
            return True, None
        ##        else:
        # Write current buffer content
        success, reason = self.proxy.write(self.stream, self.buffer)
        if success:
            # If data will not fit in buffer, use iterative writeing with data partitioning
            if len(data) > BUFFER_SIZE:
                for i in range(0, math.ceil(len(data) / BUFFER_SIZE), BUFFER_SIZE):
                    ##                    print(data[i:i+BUFFER_SIZE])
                    success, reason = self.proxy.write(
                        self.stream, data[i : i + BUFFER_SIZE]
                    )

                    if not success:
                        break

                # Clear buffer reserving type.
                self.buffer = self.buffer[0:0]

                return success, reason
            ##            else:
            # Data will perfectaly fit into an empty buffer
            # First clear buffer though to preserve type.
            self.buffer = self.buffer[0:0] + data
            return True, None
        ##        else:
        return False, reason

    def writeBytes(self, *args):
        "Writes passed numbers in [0; 255] range as bytes to file. Returns True, None on success, False and reason message otherwise."
        ##        if len(args) > 1:
        ##            print([string.byte(i) for i in args])
        return self.write(
            *[string.byte(i) for i in args]
        )  # b''.join(bytearray(args)).decode('utf-8'))

    def __bool__(self):
        return True

    pass


def open_(path_, mode):
    """Opens a file at the specified path for reading or writing with specified string mode. By default, mode is r. Possible modes are: r, rb, w, wb, a and ab. If file has been opened, returns file handle table or None and string error otherwise.

    Independent of mode, every handle will have a close and seek methods"""
    if not mode in ("r", "rb", "w", "wb", "a", "ab"):
        error(
            f"Bad argument #2 ('a' (whole file), 'l' (line), 'u' (unicode char), 'b' (byte as number) or 'bs' (sequence of n bytes as number) expected, got {type(_format)})"
        )
    proxy, proxyPath = get(path_)
    stream, reason = proxy.open(proxyPath, mode)

    if stream:
        handle = _Handle(proxy, stream, mode=mode)
        return handle, None
    ##    else:
    return None, reason


def copy(fromPath, toPath):
    "Tries to copy file from first path to second one. Returns True on success, False and reason message otherwise."

    def copyRecursively(fromPath, toPath):
        if isDirectory(fromPath):
            makeDirectory(toPath)

            list__ = list_(fromPath)
            for item in list__:
                copyRecursively(f"{fromPath}/{item}", f"{toPath}/{item}")
        else:
            fromHandle = open_(fromPath, "rb")
            if fromHandle:
                toHandle = open_(toPath, "wb")
                if toHandle:
                    while True:
                        chunk = fromHandle.readString(BUFFER_SIZE)
                        if chunk:
                            if not toHandle.write(chunk):
                                return False, "Cannot write chunk."
                        else:
                            toHandle.close()
                            fromHandle.close()
                            break
                return False, f'Cannot aquire handle for path "{toPath}"'
            return False, f'Cannot aquire handle for path "{fromHandle}"'
        pass

    return copyRecursively(fromPath, toPath)


def rename(fromPath, toPath):
    "Tries to rename file or directory from first path to second one. Returns True on success, False and reason message otherwise."
    fromProxy, fromProxyPath = get(fromPath)
    toProxy, toProxyPath = get(toPath)

    # If it's the same filesystem component
    if fromProxy.address == toProxy.address:
        return fromProxy.rename(fromProxyPath, toProxyPath)
    else:
        # Copy files to destination
        copy(fromPath, toPath)
        # Remove original files
        remove(fromPath)


def read(path_):
    "Reads whole file as string. Returns string data, None if reading operation was successful, None and reason message otherwise."
    handle, reason = open_(path_, "rb")
    if reason is None:
        data = handle.readAll()
        handle.close()

        return data, None
    return False, reason


def _infgen():
    x = 0
    while True:
        yield x
        x += 1


def lines(path_):
    handle, reason = open_(path_, "rb")
    if reason is None:
        return handle.lines()
    error(reason)


def readLines(path_):
    "Reads string lines from file and packs them to table. Returns table of strings, None if reading operation was successful, None and reason message otherwise."
    handle, reason = open_(path, "rb")
    if handle:
        lines, index = {}, _infgen()
        while True:
            line = handle.readLine()
            lines[next(index)] = line
            if not line:
                break
        handle.close()

        return lines, None
    return False, reason


def _writeOrAppend(append, path_, *write):
    "Return status, reason of handle.write(*args) where handle is retrieved from path_."
    makeDirectory(path(path_))

    mode = {True: "ab", False: "wb"}[bool(append)]

    handle, reason = open_(path_, mode)
    # append and 'ab' or 'wb')
    if handle:
        result, reason = handle.write(*write)
        handle.close()

        return result, reason
    return False, reason


def write(path_, *write_):
    "Overwrites file with passed data. Data can be a string, number or boolean type. Returns True, None if writing operation was successful, False and reason message otherwise."
    return _writeOrAppend(False, path_, *write_)


def append(path_, *append_):
    "Works the same way as filesystem.write(), but appends passed data to end of file without overwriting."
    return _writeOrAppend(True, path_, *append_)


def writeTable(path_, *table):
    "Serializes given table as string and writes it to file. Multiple arguments are passed to text.serialize method. Returns True, None if serializing and writing operation was successful, False and reason message otherwise."
    import Text

    serialized = Text.serialize(*table)
    del Text
    return write(path_, serialized)


def readTable(path_):
    "Reads whole file and deserializes it as table. Returns table, None if reading operation was successful, None and reason message otherwise."
    result, reason = read(path_)
    if result:
        import Text

        deserialized = Text.deserialize(result)
        del Text
        return deserialized, None
    return result, reason


def setProxy(proxy):
    "Sets the boot proxy to given proxy."
    global BOOT_PROXY
    BOOT_PROXY = proxy


def getProxy():
    "Return the boot proxy."
    return BOOT_PROXY


def loadfile(path_):
    "Load file from path as a module."
    data, reason = read(path_)
    if data:
        moduleName = hideExtension(path_)
        with open(moduleName + ".py", mode="w") as writeFile:
            writeFile.write(data)
            writeFile.close()
        import importlib
        import os

        module = importlib.import_module(moduleName)
        os.remove(moduleName + ".py")
        del os, importlib
        ##        exec(f'global {moduleName}')
        ##        exec(f'{moduleName} = module')
        return module, None
    return None, reason


def doFile(path_, *args, **kwargs):
    "Execute a given file from path with arguments."
    result, reason = loadfile(path_)
    if result:
        data = result(*args, **kwargs)
        if data:
            return data[1]
        error(data[1])
    error(reason)


BOOT_PROXY = component.BOOT_PROXY

# Mount all existing filesystem components
for address in component.list("filesystem"):
    mount(component.proxy(address), paths.system.mounts + address + "/")


# Automatically mount/unmount filesystem components
def _addRemoveComponents(signal, address, type_):
    if signal == "component_added" and type_ == "filesystem":
        mount(component.proxy(address), paths.system.mounts + address + "/")
    elif signal == "component_removed" and type_ == "filesystem":
        unmount(address)


event.addHandler(_addRemoveComponents)

list = list_
open = open_
