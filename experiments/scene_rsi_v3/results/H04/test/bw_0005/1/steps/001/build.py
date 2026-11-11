from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory and visual anchors, estimated from the classroom inset:
# The inset occupies approximately x=.58-.93, y=.44-.96 in the supplied graphic.
# Within that inset: a light wood floor fills the lower half; a cream back wall
# and a row of large windows occupy the upper left and center. Low open shelves
# form a foreground island, a left-side run, and a shorter rear/right run.
# A small table and chairs stand between the shelves. A reddish round rug is
# partly occluded under the foreground cabinet. Small trays and blocks sit on
# cabinet tops. The right wall and far corners are partly obscured or cropped.
# Approximate normalized anchors within the classroom view, not the entire
# graphic: upper-left window (.12,.10), last window (.62,.09), front cabinet
# top left (.33,.57), front cabinet top right (.78,.54), rug front (.65,.96).
# Major horizontal shelf edges slope gently downward toward the right; floor
# depth lines converge toward the rear. The foreground cabinet overlaps the rug
# and table, while the table overlaps the back wall.
#
# Primitive estimate: room 15; windows 40; floor seams 15; cabinets ~60;
# table/stools ~24; materials ~35; rug 1; total approximately 190 meshes.
# Occluded backs and small individual teaching materials remain uncertain.

scene = Scene("Montessori classroom")

# Room and furniture dimensions, in meters.
ROOM_W, ROOM_D, ROOM_H = 8.8, 6.8, 3.15
WOOD = (0.63, 0.40, 0.21)
WOOD_LIGHT = (0.77, 0.57, 0.34)
WOOD_EDGE = (0.52, 0.31, 0.15)
CREAM = (0.86, 0.84, 0.77)
FLOOR = (0.72, 0.60, 0.46)
WHITE = (0.91, 0.90, 0.84)
DARK = (0.20, 0.18, 0.14)
CAMERA_POS = (10.8, -13.8, 8.3)
CAMERA_TARGET = (0.0, 0.4, 0.65)
CAMERA_LENS = 35

room = Asset("Architecture")
room.include("floor", box((ROOM_W, ROOM_D, .12), center=(0, 0, -.06), color=FLOOR))
room.include("back_wall", box((ROOM_W, .14, ROOM_H), center=(0, ROOM_D/2, ROOM_H/2), color=CREAM))
room.include("right_wall", box((.14, ROOM_D, ROOM_H), center=(ROOM_W/2, 0, ROOM_H/2), color=CREAM))
room.include("back_baseboard", box((ROOM_W, .05, .12), center=(0, ROOM_D/2-.10, .06), color=WHITE))
room.include("right_baseboard", box((.05, ROOM_D, .12), center=(ROOM_W/2-.10, 0, .06), color=WHITE))
# Restrained plank seams give a readable light timber floor.
for i in range(1, 15):
    x = -ROOM_W/2 + i * ROOM_W/15
    room.include("floor_seam_%02d" % i,
                 box((.012, ROOM_D, .003), center=(x, 0, .002),
                     color=(.60, .48, .36)))
scene.include("architecture", room)

# Window glazing is placed just inside the wall. Pale glass and thin mullions
# indicate the full row of daylight openings without depending on external maps.
windows = Asset("Back wall windows")
win_y = ROOM_D/2 - .085
for i, x in enumerate((-3.55, -2.35, -1.15, .05, 1.25, 2.45)):
    w, h, z = 1.02, 1.67, 2.04
    windows.include("glazing_%d" % i,
        box((w, .025, h), center=(x, win_y-.015, z), color=(.65, .80, .79)))
    for side in (-1, 1):
        windows.include("frame_%d_%d" % (i, side),
            box((.055, .06, h+.10), center=(x+side*w/2, win_y-.045, z), color=WHITE))
    for dz in (-h/2, h/2):
        windows.include("rail_%d_%s" % (i, dz),
            box((w+.10, .06, .055), center=(x, win_y-.045, z+dz), color=WHITE))
    windows.include("sash_%d" % i,
        box((w, .06, .035), center=(x, win_y-.047, z-.13), color=WHITE))
windows.include("continuous_sill",
    box((7.42, .20, .07), center=(-.55, win_y-.10, 1.16), color=WHITE))
scene.include("windows", windows)

def cabinet(name, cx, cy, width, depth, height=.86, bays=3, facing=-1):
    a = Asset(name)
    t = .065
    # Shelves are open toward the camera; a light back shows the cubby gaps.
    a.include("back", box((width, t, height), center=(cx, cy-facing*(depth/2-t/2), height/2), color=WOOD))
    for z, label in ((t/2, "bottom"), (height/2, "middle"), (height-t/2, "top")):
        a.include(label, box((width, depth, t), center=(cx, cy, z), color=WOOD_LIGHT))
    for j in range(bays+1):
        x = cx-width/2 + j*width/bays
        a.include("partition_%d" % j,
            box((t, depth, height), center=(x, cy, height/2), color=WOOD))
    scene.include(name, a)
    return a

# Foreground island, left shelf, and rear/right low storage define the circulation.
cabinet("Foreground open island", .55, -1.25, 3.35, .69, .88, 3)
cabinet("Left wall low shelf", -3.02, .48, 2.25, .65, .88, 3)
cabinet("Back low shelf", .10, 2.45, 2.55, .55, .76, 3)
cabinet("Right low shelf", 3.05, 1.10, 2.00, .60, .82, 2)

# Round, muted terracotta rug, partially covered by the foreground island.
rug = Asset("Round terracotta rug")
rug.include("rug_surface", rod(.99, length=.018, center=(.60, -1.30, .018), color=(.54, .20, .12)))
rug.include("rug_inner", rod(.86, length=.020, center=(.60, -1.30, .020), color=(.67, .30, .19)))
scene.include("rug", rug)

def table(name, cx, cy, width, depth):
    a = Asset(name)
    a.include("top", box((width, depth, .07), center=(cx, cy, .60), color=WOOD_LIGHT))
    for i, dx in enumerate((-width/2+.10, width/2-.10)):
        for j, dy in enumerate((-depth/2+.10, depth/2-.10)):
            a.include("leg_%d_%d" % (i,j),
                box((.07, .07, .56), center=(cx+dx, cy+dy, .28), color=WOOD))
    scene.include(name, a)

def stool(name, x, y):
    a = Asset(name)
    a.include("seat", box((.35, .32, .045), center=(x, y, .34), color=WOOD_LIGHT))
    for i, dx in enumerate((-.125, .125)):
        for j, dy in enumerate((-.11, .11)):
            a.include("leg_%d_%d" % (i,j),
                box((.042, .042, .32), center=(x+dx, y+dy, .16), color=WOOD))
    scene.include(name, a)

table("Child activity table", -.60, .75, 1.55, .82)
stool("Stool left", -1.40, .20)
stool("Stool right", .10, .16)
stool("Stool back", -.52, 1.45)

# Loose, deliberately sparse Montessori materials on tops and in a few cubbies.
materials = Asset("Montessori learning materials")
def tray(name, x, y, z, w=.38, d=.24):
    materials.include(name + "_base",
        box((w,d,.035), center=(x,y,z), color=(.71,.48,.26)))
    materials.include(name + "_back_rim",
        box((w,.025,.06), center=(x,y+d/2-.012,z+.035), color=WOOD_EDGE))
    materials.include(name + "_left_rim",
        box((.025,d,.06), center=(x-w/2+.012,y,z+.035), color=WOOD_EDGE))
    materials.include(name + "_right_rim",
        box((.025,d,.06), center=(x+w/2-.012,y,z+.035), color=WOOD_EDGE))

for i, x in enumerate((-.70, -.18, .34, .86, 1.38)):
    tray("island_tray_%d" % i, x, -1.25, .91, .37, .25)
    materials.include("block_%d" % i,
        box((.10,.10,.09), center=(x,-1.25,.98),
            color=((.71,.57,.37),(.78,.70,.49),(.48,.36,.22))[i%3]))
for i, x in enumerate((-3.65,-3.05,-2.48)):
    tray("left_tray_%d" % i, x, .48, .91)
for i, x in enumerate((-.72,.05,.80)):
    tray("back_tray_%d" % i, x, 2.45, .79)
for i, x in enumerate((2.45,3.05,3.65)):
    materials.include("right_box_%d" % i,
        box((.30,.22,.13), center=(x,1.10,.90), color=WOOD_LIGHT))
# Visible objects on the open shelves.
for i, x in enumerate((-.60,.45,1.55)):
    materials.include("cubby_box_%d" % i,
        box((.40,.30,.18), center=(x,-1.31,.17), color=(.48,.33,.21)))
for i, x in enumerate((-3.65,-2.95,-2.30)):
    materials.include("left_cubby_box_%d" % i,
        box((.38,.28,.16), center=(x,.40,.17), color=(.66,.48,.29)))
scene.include("learning materials", materials)

# A low side work surface and a wall-mounted board are visible secondary pieces.
extras = Asset("Secondary furnishings")
extras.include("wall_board", box((1.05,.035,.55), center=(3.52,3.29,1.62), color=(.72,.68,.55)))
extras.include("board_panel", box((.91,.025,.41), center=(3.52,3.265,1.62), color=(.87,.86,.78)))
extras.include("side_worktop", box((1.25,.48,.055), center=(3.55,2.30,.73), color=WOOD_LIGHT))
for i, x in enumerate((3.03,4.05)):
    extras.include("side_leg_%d" % i, box((.06,.06,.70), center=(x,2.30,.35), color=WOOD))
scene.include("secondary furnishings", extras)

realize(scene)

# Camera and lighting are configured after realization.
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
background.inputs["Color"].default_value = (0.80, 0.86, 1.0, 1)
background.inputs["Strength"].default_value = .55

area_emitter((0, 2.6, 3.0), power=950, size=5.0,
             target=(0, -.5, .2), color=(1.0, .91, .78))
area_emitter((1, -4, 5.8), power=850, size=7.0,
             target=(0, 0, .4), color=(1.0, .96, .88))
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True

# Reference estimates are approximate and refer to the inset's own bounds.
# The projections are diagnostic, not a claim of pixel calibration.
landmarks = [
    ("window upper left", (-4.06, win_y-.05, 2.875), (.12,.10)),
    ("window upper right", (2.96, win_y-.05, 2.875), (.62,.09)),
    ("island top left", (-1.125,-1.595,.88), (.33,.57)),
    ("island top right", (2.225,-1.595,.88), (.78,.54)),
    ("rug front", (.60,-2.29,.03), (.65,.96)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("Landmark | reference UV | projected UV")
for label, point, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(label, ref, None if uv is None else tuple(round(v,3) for v in uv))
