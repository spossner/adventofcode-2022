import os
import random
import sys
import math
import operator
import re
from collections import *
from functools import *
from itertools import *
from os.path import exists
import bisect

import requests
from aoc import *
from dotenv import load_dotenv

load_dotenv()

DEV = False
PART2 = True

STRIP = True
SPLIT_LINES = True
SPLIT_CHAR = None
DATA = None
# '''#.#####
# #.....#
# #>....#
# #.....#
# #...v.#
# #.....#
# #####.#'''
AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022

DIRS = (EAST, SOUTH, WEST, NORTH)
ICONS = ['>', 'v', '<', '^']
DIR_ICONS = {
    EAST: '>',
    SOUTH: 'v',
    WEST: '<',
    NORTH: '^',
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
        self.w = len(self.data[0]) - 2  # cut away the walls
        self.h = len(self.data) - 2
        self.queue = deque()
        self.states = [None] * 601
        self.loop = None
        self.create_states()

    def create_states(self):
        state = defaultdict(list)
        for y, row in enumerate(self.data[1:-1]):
            for x, v in enumerate(row[1:-1]):
                if v in ICONS:
                    state[Point(x, y)].append(DIRS[ICONS.index(v)])
        self.states[0] = state

        for i in range(1, len(self.states)):
            state = defaultdict(list)
            for s, d_list in self.states[0].items():
                d = d_list[0]
                np = Point((s.x + d.x * i) % self.w, (s.y + d.y * i) % self.h)
                state[np].append(d)

            if state.keys() == self.states[0].keys():
                self.loop = i
                print(f"FOUND LOOP IN MINUTE {i}")
                break

            self.states[i] = state

    def dump(self, state, pos=None):
        for y in range(self.h):
            for x in range(self.w):
                p = Point(x, y)
                if p in state:
                    print(DIR_ICONS[state[p][0]] if len(state[p]) == 1 else str(len(state[p])), end="")
                elif p == pos:
                    print("E", end="")
                else:
                    print(".", end="")
            print()
        print()

    def first_part(self):
        return self.solve(Point(0, -1), Point(self.w - 1, self.h))

    def solve(self, start, end, start_time=0):
        print(f"== Trip {start}, {end} starting at {start_time} ==")
        if DEV:
            self.dump(self.states[start_time % self.loop])

        self.queue.clear()  # reset queue (should be empty anyways...)
        self.enqueue(start_time, start, end)  # enqueue initial position
        best_so_far = None
        seen = set()
        ptr = 0
        while self.queue:
            minute, pos, distance = self.queue.popleft()

            if best_so_far and minute > best_so_far:
                continue

            if ptr % 100_000 == 0:
                print(f"minute {minute:4d} with queue containing {len(self.queue):4d} paths")
            ptr += 1

            key = (minute % self.loop, pos)
            if key in seen:
                continue  # had this position with the identical storm already earlier
            seen.add(key)

            if DEV:
                print(f"== Minute {minute} ==")
                self.dump(self.states[minute % self.loop], pos)

            if pos == end:
                print(f"found exit in {minute}")
                best_so_far = minute if not best_so_far else min(best_so_far, minute)
                continue

            minute = minute + 1
            state = self.states[minute % self.loop]

            if distance == 1:
                self.enqueue(minute, end, end)  # found exit near by... just take that option and ignore others
                continue

            to_enqueue = set()

            if pos.x == 0 and pos.y == 0:
                to_enqueue.add((minute, Point(0, -1)))  # into entrance
            if pos.x == self.w - 1 and pos.y == self.h - 1:
                to_enqueue.add((minute, Point(self.w - 1, self.h)))  # into entrance

            if pos.y == -1 and Point(0, 0) in state or pos.y == self.h and Point(self.w - 1, self.h - 1) in state:
                to_enqueue.add((minute, pos))  # wait in entrance

            if pos.y >= 0 and pos.y < self.h and pos not in state:
                to_enqueue.add((minute, pos))  # wait

            for p in direct_adjacent_iter(pos, self.w, self.h):
                if p == end:
                    self.enqueue(minute, p)  # add this and ignore all other possibilites
                    break

                if p not in state:
                    to_enqueue.add((minute, p))  # move

            for item in to_enqueue:
                self.enqueue(item[0], item[1], end)

        return best_so_far

    def enqueue(self, minute, pos, end):
        bisect.insort(self.queue, (minute, pos, manhattan_distance(pos, end)), key=lambda x: x[2])

    def second_part(self):
        trip1 = self.solve(Point(0, -1), Point(self.w - 1, self.h))
        trip2 = self.solve(Point(self.w - 1, self.h), Point(0, -1), trip1)
        trip3 = self.solve(Point(0, -1), Point(self.w - 1, self.h), trip2)
        return trip3


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
