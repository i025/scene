from sceneact import *
import bpy
from mathutils import Vector

# Reference inventory, estimated within the classroom photograph inset:
# Windows occupy roughly (.08,.04)-(.63,.37); a cream wall extends rightward.
# The floor fills roughly the lower half. A long low cabinet at (.30,.49)-(.83,.90)
# overlaps a rust-red oval rug at (.27,.77)-(.88,.98). Its front has two rows of
# dark, open cubbies; trays and small objects sit on top. Left shelves occupy
# (.08,.36)-(.34,.69); shorter right and rear shelves occupy approximately
# (.70,.34)-(.99,.68). Small activity tables and child chairs are in the center.
# Details behind furniture and outside the inset are uncertain.
# Background window edges are nearly horizontal, rising slightly toward the right.
# Cabinet top edges slope gently down toward the right; receding edges slope upward.
#
# Previous render versus inset: windows were around (.43,.20)-(.71,.30), instead
# of spanning about (.08,.04)-(.63,.37); the island was around (.39,.51)-(.53,.60),
# instead of spanning roughly (.30,.49)-(.83,.90). The rug appeared around
# (.44,.66), far above and smaller than the reference. A large exterior right wall
# obscured the room and the whole scene floated within gray margins.
# Largest discrepancies: (1) camera too distant and aimed at an exterior corner;
# (2) foreground island and rug too small in the view; (3) walls and floor too
# pale and lacking the reference's warm wood contrast.
# Correction: put CAMERA_POS inside the front left corner and aim toward the back
# right, with a wide lens; this expands the room and island across the frame and
# removes the exterior wall silhouette. Keep the back wall and floor large enough
# to extend beyond the camera crop. Increase island width and bring it forward;
# its contour should expand across the lower center and overlap more of the rug.
# Window spacing and shelf positions are changed locally to follow the inset.
# Projection values printed below are computed point locations, not observed
# contours. A small upward camera-aim trial is printed then restored.
#
# Approximate expanded primitive count: architecture 17, windows 37, cabinets
# 42, table and stools 22, rug 2, materials 45, secondary furniture 15:
# about 180 meshes. Hidden geometry and exact object identities remain uncertain.

scene = Scene("Montessori classroom")

# Independent camera and room parameters.
ROOM_W, ROOM_D, ROOM_H = 9.2, 7.4, 3.05
CAMERA_POS = (-4.0, -5.15, 2.45)
CAMERA_TARGET = (0.15, 1.15, 1.05)
CAMERA_LENS = 25

FLOOR = (0.62, 0.46, 0.31)
FLOOR_SEAM = (0.49, 0.35, 0.23)
WALL = (0.76, 0.73, 0.65)
WHITE = (0.90, 0.88, 0.80)
GLASS = (0.66, 0.77, 0.73)
WOOD = (0.54, 0.34, 0.16)
WOOD_LIGHT = (0.70, 0.49, 0.28)
WOOD_DARK = (0.31, 0.22, 0.13)
RUG = (0.46, 0.105, 0.065)

room = Asset("Room architecture")
room.include("light wood floor", box((ROOM_W, ROOM_D, .10),
    center=(0, 0, -.05), color=FLOOR))
room.include("cream back wall", box((ROOM_W, .12, ROOM_H),
    center=(0, ROOM_D/2, ROOM_H/2), color=WALL))
room.include("cream right wall", box((.12, ROOM_D, ROOM_H),
    center=(ROOM_W/2, 0, ROOM_H/2), color=WALL))
room.include("back baseboard", box((ROOM_W, .05, .13),
    center=(0, ROOM_D/2-.085, .065), color=WHITE))
room.include("right baseboard", box((.05, ROOM_D, .13),
    center=(ROOM_W/2-.085, 0, .065), color=WHITE))
for i in range(12):
    x = -ROOM_W/2 + (i+1)*ROOM_W/13
    room.include("floor board seam %02d" % i,
        box((.008, ROOM_D, .003), center=(x, 0, .002), color=FLOOR_SEAM))
scene.include("architecture", room)

windows = Asset("Large back wall windows")
wy = ROOM_D/2 - .085
window_xs = (-3.62, -2.55, -1.48, -.41, .66, 1.73)
for i, x in enumerate(window_xs):
    width, height, z = .96, 1.45, 2.00
    windows.include("window %d glazing" % i,
        box((width, .028, height), center=(x, wy-.02, z), color=GLASS))
    for side in (-1, 1):
        windows.include("window %d vertical frame %d" % (i, side),
            box((.055, .065, height+.11),
                center=(x+side*width/2, wy-.055, z), color=WHITE))
    for j, dz in enumerate((-height/2, height/2)):
        windows.include("window %d horizontal frame %d" % (i, j),
            box((width+.11, .065, .055),
                center=(x, wy-.055, z+dz), color=WHITE))
    windows.include("window %d sash" % i,
        box((width, .065, .035), center=(x, wy-.06, z-.15), color=WHITE))
windows.include("continuous windowsill", box((6.55, .20, .07),
    center=(-.945, wy-.11, 1.24), color=WHITE))
scene.include("windows", windows)

def cabinet(name, x, y, width, depth, height=.83, bays=3):
    a = Asset(name)
    t = .055
    # Cabinet openings face the camera, with a darker recessed back.
    a.include("recessed back", box((width, t, height),
        center=(x, y+depth/2-t/2, height/2), color=WOOD_DARK))
    for label, z in (("bottom", t/2), ("middle", height*.49), ("top", height-t/2)):
        a.include(label, box((width, depth, t), center=(x, y, z), color=WOOD_LIGHT))
    for j in range(bays+1):
        xx = x-width/2+j*width/bays
        a.include("upright %d" % j, box((t, depth, height),
            center=(xx, y, height/2), color=WOOD))
    scene.include(name, a)

# Broad foreground island, left wall run, and rear/right storage.
cabinet("Foreground island cabinet", .35, -1.20, 3.55, .82, .91, 3)
cabinet("Left low shelf", -3.15, 1.06, 2.05, .64, .83, 3)
cabinet("Back low shelf", -.30, 2.85, 2.55, .58, .76, 3)
cabinet("Right low shelf", 3.10, 1.90, 2.15, .58, .80, 3)

rug = Asset("Round rust red rug")
rug.include("outer red rug", rod(1.25, length=.018,
    center=(.35, -1.22, .012), color=RUG))
rug.include("inner muted field", rod(1.08, length=.019,
    center=(.35, -1.22, .022), color=(.58, .25, .14)))
scene.include("rug", rug)

def table(name, x, y, w, d):
    a = Asset(name)
    a.include("top", box((w, d, .065), center=(x, y, .59), color=WOOD_LIGHT))
    for i, dx in enumerate((-w/2+.09, w/2-.09)):
        for j, dy in enumerate((-d/2+.09, d/2-.09)):
            a.include("leg %d %d" % (i, j), box((.065, .065, .56),
                center=(x+dx, y+dy, .28), color=WOOD))
    scene.include(name, a)

def stool(name, x, y):
    a = Asset(name)
    a.include("seat", box((.34, .32, .045), center=(x, y, .34), color=WOOD_LIGHT))
    for i, dx in enumerate((-.12, .12)):
        for j, dy in enumerate((-.11, .11)):
            a.include("leg %d %d" % (i,j), box((.04,.04,.32),
                center=(x+dx,y+dy,.16), color=WOOD))
    scene.include(name, a)

table("Center activity table", -.75, 1.12, 1.45, .76)
stool("Left child stool", -1.58, .63)
stool("Right child stool", .13, .71)
stool("Back child stool", -.69, 1.78)

materials = Asset("Trays and Montessori materials")
def tray(name, x, y, z, width=.35, depth=.23):
    materials.include(name+" base", box((width,depth,.025),
        center=(x,y,z), color=WOOD_LIGHT))
    materials.include(name+" rear edge", box((width,.025,.045),
        center=(x,y+depth/2-.012,z+.028), color=WOOD))
    materials.include(name+" left edge", box((.025,depth,.045),
        center=(x-width/2+.012,y,z+.028), color=WOOD))
    materials.include(name+" right edge", box((.025,depth,.045),
        center=(x+width/2-.012,y,z+.028), color=WOOD))

for i, x in enumerate((-.95, -.40, .15, .70, 1.25)):
    tray("Island tray %d" % i, x, -1.20, .93)
    materials.include("Island block %d" % i, box((.10,.10,.09),
        center=(x,-1.20,1.00),
        color=((.77,.64,.42),(.55,.40,.23),(.82,.74,.52))[i%3]))
for i, x in enumerate((-3.72,-3.15,-2.58)):
    tray("Left tray %d" % i, x, 1.06, .85)
for i, x in enumerate((-1.12,-.30,.52)):
    tray("Back tray %d" % i, x, 2.85, .78)
for i, x in enumerate((2.42,3.10,3.78)):
    materials.include("Right wooden box %d" % i, box((.31,.23,.12),
        center=(x,1.90,.87), color=WOOD_LIGHT))
for i, x in enumerate((-.82,.35,1.52)):
    materials.include("Island cubby material %d" % i, box((.37,.25,.15),
        center=(x,-1.37,.14), color=(.42,.30,.18)))
scene.include("learning materials", materials)

extras = Asset("Additional classroom furnishings")
extras.include("wall board frame", box((1.05,.04,.54),
    center=(3.35,wy-.03,1.78), color=WOOD))
extras.include("wall board", box((.94,.025,.43),
    center=(3.35,wy-.06,1.78), color=(.82,.80,.70)))
extras.include("right work surface", box((1.25,.48,.055),
    center=(3.50,2.82,.72), color=WOOD_LIGHT))
for i,x in enumerate((2.97,4.03)):
    extras.include("work surface leg %d" % i, box((.06,.06,.69),
        center=(x,2.82,.345), color=WOOD))
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
background.inputs["Color"].default_value = (0.78, 0.82, 0.83, 1)
background.inputs["Strength"].default_value = .55

# Window-side key and soft ambient fill.
area_emitter((-1.4, 3.05, 2.55), power=1250, size=5.0,
             target=(0, -.5, .3), color=(1.0,.91,.78))
area_emitter((-2.0, -2.5, 4.8), power=550, size=6.0,
             target=(0, .7, .4), color=(1.0,.95,.86))

sc.render.engine = 'CYCLES'
sc.cycles.samples = 128
sc.cycles.use_denoising = True

# Diagnostic point projections. Reference estimates are inset coordinates.
landmarks = [
    ("window upper left", (-4.10,wy-.055,2.725), (.08,.04)),
    ("window upper right", (2.21,wy-.055,2.725), (.63,.04)),
    ("island top left", (-1.425,-1.61,.91), (.30,.49)),
    ("island top right", (2.125,-1.61,.91), (.83,.56)),
    ("rug front", (.35,-2.47,.022), (.57,.98)),
]

def projected_points():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    mat = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    result = []
    for name, point, ref in landmarks:
        clip = mat @ cam.matrix_world.inverted() @ Vector((*point,1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        result.append((name, ref, None if uv is None else tuple(round(v,3) for v in uv)))
    return result

print("Selected camera: landmark | reference estimate | computed projection")
for row in projected_points():
    print(row)

# A small upward trial should move stationary geometry down in the image.
cam = sc.camera
saved_rotation = cam.rotation_euler.copy()
trial_target = Vector(CAMERA_TARGET) + Vector((0,0,.12))
cam.rotation_euler = (trial_target - cam.location).to_track_quat('-Z','Y').to_euler()
print("Upward aim trial: landmark | reference estimate | computed projection")
for row in projected_points():
    print(row)
cam.rotation_euler = saved_rotation
bpy.context.view_layer.update()
