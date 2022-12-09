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
from aoc import Point, Rect, NORTH, rot_ccw, rot_cw, translate, WEST, SOUTH, EAST, manhattan_distance
from dotenv import load_dotenv

load_dotenv()

DIRS = {
    'U': NORTH,
    'D': SOUTH,
    'L': WEST,
    'R': EAST,
}


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

    def calculate_new_pos(self, p1, p2):
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        if abs(dx) < 2 and abs(dy) < 2:
            print(p1, p2, "skpped")
            return p2

        dx = (dx / 2.0)
        dx = math.ceil(dx) if dx > 0 else math.floor(dx)
        dy = (dy / 2.0)
        dy = math.ceil(dy) if dy > 0 else math.floor(dy)

        new_p2 = Point(p2.x + dx, p2.y + dy)
        print(p1, new_p2, f"[{dx},{dy}]")
        return new_p2

    def first_part(self):
        seen = set()
        head = tail = Point(0, 0)
        seen.add(tail)
        for move in self.data:
            for i in range(int(move[1])):
                head = translate(head, DIRS[move[0]])
                tail = self.calculate_new_pos(head, tail)
                seen.add(tail)
        return len(seen)

    def second_part(self, knot_count=10):
        seen = set()
        knots = [Point(0, 0) for _ in range(knot_count)]
        print(knots)
        seen.add(knots[-1])  # last know is tail
        for move in self.data:
            for i in range(int(move[1])):
                knots[0] = translate(knots[0], DIRS[move[0]])
                for i in range(1, knot_count):
                    knots[i] = self.calculate_new_pos(knots[i - 1], knots[i])
                seen.add(knots[-1])  # finally store seen position of tail
        return len(seen)


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = True

    STRIP = True
    SPLIT_LINES = True
    SPLIT_CHAR = ' '
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
