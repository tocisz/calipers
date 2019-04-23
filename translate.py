#!/usr/bin/env python3
import math
import numpy as np
import json
import sys

def scale_list(l, scale):
    return [[x*scale for x in p] for p in l]

def translate_list(l, dx, dy):
    return [[p[0]+dx, p[1]+dy] for p in l]

def main(fn, dx, dy):
    with open(fn, 'r') as f:
        problem = json.load(f)

    problem['v'] = translate_list(problem['v'], dx, dy)

    with open(fn, 'w') as f:
        json.dump(problem,f)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Give me problem, x-translate, y-translate.")
        sys.exit(1)
    main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
