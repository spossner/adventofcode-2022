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
from aoc import Point, Rect, NORTH, rot_ccw, rot_cw, translate, direct_adjacent_iter
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

    def first_part(self, is_part1=True):
        h = len(self.data)
        w = len(self.data[0])
        starting_points = []
        for y, row in enumerate(self.data):
            row = list(map(ord, row))
            self.data[y] = row
            if 83 in row:
                pos = row.index(83)
                start = Point(pos, y)
                row[pos] = 97

            if 69 in row:
                pos = row.index(69)
                dest = Point(pos, y)
                row[pos] = 122

            for pos, v in enumerate(row):
                if v == 97:
                    starting_points.append(Point(pos, y))
        # print(self.data, w, h, start, dest)
        print(starting_points)
        if is_part1:
            starting_points = [start]

        results = []
        for start in starting_points:
            # bfs
            result = 0
            seen = set()
            queue = deque()
            queue.append(start)
            while queue:
                for i in range(len(queue)):
                    pos = queue.popleft()
                    if pos == dest:
                        results.append(result)
                        queue.clear()
                        break
                    if (pos in seen):
                        continue
                    seen.add(pos)
                    # print(f"checking {pos}")
                    for next_pos in direct_adjacent_iter(pos, w, h):
                        if next_pos in seen:
                            continue
                        v = self.data[pos.y][pos.x]
                        new_v = self.data[next_pos.y][next_pos.x]
                        if new_v <= v + 1:
                            # print(f"  {next_pos}: {chr(new_v)} reachable from {chr(v)}")
                            queue.append(next_pos)
                result += 1
        return list(sorted(results))

    def second_part(self):
        return self.first_part(False)


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = True

    STRIP = True
    SPLIT_LINES = True
    SPLIT_CHAR = ''
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
