import os
import sys
import math
import operator
import re
from collections import *
from enum import Enum
from functools import *
from itertools import *
from os.path import exists
import bisect

import requests
import networkx as nx
import numpy as np
from aoc import *
from dotenv import load_dotenv

load_dotenv()

DEV = False
PART2 = True

STRIP = False
SPLIT_LINES = True
SPLIT_CHAR = None
DATA = None
AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022

FACING_EAST = 0
FACING_SOUTH = 1
FACING_WEST = 2
FACING_NORTH = 3

DIRS = (EAST, SOUTH, WEST, NORTH)
ICON = ['>', 'v', '<', '^']

WARP = {
    (6, FACING_EAST): (11, 90, FACING_SOUTH),
    (10, FACING_SOUTH): (4, 180, FACING_NORTH),
    (5, FACING_NORTH): (2, 90, FACING_EAST)
} if DEV else {
    (1, FACING_WEST): (8, 180, FACING_EAST),
    (1, FACING_NORTH): (12, 90, FACING_EAST),
    (2, FACING_NORTH): (12, 0, FACING_NORTH),
    (2, FACING_SOUTH): (5, 90, FACING_WEST),
    (2, FACING_EAST): (9, 180, FACING_WEST),
    (5, FACING_EAST): (2, 270, FACING_NORTH),
    (5, FACING_WEST): (8, 270, FACING_SOUTH),
    (8, FACING_WEST): (1, 180, FACING_EAST),
    (8, FACING_NORTH): (5, 90, FACING_EAST),
    (9, FACING_EAST): (2, 180, FACING_WEST),
    (9, FACING_SOUTH): (12, 90, FACING_WEST),
    (12, FACING_EAST): (9, 270, FACING_NORTH),
    (12, FACING_WEST): (1, 270, FACING_SOUTH),
    (12, FACING_SOUTH): (2, 0, FACING_SOUTH),
}


class Solution:
    def __init__(self, data):
        if data and STRIP and type(data) == str:
            data = data.strip()
        if data and SPLIT_LINES and type(data) == str:
            data = data.splitlines()
        if data and SPLIT_CHAR is not None:
            if SPLIT_CHAR == '':
                data = [list(row) for row in data] if SPLIT_LINES else list(data)
            else:
                data = [row.split(SPLIT_CHAR) for row in data] if SPLIT_LINES else data.split(SPLIT_CHAR)
        self.data = data

    def get_surface(self, p, cube_size):
        return int(p.x / cube_size) + int(p.y / cube_size) * 4

    def rotate(self, cube_point, cube_size, degrees=90):
        rot = Point(cube_size - 1 - cube_point.y, cube_point.x)
        if degrees == 0:
            return cube_point
        if degrees == 90:
            return rot
        if degrees == 180:
            return self.rotate(rot, cube_size)
        if degrees == 270:
            return self.rotate(rot, cube_size, 180)
        raise ValueError(f"unsupported degrees of {degrees}")

    def warp(self, cube_point, cube_size, w):
        cube_point = self.rotate(cube_point, cube_size, w[1])  # rotate cube point
        cube_point = Point(cube_point.x + (w[0] % 4) * cube_size,
                           cube_point.y + int(w[0] / 4) * cube_size)  # translate to new surface
        return cube_point, w[2]

    def first_part(self):
        w = 0
        h = 0
        cube_size = 4 if DEV else 50
        result = 0
        offsets = []
        p = re.compile("\s*([#.]+)\s*")
        for row in self.data:
            if not row:
                break
            m = p.match(row)
            offsets.append(m.span(1))
            w = max(w, len(row))
            h += 1
        grid = list(map(list, self.data[0:h]))
        columns = []
        for i in range(w):
            top = 0
            bottom = h - 1
            while i >= len(grid[top]) or grid[top][i] == " ":
                top += 1
            while i >= len(grid[bottom]) or grid[bottom][i] == " ":
                bottom -= 1
            columns.append((top, bottom + 1))  # add top-bottom span excluding bottom position
        pos = Point(offsets[0][0], 0)
        facing = 0  # index in DIRS
        path = re.findall("(\d+|[RL])", self.data[-1])
        print(pos, path, facing, DIRS[facing], columns, WARP)
        for cmd in path:
            if cmd.isnumeric():
                steps = int(cmd)
                for _ in range(steps):
                    new_pos = translate(pos, DIRS[facing])
                    new_facing = facing

                    # PART 2
                    if PART2:
                        src_surface = self.get_surface(pos, cube_size)
                        cube_point = Point(new_pos.x % cube_size, new_pos.y % cube_size)

                    if facing == FACING_EAST and new_pos.x >= offsets[new_pos.y][1]:
                        if PART2:
                            print(pos, new_pos, src_surface, ICON[facing])
                            new_pos, new_facing = self.warp(cube_point, cube_size, WARP[(src_surface, facing)])
                        else:
                            new_pos = Point(offsets[new_pos.y][0], new_pos.y)
                    elif facing == FACING_WEST and new_pos.x < offsets[new_pos.y][0]:
                        if PART2:
                            print(pos, new_pos, src_surface, ICON[facing])
                            new_pos, new_facing = self.warp(cube_point, cube_size, WARP[(src_surface, facing)])
                        else:
                            new_pos = Point(offsets[new_pos.y][1] - 1, new_pos.y)
                    elif facing == FACING_NORTH and new_pos.y < columns[new_pos.x][0]:
                        if PART2:
                            print(pos, new_pos, src_surface, ICON[facing])
                            new_pos, new_facing = self.warp(cube_point, cube_size, WARP[(src_surface, facing)])
                        else:
                            new_pos = Point(new_pos.x, columns[new_pos.x][1] - 1)
                    elif facing == FACING_SOUTH and new_pos.y >= columns[new_pos.x][1]:
                        if PART2:
                            print(pos, new_pos, src_surface, ICON[facing])
                            new_pos, new_facing = self.warp(cube_point, cube_size, WARP[(src_surface, facing)])
                        else:
                            new_pos = Point(new_pos.x, columns[new_pos.x][0])
                    else:
                        # no warping
                        pass
                    if grid[new_pos.y][new_pos.x] == "#":  # blocked
                        break
                    else:
                        grid[pos.y][pos.x] = ICON[facing]
                        pos = new_pos
                        facing = new_facing
            else:
                if cmd == "R":
                    facing = (facing + 1) % len(DIRS)
                else:
                    assert cmd == "L"
                    facing = (facing - 1) % len(DIRS)
                grid[pos.y][pos.x] = ICON[facing]

        if DEV: self.dump(grid)
        return (pos.y + 1) * 1000 + (pos.x + 1) * 4 + facing

    def dump(self, grid):
        for row in grid:
            print("".join(row))
        print()

    def second_part(self):
        return self.first_part()


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DATA_URL = f"https://adventofcode.com/{YEAR}/day/{int(script)}/input"

    if not DATA:
        file_name = f"{script}-dev{DEV if type(DEV) != bool else ''}.txt" if DEV else f"{script}.txt"
        if exists(file_name):
            with open(file_name) as f:
                DATA = f.read()
        elif AOC_SESSION and DATA_URL:
            DATA = requests.get(DATA_URL, headers={'Cookie': f"session={AOC_SESSION}"}).text
            with open(file_name, "w") as f:
                f.write(DATA)

    print(f"DAY {int(script)}")
    s = Solution(DATA)
    print("RESULT", s.first_part() if not PART2 else s.second_part())
