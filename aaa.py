import numpy as np
import libs.transformations as tr


ls = [2, 5, -7 , 3, 1, 9]
ind1 = ls.index(min(ls))
m1 = ls.pop(ind1)
ind2 = ls.index(min(ls))
m2 = ls.pop(ind2)
print(m1,m2)