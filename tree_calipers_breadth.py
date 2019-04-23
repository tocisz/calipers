#!/usr/bin/env python
import math
import random
import numpy as np
from PIL import Image, ImageDraw

SIZE = 5
WIDTH = 1280
HEIGHT = 1024
MIN_BASE_DIST = 1.0
MIN_DIST = 0.0001
MIN_SOL_DIST = 0.0000001

random.seed()

def connect(p1, p2, p3, p4, direction):
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
    if direction:
        x = l / d * (p3[0] - p1[0]) + h / d * (p3[1] - p1[1]) + p1[0]
        y = l / d * (p3[1] - p1[1]) - h / d * (p3[0] - p1[0]) + p1[1]
    else:
        x = l / d * (p3[0] - p1[0]) - h / d * (p3[1] - p1[1]) + p1[0]
        y = l / d * (p3[1] - p1[1]) + h / d * (p3[0] - p1[0]) + p1[1]
    return (x,y)

def randbool():
    return random.randint(0, 1) == 0

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

D = 100
P1 = (WIDTH/2 - D, HEIGHT/2)
P2 = (WIDTH/2 + D, HEIGHT/2)
P3 = (WIDTH/2 - D, HEIGHT/2 - 2*D)

# for gen = 3 we have 6283 nodes
# for gen = 4 there are too many possibilities to go...
MAX_GEN = 3
from collections import deque
# For finding optimal solution, we should create a graph
# by calling findCandidates on each point in the next genration
# (basing on previous generation).
# So in this method, we only need to generate coordinates
# and it should be simplified.
def points():
    global MAX_GEN
    graph = [] #np.empty([0,6],dtype=int)
    coordinates = []
    ps = []
    pss = dict()
    waiting = deque()
    ps.append( P1 )
    ps.append( P2 )
    pss[point_key(ps[0])] = [ps[0]]
    pss[point_key(ps[1])] = [ps[1]]
    waiting.append( (0, 0) )
    waiting.append( (0, 1) )
    graph.append([0, 0, 0, 0, 0])
    graph.append([0, 0, 0, 0, 0])
    coordinates.append([ps[0][0], ps[0][1]])
    coordinates.append([ps[1][0], ps[1][1]])
    parents = [set([0]),set([1])]

    generation = 0
    psrange = range(0)
    while waiting:
        (gen, p3i) = waiting.popleft()
        if gen == MAX_GEN:
            break
        if gen != generation-1:
            psrange = range(len(ps))
            generation = gen+1

        for direction in [True, False]:
            for p1i in psrange:
                for p2i in psrange:
                    for p4i in psrange:
                        if p1i == p2i or p1i == p3i or p3i == p4i:
                            continue
                        pn = connect(ps[p1i], ps[p2i], ps[p3i], ps[p4i], direction)
                        if pn == None:
                            #print(',', end='')
                            continue
                        if has_duplicate(pss, pn):
                            continue # atcually, duplicate with different parent could be useful
                        if 0 <= pn[0] < WIDTH and 0 <= pn[1] < HEIGHT:
                            ps.append(pn)
                            new_index = len(ps)-1
                            graph.append([p1i, p2i, p3i, p4i, 1 if direction else 0])
                            coordinates.append([pn[0], pn[1]])
                            #print(f" {new_index} <- ({p1i},{p2i},{p3i},{p4i},{direction})", flush=True)
                            waiting.append( (generation, new_index) )
                            pk = point_key(pn)
                            if pk in pss:
                                pss[pk].append(pn)
                            else:
                                pss[pk] = [pn]
                            par = set.union(set([new_index]),parents[p1i],parents[p2i],parents[p3i],parents[p4i])
                            parents.append(par) # TODO create list of all possible parents
    graph = np.array(graph, dtype='uint16')
    coordinates = np.array(coordinates, dtype='double')
    # OK, so we know coordinates
    return graph, coordinates, parents

def findCandidates(coords, point, delta):
    closest = np.argmin(np.sum(np.square(coords - point), axis=1))
    closest_dist2 = np.sum(np.square(coords[closest]-point))
    print(coords[closest], closest_dist2)
    # This is a list of arrays
    # Each array has two colums: ids of two dots
    # Pair of dots in a row can be used to reach destination point
    # Two such pairs need to be selected to locate a point
    all_idxs = []
    # Error when reaching point with a pair of two other points
    # (Arrays as above, but only one column)
    all_dists = []
    for i in range(coords.shape[0]):
        translated = coords-coords[i]
        translated_dist = np.sqrt(np.sum(np.square(translated), axis=1))
        dist = np.sqrt(np.sum(np.square(coords[i]-point)))
        diff = np.abs(translated_dist-dist)
        idxs = np.where(diff <= delta)[0]
        if len(idxs) > 0:
            selected_dist = np.take(diff,idxs)
            idxs = np.reshape(idxs, (idxs.shape[0],1))
            idxs = np.insert(idxs, 0, i, axis=1)
            all_idxs.append(idxs)
            all_dists.append(selected_dist)
    return all_idxs, all_dists

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
    main()
