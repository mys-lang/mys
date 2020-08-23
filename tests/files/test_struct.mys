import struct


def main():
    packed = struct.pack('>I', 1)
    unpacked = struct.unpack('>I', packed)
    assert unpacked == (1, )

    packed = struct.pack('>I', 1)
    unpacked = struct.unpack('>I', packed)[0]
    assert unpacked == 1

    packed = struct.pack('>Ii', 1, -1)
    unpacked = struct.unpack('>Ii', packed)
    assert unpacked == (1, -1)

    # Not supported.

    # fmt = '>I'
    # packed = struct.pack(fmt, 1)
    # unpacked = struct.unpack(fmt, packed)
    # assert unpacked == (1, )
