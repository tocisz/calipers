G = 0

def p():
    print(G)

def s():
    global G
    G = 1

p()
s()
p()
