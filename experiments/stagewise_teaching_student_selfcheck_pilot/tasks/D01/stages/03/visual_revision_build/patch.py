import bpy
import math
import random
from mathutils import Vector

# Move the existing foreground plant into the camera's lower-left field of view.
foreground = bpy.data.objects.get('Foreground ficus')
if foreground:
    foreground.location.x += 1.05
    foreground.location.y += 0.15

leaf_materials = [bpy.data.materials.get('Leaf green %d' % i) for i in range(4)]

def add_foliage(name, parent, center, radius, count, seed, length_range):
    rng = random.Random(seed)
    verts, faces, indices = [], [], []
    cx, cy, cz = center
    for i in range(count):
        # An irregular oval crown with foliage distributed throughout its volume.
        z = rng.uniform(-1.0, 1.0)
        theta = rng.uniform(0.0, 2.0 * math.pi)
        radial = math.sqrt(max(0.0, 1.0 - z*z)) * rng.uniform(0.25, 1.0)
        p = Vector((cx + radius[0]*radial*math.cos(theta),
                    cy + radius[1]*radial*math.sin(theta),
                    cz + radius[2]*z))
        direction = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.35, 0.9)))
        if direction.length < 0.01:
            direction = Vector((1, 0, 0))
        direction.normalize()
        side = direction.cross(Vector((0, 0, 1)))
        if side.length < 0.01:
            side = direction.cross(Vector((0, 1, 0)))
        side.normalize()
        normal = direction.cross(side).normalized()
        length = rng.uniform(*length_range)
        width = length * rng.uniform(0.28, 0.42)
        # Folded lance-shaped leaves remain individual editable polygons in one mesh.
        points = [p - direction*length*0.50,
                  p - direction*length*0.12 + side*width*0.50,
                  p + direction*length*0.50,
                  p - direction*length*0.12 - side*width*0.50,
                  p + normal*length*0.06]
        base = len(verts)
        verts.extend([tuple(v) for v in points])
        faces.extend([(base, base+1, base+4), (base+1, base+2, base+4),
                      (base+2, base+3, base+4), (base+3, base, base+4)])
        indices.extend([rng.randrange(4)] * 4)
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    for mat in leaf_materials:
        if mat:
            mesh.materials.append(mat)
    if len(mesh.materials):
        for poly, idx in zip(mesh.polygons, indices):
            poly.material_index = idx % len(mesh.materials)
    return obj

rear = bpy.data.objects.get('Rear ficus')
add_foliage('Rear ficus fuller canopy', rear, (-1.17, 3.47, 1.47), (0.55, 0.39, 0.64), 260, 431, (0.12, 0.23))
add_foliage('Foreground ficus fuller canopy', foreground, (-2.95, -2.15, 1.37), (0.78, 0.54, 0.63), 300, 732, (0.18, 0.33))