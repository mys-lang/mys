def func_1(a: int) -> (int, str):
    return 2 * a, 'Bar'


def func_2(a: int, b: int=1) -> int:
    return a * b


def func_3(a: Optional[int]) -> int:
    if a is None:
        return 0
    else:
        return 2 * a


def func_4(a: int) -> {int: [float]}:
    return {10 * a: [7.5, -1.0]}


def main(args: [str]):
    value = int(args[1])
    print('func_1(value):', func_1(value))
    print('func_2(value):', func_2(value))
    print('func_3(None): ', func_3(None))
    print('func_3(value):', func_3(value))
    print('func_4(value):', func_4(value))

