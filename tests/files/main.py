from typing import Tuple
from typing import List
from typing import Optional

u8 = int
u64 = int
s8 = int
s32 = int
f64 = float

# Explicit types.
ve1: u8 = 1
ve2: s8 = -4
ve3: f64 = 1.2
ve4: str = 'apa'
ve5: Tuple[str, f64] = ('hello', 5.6)
ve6: List[Tuple[u8, s8]] = [(ve1, ve2), (2, 6)]
ve7: List[u8] = [v + k for v, k in ve6]
ve8: Optional[u8] = None
ve8 = 5
ve9: Optional[List[str]] = None
ve9 = ['foo']

print("ve1: ", ve1)
print("ve2: ", ve2)
print("ve3: ", ve3)
print("ve4: ", ve4)
print("ve8: ", ve8)

# Inferred types.
vi1 = ve1  # Same type as v1 (u8)
vi2 = 99  # s32 by default
vi3 = 9999999999  # s64 by default for big integers
vi4 = 1.2  # f32 by default
vi5 = 'apa'  # A string
vi6 = ('hello', 5.6)  # Tuple of str and f32
vi7 = [(vi1, vi2), (2, 6)]
vi8 = [2 * v for v in [1, 2, 3]]  # List of s32
vi9 = {'1': 1, '2': 2}

print("vi1: ", vi1)
print("vi2: ", vi2)
print("vi3: ", vi3)
print("vi4: ", vi4)
print("vi5: ", vi5)

# Functions must always be typed.
def f1(a: s32) -> Tuple[s32, s32]:
    return 2 * a, 6

# i becomes s32 by default
for i in range(5):
    print(i)

# Read strings. fin becomes TextIO.
with open('tests/files/main.py') as tfin:
    for line in tfin:
        if 'main.py' in line:
            print(line)

# Read bytes. fin becomes BinaryIO.
with open('tests/files/main.py', 'rb') as bfin:
    print(bfin.read(10))

# # This is not supported. fin becomes IO[Any].
# mode = 'r'
#
# with open('tests/files/main.py', mode) as fin:
#     print(fin.read(10))

# Wrap around is silently ignored by default. Possibly add an option to
# raise an overflow exception.
a: u8 = 255
a += 1

# Inheritance.
class A:

    def __init__(self):
        self.value: u64 = 0

    def add(self, value: u64):
        raise NotImplementedError()

class B(A):

    def add(self, value: u64):
        self.value += value

class C(A):

    def add(self, value: u64):
        self.value += (2 * value)

b = B()
assert not isinstance(b, C)
assert isinstance(b, B)
assert isinstance(b, A)
c = C()
assert isinstance(c, C)
assert not isinstance(c, B)
assert isinstance(c, A)
b.add(2)
c.add(1)
assert b.value == c.value
