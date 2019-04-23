#!/usr/bin/env python3
import json
import sys
import numpy as np

MAXDIST = 1.0e-5

def read(fn):
    with open(fn, 'r') as f:
        return json.load(f)

def main(sol1fn, sol2fn, outsol):
    sol1 = read(sol1fn)
    sol2 = read(sol2fn)
    ps1 = np.array(sol1['coordinates'])
    mapping = [-1] * len(sol2['coordinates'])
    print("Checking that solutions stitch")
    for p in sol2['base']['points']:
        closest = np.argmin(np.sum(np.square(ps1 - p), axis=1))
        dist = np.sqrt(np.sum(np.square(ps1[closest]-p)))
        print(f"Closest to {p} is {closest} with dist {dist}")
        if dist > MAXDIST:
            raise Exception("Solutions don't stitch")

    print(f"Mapping base of {sol2fn} to points of {sol1fn}")
    for i,p in enumerate(sol2['coordinates']):
        closest = np.argmin(np.sum(np.square(ps1 - p), axis=1))
        dist = np.sqrt(np.sum(np.square(ps1[closest]-p)))
        print(f"Closest to {p} is {closest} with dist {dist}")
        if dist <= MAXDIST:
            mapping[i] = int(closest)

    sol = {}
    coordinates = sol1['coordinates'][:]
    n = len(sol1['coordinates'])
    for i in range(len(mapping)):
        if mapping[i] < 0:
            mapping[i] = n
            coordinates.append(sol2['coordinates'][i])
            n += 1
    print(mapping)
    sol['coordinates'] = coordinates

    v = sol1['v'][:]
    for move in sol2['v']:
        # TODO detect moves that lead to points that are in the first solution
        v.append( [ mapping[p] for p in move ] )
    sol['v'] = v

    e = sol1['e'][:]
    for path in sol2['e']:
        # TODO detect moves that lead to points that are in the first solution
        e.append( [ mapping[p] for p in path ] )
    sol['e'] = e

    sol['base'] = sol1['base']

    with open(outsol, 'w') as outfile:
        json.dump(sol, outfile, separators=(',',':'))


if __name__ == '__main__':
    # test()
    if len(sys.argv) < 4:
        print("Give me solution file names!")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
