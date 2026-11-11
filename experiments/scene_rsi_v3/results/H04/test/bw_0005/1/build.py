from sceneact import *
import bpy
from mathutils import Vector

# Reference inventory, in the classroom inset's approximate normalized bounds:
# Back windows: (.08,.06)-(.65,.38), with cream wall continuing right.
# Left low shelves: (.05,.38)-(.34,.72); central child table and chairs:
# (.30,.39)-(.64,.65); foreground open cabinet: (.34,.45)-(.83,.86).
# A rust-red round rug extends beneath and in front of that cabinet, roughly
# (.30,.73)-(.87,.98). Additional low storage occupies the rear and right.
# Windows, furniture and rug overlap; objects behind the shelves are uncertain.
# Cabinet and window edges are nearly horizontal, while receding floor edges
# angle toward the back. The room outside the photo's irregular crop is unknown.
#
# Previous render, estimated visually: windows span approximately (.02,.22) to
# (.53,.48); the island spans (.46,.55) to (.84,.91), and the exposed rug is
# around (.60,.77)-(.83,.91). Gray space above the walls occupies roughly the
# top fifth. The island obscures part of the table, as in the reference, but
# its light, nearly empty cubbies have less contrast and material variety.
#
# Ranked corrections:
# 1. Extend the walls and add a ceiling: the gray upper crop becomes a light
#    indoor ceiling while preserving the current camera and window positions.
# 2. Move the foreground island and rug left by .55 m: their contours and the
#    rug's visible front should move left, without moving background windows.
# 3. Darken recessed cabinet backs and add a few loose items: the shelf openings
#    should read as distinct gaps. Lower the light intensity for warmer contrast;
#    observed brightness depends on both illumination and material color.
# The camera pose and lens remain unchanged. The projection diagnostic prints
# both the selected camera and a small upward-aim trial, then restores the pose.
# Computed points are not the same as observed silhouette bounds.
#
# Expanded primitive estimate: architecture 19, windows 37, cabinets 32,
# rug 2, tables and stools 20, materials and secondary furniture about 45:
# approximately 155 meshes, with no Boolean operations or repeated fillets.

scene = Scene("Montessori classroom")

ROOM_W, ROOM_D, ROOM_H = 9.2, 11.0, 3.05
BACK_Y = 3.70
FRONT_Y = BACK_Y - ROOM_D
CAMERA_POS = (-4.0, -5.15, 2.45)
CAMERA_TARGET = (0.15, 1.15, 1.05)
CAMERA_LENS = 25

FLOOR = (0.62, 0.46, 0.31)
FLOOR_SEAM = (0.49, 0.35, 0.23)
WALL = (0.76, 0.73, 0.65)
CEILING = (0.82, 0.80, 0.73)
WHITE = (0.90, 0.88, 0.80)
GLASS = (0.61, 0.73, 0.69)
WOOD = (0.54, 0.34, 0.16)
WOOD_LIGHT = (0.70, 0.49, 0.28)
WOOD_DARK = (0.27, 0.18, 0.10)
RUG = (0.46, 0.105, 0.065)

room = Asset("Room architecture")
room.include("wood floor", box((ROOM_W, ROOM_D, .10),
    center=(0, (BACK_Y+FRONT_Y)/2, -.05), color=FLOOR))
room.include("back wall", box((ROOM_W, .12, ROOM_H),
    center=(0, BACK_Y, ROOM_H/2), color=WALL))
room.include("right wall", box((.12, ROOM_D, ROOM_H),
    center=(ROOM_W/2, (BACK_Y+FRONT_Y)/2, ROOM_H/2), color=WALL))
room.include("ceiling", box((ROOM_W, ROOM_D, .10),
    center=(0, (BACK_Y+FRONT_Y)/2, ROOM_H+.05), color=CEILING))
room.include("back baseboard", box((ROOM_W, .05, .13),
    center=(0, BACK_Y-.085, .065), color=WHITE))
room.include("right baseboard", box((.05, ROOM_D, .13),
    center=(ROOM_W/2-.085, (BACK_Y+FRONT_Y)/2, .065), color=WHITE))
for i in range(12):
    x = -ROOM_W/2 + (i+1)*ROOM_W/13
    room.include("floor board seam %02d" % i,
        box((.008, ROOM_D, .003),
            center=(x, (BACK_Y+FRONT_Y)/2, .002), color=FLOOR_SEAM))
scene.include("architecture", room)

windows = Asset("Back wall windows")
wy = BACK_Y - .085
for i, x in enumerate((-3.62, -2.55, -1.48, -.41, .66, 1.73)):
    width, height, z = .96, 1.45, 2.00
    windows.include("glazing %d" % i,
        box((width, .028, height), center=(x, wy-.02, z), color=GLASS))
    for j, side in enumerate((-1, 1)):
        windows.include("vertical frame %d %d" % (i, j),
            box((.055, .065, height+.11),
                center=(x+side*width/2, wy-.055, z), color=WHITE))
    for j, dz in enumerate((-height/2, height/2)):
        windows.include("horizontal frame %d %d" % (i, j),
            box((width+.11, .065, .055),
                center=(x, wy-.055, z+dz), color=WHITE))
    windows.include("sash %d" % i,
        box((width, .065, .035),
            center=(x, wy-.06, z-.15), color=WHITE))
windows.include("continuous sill", box((6.55, .20, .07),
    center=(-.945, wy-.11, 1.24), color=WHITE))
scene.include("windows", windows)

def cabinet(name, x, y, width, depth, height=.83, bays=3):
    a = Asset(name)
    t = .055
    a.include("recessed back", box((width, t, height),
        center=(x, y+depth/2-t/2, height/2), color=WOOD_DARK))
    for label, z in (("bottom", t/2), ("middle", height*.49),
                     ("top", height-t/2)):
        a.include(label, box((width, depth, t),
            center=(x, y, z), color=WOOD_LIGHT))
    for j in range(bays+1):
        xx = x-width/2+j*width/bays
        a.include("upright %d" % j, box((t, depth, height),
            center=(xx, y, height/2), color=WOOD))
    scene.include(name, a)

island_x = -.20
island_y = -1.20
cabinet("Foreground island", island_x, island_y, 3.55, .82, .91, 3)
cabinet("Left low shelf", -3.15, 1.06, 2.05, .64, .83, 3)
cabinet("Back low shelf", -.30, 2.85, 2.55, .58, .76, 3)
cabinet("Right low shelf", 3.10, 1.90, 2.15, .58, .80, 3)

rug = Asset("Round rust red rug")
rug.include("outer rug", rod(1.25, length=.018,
    center=(island_x, -1.22, .012), color=RUG))
rug.include("inner rug", rod(1.08, length=.019,
    center=(island_x, -1.22, .022), color=(.58, .25, .14)))
scene.include("rug", rug)

def table(name, x, y, w, d):
    a = Asset(name)
    a.include("top", box((w, d, .065),
        center=(x, y, .59), color=WOOD_LIGHT))
    for i, dx in enumerate((-w/2+.09, w/2-.09)):
        for j, dy in enumerate((-d/2+.09, d/2-.09)):
            a.include("leg %d %d" % (i, j), box((.065, .065, .56),
                center=(x+dx, y+dy, .28), color=WOOD))
    scene.include(name, a)

def stool(name, x, y):
    a = Asset(name)
    a.include("seat", box((.34, .32, .045),
        center=(x, y, .34), color=WOOD_LIGHT))
    for i, dx in enumerate((-.12, .12)):
        for j, dy in enumerate((-.11, .11)):
            a.include("leg %d %d" % (i, j), box((.04, .04, .32),
                center=(x+dx, y+dy, .16), color=WOOD))
    scene.include(name, a)

table("Center activity table", -.75, 1.12, 1.45, .76)
stool("Left child stool", -1.58, .63)
stool("Right child stool", .13, .71)
stool("Back child stool", -.69, 1.78)

materials = Asset("Trays and Montessori materials")
def tray(name, x, y, z, width=.35, depth=.23):
    materials.include(name+" base", box((width, depth, .025),
        center=(x, y, z), color=WOOD_LIGHT))
    materials.include(name+" rear edge", box((width, .025, .045),
        center=(x, y+depth/2-.012, z+.028), color=WOOD))
    materials.include(name+" left edge", box((.025, depth, .045),
        center=(x-width/2+.012, y, z+.028), color=WOOD))
    materials.include(name+" right edge", box((.025, depth, .045),
        center=(x+width/2-.012, y, z+.028), color=WOOD))

for i, dx in enumerate((-1.30, -.75, -.20, .35, .90)):
    x = island_x + dx
    tray("Island tray %d" % i, x, island_y, .93)
    materials.include("Island block %d" % i, box((.10, .10, .09),
        center=(x, island_y, 1.00),
        color=((.77,.64,.42), (.55,.40,.23), (.82,.74,.52))[i%3]))
for i, x in enumerate((-3.72, -3.15, -2.58)):
    tray("Left tray %d" % i, x, 1.06, .85)
for i, x in enumerate((-1.12, -.30, .52)):
    tray("Back tray %d" % i, x, 2.85, .78)
for i, x in enumerate((2.42, 3.10, 3.78)):
    materials.include("Right wooden box %d" % i, box((.31, .23, .12),
        center=(x, 1.90, .87), color=WOOD_LIGHT))
for i, dx in enumerate((-1.17, 0, 1.17)):
    materials.include("Island cubby box %d" % i, box((.37, .25, .15),
        center=(island_x+dx, -1.37, .14), color=(.48, .32, .17)))
scene.include("learning materials", materials)

extras = Asset("Additional classroom furnishings")
extras.include("wall board frame", box((1.05, .04, .54),
    center=(3.35, wy-.03, 1.78), color=WOOD))
extras.include("wall board", box((.94, .025, .43),
    center=(3.35, wy-.06, 1.78), color=(.82, .80, .70)))
extras.include("right work surface", box((1.25, .48, .055),
    center=(3.50, 2.82, .72), color=WOOD_LIGHT))
for i, x in enumerate((2.97, 4.03)):
    extras.include("work surface leg %d" % i, box((.06, .06, .69),
        center=(x, 2.82, .345), color=WOOD))
scene.include("secondary furnishings", extras)

realize(scene)
set_view(CAMERA_POS, CAMERA_TARGET, lens=CAMERA_LENS)

sc = bpy.context.scene
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background")
if background is None:
    background = nodes.new("ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.78, .82, .83, 1)
background.inputs["Strength"].default_value = .38

area_emitter((-1.4, 3.05, 2.55), power=850, size=5.0,
    target=(0, -.5, .3), color=(1.0, .91, .78))
area_emitter((-2.0, -2.5, 2.85), power=350, size=6.0,
    target=(0, .7, .4), color=(1.0, .95, .86))

sc.render.engine = 'CYCLES'
sc.cycles.samples = 128
sc.cycles.use_denoising = True

# Reference coordinates are estimates within the photographic inset.
landmarks = [
    ("window upper left", (-4.10, wy-.055, 2.725), (.08, .06)),
    ("window upper right", (2.21, wy-.055, 2.725), (.65, .06)),
    ("island top left", (island_x-1.775, island_y-.41, .91), (.34, .49)),
    ("island top right", (island_x+1.775, island_y-.41, .91), (.83, .56)),
    ("rug front", (island_x, -2.47, .022), (.57, .98)),
]

def projected_points():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    rows = []
    for name, point, reference in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        rows.append((name, reference,
                     None if uv is None else tuple(round(v, 3) for v in uv)))
    return rows

print("Selected camera: landmark | reference estimate | computed projection")
for row in projected_points():
    print(row)

cam = sc.camera
saved_rotation = cam.rotation_euler.copy()
trial_target = Vector(CAMERA_TARGET) + Vector((0, 0, .12))
cam.rotation_euler = (trial_target - cam.location).to_track_quat('-Z', 'Y').to_euler()
print("Upward aim trial: landmark | reference estimate | computed projection")
for row in projected_points():
    print(row)
cam.rotation_euler = saved_rotation
bpy.context.view_layer.update()
