import crccheck

class CrcCustom(crccheck.crc.CrcBase):
    _names = ('CRC/Custom',)
    _width = 7
    _poly = 0xb7
    _initvalue = 0x00
    _reflect_input = False
    _reflect_output = False
    _xor_output = 0x00
    _check_result = 0x04
    _residue = 0x00

def test():
    crc = CrcCustom()
    crc.selftest()
    crc.reset()
    crc.process(bytearray(b"123456789"))
    crc_out = crc.final()
    print(hex(crc_out))
    crc.process([crc_out<<1])
    print(crc.finalhex())

test()