#!/usr/bin/env python
"""
Based on cairo-demo/X11/cairo-demo.c
"""

import math
import random
import PIL
from PIL import Image

SIZE = 5
WIDTH = 1280
HEIGHT = 1024

random.seed()

def connect(p1, p2, p3, p4, direction):
    r1 = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    r2 = (p3[0]-p4[0])**2 + (p3[1]-p4[1])**2
    d2 = (p1[0]-p3[0])**2 + (p1[1]-p3[1])**2
    d  = math.sqrt(d2)
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

MAX_GEN = 0
from collections import deque
def points():
    global MAX_GEN
    ps = []
    pss = set()
    waiting = deque()
    # global ps, pss
    ps.append( (WIDTH/2 - 30, HEIGHT/2) )
    ps.append( (WIDTH/2 + 30, HEIGHT/2) )
    ps.append( connect(ps[0], ps[1], ps[1], ps[0], randbool()) )
    pss.update(ps)
    waiting.append( (0, 0) )
    waiting.append( (0, 1) )
    waiting.append( (0, 2) )
    yield ps[0]
    yield ps[1]
    yield ps[2]

    generation = 0
    psrange = range(0)
    while waiting:
        (gen, p3i) = waiting.popleft()
        if gen == MAX_GEN:
            break
        #if p3i == 26: # ~1/3 of 3rd gen
        #    break
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
                            print(',', end='')
                            continue
                        if pn in pss:
                            print('.', end='')
                            continue
                        if 0 <= pn[0] < WIDTH and 0 <= pn[1] < HEIGHT:
                            yield pn
                            if generation < MAX_GEN:
                                ps.append(pn)
                                new_index = len(ps)-1
                                print(f" {new_index} <- ({p1i},{p2i},{p3i},{p4i})", flush=True)
                                waiting.append( (generation, new_index) )
                                pss.add(pn)
                            else:
                                print(f" _ <- ({p1i},{p2i},{p3i},{p4i})", flush=True)


def point(out, x, y):
    out.putpixel((int(x),int(y)), (255,255,255) )

def main():
    out = Image.new("RGB", (WIDTH, HEIGHT), color=0)
    for p in points():
        point(out, p[0], p[1])
    out.save('img.png')

if __name__ == '__main__':
    main()
