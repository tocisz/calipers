#!/usr/bin/env python
import math
from PIL import Image, ImageDraw
import json

WIDTH = 1920
HEIGHT = 1200
MIN_BASE_DIST = 1.0

D = 80
P1 = (WIDTH/2 - D, HEIGHT/2)
P2 = (WIDTH/2 + D, HEIGHT/2)

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

def readInput():
    with open('solution.json', 'r') as infile:
        return json.load(infile)

def draw(points):
    out = Image.new("RGB", (WIDTH, HEIGHT), color=0)
    # draw = ImageDraw.Draw(out)
    for p in points:
        x, y = p
        print(x,y)
        out.putpixel((int(x),int(y)), (255,255,255) )
    out.save('solution.png')

def main():
    recipe = readInput()
    ps = [P1, P2]
    for r in recipe:
        p = connect(ps[r[0]], ps[r[1]], ps[r[2]], ps[r[3]])
        ps.append(p)
    draw(ps)

if __name__ == '__main__':
    main()
