def fibonaccis(count: int) -> (int, int):
    curr = 0
    next = 1
    i = 0

    while i < count:
        yield (i, curr)
        temp = curr
        curr = next
        next += temp
        i += 1

class Fibonaccis:

    def __init__(self, count: int):
        self._curr = None
        self._next = None
        self._i = None
        self._count = count
        self._state = 0

    def next(self) -> (int, int):
        while True:
            if self._state == 0:
                self._curr = 0
                self._next = 1
                self._i = 0
                self._state = 1
            elif self._state == 1:
                if self._i < self._count:
                    self._state = 2

                    return (self._i, self._curr)
                else:
                    self._state = 3
            elif self._state == 2:
                temp = self._curr
                self._curr = self._next
                self._next += temp
                self._i += 1
                self._state = 1
            elif self._state == 3:
                raise RuntimeError()

def main():
    fibonaccis = Fibonaccis(10)

    while True:
        try:
            index, number = fibonaccis.next()
        except RuntimeError:
            break

        print(f"fibonacci({index}): {number}")

main()


def foo():
    yield 1

class Foo:

    def __init__(self):
        self._state = 0

    def next(self):
        while True:
            if self._state == 0:
                self._state = 1

                return 1
            elif self._state == 1:
                raise RuntimeError()

def main():
    foo = Foo()

    while True:
        try:
            number = foo.next()
        except RuntimeError:
            break

        print(f"foo(): {number}")

main()

def bar(ok):
    if ok:
        yield 1
    else:
        i = 3

        while i < 5:
            yield i
            i += 1

    yield 10

class Bar:

    def __init__(self, ok):
        self._ok = ok
        self._state = 0
        self._i = None

    def next(self):
        while True:
            if self._state == 0:
                if self._ok:
                    self._state = 1

                    return 1
                else:
                    self._i = 3
                    self._state = 3
            elif self._state == 1:
                self._state = 2

                return 10
            elif self._state == 2:
                raise RuntimeError()
            elif self._state == 3:
                if self._i < 5:
                    i = self._i
                    self._state = 3
                    self._i += 1

                    return i
                else:
                    self._state = 1

def main():
    bar = Bar(True)

    while True:
        try:
            number = bar.next()
        except RuntimeError:
            break

        print(f"bar(): {number}")

    bar = Bar(False)

    while True:
        try:
            number = bar.next()
        except RuntimeError:
            break

        print(f"bar(): {number}")

main()

def fie():
    for number in bar(False):
        yield 2 * number

    yield -1

class Fie:

    def __init__(self):
        self._state = 0
        self._bar = None

    def next(self):
        while True:
            if self._state == 0:
                self._bar = Bar(False)
                self._state = 1
            elif self._state == 1:
                try:
                    return 2 * self._bar.next()
                except RuntimeError:
                    self._state = 2
            elif self._state == 2:
                self._state = 3

                return -1
            elif self._state == 3:
                raise RuntimeError()

def main():
    fie = Fie()

    while True:
        try:
            number = fie.next()
        except RuntimeError:
            break

        print(f"fie(): {number}")

main()
