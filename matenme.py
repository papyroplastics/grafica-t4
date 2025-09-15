def squere_colision(self, other, dif):
    self_verts = self.pos.reshape(2,1) + self.rotmat[:2,:2] @ squere_bbox
    other_verts = other.pos.reshape(2,1) + other.rotmat[:2,:2] @ squere_bbox

    self_difs = (self_verts - other.pos.reshape(2,1)) 
    other_difs = (other_verts - self.pos.reshape(2,1)) 

    self_sqr_norms = np.sum(self_difs**2, axis=0)
    other_sqr_norms = np.sum(other_difs**2, axis=0)

    self_inds = np.argsort(self_sqr_norms)[:2]
    other_inds = np.argsort(other_sqr_norms)[:2]

    if self_sqr_norms[self_inds[0]] < other_sqr_norms[other_inds[0]]:
        print("caso 1")
        closest_vert = self_verts[:,self_inds[0]]
        other_closest_verts = other_verts[:,other_inds]
        self.handle_colision(other, closest_vert, other_closest_verts, other_inds,dif)
    else:
        print("caso 2")
        closest_vert = other_verts[:,other_inds[0]]
        other_closest_verts = self_verts[:,self_inds]
        self.handle_colision(other, closest_vert, other_closest_verts, other_inds,dif)

def handle_colision(self, other, closest_vert, other_closest_verts, small_inds, dif):
    difs = (other_closest_verts - closest_vert)
    norms = np.linalg.norm(difs, axis=0)
    dif_sum = np.sum(norms) - 1.4
    
    if dif_sum < 0.2:
        dif_norm = np.dot(dif,dif)
        speed_change = np.zeros(2)
        self_sp_proj = np.dot(dif, self.speed)
        other_sp_proj = np.dot(dif, other.speed)

        if self_sp_proj > 0:
            speed_change -= self_sp_proj * dif / dif_norm
        if other_sp_proj < 0:
            speed_change += other_sp_proj * dif / dif_norm
        self.speed += speed_change * 0.5
        other.speed -= speed_change * 0.5

        change = np.linalg.norm(speed_change) * 0.5
        if small_inds[0] > small_inds[1] or (small_inds[0] == 0 and small_inds[1] == 3):
            other.rot += change
        else:
            other.rot -= change
