"""This type stub file was generated by pyright."""

import enum

"""

Copyright (c) 2020 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

class AxiBurstType(enum.IntEnum):
    FIXED = ...
    INCR = ...
    WRAP = ...

class AxiBurstSize(enum.IntEnum):
    SIZE_1 = ...
    SIZE_2 = ...
    SIZE_4 = ...
    SIZE_8 = ...
    SIZE_16 = ...
    SIZE_32 = ...
    SIZE_64 = ...
    SIZE_128 = ...

class AxiLockType(enum.IntEnum):
    NORMAL = ...
    EXCLUSIVE = ...

class AxiCacheBit(enum.IntFlag):
    B = ...
    M = ...
    RA = ...
    WA = ...

ARCACHE_DEVICE_NON_BUFFERABLE = ...
ARCACHE_DEVICE_BUFFERABLE = ...
ARCACHE_NORMAL_NON_CACHEABLE_NON_BUFFERABLE = ...
ARCACHE_NORMAL_NON_CACHEABLE_BUFFERABLE = ...
ARCACHE_WRITE_THROUGH_NO_ALLOC = ...
ARCACHE_WRITE_THROUGH_READ_ALLOC = ...
ARCACHE_WRITE_THROUGH_WRITE_ALLOC = ...
ARCACHE_WRITE_THROUGH_READ_AND_WRITE_ALLOC = ...
ARCACHE_WRITE_BACK_NO_ALLOC = ...
ARCACHE_WRITE_BACK_READ_ALLOC = ...
ARCACHE_WRITE_BACK_WRITE_ALLOC = ...
ARCACHE_WRITE_BACK_READ_AND_WRITE_ALLOC = ...
AWCACHE_DEVICE_NON_BUFFERABLE = ...
AWCACHE_DEVICE_BUFFERABLE = ...
AWCACHE_NORMAL_NON_CACHEABLE_NON_BUFFERABLE = ...
AWCACHE_NORMAL_NON_CACHEABLE_BUFFERABLE = ...
AWCACHE_WRITE_THROUGH_NO_ALLOC = ...
AWCACHE_WRITE_THROUGH_READ_ALLOC = ...
AWCACHE_WRITE_THROUGH_WRITE_ALLOC = ...
AWCACHE_WRITE_THROUGH_READ_AND_WRITE_ALLOC = ...
AWCACHE_WRITE_BACK_NO_ALLOC = ...
AWCACHE_WRITE_BACK_READ_ALLOC = ...
AWCACHE_WRITE_BACK_WRITE_ALLOC = ...
AWCACHE_WRITE_BACK_READ_AND_WRITE_ALLOC = ...

class AxiProt(enum.IntFlag):
    PRIVILEGED = ...
    NONSECURE = ...
    INSTRUCTION = ...

class AxiResp(enum.IntEnum):
    OKAY = ...
    EXOKAY = ...
    SLVERR = ...
    DECERR = ...
