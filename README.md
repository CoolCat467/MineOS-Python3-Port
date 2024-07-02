## MineOS Python3 Port

This is my attempt at porting MineOS to Python3.
Mostly to learn how MineOS functions, but also as a challenge to self.

This is in no way ready to function properly.

Current Status:

Parts of the computer component is implemented, but not much.
Component proxy is almost completely implemented.
Component module is almost completely implemented, but some functions may be broken.
Color API is completely implemented.
Bit32 is completely implemented, but may have typographical issues.
Screen is partially implemented.
Event API is mostly implemented, maybe fully.
Paths API is completely implemented.
Sides API is completely implemented.
Filesystem API is implemented, but loadfile is probably broken and numerouse issues have been observed with the handler class, some coming from component.Proxy.
Filesystem API write is known to function properly, reading may be broken.
Image API is completely implemented, but I am having difficulties getting encoding method six to load files, and saving images works for the most part.
I have observed that small images can be saved and loaded successfully, larger ones break. I suspect that the digit bytes for length of packet are being loaded improperly, as it reaches EOF prematurely.


Anything not listed above is not implemented.
