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

    def priority(self, t):
        return ord(t) - 96 if t >= "a" else ord(t) - 38

    def first_part(self):
        total = 0
        for items in self.data:
            duplicate = set(items[0:len(items) >> 1]) & set(items[len(items) >> 1:])
            assert len(duplicate) == 1
            v = self.priority(duplicate.pop())
            total += v
        return total

    def second_part(self):
        total = 0
        for group in batched(self.data, 3):
            shared = set(group.pop())
            while group:
                shared &= set(group.pop())
            assert len(shared) == 1
            v = self.priority(shared.pop())
            total += v
        return total


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
    print(s.first_part() if not PART2 else s.second_part())
