# Reference inventory (normalized bounds refer to the phone-screen interior):
# - Warm stone Gothic hall fills the image; high ribbed vaults occupy the upper
#   half, with pointed arcades and clustered columns receding along both sides.
# - A chandelier hangs left of center. Its fine details and suspension are partly
#   obscured by the small magenta sphere.
# - A stair and ornate red-and-gold railing cross the lower foreground. The
#   landing, lower floor, and exact stair direction are partly hidden.
# - A magenta solid sphere sits near the center, behind a much larger iridescent
#   sphere whose right side is cropped by the phone screen.
# - Bright openings and detailed architecture beyond the near bays are uncertain.
#
# Comparison with the first render: the vault and bay rhythm are recognizable,
# but the hall is too uniformly pale, the large bubble is too small, the stair
# reads as a frontal flight rather than a diagonal foreground feature, and the
# far end lacks a bright opening. The visible black ceiling seam is unintended.
# This revision retains the hall and chandelier hierarchy while strengthening
# depth, contrast, the railing silhouette, and the foreground bubble.
#
# Estimated expanded primitive count: shell 5; cross ribs 60; diagonal ribs
# 144; side arches 72; columns 112; stair and railing about 55; chandelier 35;
# distant opening 8; spheres 2. Total approximately 493 primitive meshes.
# Curves are short rod paths; there are no Boolean operations.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter

scene = Scene("Heritage Gothic gallery")
stone = (0.69, 0.63, 0.54)
light_stone = (0.80, 0.75, 0.66)
shadow_stone = (0.41, 0.36, 0.30)
red = (0.25, 0.025, 0.022)
gold = (0.62, 0.39, 0.12)
marble = (0.79, 0.76, 0.69)

def line(asset, name, a, b, radius, color):
    if (Vector(a) - Vector(b)).length > 0.00001:
        asset.include(name, rod(radius, start=a, end=b, color=color))

def path(asset, name, points, radius, color):
    for i in range(len(points) - 1):
        line(asset, "%s_%02d" % (name, i), points[i], points[i + 1],
             radius, color)

# Long hall, camera looking toward positive Y.
vaults = Asset("vaults")
vaults.include("floor", box((9.8, 32, .20), center=(0, 10, -.12),
                            color=(.48, .44, .38)))
vaults.include("left_wall", box((.30, 32, 8.8), center=(-4.9, 10, 4.3),
                                color=stone))
vaults.include("right_wall", box((.30, 32, 8.8), center=(4.9, 10, 4.3),
                                 color=stone))
# The continuous ceiling is above the rib crowns, avoiding a dark seam.
vaults.include("ceiling", box((10, 32, .22), center=(0, 10, 8.70),
                              color=light_stone))
bays = [-2.0, 1.8, 5.6, 9.4, 13.2, 17.0, 20.8]
profile = [(-4.55, 4.25), (-4.25, 5.45), (-3.55, 6.52),
           (-2.55, 7.38), (-1.35, 8.00), (0, 8.46),
           (1.35, 8.00), (2.55, 7.38), (3.55, 6.52),
           (4.25, 5.45), (4.55, 4.25)]
for j, y in enumerate(bays):
    path(vaults, "cross_arch_%d" % j,
         [(x, y, z) for x, z in profile], .105, shadow_stone)
    if j < len(bays) - 1:
        y2 = bays[j + 1]
        for side in (-1, 1):
            mid = (0, (y + y2) / 2, 8.43)
            path(vaults, "diagonal_a_%d_%d" % (j, side),
                 [(side*4.48, y, 4.30), (side*3.8, y+.35, 5.75),
                  (side*2.6, y+.85, 6.95), mid], .075, shadow_stone)
            path(vaults, "diagonal_b_%d_%d" % (j, side),
                 [mid, (side*2.6, y2-.85, 6.95),
                  (side*3.8, y2-.35, 5.75), (side*4.48, y2, 4.30)],
                 .075, shadow_stone)
for side in (-1, 1):
    x = side * 4.5
    for j in range(len(bays)-1):
        ya, yb = bays[j], bays[j+1]
        mid = (ya + yb) / 2
        path(vaults, "arcade_%d_%d" % (side,j),
             [(x,ya,3.7), (x,ya+.35,4.7), (x,ya+1.05,5.45),
              (x,mid,6.15), (x,yb-1.05,5.45),
              (x,yb-.35,4.7), (x,yb,3.7)], .09, shadow_stone)
scene.include("vaults", vaults)

columns = Asset("columns")
for side in (-1, 1):
    for j, y in enumerate(bays):
        x = side * 4.40
        columns.include("base_%d_%d" % (side,j),
                        box((.76,.76,.22), center=(x,y,.12),
                            color=shadow_stone))
        columns.include("plinth_%d_%d" % (side,j),
                        box((.59,.59,.35), center=(x,y,.38), color=stone))
        for k, (dx,dy,r) in enumerate([(0,0,.22),(-.24,0,.105),
                                       (.24,0,.105),(0,-.22,.105)]):
            line(columns, "shaft_%d_%d_%d" % (side,j,k),
                 (x+dx,y+dy,.53), (x+dx,y+dy,4.05), r, light_stone)
        columns.include("capital_%d_%d" % (side,j),
                        box((.74,.72,.24), center=(x,y,4.10), color=stone))
        columns.include("abacus_%d_%d" % (side,j),
                        box((.85,.80,.12), center=(x,y,4.28),
                            color=shadow_stone))
scene.include("columns", columns)

# Pale end wall with a tall, luminous entrance framed by a pointed arch.
far = Asset("far daylight")
far.include("wall", box((9.5,.24,8.5), center=(0,23.2,4.25),
                        color=(.77,.72,.63)))
far.include("bright opening", box((2.1,.035,4.65), center=(0,23.05,2.45),
                                  color=(1.0,.96,.82)))
for x in (-1.12,1.12):
    line(far, "jamb_%s" % x, (x,22.98,.12), (x,22.98,4.5),
         .13, stone)
path(far, "pointed portal",
     [(-1.12,22.98,4.5),(-.80,22.98,5.05),(0,22.98,5.7),
      (.80,22.98,5.05),(1.12,22.98,4.5)], .12, stone)
scene.include("far daylight", far)

stairs = Asset("staircase & railing")
# Steps span the lower foreground; the red balustrade is offset to the left
# and runs diagonally through the view, with open gaps between balusters.
for i in range(10):
    y = -2.1 + i*.37
    z = .12 + i*.135
    stairs.include("marble_step_%02d" % i,
                   box((3.5,.40,.14), center=(-.35,y,z), color=marble))
    stairs.include("nosing_%02d" % i,
                   box((3.52,.045,.045), center=(-.35,y-.19,z+.065),
                       color=light_stone))
stairs.include("landing", box((4.0,1.5,.20), center=(-.35,2.22,1.40),
                              color=marble))
xrail = -1.98
y0, y1 = -2.26, 1.45
z0, z1 = .20, 1.55
line(stairs, "lower_red_rail", (xrail,y0,z0+.28), (xrail,y1,z1+.28), .06, red)
line(stairs, "red_handrail", (xrail,y0,z0+1.25), (xrail,y1,z1+1.25), .09, red)
line(stairs, "gold_handrail_trim", (xrail,y0,z0+1.32),
     (xrail,y1,z1+1.32), .026, gold)
for i in range(11):
    t = i/10
    y, z = y0+(y1-y0)*t, z0+(z1-z0)*t
    line(stairs, "baluster_%02d" % i, (xrail,y,z+.28),
         (xrail,y,z+1.25), .037, red)
    if i < 10:
        yn = y0+(y1-y0)*(i+1)/10
        zn = z0+(z1-z0)*(i+1)/10
        line(stairs, "ornament_%02d" % i, (xrail,y,z+.39),
             (xrail,yn,zn+1.06), .022, gold)
for i, (y,z) in enumerate([(y0,z0),(y1,z1)]):
    line(stairs, "newel_%d" % i, (xrail,y,z), (xrail,y,z+1.42), .09, red)
    stairs.include("newel_finial_%d" % i,
                   ball(.11, center=(xrail,y,z+1.45), color=gold))
scene.include("staircase & railing", stairs)

chandelier = Asset("chandelier")
cx, cy, cz = -1.30, 7.2, 4.15
line(chandelier, "suspension", (cx,cy,cz+.3), (cx,cy,8.3), .025, gold)
line(chandelier, "stem", (cx,cy,cz-.45), (cx,cy,cz+.35), .07, gold)
chandelier.include("drop", ball(.16, center=(cx,cy,cz-.45), color=gold))
for i in range(8):
    a = 2*math.pi*i/8
    dx, dy = math.cos(a), math.sin(a)
    p0 = (cx,cy,cz-.18)
    p1 = (cx+.42*dx,cy+.42*dy,cz-.35)
    p2 = (cx+.78*dx,cy+.78*dy,cz-.10)
    path(chandelier, "arm_%d" % i, [p0,p1,p2], .035, gold)
    line(chandelier, "candle_%d" % i, p2,
         (p2[0],p2[1],p2[2]+.24), .055, light_stone)
    chandelier.include("bulb_%d" % i,
                        ball(.075, center=(p2[0],p2[1],p2[2]+.29),
                             color=(1,.88,.63)))
scene.include("chandelier", chandelier)

spheres = Asset("spheres")
spheres.include("large iridescent bubble",
                ball(1.85, center=(3.10,1.65,3.45), color=(.6,.5,.8)))
spheres.include("small magenta sphere",
                ball(.58, center=(-.25,6.4,3.85), color=(.72,.005,.36)))
scene.include("spheres", spheres)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
wn = sc.world.node_tree.nodes
background = wn.get("Background") or wn.new("ShaderNodeBackground")
output = wn.get("World Output") or wn.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.64,.68,.72,1)
background.inputs["Strength"].default_value = .28

def lineage(obj):
    names = []
    while obj:
        names.append(obj.name.lower())
        obj = obj.parent
    return " ".join(names)

def principled_material(name, color, roughness=.5, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    p = mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color,1)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic
    return mat

limestone = principled_material("Warm aged limestone", (.68,.61,.51), .79)
n = limestone.node_tree.nodes
links = limestone.node_tree.links
p = n.get("Principled BSDF")
noise = n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 7
noise.inputs["Detail"].default_value = 3
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (.42,.37,.30,1)
ramp.color_ramp.elements[1].color = (.78,.72,.62,1)
bump = n.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .12
bump.inputs["Distance"].default_value = .035
links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], p.inputs["Base Color"])
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], p.inputs["Normal"])

bubble = principled_material("Iridescent soap film", (.65,.35,.68), .10, .12)
n = bubble.node_tree.nodes
links = bubble.node_tree.links
p = n.get("Principled BSDF")
if "Transmission Weight" in p.inputs:
    p.inputs["Transmission Weight"].default_value = .36
elif "Transmission" in p.inputs:
    p.inputs["Transmission"].default_value = .36
p.inputs["IOR"].default_value = 1.33
if "Thin Film Thickness" in p.inputs:
    p.inputs["Thin Film Thickness"].default_value = 420
    p.inputs["Thin Film IOR"].default_value = 1.33
layer = n.new("ShaderNodeLayerWeight")
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
colors = [(0,(.05,.55,.9,1)),(.18,(.95,.10,.55,1)),
          (.36,(1,.65,.05,1)),(.53,(.12,.8,.65,1)),
          (.70,(.40,.13,.90,1)),(.84,(.95,.38,.19,1)),
          (1,(.45,.78,.9,1))]
for pos, col in colors:
    e = ramp.color_ramp.elements[0] if pos == 0 else ramp.color_ramp.elements.new(pos)
    e.position = pos
    e.color = col
links.new(layer.outputs["Facing"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], p.inputs["Base Color"])

magenta = principled_material("Matte deep magenta", (.55,.002,.26), .72)
bulb = principled_material("Warm glowing bulbs", (1,.82,.55), .35)
p = bulb.node_tree.nodes.get("Principled BSDF")
if "Emission Color" in p.inputs:
    p.inputs["Emission Color"].default_value = (1,.70,.35,1)
    p.inputs["Emission Strength"].default_value = 4
elif "Emission" in p.inputs:
    p.inputs["Emission"].default_value = (1,.70,.35,1)

opening = principled_material("Daylight in distant portal", (1,.94,.78), .8)
p = opening.node_tree.nodes.get("Principled BSDF")
if "Emission Color" in p.inputs:
    p.inputs["Emission Color"].default_value = (1,.90,.70,1)
    p.inputs["Emission Strength"].default_value = 2

for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    name = lineage(obj)
    mat = None
    if "large iridescent bubble" in name:
        mat = bubble
        for poly in obj.data.polygons:
            poly.use_smooth = True
    elif "small magenta sphere" in name:
        mat = magenta
        for poly in obj.data.polygons:
            poly.use_smooth = True
    elif "bulb_" in name:
        mat = bulb
    elif "bright opening" in name:
        mat = opening
    elif ("vaults" in name or "columns" in name) and not any(
            s in name for s in ("arch", "diagonal", "arcade", "abacus")):
        mat = limestone
    if mat is not None:
        obj.data.materials.clear()
        obj.data.materials.append(mat)

set_view((.25,-8.7,4.55), (.05,8.3,4.05), lens=31, sensor=36)
area_emitter((-1.3,7.0,4.4), power=950, size=2.2,
             target=(0,5,1.0), color=(1.0,.71,.43))
area_emitter((0,22.7,4.7), power=2800, size=3.8,
             target=(0,5,3.0), color=(1.0,.91,.75))
area_emitter((-2,-4,6.8), power=650, size=5,
             target=(0,6,3.0), color=(1.0,.82,.65))

for label in ("vaults", "columns", "staircase & railing", "chandelier", "spheres"):
    coll = bpy.data.collections.get(label)
    if coll is None:
        coll = bpy.data.collections.new(label)
        sc.collection.children.link(coll)
    for obj in list(bpy.data.objects):
        if label in lineage(obj) and obj.name not in coll.objects:
            coll.objects.link(obj)
            for old in list(obj.users_collection):
                if old != coll:
                    old.objects.unlink(obj)

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.resolution_x = 3840
sc.render.resolution_y = 2160
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "Filmic"
except Exception:
    pass
