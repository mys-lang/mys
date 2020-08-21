import struct

PB_CONFIG_A_ENABLED: u32 = (1 << 0)
PB_CONFIG_B_ENABLED: u32 = (1 << 1)
PB_CONFIG_A_VERIFIED: u32 = (1 << 0)
PB_CONFIG_B_VERIFIED: u32 = (1 << 1)


def bool_string(value: bool) -> str:
    if value:
        return 'true'
    else:
        return 'false'


def is_bit_set(value: u32, bit: u32) -> bool:
    return bool_string((value & bit) == bit)


def command_pbconfig_print_system(system: str,
                                  enabled: u32,
                                  verified: u32,
                                  enabled_bit: u32,
                                  verified_bit: u32):
    print('System', system, ':')
    print('  Enabled: ', is_bit_set(enabled, enabled_bit))
    print('  Verified:', is_bit_set(verified, verified_bit))


def command_pbconfig_status():
    with open('/dev/mmcblk0p5', 'rb') as fin:
        config = fin.read(512)

    enabled = struct.unpack('I', config[4:8])[0]
    verified = struct.unpack('I', config[8:12])[0]

    command_pbconfig_print_system(enabled,
                                  verified,
                                  'A',
                                  PB_CONFIG_A_ENABLED,
                                  PB_CONFIG_A_VERIFIED)
    command_pbconfig_print_system(enabled,
                                  verified,
                                  'B',
                                  PB_CONFIG_B_ENABLED,
                                  PB_CONFIG_B_VERIFIED)

    return True


def command_pbconfig(args: List[str]):
    ok: bool = False

    if len(args) == 2:
        if args[1] == 'reset':
            pass
        elif args[1] == 'status':
            ok = command_pbconfig_status()

    if not ok:
        print('Usage: pbconfig {reset,status}')
