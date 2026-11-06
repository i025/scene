from sceneact import *
import bpy
import math
import random

# Reference inventory, normalized bounds:
# Room: carpet (0,.59)-(1,1), rear cream wall (.12,.38)-(.53,.61),
# right cream wall (.53,0)-(1,.83), bright left partition (0,.33)-(.12,.67).
# Ceiling: rectangular acoustic tiles, fluorescent diffusers, detector,
# and missing tiles along the left edge exposing a dark plenum.
# Board: quadrilateral (.59,.40),(.90,.26),(.91,.58),(.59,.55);
# thin silver perimeter, central joining strip, bottom ledge.
# Flag: (.45,.32)-(.51,.43), dark canton, hanging striped cloth, angled pole.
# Rear fittings: vent (.15,.44)-(.25,.48), open cabinet, tilted cover, labels.
# Floor: overlapping dark broken panels (.02,.64)-(.43,.80), silver rails,
# overlapping yellow insulation (.56,.67)-(.90,.79), small scattered chips.
# Hidden room extent and exact debris fracture contours remain uncertain.
#
# Revision: combined camera, placement, local-profile, and material correction.
# Shared evidence: first render's rear wall reaches the left image boundary;
# reference rear wall begins at x~46. Its right-wall depth lines also converge
# much farther right. Reduce camera yaw and move backward, preserving room width.
# Board far edge already approximately matches, but its near edge is too short
# and shallow in projection. Extend its local length and move it forward along
# the wall; preserve its frame, seam, and tray hierarchy.
# Flag sits too far back and reads as horizontal bands. Move its support forward
# and make the visible stripes run down the hanging cloth.
# Fallen panels are too large and bright in the feedback. Adjust their depths
# with the camera and darken their materials; retain independent instances.
# Yellow pile is too flat: increase sheet depth and separate its tilted layers.
# Carpet procedural shading is assigned by geometry after realization because
# realized mesh names do not necessarily retain semantic SceneAct part names.
#
# Primitive estimate: 108 ceiling/grid/plenum pieces, 12 shell/partition pieces,
# 8 board parts, 22 rear fittings, 28 flag parts, 23 debris/rails, 15 chips,
# 5 light/detector pieces: approximately 225 meshes. No Boolean operations.

scene = Scene("Damaged classroom revised")

cream = (.69, .665, .59)
silver = (.48, .53, .54)
dark = (.045, .055, .050)

def add(parent, name, size, center, color):
    node = box(size=size, center=center, color=color)
    parent.include(name, node)
    return node

def place(asset, name, position, rotation=(0, 0, 0)):
    asset.turn(euler=rotation, pivot=(0, 0, 0))
    asset.move(position)
    scene.include(name, asset)
    return asset

# Architecture remains independent of camera parameters.
room = Asset("Room architecture")
add(room, "Carpet substrate", (5.5, 16, .12), (-.25, -4, -.06), (.075, .085, .069))
add(room, "Rear plaster", (5.6, .15, 3.9), (-.25, 4.075, 1.95), cream)
add(room, "Right plaster", (.15, 16, 3.9), (2.575, -4, 1.95), (.75, .716, .635))
add(room, "Left plaster", (.12, 16, 3.9), (-3.06, -4, 1.95), (.77, .78, .73))
add(room, "Rear baseboard", (5.5, .045, .13), (-.25, 3.985, .065), dark)
add(room, "Right baseboard", (.045, 16, .14), (2.485, -4, .07), dark)
scene.include("Room shell", room)

ceiling = Asset("Suspended ceiling")
add(ceiling, "Dark overhead plenum", (5.5, 16, .07),
    (-.25, -4, 4.09), (.065, .085, .085))
tile_w, tile_d = .61, 1.22
# Extended tiles cover the revised camera position.
for ix in range(9):
    for iy in range(13):
        x = -3 + (ix + .5) * tile_w
        y = -11.86 + (iy + .5) * tile_d
        missing = ix == 0 and iy in (8, 9, 10, 11)
        if not missing:
            c = (.62 + .01 * ((ix + iy) % 3),
                 .65 + .01 * ((ix + iy) % 3), .645)
            add(ceiling, "Acoustic tile %d %d" % (ix, iy),
                (tile_w - .012, tile_d - .012, .035), (x, y, 3.9), c)
for ix in range(10):
    add(ceiling, "Longitudinal grid %d" % ix, (.012, 15.86, .022),
        (-3 + ix * tile_w, -3.93, 3.875), (.49, .53, .52))
for iy in range(14):
    add(ceiling, "Cross grid %d" % iy, (5.49, .012, .022),
        (-.255, -11.86 + iy * tile_d, 3.875), (.49, .53, .52))
scene.include("Ceiling tiles and open bays", ceiling)

for i, y in enumerate((-5.15, -2.71, -.27)):
    light = Asset("Recessed fluorescent fixture")
    add(light, "Metal rim", (.59, 1.19, .026), (0, 0, 0), (.52, .57, .56))
    add(light, "Clouded diffuser", (.55, 1.14, .014), (0, 0, -.022), (.76, .81, .81))
    place(light, "Ceiling diffuser %d" % i, (-1.78, y, 3.865))

partition = Asset("Bright left partition")
for i in range(9):
    add(partition, "Pale panel %d" % i, (.035, 1.12, 3.87),
        (0, i * 1.13, 1.935), (.85, .875, .86))
    add(partition, "Panel joint %d" % i, (.043, .009, 3.87),
        (.004, i * 1.13 - .56, 1.935), (.70, .74, .73))
place(partition, "Left wall partition panels", (-2.985, -6, 0))

board = Asset("Whiteboard assembly")
board_length = 5.4
board_height = 1.90
add(board, "White enamel writing surface", (.034, board_length, board_height),
    (0, 0, 0), (.79, .81, .81))
for y in (-board_length / 2, board_length / 2):
    add(board, "End frame %.2f" % y, (.057, .034, board_height + .055),
        (-.018, y, 0), silver)
for z in (-board_height / 2, board_height / 2):
    add(board, "Long frame %.2f" % z, (.058, board_length + .034, .032),
        (-.018, 0, z), silver)
add(board, "Central board joining strip", (.041, .016, board_height),
    (-.025, .70, 0), (.67, .71, .71))
add(board, "Bottom marker ledge", (.09, board_length, .027),
    (-.055, 0, -board_height / 2 - .023), silver)
place(board, "Whiteboard mounted on right wall", (2.455, -2.55, 1.98))

fixtures = Asset("Rear wall service fittings")
add(fixtures, "Vent inset", (.98, .026, .40), (-2.05, 3.97, 2.15), (.25, .31, .33))
for i in range(7):
    add(fixtures, "Vent louver %d" % i, (.92, .023, .007),
        (-2.05, 3.949, 1.985 + i * .047), (.34, .39, .40))
add(fixtures, "Electrical cabinet outer frame", (.34, .07, .47),
    (-.72, 3.945, 1.85), (.43, .48, .46))
add(fixtures, "Open electrical cabinet recess", (.27, .017, .38),
    (-.72, 3.898, 1.85), (.10, .14, .13))
add(fixtures, "Visible internal equipment", (.12, .023, .25),
    (-.72, 3.879, 1.86), (.58, .61, .56))
fixtures.include("Exposed cable", rod(radius=.012,
    start=(-.80, 3.85, 1.98), end=(-.77, 3.85, 1.75), color=(.10, .13, .12)))
cover = Asset("Displaced cabinet cover")
add(cover, "Gray sheet-metal door", (.52, .035, .43), (0, 0, 0), (.35, .42, .41))
add(cover, "Small cover fastener", (.024, .013, .024), (.15, -.025, -.08), (.16, .20, .19))
cover.turn("y", 38, pivot=(0, 0, 0))
cover.move((-.46, 3.84, 1.48))
fixtures.include("Hanging cabinet door", cover)
for i in range(2):
    add(fixtures, "Paper label %d" % i, (.15, .014, .21),
        (.04 + i * .24, 3.973, 1.51 + i * .04), (.79, .78, .69))
    add(fixtures, "Label text indication %d" % i, (.083, .008, .025),
        (.04 + i * .24, 3.961, 1.54 + i * .04), (.30, .34, .31))
scene.include("Back wall fittings", fixtures)

# Hanging flag: local width and length independent of its wall placement.
flag = Asset("American flag and angled support")
flag.include("Angled flagpole", rod(radius=.011,
    start=(0, 0, 0), end=(-1.22, -.12, .52), color=(.21, .23, .21)))
flag_width, flag_drop = .43, 1.04
for i in range(13):
    x = -1.16 + (i + .5) * flag_width / 13
    stripe_length = flag_drop * (1 - .07 * i / 12)
    add(flag, "Hanging cloth stripe %02d" % i,
        (flag_width / 13 + .001, .013, stripe_length),
        (x, -.14 + .028 * math.sin(i * .65), .48 - stripe_length / 2),
        (.60, .045, .037) if i % 2 == 0 else (.82, .80, .71))
add(flag, "Blue canton", (.205, .018, .42),
    (-1.055, -.175, .27), (.075, .12, .19))
for row in range(4):
    for col in range(3):
        add(flag, "Star indication %d %d" % (row, col), (.012, .004, .012),
            (-1.127 + col * .056, -.187, .115 + row * .083), (.79, .80, .73))
place(flag, "Flag near ceiling corner", (2.45, .05, 3.20))

# Fallen panels preserve separate mesh parts and editable poses.
def fallen_panel(name, dimensions, position, angle, color, tilt=(0, 0)):
    asset = Asset(name)
    add(asset, "Acoustic panel fragment", dimensions,
        (0, 0, dimensions[2] / 2), color)
    add(asset, "Torn pale edge", (dimensions[0], .014, .009),
        (0, -dimensions[1] / 2, dimensions[2] * .65), (.37, .38, .31))
    return place(asset, name, position, (tilt[0], tilt[1], angle))

fallen_panel("Rear fallen panel", (.85, .48, .023), (-.85, -2.0, .014),
             -12, (.17, .19, .16))
fallen_panel("Rear small overlap", (.50, .26, .022), (-1.02, -1.86, .038),
             9, (.28, .29, .23))
fallen_panel("Middle left broken panel", (.95, .46, .024), (-1.30, -3.80, .014),
             -17, (.24, .26, .21))
fallen_panel("Middle overlapping fragment", (.56, .29, .023), (-1.08, -3.63, .042),
             12, (.14, .17, .14))
fallen_panel("Foreground broad broken panel", (1.17, .56, .030), (-.38, -5.40, .012),
             14, (.19, .21, .17))
fallen_panel("Foreground upper fragment", (.86, .43, .024), (-.20, -5.20, .046),
             -17, (.27, .28, .22), (2, -3))
fallen_panel("Foreground narrow fragment", (.73, .19, .022), (-.06, -5.43, .073),
             29, (.13, .16, .13))

insulation = Asset("Overlapping yellow insulation")
add(insulation, "Lower ochre sheet", (1.25, 1.28, .044),
    (-.12, .10, .04), (.56, .42, .12))
upper = add(insulation, "Raised yellow sheet", (1.26, 1.38, .055),
    (.16, -.19, .14), (.66, .51, .17))
upper.turn("x", -12, pivot=(.16, -.19, .14))
add(insulation, "Broken left tongue", (.20, 1.08, .045),
    (-.64, .02, .065), (.63, .49, .16))
place(insulation, "Yellow insulation on carpet", (1.76, -4.68, .012), (0, 0, -9))

rail_specs = [
    ((-.98, -4.37, .025), (.17, -4.61, .025)),
    ((-1.12, -4.28, .026), (-.53, -4.48, .026)),
    ((1.62, -5.21, .024), (2.48, -6.76, .028)),
    ((1.85, -5.33, .026), (2.50, -7.02, .029)),
    ((2.20, -5.48, .028), (2.50, -6.11, .030)),
]
for i, (p, q) in enumerate(rail_specs):
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy)
    rail = Asset("Detached ceiling T rail")
    add(rail, "Silver horizontal flange", (length, .034, .012),
        (0, 0, .006), (.58, .62, .62))
    add(rail, "Thin upright web", (length, .008, .023),
        (0, 0, .018), (.33, .39, .39))
    place(rail, "Loose floor rail %d" % i,
          ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, (p[2] + q[2]) / 2),
          (0, 0, math.degrees(math.atan2(dy, dx))))

random.seed(12)
chips = Asset("Small scattered floor chips")
for i in range(15):
    add(chips, "Chip %d" % i,
        (random.uniform(.025, .065), random.uniform(.025, .08), .006),
        (random.uniform(-2.4, 2.2), random.uniform(-6.2, 2.7), .007),
        (.36, .35, .27))
scene.include("Scattered small debris", chips)

detector = Asset("Ceiling smoke detector")
housing = ball(radius=.09, center=(0, 0, 0), color=(.73, .74, .68))
housing.resize((1, 1, .38), pivot=(0, 0, 0))
detector.include("Flattened round housing", housing)
place(detector, "Smoke detector", (-1.54, -6.35, 3.84))

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
background.inputs["Color"].default_value = (.69, .74, .78, 1)
background.inputs["Strength"].default_value = .24

# Dedicated carpet material: subtle dense flecking, dark overall value.
carpet = bpy.data.materials.new("Dark mottled woven carpet")
carpet.use_nodes = True
nt = carpet.node_tree
bs = nt.nodes.get("Principled BSDF")
bs.inputs["Roughness"].default_value = .96
tex = nt.nodes.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value = 220
tex.inputs["Detail"].default_value = 2
coord = nt.nodes.new("ShaderNodeTexCoord")
mapping = nt.nodes.new("ShaderNodeVectorMath")
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (1, .38, 1)
nt.links.new(coord.outputs["Generated"], mapping.inputs[0])
nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .18
ramp.color_ramp.elements[0].color = (.025, .033, .028, 1)
ramp.color_ramp.elements[1].position = .83
ramp.color_ramp.elements[1].color = (.105, .113, .086, 1)
nt.links.new(tex.outputs["Fac"], ramp.inputs[0])
nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .15
bump.inputs["Distance"].default_value = .008
nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])

for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        if mat:
            mat.use_nodes = True
            shader = mat.node_tree.nodes.get("Principled BSDF")
            if shader:
                shader.inputs["Roughness"].default_value = .86
    if obj.dimensions.x > 5 and obj.dimensions.y > 15 and obj.location.z < .1:
        obj.data.materials.clear()
        obj.data.materials.append(carpet)

# Camera family: reduced yaw and greater distance, based on multiple room anchors.
camera_position = (.10, -9.30, 1.36)
camera_target = (2.15, 4.0, 1.68)
set_view(position=camera_position, target=camera_target, lens=26.5, sensor=36)

area_emitter(position=(-2.65, -4.2, 2.5), power=430, size=5.0,
             target=(.6, -.8, 1.2), color=(.86, .93, 1.0))
area_emitter(position=(-1.3, 1.1, 3.72), power=95, size=2.2,
             target=(0, 0, .5), color=(.96, .94, .85))

sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'
sc.view_settings.exposure = 0
sc.view_settings.gamma = 1
