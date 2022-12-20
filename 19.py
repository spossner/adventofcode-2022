import os
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
import networkx as nx
import numpy as np
from aoc import *
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

DEV = False
PART2 = True
DEBUG = False

STRIP = True
SPLIT_LINES = True
SPLIT_CHAR = None
DATA = None
AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022


@dataclass(unsafe_hash=True)
@total_ordering
class Resources:
    ore: int = 0
    clay: int = 0
    obsidian: int = 0
    geode: int = 0

    def __contains__(self, item):  # ignoring geode: all resources must be at least matched
        return type(item) == Resources and self.ore >= item.ore and self.clay >= item.clay and self.obsidian >= item.obsidian

    def satisfy(self, other):
        return Resources(max(self.ore, other.ore), max(self.clay, other.clay), max(self.obsidian, other.obsidian),
                         max(self.geode, other.geode))

    def __add__(self, other):
        assert type(other) == Resources
        return Resources(self.ore + other.ore, self.clay + other.clay, self.obsidian + other.obsidian, self.geode + other.geode)

    def __sub__(self, other):
        assert type(other) == Resources
        return Resources(self.ore - other.ore, self.clay - other.clay, self.obsidian - other.obsidian, self.geode - other.geode)

    def __lt__(self, other):
        if self.geode != other.geode:
            return self.geode.__lt__(other.geode)
        if self.obsidian != other.obsidian:
            return self.obsidian.__lt__(other.obsidian)
        if self.clay != other.clay:
            return self.clay.__lt__(other.clay)
        return self.ore.__lt__(other.ore)

    def __eq__(self, other):
        return type(other) == Resources and \
            self.ore == other.ore and \
            self.clay == other.clay and \
            self.obsidian == other.obsidian and \
            self.geode == other.geode

    def __mul__(self, other):
        if type(other) != int:
            raise ValueError(f"resources can only be multiplied with scalar - not {type(other)}")
        return Resources(self.ore * other, self.clay * other, self.obsidian * other, self.geode * other)

    def __repr__(self):
        result = []
        if self.ore:
            result.append(f"{self.ore} ore")
        if self.clay:
            result.append(f"{self.clay} clay")
        if self.obsidian:
            result.append(f"{self.obsidian} obsidian")
        if self.geode:
            result.append(f"{self.geode} geode")
        return "+".join(result)


ORE_ROBOT = Resources(1, 0, 0, 0)
CLAY_ROBOT = Resources(0, 1, 0, 0)
OBSIDIAN_ROBOT = Resources(0, 0, 1, 0)
GEODE_ROBOT = Resources(0, 0, 0, 1)


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

    def get_blueprints(self):
        blueprints = []
        for row in self.data:
            data = get_ints(row)[1:]
            blueprints.append({
                ORE_ROBOT: Resources(data[0]),
                CLAY_ROBOT: Resources(data[1]),
                OBSIDIAN_ROBOT: Resources(data[2], data[3]),
                GEODE_ROBOT: Resources(data[4], 0, data[5])
            })

        return blueprints

    def find_largest(self, blueprints, max_time=24):
        result = []

        for c, b in enumerate(blueprints):
            max_robots_needed = reduce(lambda a, b: a.satisfy(b), b.values(), Resources())
            best = defaultdict(int)

            queue = deque()
            # start with 1 ore roboter and no resources
            '''
            the tuple consists of
            0: minute - starting with 0
            1: roboters
            2: resources
            3: skipped possible robots in last iteration
            '''
            queue.append((0, Resources(1), Resources(), {}))
            while queue:
                minute, robots, resources, skipped = queue.popleft()

                if minute > max_time:
                    continue

                if resources.geode < best[minute]:
                    continue
                best[minute] = max(best[minute], resources.geode)

                # begin of minute
                possible_robots = {roboter: costs for (roboter, costs) in b.items() if costs in resources}
                if GEODE_ROBOT in possible_robots:  # if geode is possible -> go for it (greedy)
                    possible_robots = {GEODE_ROBOT: b[GEODE_ROBOT]}
                else:  # only go this path if no geode robot possible to build...
                    new_resources = resources + robots
                    queue.append((minute + 1, robots, new_resources, possible_robots))  # go on w/o building - just farming
                    if DEBUG:
                        print(f"== Minute {minute + 1} ==")
                        print(f"robots {robots}; you now have {new_resources}\n")

                for to_build, costs in possible_robots.items():  # filter possible robots with current resources
                    # do not build robots now which could have been build in the last step..
                    if to_build in skipped:
                        continue

                    # build not more than needed to create any roboter with 1 round of harvesting
                    # this is super good to prune the possible paths
                    if to_build == ORE_ROBOT and robots.ore + 1 > max_robots_needed.ore or \
                            to_build == CLAY_ROBOT and robots.clay + 1 > max_robots_needed.clay or \
                            to_build == OBSIDIAN_ROBOT and robots.obsidian + 1 > max_robots_needed.obsidian:
                        continue

                    new_resources = resources + robots - costs
                    new_robots = robots + to_build
                    queue.appendleft((minute + 1, new_robots, new_resources, {}))  # append at front and reset skipping
                    if DEBUG:
                        print(f"== Minute {minute + 1} ==")
                        print(f"spend {costs} to start building {to_build}-collecting robot")
                        print(f"robots {robots}; you now have {new_resources}")
                        print(f"new {to_build}-collecting robot is ready: {new_robots}\n")

            print(f"{c + 1}: {best[max_time]}")
            result.append((c + 1, best[max_time]))

        return result

    def first_part(self):
        return sum(map(lambda t: t[0] * t[1], self.find_largest(self.get_blueprints(), 24)))

    def second_part(self):
        return reduce(lambda a, b: a * b[1], self.find_largest(self.get_blueprints()[:3], 32), 1)


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

    r = Resources(4, 2, 1, 0)
    assert ORE_ROBOT in r
    assert r not in ORE_ROBOT
    assert CLAY_ROBOT in r
    assert r not in CLAY_ROBOT
    assert OBSIDIAN_ROBOT in r
    assert r not in OBSIDIAN_ROBOT

    d = Resources(1, 0, 0, 0)
    assert ORE_ROBOT in d
    assert d in ORE_ROBOT
    assert ORE_ROBOT == d

    print("RESULT", s.first_part() if not PART2 else s.second_part())
