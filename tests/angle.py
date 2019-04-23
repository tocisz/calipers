import math
import numpy as np
p1 = [960.0, 461.4359353944898]
p2 = [960.0, 738.5640646055102]
p3 = [1113.188337241014, 507.62395692965987]

p1 = [880, 600]
p2 = [960.0, 461.4359353944898]
p3 = [1113.188337241014, 507.62395692965987]

p1 = np.array(p1)
p2 = np.array(p2)
p3 = np.array(p3)


v1 = p2-p1
v2 = p2-p3
c = np.stack((v1, v2))
print(c)

#print(c[:,0],c[:,1])
a = np.arctan2(c[:,0], c[:,1]) * 180 / np.pi
print(a)
print(360+(a[1]-a[0]))
