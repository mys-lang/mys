import binascii


def crc_srec(hexstr):
    crc = sum(binascii.unhexlify(hexstr))
    crc &= 0xff
    crc ^= 0xff

    return crc


def unpack_srec(record: str) -> Tuple[str, int, int, str]:
    if len(record) < 6:
        raise Error()

    if record[0] != 'S':
        raise Error()

    value = bytearray.fromhex(record[2:])
    size = value[0]

    if size != len(value) - 1:
        raise Error()

    type_ = record[1]

    if type_ in '0159':
        width = 2
    elif type_ in '268':
        width = 3
    elif type_ in '37':
        width = 4
    else:
        raise Error()

    data_offset = (1 + width)
    address = int.from_bytes(value[1:data_offset], byteorder='big')
    data = value[data_offset:-1]
    actual_crc = value[-1]
    expected_crc = crc_srec(record[2:-2])

    if actual_crc != expected_crc:
        raise Error()

    return (type_, address, len(data), data)


def run() -> int:
    records = [
        'S214400254040000001000000001000000474E550056',
        'S2144002640000000002000000060000001800000025',
        'S214400274040000001400000003000000474E550030',
        'S214400284BB192DAB28022B1866A9BC5BBD1359DBE2',
        'S2084002942F4F95AF5F'
    ]
    result = []

    for record in records:
        result.append(unpack_srec(record))

    return sum([l for _, _, l, _ in result])
    

def main():
    result = 0

    for _ in range(10000):
        result += run()

    print('Result:', result)
