def foo(a: s32) -> Tuple[s32, str]:
    return 2 * a, 'Bar'


def main(args: List[str]):
    print(foo(s32(args[1])))
