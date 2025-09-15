import numpy as np
import libs.transformations as tr


other_closest_verts = np.array([[1,0],[0,0]])

closest_vert = np.array([[0.5],[0.1]])


difs = (other_closest_verts - closest_vert)

print(difs)

norms = np.linalg.norm(difs, axis=0)

print(norms)

dif_sum = np.sum(norms) - 1

print(dif_sum)