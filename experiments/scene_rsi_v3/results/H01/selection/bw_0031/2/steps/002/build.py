# Reference inventory and discrepancy ledger (normalized image coordinates):
# 1. The historical room photograph occupies x=.03-.94, y=.65-1.00 in the
#    reference. The render instead shows a small open-sided model at roughly
#    x=.02-1.00, y=.32-.84, surrounded by empty space. The room is visible
#    with incorrect framing; the large ceiling slab also occludes the upper
#    wall. Change camera position, aim and focal length to fill the frame with
#    the interior, and omit the obstructing near ceiling slab.
# 2. The long operating console occupies approximately x=.03-.68, y=.78-1.00
#    in the reference; in the render it is approximately x=.15-.74, y=.48-.64.
#    It is visible but too small and too far from the foreground. Move the
#    camera inside the room, enlarge its projection, and keep its base on the
#    floor. Its sloped surface, writing ledge and dark pedestal remain connected.
# 3. The back-wall doorway and small right console appear at approximately
#    x=.65-.94, y=.67-.90 in the photograph. In the render the doorway is
#    occluded or outside the view and the small console is not clearly visible.
#    The cause is partly uncertain; change the camera framing and place these
#    elements on the visible back wall to bring both into view.
# Architectural check: the reference back-wall upper and lower edges slope
# gently down toward the right; the render has strong roof and floor diagonals.
# The back cabinets and foreground console are both too small, supporting a
# framing correction. Preserve the cabinet-array/vent arrangement and the main
# console's left-to-right orientation. A small foreground fragment at the left
# edge is represented by the cropped continuation of the console and floor.
# The separate yellow GRID image is not part of the room photograph; its exact
# in-room position is uncertain, so it is placed on the right-hand return wall.
# Primitive estimate: architecture 7, wall cabinets and meters 102, main
# console 125, secondary console 25, GRID panel 45, lights 4: about 308 meshes.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("1970s grid dispatch control room")

ivory = (0.73, 0.71, 0.66)
wall_color = (0.77, 0.75, 0.70)
floor_color = (0.32, 0.29, 0.25)
metal = (0.59, 0.58, 0.54)
pale = (0.86, 0.84, 0.77)
dark = (0.105, 0.10, 0.09)
black = (0.025, 0.025, 0.023)
yellow = (0.92, 0.68, 0.13)
red = (0.72, 0.035, 0.025)
amber = (1.0, 0.45, 0.035)

room = Asset("Architecture")
room.include("floor", box((11, 9, .12), center=(0, 0, -.06), color=floor_color))
room.include("back wall", box((11, .12, 3.4), center=(0, 3.5, 1.7), color=wall_color))
room.include("right return wall", box((.12, 9, 3.4), center=(5.5, -.95, 1.7), color=wall_color))
room.include("back skirting", box((11, .035, .12), center=(0, 3.42, .06), color=metal))
# Ceiling is retained as architecture but stops behind the viewpoint, so it
# cannot conceal the cabinet wall in the overview.
room.include("ceiling", box((11, 4.0, .08), center=(0, 1.55, 3.44), color=pale))
scene.include("Architecture", room)

cabinets = Asset("Main wall instrument cabinets")
cabinets.include("cabinet body", box((7.1, .22, 2.55), center=(-1.62, 3.31, 1.50), color=ivory))
for i, x in enumerate((-5.13, -3.98, -2.83, -1.68, -.53, .62, 1.90)):
    cabinets.include("cabinet seam %d" % i,
                     box((.018, .018, 2.48), center=(x, 3.185, 1.50), color=metal))
# Meter frames and faces: a consistent row/column array with visible gaps.
for c in range(5):
    for r in range(4):
        x = -4.84 + c*.43
        z = .70 + r*.40
        cabinets.include("meter frame %d %d" % (c,r),
                         box((.31,.03,.30), center=(x,3.165,z), color=dark))
        cabinets.include("meter face %d %d" % (c,r),
                         box((.245,.012,.235), center=(x,3.143,z), color=pale))
        cabinets.include("meter pointer %d %d" % (c,r),
                         box((.016,.008,.10), center=(x,3.133,z), color=dark))
cabinets.include("vent dark recess",
                 box((1.28,.03,.71), center=(-1.84,3.16,1.54), color=dark))
for i in range(7):
    cabinets.include("vent slat %d" % i,
                     box((1.20,.025,.045), center=(-1.84,3.135,1.28+i*.085), color=metal))
for c in range(4):
    for r in range(5):
        x = -.73 + c*.31
        z = .66 + r*.31
        cabinets.include("right instrument frame %d %d" % (c,r),
                         box((.22,.025,.23), center=(x,3.16,z), color=dark))
        cabinets.include("right instrument face %d %d" % (c,r),
                         box((.17,.012,.18), center=(x,3.14,z), color=pale))
scene.include("Main wall instrument cabinets", cabinets)

# The doorway is a dark recessed-looking panel in the back wall.
door = Asset("Back wall doorway")
door.include("opening", box((.76,.035,2.22), center=(2.30,3.41,1.11), color=dark))
door.include("inner surface", box((.59,.02,1.93), center=(2.30,3.385,1.12), color=(.31,.30,.27)))
door.include("upper glazed section", box((.47,.012,.58), center=(2.30,3.37,1.78), color=(.47,.46,.42)))
scene.include("Back wall doorway", door)

console = Asset("Long operating console")
console.include("floor standing dark base",
                box((6.15,1.16,.72), center=(-1.66,.50,.36), color=(.19,.18,.16)))
console.include("front writing ledge",
                box((6.35,.48,.09), center=(-1.66,-.29,.84), color=pale))
angle = math.radians(17)
center = Vector((-1.66,.53,1.10))
panel = box((6.35,1.35,.10), center=tuple(center), color=pale)
panel.turn(axis="+x", degrees=17, pivot=tuple(center))
console.include("sloped control surface", panel)

def panel_point(x, y, h=.065):
    return (x, center.y + y*math.cos(angle) - h*math.sin(angle),
            center.z + y*math.sin(angle) + h*math.cos(angle))

for i in range(8):
    x = -4.72 + i*.87
    p = panel_point(x,0,.058)
    seam = box((.017,1.27,.012), center=p, color=metal)
    seam.turn(axis="+x", degrees=17, pivot=p)
    console.include("panel division %d" % i, seam)
for c in range(19):
    for r in range(4):
        x = -4.62 + c*.32
        y = -.46 + r*.28
        p = panel_point(x,y,.073)
        button = box((.07,.07,.04), center=p, color=dark if (c+r)%3 else metal)
        button.turn(axis="+x", degrees=17, pivot=p)
        console.include("switch %02d %d" % (c,r), button)
for i in range(10):
    x = -4.5+i*.59
    p = panel_point(x,.49,.07)
    indicator = box((.19,.14,.025), center=p, color=dark)
    indicator.turn(axis="+x", degrees=17, pivot=p)
    console.include("instrument %d" % i, indicator)
scene.include("Long operating console", console)

small = Asset("Right independent console")
small.include("pedestal", box((1.65,.78,.72), center=(4.05,2.64,.36), color=(.29,.28,.25)))
p = (4.05,2.58,.83)
top = box((1.75,.92,.10), center=p, color=pale)
top.turn(axis="+x", degrees=13, pivot=p)
small.include("sloped top", top)
for c in range(7):
    for r in range(3):
        x = 3.37+c*.22
        y = 2.28+r*.22
        z = .90+(y-2.58)*math.sin(math.radians(13))
        small.include("button %d %d" % (c,r),
                      box((.065,.065,.035), center=(x,y,z), color=dark))
scene.include("Right independent console", small)

grid = Asset("Yellow GRID mimic panel")
grid.include("yellow plate", box((.08,1.55,1.90), center=(5.42,1.35,1.91), color=yellow))
def grid_bar(name, y, z, width, height, color=black, x=5.365):
    grid.include(name, box((.018,width,height), center=(x,y,z), color=color))
grid_bar("vertical bus",1.27,1.92,.035,1.64)
for i,z in enumerate((1.31,1.67,2.16,2.52)):
    grid_bar("horizontal bus %d" % i,1.27,z,.66,.035)
for c,y in enumerate((.99,1.27,1.55)):
    for r,z in enumerate((1.67,2.16)):
        grid_bar("lamp frame %d %d" % (c,r),y,z,.17,.19,black,5.35)
        grid_bar("amber lamp %d %d" % (c,r),y,z,.10,.12,amber,5.335)
for i,(y,z) in enumerate(((1.27,1.17),(1.27,2.70),(1.77,2.48),(1.77,1.28))):
    grid.include("red indicator %d" % i,
                 rod(.067, start=(5.35,y,z), end=(5.30,y,z), color=red))
for i in range(4):
    y=.77
    z=1.30+i*.38
    grid_bar("selector dial %d" % i,y,z,.21,.21,pale,5.35)
    grid.include("black selector %d" % i,
                 rod(.045, start=(5.34,y,z), end=(5.29,y,z), color=black))
scene.include("Yellow GRID mimic panel", grid)

fixtures = Asset("Ceiling fluorescent fixtures")
for i,x in enumerate((-3.5,-1.0,1.5,4.0)):
    fixtures.include("troffer %d" % i,
                     box((1.45,.35,.03), center=(x,2.4,3.38), color=(.96,.95,.88)))
scene.include("Ceiling fluorescent fixtures", fixtures)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.68,.66,.61,1)
background.inputs["Strength"].default_value = .45

# An interior viewpoint keeps the room boundaries outside the picture and
# makes the long console the foreground anchor.
set_view((-5.9,-6.9,3.25), (-.15,2.15,1.34), lens=34)
overview = sc.camera
overview.name = "Camera - room overview"
area_emitter((-2,-1,3.25), power=850, size=5, target=(-1,2,0))
area_emitter((3,1,3.15), power=420, size=3, target=(2,2,0))

bpy.ops.object.camera_add(location=(2.2,-3.4,2.55))
detail_camera = bpy.context.object
detail_camera.name = "Camera - console and GRID detail"
detail_camera.rotation_euler = (Vector((2.4,1.3,1.35))-detail_camera.location).to_track_quat("-Z","Y").to_euler()
detail_camera.data.lens = 38
sc.camera = overview

# German labels on the panel, kept as editable physical text.
def grid_text(body, y, z, size):
    curve = bpy.data.curves.new("GRID label " + body, "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = .001
    obj = bpy.data.objects.new("GRID label " + body, curve)
    sc.collection.objects.link(obj)
    obj.location = (5.28,y,z)
    obj.rotation_euler = (math.pi/2,0,math.pi/2)
    mat = bpy.data.materials.get("GRID label ink")
    if mat is None:
        mat = bpy.data.materials.new("GRID label ink")
        mat.diffuse_color = (.025,.025,.02,1)
    curve.materials.append(mat)

grid_text("NETZ",1.02,2.78,.075)
grid_text("FEHLERSTELLE",1.00,1.02,.052)

# Reuse emissive materials for the visible lamps.
def emissive_material(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color,1)
        bsdf.inputs["Emission Color"].default_value = (*color,1)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

# SceneAct-generated material colors are shared by surface family; only
# materials matching indicator colors receive emission.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    rgb = tuple(bsdf.inputs["Base Color"].default_value[:3])
    if sum(abs(rgb[i]-red[i]) for i in range(3)) < .03:
        bsdf.inputs["Emission Color"].default_value = (*red,1)
        bsdf.inputs["Emission Strength"].default_value = .8
    elif sum(abs(rgb[i]-amber[i]) for i in range(3)) < .03:
        bsdf.inputs["Emission Color"].default_value = (*amber,1)
        bsdf.inputs["Emission Strength"].default_value = .8

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
