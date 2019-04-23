#!/usr/bin/env python3
import math
import numpy as np
import json
import sys

def scale_list(l, scale):
    return [[x*scale for x in p] for p in l]

def main(fn, scale):
    with open(fn, 'r') as f:
        problem = json.load(f)

    problem['base']['points'] = scale_list(problem['base']['points'], scale)
    problem['v'] = scale_list(problem['v'], scale)

    with open(fn, 'w') as f:
        json.dump(problem,f)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Give me problem, scale.")
        sys.exit(1)
    main(sys.argv[1], float(sys.argv[2]))
