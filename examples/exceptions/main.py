def divide(a: int, b: int) -> int:
    try:
        return a / b
    except ZeroDivisionError as e:
        print('ZeroDivisionError:', e)
    except:
        print(e)


def main():
    divide(1, 0)
