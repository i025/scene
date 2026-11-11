# Reference inventory, approximate normalized image bounds:
# Back blue modular wall: x .10-.70, y .21-.84, with vertical joints.
# Right blue return wall: x .69-.91, y .13-.94, with vertical joints.
# Gray floor: lower image, with continuous white coved skirting.
# Stainless glazed double cabinet: x .16-.31, y .40-.83, with shelves.
# Dandelion feature: x .37-.64, y .24-.81, with pale background and
# dark crossing stems and fine radiating seed filaments.
# Right-wall clock: x .79-.88, y .33-.51.
# Exposed ceiling: upper .24 of image, with dark slab, beams, suspended
# grid, hangers, services and rectangular illuminated panels.
# The reference annotations are omitted. Unseen construction is uncertain.
#
# Feedback comparison: the previous room appeared too small, the viewpoint
# looked too steeply downward, the walls and cabinet were too washed out,
# and the ceiling lacked the broad white perimeter panels. The revised view
# is closer and more level; the cabinet, mural and display retain their
# separate editable parts. Mural photography remains an interpretation.
#
# Expanded primitive estimate: architecture 18, cabinet 30, mural 160,
# ceiling 50, display 6, lights 3: approximately 267 mesh primitives.

from sceneact import *
import bpy
import math
import random

random.seed(22)
scene = Scene("Clean laboratory corner")

blue = (0.025, 0.35, 0.58)
joint = (0.018, 0.19, 0.30)
white = (0.82, 0.86, 0.85)
steel = (0.48, 0.53, 0.53)
darksteel = (0.17, 0.21, 0.21)
glass = (0.12, 0.17, 0.17)
floor_color = (0.43, 0.47, 0.46)
dark_ceiling = (0.11, 0.14, 0.14)
grid_color = (0.45, 0.51, 0.51)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

room = Asset("Modular room")
add(room, "self_leveling_floor", (8, 8, .12), (0, -1, -.08), floor_color)
add(room, "back_wall", (6.6, .12, 3.15), (0, 2, 1.575), blue)
add(room, "right_wall", (.12, 5.5, 3.15), (3.3, -.70, 1.575), blue)

for i, x in enumerate([-2.75, -1.70, -.65, .45, 1.55, 2.65]):
    add(room, "back_joint_%02d" % i, (.012, .014, 3.05),
        (x, 1.93, 1.56), joint)
for i, y in enumerate([1.28, .38, -.52, -1.42, -2.32]):
    add(room, "return_joint_%02d" % i, (.014, .012, 3.05),
        (3.23, y, 1.56), joint)

add(room, "back_cove_base", (6.6, .17, .12), (0, 1.88, .07), white)
add(room, "right_cove_base", (.17, 5.5, .12), (3.18, -.70, .07), white)
room.include("back_cove_curve",
    rod(radius=.06, start=(-3.3, 1.78, .095),
        end=(3.24, 1.78, .095), color=white))
room.include("right_cove_curve",
    rod(radius=.06, start=(3.08, 1.78, .095),
        end=(3.08, -3.4, .095), color=white))
# Slim exposed trim at the free edge of the return.
add(room, "right_edge_trim", (.07, .07, 3.2), (3.27, -3.35, 1.6),
    (.45, .49, .48))
scene.include("architecture", room)

mural = Asset("Dandelion feature panels")
x0, x1 = -.96, 1.12
bands = [
    (.12, .40, (.58, .43, .24)),
    (.40, .70, (.76, .68, .42)),
    (.70, 1.05, (.80, .82, .61)),
    (1.05, 1.45, (.75, .84, .71)),
    (1.45, 1.90, (.68, .81, .77)),
    (1.90, 2.40, (.69, .83, .81)),
    (2.40, 3.08, (.72, .85, .84))
]
for i, (lo, hi, c) in enumerate(bands):
    add(mural, "background_%02d" % i, (x1-x0, .025, hi-lo),
        ((x0+x1)/2, 1.905, (lo+hi)/2), c)
for i, x in enumerate([-.28, .42]):
    add(mural, "panel_joint_%d" % i, (.008, .009, 2.96),
        (x, 1.88, 1.60), (.38, .52, .49))

ink = (.15, .065, .13)
fine = (.25, .24, .25)
def line(name, a, b, radius=.009, color=ink, depth=1.86):
    mural.include(name, rod(radius=radius,
        start=(a[0], depth, a[1]), end=(b[0], depth, b[1]), color=color))

stems = [
    [(-.95,.18),(-.68,.50),(-.42,.83),(-.18,1.20),(.02,1.85),(-.08,2.56)],
    [(-.92,.18),(-.55,.37),(-.18,.53),(.15,.60),(.55,.98),(.83,1.50)],
    [(1.08,.12),(.77,.43),(.49,.66),(.20,.80),(-.24,1.02),(-.72,1.12)],
    [(1.04,.18),(.69,.35),(.37,.63),(.23,1.06),(.54,1.51)],
    [(-.95,.42),(-.53,.48),(-.13,.40),(.21,.21),(.54,.13)],
    [(-.93,.75),(-.50,.66),(-.11,.76),(.30,1.25),(.42,1.67)],
    [(-.83,.13),(-.45,.24),(.02,.19),(.40,.32),(.78,.20)]
]
for j, points in enumerate(stems):
    for k in range(len(points)-1):
        line("stem_%d_%d" % (j,k), points[k], points[k+1],
             .012 if j < 4 else .006)

# Sparse, thin radial lines preserve the airy appearance of the printed seeds.
heads = [(-.08,2.55,.61), (.83,1.50,.49), (-.70,1.13,.43),
         (.55,1.50,.40), (.14,.61,.38), (.93,2.45,.48)]
for h, (cx, cz, radius) in enumerate(heads):
    for k in range(18):
        a = 2*math.pi*k/18 + .12*h
        ex, ez = cx + radius*math.cos(a), cz + radius*math.sin(a)
        sx, sz = cx + .14*radius*math.cos(a), cz + .14*radius*math.sin(a)
        if x0+.01 < ex < x1-.01 and .13 < ez < 3.07:
            line("seed_%d_%02d" % (h,k), (sx,sz), (ex,ez),
                 .0028, fine, 1.855)
            dx, dz = -.042*math.sin(a), .042*math.cos(a)
            if x0 < ex-dx < x1 and x0 < ex+dx < x1 and .12 < ez-dz < 3.08 and .12 < ez+dz < 3.08:
                line("seed_tip_%d_%02d" % (h,k), (ex-dx,ez-dz),
                     (ex+dx,ez+dz), .002, fine, 1.85)
scene.include("feature_wall", mural)

cab = Asset("Stainless double door cabinet")
cx = -2.05
add(cab, "body", (1.08,.23,1.95), (cx,1.79,1.035), steel)
add(cab, "recess", (.96,.025,1.76), (cx,1.65,1.05), darksteel)
for side, x in enumerate([cx-.265, cx+.265]):
    add(cab, "glazed_panel_%d" % side, (.39,.018,1.67),
        (x,1.62,1.05), glass)
    for j, z in enumerate([.27,.59,.91,1.23,1.55,1.87]):
        add(cab, "shelf_%d_%d" % (side,j), (.38,.022,.019),
            (x,1.595,z), (.58,.64,.63))
    for j, xx in enumerate([x-.235,x+.235]):
        add(cab, "stile_%d_%d" % (side,j), (.048,.045,1.84),
            (xx,1.585,1.05), steel)
    for j, z in enumerate([.14,1.96]):
        add(cab, "rail_%d_%d" % (side,j), (.49,.045,.055),
            (x,1.585,z), steel)
for i, x in enumerate([cx-.055,cx+.055]):
    cab.include("handle_%d" % i, rod(radius=.012,
        start=(x,1.55,.98), end=(x,1.55,1.17), color=(.75,.79,.78)))
scene.include("storage_cabinet", cab)

screen = Asset("Digital time display")
add(screen, "frame", (.055,.92,.70), (3.20,.15,2.13), darksteel)
add(screen, "face", (.014,.86,.64), (3.165,.15,2.13), (.012,.045,.13))
for i, z in enumerate([1.92,2.02,2.22]):
    add(screen, "rule_%d" % i, (.008,.71,.006), (3.15,.15,z),
        (.12,.24,.35))
scene.include("digital_display", screen)

ceiling = Asset("Suspended ceiling")
add(ceiling, "dark_upper_slab", (7,5.8,.12), (0,-.05,3.70), dark_ceiling)
for i, x in enumerate([-3,-1.8,-.6,.6,1.8,3]):
    add(ceiling, "overhead_beam_%d" % i, (.12,5.8,.16),
        (x,-.05,3.53), (.19,.22,.22))
for i, y in enumerate([-2.4,-1.2,0,1.2]):
    add(ceiling, "cross_beam_%d" % i, (6.8,.10,.12),
        (0,y,3.54), (.23,.26,.26))
for i, x in enumerate([-3,-2,-1,0,1,2,3]):
    add(ceiling, "long_T_grid_%d" % i, (.035,5.6,.055),
        (x,-.15,3.17), grid_color)
for i, y in enumerate([-2.8,-1.8,-.8,.2,1.2,1.9]):
    add(ceiling, "cross_T_grid_%d" % i, (6.6,.035,.055),
        (0,y,3.17), grid_color)
for i, x in enumerate([-2,0,2]):
    for j, y in enumerate([-1.8,.2,1.2]):
        ceiling.include("hanger_%d_%d" % (i,j),
            rod(radius=.012, start=(x,y,3.19), end=(x,y,3.57),
                color=darksteel))
for i, x in enumerate([-2.45,-.35,1.45]):
    ceiling.include("service_%d" % i,
        rod(radius=.025, start=(x,-2.8,3.42), end=(x,1.85,3.42),
            color=(.28,.32,.32)))
# White perimeter strip at the back and at the right edge of the grid.
add(ceiling, "rear_white_soffit", (6.6,.50,.055),
    (0,1.70,3.13), (.75,.78,.76))
add(ceiling, "right_white_soffit", (.55,5.0,.055),
    (3.00,-.80,3.13), (.75,.78,.76))
for i, (x,y) in enumerate([(.65,.70),(-1.6,-1.4),(1.7,-2.3)]):
    add(ceiling, "led_frame_%d" % i, (.96,.88,.045),
        (x,y,3.13), (.73,.79,.78))
    add(ceiling, "led_diffuser_%d" % i, (.87,.79,.025),
        (x,y,3.10), (.92,.98,1.0))
scene.include("ceiling", ceiling)

realize(scene)

for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        c = mat.diffuse_color
        if abs(c[0]-steel[0]) < .015 and abs(c[1]-steel[1]) < .015:
            bsdf.inputs["Metallic"].default_value = .72
            bsdf.inputs["Roughness"].default_value = .30
        else:
            bsdf.inputs["Roughness"].default_value = .65

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
background.inputs["Color"].default_value = (.72,.78,.80,1)
background.inputs["Strength"].default_value = .38

set_view((0,-8.8,2.25), (-.48,1.25,1.70), lens=40, sensor=36)
area_emitter((.65,.70,3.04), power=300, size=1.25,
             target=(0,.5,.2), color=(.90,.97,1))
area_emitter((-1.6,-1.4,3.04), power=220, size=1.3,
             target=(-1,1,1), color=(.94,.98,1))
area_emitter((1.7,-2.3,3.04), power=200, size=1.3,
             target=(2,1,1), color=(.94,.98,1))

def screen_text(name, text, y, z, size):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = (3.145,y,z)
    obj.rotation_euler = (math.pi/2,0,math.pi/2)
    mat = bpy.data.materials.get("Display lettering")
    if mat is None:
        mat = bpy.data.materials.new("Display lettering")
        mat.diffuse_color = (.60,.78,.90,1)
    obj.data.materials.append(mat)

screen_text("Time", "09:29:07", .15, 2.15, .13)
screen_text("Date", "2024 / 06 / 18", .15, 1.98, .055)
