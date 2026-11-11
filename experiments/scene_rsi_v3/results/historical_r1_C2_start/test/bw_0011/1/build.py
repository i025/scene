# Reference inventory, approximate normalized bounds:
# - Blue back wall x .10-.70, y .22-.84; vertical panel joints.
# - Blue right return x .69-.91, y .13-.94; vertical joints and edge trim.
# - Pale gray floor below walls, with continuous rounded white wall coves.
# - Stainless double-door glazed cabinet x .16-.31, y .40-.83, shelves.
# - Dandelion photographic feature x .37-.64, y .24-.82, behind cabinet
#   and room fixtures; delicate seed heads and intersecting dark stems.
# - Clock display x .79-.88, y .33-.51 on the right wall.
# - Dark exposed ceiling and T-grid x 0-1, y 0-.24, white perimeter
#   panels, LED panel, overhead beams, hangers and services.
# - Numbered reference annotations are intentionally omitted.
# Hidden construction and the precise photographic details are uncertain.
#
# Render comparison: the previous view placed the corner and cabinet too far
# right, the mural was too narrow, the right wall extended off-frame, and
# the ceiling grid was visually too busy and bright. The camera and return
# length are adjusted; the cabinet and feature panel remain separate assets.
#
# Expanded mesh estimate: architecture 23, cabinet 26, mural background
# and stems 45 plus up to 150 seed filaments, display 5, ceiling 45.
# Total approximately 294 primitives. Text adds two Blender curve objects.

from sceneact import *
import bpy
import math
import random

random.seed(12)
scene = Scene("Clean laboratory corner")

blue = (0.025, 0.33, 0.55)
joint = (0.018, 0.18, 0.27)
white = (0.80, 0.84, 0.83)
steel = (0.50, 0.55, 0.54)
darksteel = (0.15, 0.19, 0.19)
glass = (0.12, 0.17, 0.17)
floor_color = (0.39, 0.43, 0.42)
dark_ceiling = (0.10, 0.13, 0.13)
grid_color = (0.32, 0.39, 0.39)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

room = Asset("Modular room architecture")
add(room, "self_leveling_floor", (8, 8, .12), (0, -1, -.08), floor_color)
add(room, "back_wall", (6.6, .12, 3.15), (0, 2, 1.575), blue)
# The free edge of the right wall is visible in the reference.
add(room, "right_wall", (.12, 3.55, 3.15), (3.3, .225, 1.575), blue)

for i, x in enumerate([-2.75, -1.70, -.65, .45, 1.55, 2.65]):
    add(room, "back_panel_joint_%02d" % i, (.012, .014, 3.05),
        (x, 1.93, 1.56), joint)
for i, y in enumerate([1.28, .38, -.52, -1.42]):
    add(room, "return_panel_joint_%02d" % i, (.014, .012, 3.05),
        (3.23, y, 1.56), joint)

add(room, "back_cove_base", (6.6, .17, .12), (0, 1.88, .07), white)
add(room, "right_cove_base", (.17, 3.55, .12), (3.18, .225, .07), white)
room.include("back_cove_curve",
    rod(radius=.06, start=(-3.3, 1.78, .095),
        end=(3.24, 1.78, .095), color=white))
room.include("right_cove_curve",
    rod(radius=.06, start=(3.08, 1.78, .095),
        end=(3.08, -1.55, .095), color=white))
add(room, "right_edge_trim", (.08, .08, 3.2), (3.27, -1.55, 1.60),
    (.40, .44, .43))
scene.include("architecture", room)

# The printed panel uses no external texture. The colored surface is given
# a soft vertical gradient after realization; drawn seed heads are geometry.
mural = Asset("Dandelion photographic feature")
x0, x1 = -.96, 1.12
add(mural, "printed_background", (x1-x0, .025, 2.96),
    ((x0+x1)/2, 1.905, 1.60), (.72, .84, .80))
for i, x in enumerate([-.28, .42]):
    add(mural, "print_panel_joint_%d" % i, (.008, .009, 2.96),
        (x, 1.88, 1.60), (.36, .48, .45))

ink = (.12, .035, .095)
fine = (.25, .23, .24)
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
    [(-.83,.13),(-.45,.24),(.02,.19),(.40,.32),(.78,.20)],
    [(-.90,1.15),(-.55,1.10),(-.22,.84),(.19,.69),(.66,.56)]
]
for j, points in enumerate(stems):
    for k in range(len(points)-1):
        line("stem_%d_%d" % (j,k), points[k], points[k+1],
             .014 if j < 4 else .007)

# Thin radiating filaments and cross-tips represent the airy print.
heads = [(-.08,2.55,.65), (.83,1.50,.50), (-.70,1.13,.48),
         (.55,1.50,.43), (.14,.61,.43), (.93,2.45,.53),
         (-.85,2.25,.46)]
for h, (cx, cz, radius) in enumerate(heads):
    for k in range(18):
        a = 2*math.pi*k/18 + .12*h
        ex = cx + radius*math.cos(a)
        ez = cz + radius*math.sin(a)
        sx = cx + .12*radius*math.cos(a)
        sz = cz + .12*radius*math.sin(a)
        if x0+.01 < ex < x1-.01 and .13 < ez < 3.07:
            line("seed_%d_%02d" % (h,k), (sx,sz), (ex,ez),
                 .0035, fine, 1.855)
            dx, dz = -.045*math.sin(a), .045*math.cos(a)
            if (x0 < ex-dx < x1 and x0 < ex+dx < x1 and
                    .12 < ez-dz < 3.08 and .12 < ez+dz < 3.08):
                line("seed_tip_%d_%02d" % (h,k), (ex-dx,ez-dz),
                     (ex+dx,ez+dz), .0025, fine, 1.85)
scene.include("feature_wall", mural)

cab = Asset("Stainless glass storage cabinet")
cx = -2.05
add(cab, "body", (1.08,.23,1.95), (cx,1.79,1.035), steel)
add(cab, "dark_recess", (.96,.025,1.76), (cx,1.65,1.05), darksteel)
for side, x in enumerate([cx-.265, cx+.265]):
    add(cab, "glazed_panel_%d" % side, (.39,.018,1.67),
        (x,1.62,1.05), glass)
    for j, z in enumerate([.27,.59,.91,1.23,1.55,1.87]):
        add(cab, "shelf_%d_%d" % (side,j), (.38,.022,.019),
            (x,1.595,z), (.58,.64,.63))
    for j, xx in enumerate([x-.235,x+.235]):
        add(cab, "door_stile_%d_%d" % (side,j), (.048,.045,1.84),
            (xx,1.585,1.05), steel)
    for j, z in enumerate([.14,1.96]):
        add(cab, "door_rail_%d_%d" % (side,j), (.49,.045,.055),
            (x,1.585,z), steel)
for i, x in enumerate([cx-.055,cx+.055]):
    cab.include("handle_%d" % i, rod(radius=.012,
        start=(x,1.55,.98), end=(x,1.55,1.17), color=(.75,.79,.78)))
scene.include("storage_cabinet", cab)

screen = Asset("Digital time and date display")
# Place the display closer to the free edge of the return so its position
# remains visible in the revised corner view.
screen_y = -.55
add(screen, "frame", (.055,.92,.70), (3.20,screen_y,2.13), darksteel)
add(screen, "face", (.014,.86,.64), (3.165,screen_y,2.13), (.012,.045,.13))
for i, z in enumerate([1.92,2.02,2.22]):
    add(screen, "rule_%d" % i, (.008,.71,.006), (3.15,screen_y,z),
        (.12,.24,.35))
scene.include("digital_display", screen)

ceiling = Asset("Suspended ceiling and exposed structure")
add(ceiling, "dark_upper_slab", (7,5.8,.12), (0,-.05,3.70), dark_ceiling)
for i, x in enumerate([-3,-1.8,-.6,.6,1.8,3]):
    add(ceiling, "overhead_beam_%d" % i, (.08,5.8,.10),
        (x,-.05,3.53), (.18,.21,.21))
for i, y in enumerate([-2.4,-1.2,0,1.2]):
    add(ceiling, "cross_beam_%d" % i, (6.8,.07,.10),
        (0,y,3.54), (.20,.23,.23))
for i, x in enumerate([-3,-2,-1,0,1,2,3]):
    add(ceiling, "long_T_grid_%d" % i, (.026,5.6,.04),
        (x,-.15,3.17), grid_color)
for i, y in enumerate([-2.8,-1.8,-.8,.2,1.2,1.9]):
    add(ceiling, "cross_T_grid_%d" % i, (6.6,.026,.04),
        (0,y,3.17), grid_color)
for i, x in enumerate([-2,0,2]):
    for j, y in enumerate([-1.8,.2,1.2]):
        ceiling.include("hanger_%d_%d" % (i,j),
            rod(radius=.009, start=(x,y,3.19), end=(x,y,3.57),
                color=darksteel))
for i, x in enumerate([-2.45,-.35,1.45]):
    ceiling.include("overhead_service_%d" % i,
        rod(radius=.018, start=(x,-2.8,3.42), end=(x,1.85,3.42),
            color=(.25,.30,.30)))
add(ceiling, "rear_white_soffit", (6.6,.50,.055),
    (0,1.70,3.13), (.75,.78,.76))
add(ceiling, "right_white_soffit", (.55,3.55,.055),
    (3.00,.225,3.13), (.75,.78,.76))
for i, (x,y) in enumerate([(.65,.70),(-1.6,-1.4),(1.7,-2.3)]):
    add(ceiling, "led_frame_%d" % i, (.96,.88,.045),
        (x,y,3.13), (.73,.79,.78))
    add(ceiling, "led_diffuser_%d" % i, (.87,.79,.025),
        (x,y,3.10), (.92,.98,1.0))
scene.include("ceiling", ceiling)

realize(scene)

# Differentiate stainless, dark glazing and matte room finishes.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        c = mat.diffuse_color
        if abs(c[0]-steel[0]) < .015 and abs(c[1]-steel[1]) < .015:
            bsdf.inputs["Metallic"].default_value = .72
            bsdf.inputs["Roughness"].default_value = .28
        elif abs(c[0]-glass[0]) < .01 and abs(c[1]-glass[1]) < .01:
            bsdf.inputs["Metallic"].default_value = .25
            bsdf.inputs["Roughness"].default_value = .18
        else:
            bsdf.inputs["Roughness"].default_value = .67

# Soft, generated color gradient for the printed photographic panel.
for mat in bpy.data.materials:
    c = mat.diffuse_color
    if abs(c[0]-.72) < .01 and abs(c[1]-.84) < .01 and abs(c[2]-.80) < .01:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        tex = nodes.new("ShaderNodeTexCoord")
        sep = nodes.new("ShaderNodeSeparateXYZ")
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .0
        ramp.color_ramp.elements[0].color = (.50,.31,.15,1)
        ramp.color_ramp.elements[1].position = 1.0
        ramp.color_ramp.elements[1].color = (.70,.85,.84,1)
        e = ramp.color_ramp.elements.new(.30)
        e.color = (.76,.73,.48,1)
        e = ramp.color_ramp.elements.new(.60)
        e.color = (.73,.84,.76,1)
        links.new(tex.outputs["Generated"], sep.inputs[0])
        links.new(sep.outputs["Z"], ramp.inputs[0])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        break

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

# A closer, almost level view, aimed toward the room corner.
set_view((-1.0,-7.0,2.18), (.55,1.5,1.67), lens=38, sensor=36)
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

screen_text("Time", "09:29:07", screen_y, 2.15, .13)
screen_text("Date", "2024 / 06 / 18", screen_y, 1.98, .055)
