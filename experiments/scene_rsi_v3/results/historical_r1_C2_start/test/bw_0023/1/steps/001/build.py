# Reference inventory, estimated from the phone-screen interior:
# - Tall neo-Gothic hall fills the view. Repeated pointed ribbed vaults and
#   arcades occupy the upper 70%, converging toward the bright far end.
# - Clustered pale stone columns line both sides; much of the lower hall is
#   obscured by the staircase, railing, chandelier, and floating spheres.
# - A marble stair and dark-red, gold-trimmed metal railing cross the lower
#   foreground and descend toward the right. The exact stair landing is hidden.
# - A brass chandelier with warm bulbs hangs left of center in the middle distance.
# - Large iridescent bubble is in the right foreground; a smaller magenta sphere
#   is behind and left of it. Their exact depth and the far wall are uncertain.
#
# Expanded primitive estimate: architectural shells ~15, columns ~70,
# vault and arcade ribs ~150, staircase and railing ~100, chandelier ~25,
# spheres 2: approximately 360 separate primitive meshes. Curved ribs use
# short sequences of rods, with no Boolean operations.

import bpy
import math
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter

scene = Scene("Heritage cathedral hall")
stone = (0.68, 0.62, 0.51)
stone_light = (0.78, 0.73, 0.64)
stone_dark = (0.42, 0.38, 0.32)
red = (0.25, 0.025, 0.025)
gold = (0.55, 0.34, 0.10)
marble = (0.78, 0.76, 0.70)

def add_rod(asset, name, a, b, radius, color):
    if (Vector(a) - Vector(b)).length > 0.0001:
        asset.include(name, rod(radius, start=a, end=b, color=color))

def path(asset, name, points, radius, color):
    for i in range(len(points) - 1):
        add_rod(asset, "%s_%02d" % (name, i), points[i], points[i + 1],
                radius, color)

# The hall axis is Y. The camera looks from the near gallery toward the far end.
hall = Asset("vaults")
hall.include("floor", box((9.6, 30, .22), center=(0, 10, -.16),
                          color=(.46, .42, .36)))
hall.include("left_outer_wall", box((.28, 30, 7.8), center=(-4.8, 10, 3.85),
                                   color=stone))
hall.include("right_outer_wall", box((.28, 30, 7.8), center=(4.8, 10, 3.85),
                                    color=stone))
# Light stone ceiling panels provide the continuous vaulted envelope.
hall.include("ceiling_left", box((4.9, 30, .20), center=(-2.35, 10, 8.10),
                                color=stone_light))
hall.include("ceiling_right", box((4.9, 30, .20), center=(2.35, 10, 8.10),
                                 color=stone_light))
# Individual pointed cross-arch profiles, deliberately coarse enough to retain
# clear large-scale silhouette and perspective.
bays = [-2, 1.8, 5.6, 9.4, 13.2, 17.0, 20.8]
arch_profile = [(-4.55, 4.25), (-4.25, 5.45), (-3.55, 6.55),
                (-2.55, 7.40), (-1.35, 7.96), (0, 8.42),
                (1.35, 7.96), (2.55, 7.40), (3.55, 6.55),
                (4.25, 5.45), (4.55, 4.25)]
for j, y in enumerate(bays):
    path(hall, "transverse_rib_%d" % j,
         [(x, y, z) for x, z in arch_profile], .105, stone_dark)
    path(hall, "rib_highlight_%d" % j,
         [(x, y-.065, z+.04) for x, z in arch_profile], .035, stone_light)
    if j < len(bays)-1:
        y2 = bays[j+1]
        # Diagonal groin ribs rise from the capitals to each bay's crown.
        for side in (-1, 1):
            x0 = side * 4.48
            mid = (0, (y+y2)/2, 8.27)
            path(hall, "groin_%d_%d_a" % (j, side),
                 [(x0,y,4.30), (side*3.8,y+.35,5.75),
                  (side*2.6,y+.85,6.95), mid], .065, stone_dark)
            path(hall, "groin_%d_%d_b" % (j, side),
                 [mid, (side*2.6,y2-.85,6.95),
                  (side*3.8,y2-.35,5.75), (x0,y2,4.30)],
                 .065, stone_dark)
# Lateral pointed arcade profiles in the wall plane.
for side in (-1, 1):
    x = side * 4.50
    for j in range(len(bays)-1):
        ya, yb = bays[j], bays[j+1]
        mid = (ya+yb)/2
        pts = [(x,ya,3.7), (x,ya+.35,4.7), (x,ya+1.05,5.45),
               (x,mid,6.15), (x,yb-1.05,5.45),
               (x,yb-.35,4.7), (x,yb,3.7)]
        path(hall, "side_arch_%d_%d" % (side,j), pts, .085, stone_dark)
scene.include("vaults", hall)

columns = Asset("columns")
for side in (-1, 1):
    for j, y in enumerate(bays):
        x = side * 4.40
        columns.include("base_%d_%d" % (side,j),
                        box((.75,.75,.22), center=(x,y,.12), color=stone_dark))
        columns.include("plinth_%d_%d" % (side,j),
                        box((.58,.58,.35), center=(x,y,.38), color=stone))
        # A central shaft and three engaged shafts read as a clustered pier.
        for k, (dx,dy,r) in enumerate([(0,0,.22),(-.24,0,.105),
                                       (.24,0,.105),(0,-.22,.105)]):
            add_rod(columns, "shaft_%d_%d_%d" % (side,j,k),
                    (x+dx,y+dy,.53), (x+dx,y+dy,4.05), r, stone_light)
        columns.include("capital_%d_%d" % (side,j),
                        box((.74,.72,.24), center=(x,y,4.10), color=stone))
        columns.include("abacus_%d_%d" % (side,j),
                        box((.85,.80,.12), center=(x,y,4.28), color=stone_dark))
scene.include("columns", columns)

# A distant light-filled opening anchors the vanishing point.
far = Asset("far_daylight")
far.include("far_wall", box((9.5,.25,7.8), center=(0,23.2,3.9),
                            color=(.83,.79,.69)))
# Slim bright portal set just in front of the far wall.
far.include("opening", box((2.0,.04,4.8), center=(0,23.03,2.8),
                           color=(1.0,.94,.76)))
for x in (-1.05,1.05):
    add_rod(far, "portal_jamb_%s" % x, (x,22.98,.35), (x,22.98,4.4),
            .13, stone_dark)
path(far, "portal_arch", [(-1.05,22.98,4.4),(-.75,22.98,5.0),
                           (0,22.98,5.65),(.75,22.98,5.0),
                           (1.05,22.98,4.4)], .12, stone_dark)
scene.include("far_daylight", far)

stairs = Asset("staircase and railing")
# Broad foreground stair, running down toward the camera.
for i in range(10):
    y = -2.1 + i*.37
    z = .12 + i*.135
    stairs.include("marble_step_%02d" % i,
                   box((3.5,.40,.14), center=(-.35,y,z), color=marble))
    stairs.include("step_nosing_%02d" % i,
                   box((3.52,.045,.045), center=(-.35,y-.19,z+.065),
                       color=stone_light))
# Landing behind the top step.
stairs.include("landing", box((4.0,1.5,.20), center=(-.35,2.22,1.40),
                               color=marble))
# Sloping ornamental balustrade at the stair's right edge.
xrail = 1.46
y0, y1 = -2.26, 1.45
z0, z1 = .20, 1.55
add_rod(stairs, "lower_rail", (xrail,y0,z0+.28), (xrail,y1,z1+.28), .055, red)
add_rod(stairs, "upper_rail", (xrail,y0,z0+1.25), (xrail,y1,z1+1.25), .080, red)
add_rod(stairs, "gold_hand_edge", (xrail,y0,z0+1.31),
        (xrail,y1,z1+1.31), .024, gold)
for i in range(11):
    t = i/10
    y = y0+(y1-y0)*t
    z = z0+(z1-z0)*t
    add_rod(stairs, "baluster_%02d" % i, (xrail,y,z+.28),
            (xrail,y,z+1.25), .035, red)
    if i < 10:
        yn = y0+(y1-y0)*(i+1)/10
        zn = z0+(z1-z0)*(i+1)/10
        # Alternating diagonals suggest the open wrought-metal scrollwork.
        add_rod(stairs, "diagonal_%02d" % i,
                (xrail,y,z+.38), (xrail,yn,zn+1.05), .021, gold)
for i, (y,z) in enumerate([(y0,z0), (y1,z1)]):
    add_rod(stairs, "newel_%d" % i, (xrail,y,z), (xrail,y,z+1.42), .09, red)
    stairs.include("newel_cap_%d" % i, ball(.11, center=(xrail,y,z+1.45),
                                             color=gold))
scene.include("staircase and railing", stairs)

chandelier = Asset("chandelier")
cx, cy, cz = -1.25, 7.2, 4.15
add_rod(chandelier, "suspension", (cx,cy,cz+.3), (cx,cy,7.9), .025, gold)
add_rod(chandelier, "central_stem", (cx,cy,cz-.45), (cx,cy,cz+.35), .07, gold)
chandelier.include("central_drop", ball(.16, center=(cx,cy,cz-.45), color=gold))
for i in range(8):
    a = 2*math.pi*i/8
    dx, dy = math.cos(a), math.sin(a)
    p0 = (cx,cy,cz-.18)
    p1 = (cx+.42*dx,cy+.42*dy,cz-.35)
    p2 = (cx+.78*dx,cy+.78*dy,cz-.10)
    path(chandelier, "arm_%d" % i, [p0,p1,p2], .035, gold)
    add_rod(chandelier, "candle_%d" % i, p2,
            (p2[0],p2[1],p2[2]+.24), .055, stone_light)
    chandelier.include("bulb_%d" % i,
                        ball(.075, center=(p2[0],p2[1],p2[2]+.29),
                             color=(1,.81,.42)))
scene.include("chandelier", chandelier)

spheres = Asset("spheres")
spheres.include("large iridescent bubble",
                ball(1.17, center=(2.45,3.4,3.40), color=(.65,.45,.75)))
spheres.include("small magenta sphere",
                ball(.46, center=(.15,7.0,3.85), color=(.72,.005,.43)))
scene.include("spheres", spheres)

realize(scene)

# Material refinements are assigned to the named realized meshes where available.
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
wn = sc.world.node_tree.nodes
background = wn.get("Background") or wn.new("ShaderNodeBackground")
output = wn.get("World Output") or wn.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.68, 0.72, 0.78, 1)
background.inputs["Strength"].default_value = 0.42

def make_stone():
    mat = bpy.data.materials.new("Warm aged limestone")
    mat.diffuse_color = (.72,.67,.57,1)
    mat.use_nodes = True
    n = mat.node_tree.nodes
    l = mat.node_tree.links
    bs = n.get("Principled BSDF")
    bs.inputs["Roughness"].default_value = .78
    tex = n.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 7
    tex.inputs["Detail"].default_value = 3
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (.42,.37,.29,1)
    ramp.color_ramp.elements[1].color = (.80,.75,.65,1)
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .16
    bump.inputs["Distance"].default_value = .055
    l.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    l.new(tex.outputs["Fac"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return mat

stone_mat = make_stone()

bubble = bpy.data.materials.new("Iridescent thin film bubble")
bubble.use_nodes = True
n = bubble.node_tree.nodes
l = bubble.node_tree.links
bs = n.get("Principled BSDF")
bs.inputs["Base Color"].default_value = (.72,.45,.8,1)
bs.inputs["Metallic"].default_value = .12
bs.inputs["Roughness"].default_value = .10
if "Transmission Weight" in bs.inputs:
    bs.inputs["Transmission Weight"].default_value = .72
elif "Transmission" in bs.inputs:
    bs.inputs["Transmission"].default_value = .72
bs.inputs["IOR"].default_value = 1.33
if "Thin Film Thickness" in bs.inputs:
    bs.inputs["Thin Film Thickness"].default_value = 420
    bs.inputs["Thin Film IOR"].default_value = 1.33
# The layer-weight ramp supplies view-dependent interference colors on versions
# of Blender that do not expose the thin-film shader inputs.
layer = n.new("ShaderNodeLayerWeight")
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
for pos, col in [(0,(.06,.65,.9,1)),(.22,(.85,.06,.55,1)),
                 (.46,(1,.66,.08,1)),(.70,(.22,.8,.66,1)),
                 (1,(.72,.56,.86,1))]:
    e = ramp.color_ramp.elements[0] if pos == 0 else ramp.color_ramp.elements.new(pos)
    e.position = pos
    e.color = col
l.new(layer.outputs["Facing"], ramp.inputs["Fac"])
l.new(ramp.outputs["Color"], bs.inputs["Base Color"])

magenta = bpy.data.materials.new("Matte magenta")
magenta.diffuse_color = (.65,.005,.32,1)
magenta.use_nodes = True
m_bs = magenta.node_tree.nodes.get("Principled BSDF")
m_bs.inputs["Base Color"].default_value = (.65,.005,.32,1)
m_bs.inputs["Roughness"].default_value = .78

bulbmat = bpy.data.materials.new("Warm glowing bulbs")
bulbmat.use_nodes = True
b = bulbmat.node_tree.nodes.get("Principled BSDF")
b.inputs["Base Color"].default_value = (1,.68,.27,1)
if "Emission Color" in b.inputs:
    b.inputs["Emission Color"].default_value = (1,.55,.16,1)
    b.inputs["Emission Strength"].default_value = 5
elif "Emission" in b.inputs:
    b.inputs["Emission"].default_value = (1,.55,.16,1)

# SceneAct names are retained in object or parent names depending on version.
def lineage(obj):
    parts = []
    while obj:
        parts.append(obj.name.lower())
        obj = obj.parent
    return " ".join(parts)

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
        mat = bulbmat
    elif ("vaults" in name or "columns" in name) and "rib" not in name:
        mat = stone_mat
    if mat is not None:
        obj.data.materials.clear()
        obj.data.materials.append(mat)

set_view((.25,-8.7,4.55), (.05,8.3,4.05), lens=31, sensor=36)
area_emitter((0,5.8,5.1), power=1300, size=2.5, target=(0,5,1.0),
             color=(1.0,.72,.43))
area_emitter((0,21.9,5.1), power=2200, size=4.0, target=(0,5,3.0),
             color=(1.0,.90,.72))
area_emitter((-2,-4,6.8), power=900, size=5.0, target=(0,6,3.0),
             color=(1.0,.82,.65))

# Collection names make the requested major elements easy to locate.
for label in ("vaults", "columns", "staircase and railing", "chandelier", "spheres"):
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
