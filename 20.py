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
from aoc.linked_list import ListNode
from dotenv import load_dotenv

load_dotenv()

DEV = False
PART2 = True

STRIP = True
SPLIT_LINES = True
SPLIT_CHAR = None
DATA = None
AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022

KEY = 811589153


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

    def dump(self, node: ListNode):
        first = True
        for i in node:
            print(f"{'' if first else ','}{i}", end="")
            first = False
        print()

    def move(self, node, n):
        if not node.val:
            return

        moves = abs(node.val) % (n - 1)
        if moves == 0:
            return

        current = node.pop()
        if node.val > 0:
            for _ in range(moves):
                current = current.next()
            current.insert_after(node)
        else:
            for _ in range(moves):
                current = current.prev()
            current.insert_before(node)

    def dump(self, node):
        print("[", end="")
        for i, n in enumerate(node):
            print(f"{', ' if i > 0 else ''}{n}", end="")
        print("]")

    # 12868 is too high...
    # 3103 too low
    # 16525..mmmmhhhh... even higher :-o
    # -4302.. oh weh
    # 4258 still shit... what!!!!
    # 7004 passt finally :-D
    def first_part(self):
        result = []
        zero = None
        nodes = []
        for v in map(int, self.data):
            node = ListNode(v * KEY if PART2 else v)
            if v == 0:
                zero = node
            nodes.append(node)
        for l, r in zip(nodes[0:-1], nodes[1:]):
            l.next_node = r
            r.prev_node = l
        nodes[0].prev_node = nodes[-1]
        nodes[-1].next_node = nodes[0]

        if DEV:
            self.dump(zero)

        for i in range(10 if PART2 else 1):
            for node in nodes:
                self.move(node, len(nodes))
            if DEV:
                print(i + 1)
                self.dump(zero)

        current = zero
        for i in range(3):
            for _ in range(1000):
                current = current.next()
            result.append((i + 1, current.val))

        print(result)
        return sum(map(lambda r: r[1], result))

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
