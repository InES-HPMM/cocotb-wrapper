"""This type stub file was generated by pyright."""

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

class Memory:
    def __init__(self, size=..., mem=..., **kwargs) -> None: ...
    def read(self, address, length):  # -> int | bytes | None:
        ...
    def write(self, address, data):  # -> None:
        ...
    def write_words(self, address, data, byteorder=..., ws=...):  # -> None:
        ...
    def write_dwords(self, address, data, byteorder=...):  # -> None:
        ...
    def write_qwords(self, address, data, byteorder=...):  # -> None:
        ...
    def write_byte(self, address, data):  # -> None:
        ...
    def write_word(self, address, data, byteorder=..., ws=...):  # -> None:
        ...
    def write_dword(self, address, data, byteorder=...):  # -> None:
        ...
    def write_qword(self, address, data, byteorder=...):  # -> None:
        ...
    def read_words(
        self, address, count, byteorder=..., ws=...
    ):  # -> list[Any]:
        ...
    def read_dwords(self, address, count, byteorder=...):  # -> list[Any]:
        ...
    def read_qwords(self, address, count, byteorder=...):  # -> list[Any]:
        ...
    def read_byte(self, address):  # -> int:
        ...
    def read_word(self, address, byteorder=..., ws=...): ...
    def read_dword(self, address, byteorder=...): ...
    def read_qword(self, address, byteorder=...): ...
    def hexdump(self, address, length, prefix=...):  # -> None:
        ...
    def hexdump_lines(self, address, length, prefix=...):  # -> list[Any]:
        ...
    def hexdump_str(self, address, length, prefix=...):  # -> LiteralString:
        ...
