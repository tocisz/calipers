#!/usr/bin/env python3
import math
import numpy as np
import json
import sys

def floatPair(a):
    return (
        float(a[0]) if a[0] != '' else float('-inf'),
        float(a[1]) if a[1] != '' else float('+inf')
    )

def inRange(p, lx, ly):
    [x,y] = p
    (xLow, xHi) = lx
    (yLow, yHi) = ly
    return x >= xLow and x <= xHi and y >= yLow and y <= yHi

def main(solfn, limits):
    with open(solfn, 'r') as f:
        sol = json.load(f)

    lx = floatPair(limits[0].split(':'))
    ly = floatPair(limits[1].split(':'))
    print(lx)
    print(ly)

    points = [ p for p in sol['coordinates'] if inRange(p,lx,ly) ]
    print(f"Number of points selected {len(points)} / {len(sol['coordinates'])}")
    print(json.dumps(points))

    outfn = solfn.replace('-solution.json','-base.json')
    with open(outfn, 'w') as f:
        json.dump(points, f)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Give me solution, x-limits, y-limits")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2:4])
