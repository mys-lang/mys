# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""
Functions to manipulate packed binary representations of number sets.

To save space, coverage stores sets of line numbers in SQLite using a packed
binary representation called a numbits.  A numbits is a set of positive
integers.

A numbits is stored as a blob in the database.  The exact meaning of the bytes
in the blobs should be considered an implementation detail that might change in
the future.  Use these functions to work with those binary blobs of data.

"""
import json
from itertools import zip_longest


def nums_to_numbits(nums):
    """Convert `nums` into a numbits.

    Arguments:
        nums: a reusable iterable of integers, the line numbers to store.

    Returns:
        A binary blob.
    """
    try:
        nbytes = max(nums) // 8 + 1
    except ValueError:
        # nums was empty.
        return b''
    bb = bytearray(nbytes)
    for num in nums:
        bb[num//8] |= 1 << num % 8
    return bytes(bb)


def numbits_to_nums(numbits):
    """Convert a numbits into a list of numbers.

    Arguments:
        numbits: a binary blob, the packed number set.

    Returns:
        A list of ints.

    When registered as a SQLite function by :func:`register_sqlite_functions`,
    this returns a string, a JSON-encoded list of ints.

    """
    nums = []
    for byte_i, byte in enumerate(numbits):
        for bit_i in range(8):
            if (byte & (1 << bit_i)):
                nums.append(byte_i * 8 + bit_i)
    return nums


def numbits_union(numbits1, numbits2):
    """Compute the union of two numbits.

    Returns:
        A new numbits, the union of `numbits1` and `numbits2`.
    """
    byte_pairs = zip_longest(numbits1, numbits2, fillvalue=0)
    return bytes(b1 | b2 for b1, b2 in byte_pairs)


def numbits_intersection(numbits1, numbits2):
    """Compute the intersection of two numbits.

    Returns:
        A new numbits, the intersection `numbits1` and `numbits2`.
    """
    byte_pairs = zip_longest(numbits1, numbits2, fillvalue=0)
    intersection_bytes = bytes(b1 & b2 for b1, b2 in byte_pairs)
    return intersection_bytes.rstrip(b'\0')


def numbits_any_intersection(numbits1, numbits2):
    """Is there any number that appears in both numbits?

    Determine whether two number sets have a non-empty intersection. This is
    faster than computing the intersection.

    Returns:
        A bool, True if there is any number in both `numbits1` and `numbits2`.
    """
    byte_pairs = zip_longest(numbits1, numbits2, fillvalue=0)
    return any(b1 & b2 for b1, b2 in byte_pairs)


def num_in_numbits(num, numbits):
    """Does the integer `num` appear in `numbits`?

    Returns:
        A bool, True if `num` is a member of `numbits`.
    """
    nbyte, nbit = divmod(num, 8)
    if nbyte >= len(numbits):
        return False
    return bool(numbits[nbyte] & (1 << nbit))


def register_sqlite_functions(connection):
    connection.create_function("numbits_union", 2, numbits_union)
    connection.create_function("numbits_intersection",
                               2,
                               numbits_intersection)
    connection.create_function("numbits_any_intersection",
                               2,
                               numbits_any_intersection)
    connection.create_function("num_in_numbits", 2, num_in_numbits)
    connection.create_function("numbits_to_nums",
                               1,
                               lambda b: json.dumps(numbits_to_nums(b)))
