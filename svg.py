#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import xml.etree as etree

import math
import numpy as np
import json
import sys

WIDTH = 1000
HEIGHT = 1000
MIN_BASE_DIST = 1.0

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


SVG = "{http://www.w3.org/2000/svg}"

tree = ET.parse('template.xml')
root = tree.getroot()

def finalDot(ps, root, i, delay=None):
    p = [str(n) for n in ps[i]]
    r = tree.find(".//{http://www.w3.org/2000/svg}g[@id='main']")
    e = ET.Element("{http://www.w3.org/2000/svg}circle", id=f"p{i}", cx=p[0], cy=p[1], r="3" )
    if delay != None:
        e.attrib['visibility'] = 'hidden'
        # <set attributeName="visibility" to="visible" begin="8s" />
        e.append(ET.Element("{http://www.w3.org/2000/svg}set", attributeName="visibility", to="visible", begin=f"{delay}s"))
    r.append(e)

# <line x1="880" y1="600" x2="880" y2="600" style="stroke:rgb(0,0,0);stroke-width:1">
# <animate attributeName="x2" from="880" to="1040" dur="1s" begin="0s" fill="freeze" />
# </line>
def finalLine(ps, root, p1i, p2i, delay):
    p1 = [str(ps[p1i][0]), str(ps[p1i][1])]
    p2 = [str(ps[p2i][0]), str(ps[p2i][1])]
    r = tree.find(".//{http://www.w3.org/2000/svg}g[@id='main']")
    l = ET.Element("{http://www.w3.org/2000/svg}line", x1=p1[0], y1=p1[1], x2=p1[0], y2=p1[1], visibility='hidden', style="stroke-width:3;stroke-linecap:round;stroke-linejoin:round")
    l.append(ET.Element("{http://www.w3.org/2000/svg}set", attributeName="visibility", to="visible", begin=f"{delay}s"))
    aa = {"attributeName": "x2", "from": p1[0], "to": p2[0], "dur": "1s", "begin": f"{delay}s", "fill": "freeze"}
    l.append(ET.Element("{http://www.w3.org/2000/svg}animate", attrib=aa))
    aa = {"attributeName": "y2", "from": p1[1], "to": p2[1], "dur": "1s", "begin": f"{delay}s", "fill": "freeze"}
    l.append(ET.Element("{http://www.w3.org/2000/svg}animate", attrib=aa))
    r.append(l)

# <g id="p8-pre" visibility="hidden">
# <line id="line" x1="880" y1="600" x2="880" y2="600" style="stroke:rgb(0,0,0);stroke-width:1">
#   <animate attributeName="x2" from="880" to="1113.188337241014" dur="1s" begin="4s" fill="freeze" />
#   <animate attributeName="y2" from="600" to="507.62395692965987" dur="1s" begin="4s" fill="freeze" />
# </line>
# <circle id="circ" cx="1113.188337241014" cy="507.62395692965987" r="3">
#   <animate attributeName="cx" from="880" to="1113.188337241014" dur="1s" begin="4s" fill="freeze" />
#   <animate attributeName="cy" from="600" to="507.62395692965987" dur="1s" begin="4s" fill="freeze" />
# </circle>
# <set attributeName="visibility" to="visible" begin="4s" />
# </g>
def drawConnect(ps,root, p1i, p2i, delay):
    p1 = [str(ps[p1i][0]), str(ps[p1i][1])]
    p2 = [str(ps[p2i][0]), str(ps[p2i][1])]
    r = tree.find(".//{http://www.w3.org/2000/svg}g[@id='evolving']")
    g = ET.Element("{http://www.w3.org/2000/svg}g", visibility='hidden', id=f"connect-{p1i}-{p2i}")
    r.append(g)
    l = ET.Element("{http://www.w3.org/2000/svg}line", x1=p1[0], y1=p1[1], x2=p1[0], y2=p1[1])
    aa = {"attributeName": "x2", "from": p1[0], "to": p2[0], "dur": "1s", "begin": f"{delay}s", "fill": "freeze"}
    l.append(ET.Element("{http://www.w3.org/2000/svg}animate", attrib=aa))
    aa = {"attributeName": "y2", "from": p1[1], "to": p2[1], "dur": "1s", "begin": f"{delay}s", "fill": "freeze"}
    l.append(ET.Element("{http://www.w3.org/2000/svg}animate", attrib=aa))
    g.append(l)
    c = ET.Element("{http://www.w3.org/2000/svg}circle", cx=p1[0], cy=p1[1], r="3")
    ca = {"attributeName": "cx", "from": p1[0], "to": p2[0], "dur": "1s", "begin": f"{delay}s", "fill": "freeze"}
    c.append(ET.Element("{http://www.w3.org/2000/svg}animate", attrib=ca))
    ca = {"attributeName": "cy", "from": p1[1], "to": p2[1], "dur": "1s", "begin": f"{delay}s", "fill": "freeze"}
    c.append(ET.Element("{http://www.w3.org/2000/svg}animate", attrib=ca))
    g.append(c)
    s = ET.Element("{http://www.w3.org/2000/svg}set", attributeName="visibility", to="visible", begin=f"{delay}s")
    g.append(s)
    s = ET.Element("{http://www.w3.org/2000/svg}set", attributeName="visibility", to="hidden", begin=f"{delay+1}s")
    g.append(s)

def angle(p1, p2, p3):
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)
    v1 = p1-p2
    v2 = p1-p3
    c = np.stack((v1, v2))
    a = np.arctan2(c[:,0], c[:,1]) * 180 / np.pi
    a = a[0]-a[1]
    if a < -180:
        a += 360
    if a > 180:
        a -= 360
    return a

# <g id="p6-1" visibility="hidden">
# <line x1="X1" y1="Y1" x2="X2" y2="Y2" style="stroke:rgb(0,0,0);stroke-width:1"/>
# <circle cx="X2" cy="Y2" r="3"/>
# <animateTransform attributeName="transform" attributeType="XML" type="rotate" from="0 X1 Y1" to="A X1 Y1" dur="1s" begin="3s" fill="freeze" restart="whenNotActive" />
# <set attributeName="visibility" to="visible" begin="3s" />
# </g>
def drawRotate(ps, root, p1i, p2i, p3i, begin, end):
    an = angle(ps[p1i], ps[p2i], ps[p3i])
    # print(an)
    p1 = [str(n) for n in ps[p1i]]
    p2 = [str(n) for n in ps[p2i]]
    r = tree.find(".//{http://www.w3.org/2000/svg}g[@id='evolving']")
    g = ET.Element("{http://www.w3.org/2000/svg}g", visibility='hidden', id=f"rotate-{p1i}-{p2i}-{p3i}")
    r.append(g)
    l = ET.Element("{http://www.w3.org/2000/svg}line", x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1])
    g.append(l)
    c = ET.Element("{http://www.w3.org/2000/svg}circle", cx=p2[0], cy=p2[1], r="3")
    g.append(c)
    a = ET.Element("{http://www.w3.org/2000/svg}animateTransform", attrib={
        "attributeName" : "transform",
        "attributeType" : "XML",
        "type" : "rotate",
        "from" : f"0 {p1[0]} {p1[1]}",
        "to" : f"{an} {p1[0]} {p1[1]}",
        "dur" : f"{end-begin}s",
        "begin" : f"{begin}s",
        "fill": "freeze"})
    g.append(a)
    # <animate attributeType="CSS" attributeName="opacity" from="1" to="0" dur="5s" />
    a = ET.Element("{http://www.w3.org/2000/svg}animate", attrib={
        "attributeName" : "opacity",
        "attributeType" : "CSS",
        "from" : "1",
        "to" : "0",
        "dur" : f"1s",
        "begin" : f"{end}s",
        "fill": "freeze"})
    g.append(a)
    s = ET.Element("{http://www.w3.org/2000/svg}set", attributeName="visibility", to="visible", begin=f"{begin}s")
    g.append(s)
    s = ET.Element("{http://www.w3.org/2000/svg}set", attributeName="visibility", to="hidden", begin=f"{end+1}s")
    g.append(s)

def deactivate(i, delay):
    r = tree.find(f".//{{http://www.w3.org/2000/svg}}circle[@id='p{i}']")
    a = ET.Element("{http://www.w3.org/2000/svg}animate", attrib={
        "attributeName" : "opacity",
        "attributeType" : "CSS",
        "from" : "1",
        "to" : "0",
        "dur" : "1s",
        "begin" : f"{delay}s",
        "fill": "freeze"})
    r.append(a)

def readInput(fn):
    with open(fn, 'r') as infile:
        return json.load(infile)

def main(solfn):
    recipe = readInput(solfn)
    ps = recipe['base']['points']
    v = recipe["v"]
    e = recipe["e"]
    lastUsed = [0] * (len(v)+len(ps))
    n = 0
    created = {}
    for i in range(len(ps)):
        finalDot(ps, root, i)
        created[i] = 0 # base is created from the beginning
        n += 1

    final = set()
    for path in e:
        for i in range(len(path)-1):
            final.add((path[i], path[i+1]))

    for r in v:
        p = connect(ps[r[0]], ps[r[1]], ps[r[2]], ps[r[3]])
        ps.append(p)

    toConnect = set(final)
    connected = {}
    toCreate = set()
    for r in v:
        toConnect.add( (r[0],r[1]) )
        toConnect.add( (r[2],r[3]) )
        toCreate.add( (n,(r[0],r[1]),(r[2],r[3])) )
        n += 1
    toConnect = list(toConnect)
    toCreate = list(toCreate)
    print(toConnect)

    time = 0
    while toCreate:
        print(f"DELAY {time}")
        print(f"connected: {connected}")
        nextToCreate = []
        for (n,(p1,p2),(p3,p4)) in toCreate:
            # print( (n,(p1,p2),(p3,p4)) )
            if (p1,p2) in connected.keys() and (p3,p4) in connected.keys():
                begin1 = connected[(p1,p2)]
                begin2 = connected[(p3,p4)]
                if begin1 < time and begin2 < time:
                    drawRotate(ps, root, p1, p2, n, begin1, time)
                    print( f"Rotate {p1}, {p2}, {n}, {begin1}, {time}" )
                    drawRotate(ps, root, p3, p4, n, begin2, time)
                    print( f"Rotate {p3}, {p4}, {n}, {begin2}, {time}" )
                    finalDot(ps, root, n, time)
                    created[n] = time
                    lastUsed[p1] = time
                    lastUsed[p2] = time
                    lastUsed[p3] = time
                    lastUsed[p4] = time
                    lastUsed[n] = time
                else:
                    nextToCreate.append( (n,(p1,p2),(p3,p4)) )
            else:
                nextToCreate.append( (n,(p1,p2),(p3,p4)) )
        toCreate = nextToCreate

        nextToConnect = []
        print(f"created: {created}")
        for (p1,p2) in toConnect:
            if p1 in created.keys() and p2 in created.keys():
                if (p1, p2) in final:
                    finalLine(ps, root, p1, p2, time)
                else:
                    drawConnect(ps, root, p1, p2, time)
                print( f"Connect {p1} {p2} {time}" )
                connected[(p1,p2)] = time+1
                lastUsed[p1] = time+1
                lastUsed[p2] = time+1
            else:
                nextToConnect.append( (p1,p2) )
        toConnect = nextToConnect

        time += 1

    # for path in e:
    #     for i in range(len(path)-1):
    #         finalLine(ps, root, path[i], path[i+1], time-1)
    #     for p in path:
    #         lastUsed[p] = time

    for i,time in enumerate(lastUsed):
        deactivate(i, time)
    outfn = sys.argv[1].replace('-solution.json', '.svg')
    tree.write(outfn, encoding="UTF-8", xml_declaration="xml") #, default_namespace="ns0:http://www.w3.org/2000/svg")
    # print(ET.tostring(root,encoding="UTF-8").decode())
    print(lastUsed)
    print(ps)

if __name__ == '__main__':
    # test()
    if len(sys.argv) < 2:
        print("Give me solution file name!")
        sys.exit(1)
    main(sys.argv[1])
