def my_func(a: int) -> (int, str):
    return 2 * a, 'Bar'


def main(args: [str]):
    print(my_func(int(args[1])))
