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
from aoc import Point, Rect, NORTH, rot_ccw, rot_cw, translate, get_ints
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

    def parse_input(self):
        i = 0
        stacks = [[] for _ in range(10)]
        while (self.data[i][0:10] != " 1   2   3"):
            row = self.data[i]
            j = 0;
            stack = 1
            while (j < len(row)):
                crate = row[j + 1:j + 2].strip()
                if crate:
                    stacks[stack].insert(0, crate)
                stack += 1
                j += 4
            i += 1
        i += 2
        moves = []
        while i < len(self.data):
            moves.append(get_ints(self.data[i]))
            i += 1
        return stacks, moves

    def first_part(self):
        stacks, moves = self.parse_input()

        for c, src, dst in moves:
            for _ in range(c):
                stacks[int(dst)].append(stacks[int(src)].pop())

        for s in stacks:
            if s:
                print(s[-1], end="")
        print()

    def second_part(self):
        stacks, moves = self.parse_input()
        print(stacks)
        for c, src, dst in moves:
            s = int(src)
            d = int(dst)
            load = stacks[s][-c:]
            new_src = stacks[s][0:-c]
            # print(c, s, d, stacks[s], load, new_src)
            stacks[s] = new_src
            stacks[d].extend(load)
            #
            # stacks[int(dst)].extend()
            # for _ in range(c):
            #     stacks[int(dst)].append(stacks[int(src)].pop())
        for s in stacks:
            if s:
                print(s[-1], end="")
        print()


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = True

    STRIP = False
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
