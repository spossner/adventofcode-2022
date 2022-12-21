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
from aoc.tree import TreeNode
from dotenv import load_dotenv

load_dotenv()

DEV = False
PART2 = True

STRIP = True
SPLIT_LINES = True
SPLIT_CHAR = ": "
DATA = None
AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022


def p(s, end="\n"):
    if DEV: print(s, end=end)


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

    def eval(self, node):
        '''
        Recursive function to eval a node with a final numeric value (-> results in that value) or by performing the operation on left and right sub-nodes.
        :param node: The node to evaluate
        :return: The result as numeric value
        '''
        if isinstance(node.val, (int, float)):
            return node.val
        return eval(f"a {node.val} b", {"a": self.eval(node.left), "b": self.eval(node.right)})

    def find_humn(self, node, target):
        if node.val == "+":
            if hasattr(node.right, "humn"):
                node.left, node.right = node.right, node.left
            return self.find_humn(node.left, target - self.eval(node.right))
        if node.val == "*":
            if hasattr(node.right, "humn"):
                node.left, node.right = node.right, node.left
            return self.find_humn(node.left, target / self.eval(node.right))
        if node.val == "-":
            if hasattr(node.right, "humn"):
                return self.find_humn(node.right, self.eval(node.left) - target)
            else:
                return self.find_humn(node.left, target + self.eval(node.right))
        if node.val == "/":
            if hasattr(node.right, "humn"):
                return self.find_humn(node.right, self.eval(node.left) / target)
            else:
                return self.find_humn(node.left, target * self.eval(node.right))

        print(node, target)
        return target

    def first_part(self):
        nodes = {}
        for row in self.data:
            if row[1].isnumeric():
                nodes[row[0]] = TreeNode(int(row[1]))
            else:
                m = re.split("(\w+)\s([\+-/*])\s(\w+)", row[1])
                nodes[row[0]] = TreeNode(m[2], m[1], m[3])  # misuse left and right to keep names of subnodes

        for node in nodes.values():
            if node.left is None:  # skip the leafs containing real values
                continue
            # replace left and right by the real nodes parsed in first step
            node.left = nodes[node.left]
            node.right = nodes[node.right]
            node.left.parent = node.right.parent = node  # add additional parent property

        if PART2:
            root = nodes["root"]
            node = nodes["humn"]  # mark all nodes leading to humn node
            node.val = "??"  # make it corrupt so in worst case we get an exception
            node.humn = True
            while node.parent != root:
                node = node.parent
                node.humn = True
            return self.find_humn(node, self.eval(root.left) if root.right == node else self.eval(root.right))

        else:
            return self.eval(nodes["root"])

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
