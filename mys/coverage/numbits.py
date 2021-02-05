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
