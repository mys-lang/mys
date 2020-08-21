def foo(a: s32) -> (s32, str):
    return 2 * a, 'Bar'


def main(args: [str]):
    print(foo(s32(args[1])))
