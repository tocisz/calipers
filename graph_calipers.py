#!/usr/bin/env python
import math
import numpy as np
from PIL import Image, ImageDraw
import json

SIZE = 5
WIDTH = 1920
HEIGHT = 1200
MIN_BASE_DIST = 1.0
MIN_DIST = 0.0001
MIN_SOL_DIST = 0.0000001

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

def point_key(p):
    return (int(p[0]), int(p[1]))

def point_keys(p):
    key = (int(p[0]), int(p[1]))
    keys = [key]
    rem = math.modf(p[0])[0]
    if rem <= MIN_DIST:
        keys.append( (key[0]-1, key[1]) )
    elif rem >= 1-MIN_DIST:
        keys.append( (key[0]+1, key[1]) )
    rem = math.modf(p[1])[0]
    if rem <= MIN_DIST:
        keys.append( (key[0], key[1]-1) )
    elif rem >= 1-MIN_DIST:
        keys.append( (key[0], key[1]+1) )
    if len(keys) == 3:
        keys.append( (keys[1][0], keys[2][1]) )
    return keys

def euclid(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def has_duplicate(pss, pn):
    pks = point_keys(pn)
    for pk in pks:
        if pk in pss:
            for other in pss[pk]:
                if euclid(pn, other) < MIN_DIST:
                    return True
    return False

D = 80
P1 = (WIDTH/2 - D, HEIGHT/2)
P2 = (WIDTH/2 + D, HEIGHT/2)
P3 = (WIDTH/2 - D, HEIGHT/2 - 2*D)

def update_pss(pss, pn):
    pk = point_key(pn)
    if pk in pss:
        pss[pk].append(pn)
    else:
        pss[pk] = [pn]


# for gen = 3 we have 6561 nodes
# for gen = 4 there are too many possibilities to go...
from collections import deque
# TODO add lower range, s.t. if p1,p2,p3,p4 \in LOWER => skip
# This will enable adding single point to the graph
def next_generation(previous):
    ps = []
    pss = dict()
    for p in previous:
        update_pss(pss, p)

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
                    if has_duplicate(pss, pn):
                        continue # atcually, duplicate with different parent could be useful
                    if 0 <= pn[0] < WIDTH and 0 <= pn[1] < HEIGHT:
                        ps.append(pn)
                        update_pss(pss, pn)

    return ps

# TODO compute for many points at once, not for just one
def findCandidates(base, points, delta):
    base = np.array(base)
    for point in points:
        closest = np.argmin(np.sum(np.square(base - point), axis=1))
        closest_dist2 = np.sum(np.square(base[closest]-point))
        if closest_dist2 < delta*delta:
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
    return all_idxs

def group_hash(g):
    return hash( (g[0], tuple(g[1])) )

def update(groupdict, edges, all_idxs):
    for idx in all_idxs:
        gs = []
        for t in idx:
            first = int(t[0,0])
            other = t[:,1].tolist()
            g = (first,other)
            hash = group_hash(g)
            groupdict[hash] = g
            gs.append(hash)
        edges.append(gs)

def make_doc(sumgen, groupdict, edges):
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
    doc["points"] = sumgen
    doc["groups"] = groups
    doc["edges"] = edges
    return doc

MAX_GEN = 3
def main2():
    gen = []
    sumgen = []
    gen.append([P1, P2])
    sumgen = gen[0]
    groupdict = dict()
    edges = [[],[]]
    for g in range(1,MAX_GEN+1):
        gen.append(next_generation(sumgen))
        all_idxs = findCandidates(sumgen, gen[g], MIN_SOL_DIST)
        update(groupdict, edges, all_idxs)
        sumgen = sumgen + gen[g]
        #print(all_idxs)
    print(len(sumgen))

    doc = make_doc(sumgen, groupdict, edges)
    with open('graph.json', 'w') as outfile:
        json.dump(doc, outfile)

    out = Image.new("RGB", (WIDTH, HEIGHT), color=0)
    for p in sumgen:
        out.putpixel((int(p[0]), int(p[1])), (255,255,255) )
    out.save('img.png')

def findBestCombinations(all_idxs, all_dists, parents):
    buckets = len(all_idxs)
    minSet = None
    minSol = None
    minCount = len(parents)
    for i in range(buckets):
        a = all_idxs[i]
        for ai in range(a.shape[0]):
            for j in range(i+1, buckets):
                b = all_idxs[j]
                for bi in range(b.shape[0]):
                    e = (a[ai][0], a[ai][1], b[bi][0], b[bi][1])
                    s = set.union(
                        parents[e[0]],
                        parents[e[1]],
                        parents[e[2]],
                        parents[e[3]])
                    size = len(s)
                    # print(a[ai],b[bi],size)
                    if size < minCount:
                        minCount = size
                        minSet = set()
                        l = list(s)
                        l.sort()
                        minSet.add(tuple(l))
                        minSol = [e]
                    elif size == minCount:
                        l = list(s)
                        l.sort()
                        minSet.add(tuple(l))
                        minSol.append(e)
    return minCount, minSet, minSol

def draw(point, minSet, tree, coords):
    num = 1
    for t in minSet:
        print(f"Solution {t}")
        out = Image.new("RGB", (WIDTH, HEIGHT), color=0)
        draw = ImageDraw.Draw(out)
        step = -1
        for i in t:
            x, y = coords[i]
            print(tree[i], x, y)
            out.putpixel((int(x),int(y)), (255,255,255) )
            if step < 1:
                step += 1
                continue
            copy = out.copy()
            draw.line(list(coords[tree[i][0]])+list(coords[tree[i][1]]),(255,0,0))
            draw.line(list(coords[tree[i][0]])+[x,y],(255,0,0))
            draw.line(list(coords[tree[i][2]])+list(coords[tree[i][3]]),(0,255,0))
            draw.line(list(coords[tree[i][2]])+[x,y],(0,255,0))
            out.save(f"img{num}_{step}.png")
            out = copy
            draw = ImageDraw.Draw(out)
            step += 1

        x, y = point[0], point[1]
        out.putpixel((int(x),int(y)), (255,255,50) )
        out.save(f"img{num}.png")
        num += 1

def main():
    tree, coords, parents = points()
    print(f"Base has {len(tree)} points")
    # print(parents)
    point = np.array(list(P3))
    print(point)
    all_idxs, all_dists = findCandidates(coords, point, MIN_SOL_DIST)
    print(all_idxs)
    print(all_dists)

    minCount, minSet, minSol = findBestCombinations(all_idxs, all_dists, parents)
    print(minCount)
    print(minSet)
    print(minSol)

    draw(point, minSet, tree, coords)

if __name__ == '__main__':
    main2()
