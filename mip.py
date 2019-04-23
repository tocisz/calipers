#!/usr/bin/env python3
import math
import numpy as np
from PIL import Image, ImageDraw
import json
import random
from pyscipopt import Model, quicksum
import sys

WIDTH = None # Set in the main
HEIGHT = None
MIN_BASE_DIST = 1.0
MAX_DIST = 0.005
MAX_SOL_DIST = 0.001
TIME_LIMIT = 86400

def connect(p1, p2, p3, p4):
    r1 = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    r2 = (p3[0]-p4[0])**2 + (p3[1]-p4[1])**2
    d2 = (p1[0]-p3[0])**2 + (p1[1]-p3[1])**2
    d  = math.sqrt(d2)
    if d < MIN_BASE_DIST:
        return None
    l  = (r1 - r2 + d2) / (2*d)
    h2 = r1 - l**2
    if h2 < 0:
        return None
    h  = math.sqrt(h2)
    x = l / d * (p3[0] - p1[0]) + h / d * (p3[1] - p1[1]) + p1[0]
    y = l / d * (p3[1] - p1[1]) - h / d * (p3[0] - p1[0]) + p1[1]
    return (x,y)

def pointKey(p):
    return (int(p[0]), int(p[1]))

def pointKeys(p):
    key = (int(p[0]), int(p[1]))
    keys = [key]
    rem = math.modf(p[0])[0]
    if rem <= MAX_DIST:
        keys.append( (key[0]-1, key[1]) )
    elif rem >= 1-MAX_DIST:
        keys.append( (key[0]+1, key[1]) )
    rem = math.modf(p[1])[0]
    if rem <= MAX_DIST:
        keys.append( (key[0], key[1]-1) )
    elif rem >= 1-MAX_DIST:
        keys.append( (key[0], key[1]+1) )
    if len(keys) == 3:
        keys.append( (keys[1][0], keys[2][1]) )
    return keys

def euclid(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def taxi(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def hasDuplicate(pss, pn):
    pks = pointKeys(pn)
    for pk in pks:
        if pk in pss:
            for other in pss[pk]:
                if taxi(pn, other) < MAX_DIST:
                    return True
    return False

def updatePss(pss, pn):
    pk = pointKey(pn)
    if pk in pss:
        pss[pk].append(pn)
    else:
        pss[pk] = [pn]


# for gen = 3 we have 6561 nodes
# for gen = 4 there are too many possibilities to go...
from collections import deque
# TODO add lower range, s.t. if p1,p2,p3,p4 \in LOWER => skip
# This will enable adding single point to the graph
def nextGeneration(previous):
    ps = []
    pss = dict()
    for p in previous:
        updatePss(pss, p)

    psrange = range(len(previous))
    for p1i in psrange:
        for p2i in psrange:
            for p3i in psrange:
                for p4i in psrange:
                    if p1i == p2i or p3i == p4i or p1i == p3i:
                        continue
                    pn = connect(previous[p1i], previous[p2i], previous[p3i], previous[p4i])
                    if pn == None:
                        #print(',', end='')
                        continue
                    if hasDuplicate(pss, pn):
                        continue # atcually, duplicate with different parent could be useful
                    if 0 <= pn[0] < WIDTH and 0 <= pn[1] < HEIGHT:
                        ps.append(pn)
                        updatePss(pss, pn)

    return ps

# new_points - range of new indexes
# new_points_mapping - maps new_points index to points index
# points_mapping - maps input points to base_points+new_points
def filterPoints(base, points, delta):
    points_mapping = []
    new_points_mapping = []

    base = np.array(base)
    new_idx = len(base) # first new_idx is just after base
    for i,point in enumerate(points):
        closest = np.argmin(np.sum(np.square(base - point), axis=1))
        closest_dist2 = np.sum(np.square(base[closest]-point))
        if closest_dist2 < delta*delta:
            points_mapping.append(int(closest))
        else:
            new_points_mapping.append(i)
            points_mapping.append(new_idx)
            new_idx += 1

    new_points = range(len(base), new_idx)
    return points_mapping, new_points, new_points_mapping

def findCandidates(base, points, delta):
    base = np.array(base)
    delta2 = delta*delta
    for point in points:
        closest = np.argmin(np.sum(np.square(base - point), axis=1))
        closest_dist2 = np.sum(np.square(base[closest]-point))
        if closest_dist2 < delta2:
            print(base[closest], closest_dist2)
            raise Exception("Point already in the base")
    # This is a list of arrays
    # Each array has two colums: ids of two dots
    # Pair of dots in a row can be used to reach destination point
    # Two such pairs need to be selected to locate a point
    # print(base)
    all_idxs = [ [] for i in range(len(points)) ]
    for i in range(base.shape[0]):
        translated = base-base[i]
        translated_dist = np.sqrt(np.sum(np.square(translated), axis=1))
        for j, point in enumerate(points):
            dist = np.sqrt(np.sum(np.square(base[i]-point)))
            diff = np.abs(translated_dist-dist)
            idxs = np.where(diff <= delta)[0]
            if len(idxs) > 0:
                idxs = np.reshape(idxs, (idxs.shape[0],1))
                idxs = np.insert(idxs, 0, i, axis=1)
                all_idxs[j].append(idxs)
    # Check if there are inaccessible points
    for i in range(len(points)):
        if len(all_idxs[i]) < 2:
            raise Exception(f"Can't find parents of {point}")
    return all_idxs

def groupHash(g):
    return hash( tuple(g) )

def update(groupdict, edges, all_idxs):
    for idx in all_idxs:
        gs = []
        for t in idx:
            first = int(t[0,0])
            other = t[:,1].tolist()
            other.sort()
            g = [first] + other
            hash = groupHash(g)
            groupdict[hash] = g
            gs.append(hash)
        edges.append(gs)

def makeDoc(sumgen, base_len, groupdict, edges, points_mapping):
    groupnum = dict()
    groups = []
    i = 0
    for h,g in groupdict.items():
        groupnum[h] = i
        groups.append(g)
        i += 1
    groupdict = None
    edges = [[groupnum[g] for g in gs] for gs in edges]
    groupnum = None

    doc = {}
    doc["points"] = sumgen # list of all points coordinates
    doc["numOfBasePoints"] = base_len # how many of them are base points
    doc["groups"] = groups # all groups
    doc["edges"] = edges # all edges
    doc["points_mapping"] = points_mapping # how input points map to graph points
    return doc

def solveMip(doc):
    # return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 441, 615, 8586, 9458, 16770, 17562, 19159, 19160, 19161, 19162, 19163]
    target = doc["points_mapping"] # target are all input points mapped to graph ids

    m = Model()
    m.setRealParam('limits/time', TIME_LIMIT)

    gv = []
    for i in range(len(doc["groups"])):
        gv.append(m.addVar(f"g{i}", vtype='B'))

    pv = []
    for i in range(len(doc["points"])):
        pv.append(m.addVar(f"p{i}", vtype='B'))

    for i in target:
        m.addCons(pv[i] == 1)

    for i,ps in enumerate(doc["groups"]):
        # first point must be selected
        m.addCons(pv[ps[0]] >= gv[i])
        # and one of the following
        m.addCons(quicksum(pv[j] for j in ps[1:]) >= gv[i])

    for i,gs in enumerate(doc["edges"]):
        if len(gs) > 0:
            # at least two groups need to be selected
            m.addCons(quicksum(gv[j] for j in gs) >= 2*pv[i])

    m.setObjective(
        quicksum(
            pv[i] for i in range(
                doc["numOfBasePoints"], # don't pay for base points
                len(doc["points"])
            )
        ),
        "minimize")

    m.optimize()

    print("Input")
    print(target)

    optimized = []
    bestObj = None
    for i,sol in enumerate(m.getSols()):
        opt = []
        for j,p in enumerate(pv):
            if m.getSolVal(sol,p) > 0:
                opt.append(j)
        obj = m.getSolObjVal(sol)
        if bestObj == None:
            bestObj = obj
        print(f"Solution {i} (objective: {obj}, points: {len(opt)})")
        if obj - bestObj <= 2:
            print(json.dumps(opt))
        optimized.append(opt)

    return optimized[0]

def allCombinations(groups, selected):
    for g1i,g1 in enumerate(selected):
        for g2 in selected[g1i+1:]:
            p1 = groups[g1][0]
            p3 = groups[g2][0]
            for p2 in groups[g1][1:]:
                for p4 in groups[g2][1:]:
                    yield p1, p2, p3, p4
                    yield p3, p4, p1, p2

def findBestCombination(p, ps, combinations):
    bestC = None
    bestDist = float("inf")
    for c in combinations:
        pc = connect(ps[c[0]], ps[c[1]], ps[c[2]], ps[c[3]])
        if pc != None: # can be None when points are too close
            dist = euclid(p, pc)
            if dist < bestDist:
                bestC = c
                bestDist = dist
    if bestC == None:
        raise Exception(f"No combination for point {p}")
    return bestC, bestDist

def makeRecipe(doc, point_list, delta):
    delta = 1.0 # don't be so strict
    points = doc["points"]
    groups = doc["groups"]
    edges  = doc["edges"]
    base_len = doc["numOfBasePoints"]
    point_set = set(point_list)
    # remove points not preset in solution from groups
    for i,g in enumerate(groups):
        if groups[i][0] not in point_set:
            # first point is a must have
            groups[i] = []
        else:
            groups[i] = [ p for p in g if p in point_set]

    recipe = []
    for p in point_list:
        if p < base_len:
            print(f"Skipping {p}")
            continue
        selected = [ gi for gi in edges[p] if len(groups[gi]) >= 2 ]
        print(f"Doing {p} {points[p]}")
        bestC, bestDist = findBestCombination(points[p], points, allCombinations(groups, selected))
        print(bestC, bestDist)
        p1, p2, p3, p4 = bestC
        recipe.append((p,p1,p2,p3,p4))
    return recipe

def normailzeRecipe(recipe, base_len, e, points_mapping):
    map = dict()
    for i in range(base_len):
        map[i] = i
    n = base_len
    for r in recipe:
        first = r[0]
        if first not in map.keys():
            map[first] = n
            n += 1
    nv = []
    for r in recipe:
        nv.append([ map[p] for p in r[1:5] ])

    ne = []
    for path in e:
        ne.append([ map[points_mapping[p]] for p in path])
    return {"v": nv, "e":  ne}

def readInput(fileName):
    with open(fileName, 'r') as infile:
        return json.load(infile)

def draw(recipe, ps):
    ps = ps[:]
    for r in recipe["v"]:
        p = connect(ps[r[0]], ps[r[1]], ps[r[2]], ps[r[3]])
        ps.append(p)
    out = Image.new("RGB", (WIDTH, HEIGHT), color=0)
    # draw = ImageDraw.Draw(out)
    for p in ps:
        x, y = p
        print(x,y)
        out.putpixel((int(x),int(y)), (255,255,255) )
    out.save('solution.png')
    return ps

# import pdb
# pdb.set_trace()
def main(inputfn, basefn):
    input = readInput(inputfn)
    if basefn:
        input['base']['points'] = readInput(basefn)
    MAX_GEN = input['base']['depth']
    base = input['base']['points']
    global WIDTH, HEIGHT
    WIDTH = input['limits']['width']
    HEIGHT = input['limits']['height']

    gen = []
    sumgen = []
    gen.append(base)
    sumgen = gen[0]
    groupdict = dict()
    edges = [[]] * len(base)
    for g in range(1,MAX_GEN+1):
        gen.append(nextGeneration(sumgen))
        all_idxs = findCandidates(sumgen, gen[g], MAX_SOL_DIST)
        update(groupdict, edges, all_idxs)
        sumgen = sumgen + gen[g]
        #print(all_idxs)
    print(len(sumgen))

    target = input["v"]
    # target += [random.choice(sumgen) for i in range(5)]
    points_mapping, new_points, new_points_mapping = filterPoints(sumgen, target, MAX_DIST)
    print(points_mapping)
    print(new_points_mapping)
    new_points_coordinates = [ target[i] for i in new_points_mapping ]
    print("Finding candidates for new points.")
    all_idxs = findCandidates(sumgen, new_points_coordinates, MAX_DIST)
    print("Updating edges.")
    update(groupdict, edges, all_idxs)
    sumgen = sumgen + new_points_coordinates

    print("Making doc.")
    doc = makeDoc(sumgen, len(base), groupdict, edges, points_mapping)
    with open('graph.json', 'w') as outfile:
       json.dump(doc, outfile, separators=(',',':'))
    # now doc and input should contain all that is needed to

    print("Building MIP.")
    optimized = solveMip(doc)

    out = Image.new("RGB", (WIDTH, HEIGHT), color=0)
    for pi in optimized:
        p = doc["points"][pi]
        out.putpixel((int(p[0]), int(p[1])), (255,255,255) )
    out.save('original.png')

    recipe = makeRecipe(doc, optimized, MAX_DIST)
    #print(recipe)
    out = normailzeRecipe(recipe, doc["numOfBasePoints"], input["e"], doc["points_mapping"])
    allPoints = draw(out, base)
    out['coordinates'] = allPoints
    out['base'] = input['base']
    outputFile = '-solution.'.join(sys.argv[1].split('.'))
    with open(outputFile, 'w') as outfile:
        json.dump(out, outfile, separators=(',',':'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Give me problem file name!")
        sys.exit(1)

    if len(sys.argv) == 3:
        basefn = sys.argv[2]
    else:
        basefn = None

    main(sys.argv[1], basefn)
