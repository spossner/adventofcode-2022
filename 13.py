import functools
import os
import sys
import math
import operator
import re
from collections import deque, defaultdict, namedtuple, Counter
from functools import total_ordering, reduce
from itertools import permutations, zip_longest, count
from os.path import exists
import bisect

import requests
import networkx as nx
import numpy as np
from aoc import Point, Rect, NORTH, rot_ccw, rot_cw, translate, batched
from dotenv import load_dotenv

load_dotenv()


class Solution:
    def __init__(self, data, modified=False, dev=False, do_strip=False, do_splitlines=True, split_char=None):
        if data and do_strip and type(data) == str:
            data = data.strip()
        if data and do_splitlines and type(data) == str:
            data = data.splitlines()
        if data and split_char is not None:
            if split_char == '':
                data = [list(row) for row in data] if do_splitlines else list(data)
            else:
                data = [row.split(split_char) for row in data] if do_splitlines else data.split(split_char)
        self.data = data
        self.modified = modified
        self.dev = dev

    def check(self, left, right):
        """
        checks the two given values.
        :param left: the left value
        :param right:
        :return: True if in correct order, False if in incorrect order, None if not decided - continue checking
        """
        if type(left) == int:
            if type(right) == int:
                if left < right:
                    return True
                if left > right:
                    return False
                return None
            else:
                # right is a list
                return self.check([left], right)
        else:
            # left is a list
            if type(right) == int:
                # right is int
                return self.check(left, [right])
            else:
                ptr = 0
                sub_check = None
                while ptr < len(left) and ptr < len(right) and sub_check is None:
                    sub_check = self.check(left[ptr], right[ptr])
                    ptr += 1
                if sub_check is not None:  # found decision
                    return sub_check
                if ptr < len(right):  # left ran out of items
                    return True
                if ptr < len(left):  # right ran out of items
                    return False
                return None  # otherwise continue checking

    def first_part(self, is_part1=True):
        result = 0
        for id, rows in enumerate(batched(self.data, 3)):
            l1 = eval(rows[0])
            l2 = eval(rows[1])
            check = self.check(l1, l2)
            if check:
                result += (id + 1)

        return result

    def compare(self, l1, l2):
        check = self.check(l1, l2)
        if check is None:
            return 0
        elif check:
            return -1
        else:
            return 1

    def second_part(self):
        rows = list(map(eval, filter(lambda row: row != "", self.data)))
        divider = [[[2]], [[6]]]
        rows.extend(divider)

        rows.sort(key=functools.cmp_to_key(self.compare))
        return (rows.index(divider[0]) + 1) * (rows.index(divider[1]) + 1)


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = True

    STRIP = True
    SPLIT_LINES = True
    SPLIT_CHAR = None
    DATA = None
    AOC_SESSION = os.environ.get('AOC_SESSION')

    DATA_URL = f"https://adventofcode.com/2022/day/{int(script)}/input"

    if not DATA:
        file_name = f"{script}-dev{DEV if type(DEV) != bool else ''}.txt" if DEV else f"{script}.txt"
        if exists(file_name):
            with open(file_name) as f:
                DATA = f.read()
        elif AOC_SESSION and DATA_URL:
            DATA = requests.get(DATA_URL, headers={'Cookie': f"session={AOC_SESSION}"}).text
            with open(file_name, "w") as f:
                f.write(DATA)

    s = Solution(DATA, PART2, DEV, STRIP, SPLIT_LINES, SPLIT_CHAR)
    print("RESULT", s.first_part() if not PART2 else s.second_part())
