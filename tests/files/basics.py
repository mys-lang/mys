def foo(a: int) -> (int, str):
    return 2 * a, 'Bar'


def main(args: [str]):
    print(foo(int(args[1])))
