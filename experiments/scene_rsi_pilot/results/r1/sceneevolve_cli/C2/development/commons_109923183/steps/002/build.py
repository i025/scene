import bpy
import math
from sceneact import *

# Revision families: framing; head/wing/apron geometry; architecture/materials.
CAMERA = (.55, -5.7, 3.55)
TARGET = (0, .05, .94)
LENS = 60
WALL_OFFSET = .25
scene = Scene("French chaise room")

wall_color = (.69, .67, .60)
trim = (.77, .75, .68)
wood = (.29, .16, .10)
frame = (.20, .27, .22)
edge = (.62, .58, .43)
fabric = (.79, .74, .64)

def tube(asset, name, points, radius, color):
    asset.include(name, sweep_tube(points=points, radius=radius, color=color))

def beam(asset, name, a, b, radius, color):
    asset.include(name, rod(radius=radius, start=a, end=b, color=color))

# Architecture: preserve panel proportions, simplify the horizontal hierarchy.
room = Asset("paneled architecture")
room.include("back wall", box((8, .15, 3.6),
                             center=(0, 1.27, 1.8), color=wall_color))
for i, (z, h, depth) in enumerate([
    (.10, .16, .075), (.23, .045, .05),
    (1.12, .035, .035), (1.18, .065, .045),
    (1.64, .035, .03), (1.85, .045, .04),
    (2.26, .035, .03)
]):
    room.include("horizontal molding %d" % i,
                 box((8, depth, h), center=(0, 1.165, z), color=trim))

for i, (left, right) in enumerate([
    (-2.8, -1.6), (-1.50, 1.60), (1.77, 2.9)
]):
    bottom, top = .34, 1.04
    for j, y in enumerate((1.167, 1.148)):
        inset = j * .026
        for k, z in enumerate((bottom + inset, top - inset)):
            room.include("panel horizontal %d %d %d" % (i, j, k),
                         box((right-left-2*inset, .018, .018),
                             center=((left+right)/2, y, z), color=trim))
        for k, x in enumerate((left+inset, right-inset)):
            room.include("panel upright %d %d %d" % (i, j, k),
                         box((.018, .018, top-bottom-2*inset),
                             center=(x, y, (top+bottom)/2), color=trim))

room.include("right pier", box((.30, .42, 3.4),
                               center=(1.99, 1.10, 1.7),
                               color=(.75, .75, .69)))
for i, x in enumerate((1.88, 2.10)):
    room.include("pier trim %d" % i,
                 box((.022, .022, 2.8), center=(x, .876, 1.75), color=trim))
room.include("pier panel lower",
             box((.18, .023, .025), center=(1.99, .873, .39), color=trim))
for i, x in enumerate((-1.08, -.98)):
    fitting = ball(.022, center=(x, 1.075, 1.52), color=(.12, .11, .075))
    fitting.resize((.6, .7, 1.7))
    room.include("wall fitting %d" % i, fitting)
room.move((0, WALL_OFFSET, 0))
scene.include("architecture", room)

floor = Asset("parquet floor")
floor.include("floor slab", box((10, 9, .10),
                                center=(0, -1, -.065), color=wood))
scene.include("floor", floor)

curtains = Asset("left window and drapery")
curtains.include("bright window", box((.05, 1.3, 3.1),
                                     center=(-1.95, .20, 1.55),
                                     color=(.91, .92, .86)))
for i in range(9):
    x = -1.86 + .038 * math.sin(i * 1.35)
    y = -.52 + i * .105
    c = .69 + .055 * math.cos(i * 1.8)
    beam(curtains, "curtain fold %d" % i,
         (x, y, .035), (x-.06, y+.025, 2.95),
         .052, (c, c*.94, c*.83))
scene.include("curtains", curtains)

chaise = Asset("antique chaise longue")
chaise.include("seat cushion",
               fillet_box((2.33, .88, .23), radius=.11,
                          center=(.035, 0, .735), color=fabric))
chaise.include("seat foundation",
               fillet_box((2.40, .90, .105), radius=.045,
                          center=(0, 0, .594), color=frame))

for side in (-1, 1):
    y = side * .443
    tube(chaise, "rail edging %d" % side,
         [(-1.13,y,.62),(-.8,y,.595),(-.35,y,.58),
          (.18,y,.565),(.72,y,.555),(1.15,y,.565)], .018, edge)
    tube(chaise, "lower shaped apron %d" % side,
         [(-1.12,y,.55),(-.83,y,.48),(-.49,y,.48),
          (-.12,y,.43),(.13,y,.455),(.59,y,.47),(1.13,y,.49)],
         .036, frame)
    tube(chaise, "apron highlight %d" % side,
         [(-1.1,y-.009,.558),(-.78,y-.009,.50),(-.42,y-.009,.50),
          (-.12,y-.009,.455),(.17,y-.009,.48),(.65,y-.009,.49),
          (1.12,y-.009,.515)], .009, edge)

# A shallow solid apron fills the gap between existing shaped outlines.
# Short adjoining sections retain the large open space underneath.
apron_sections = [
    (-1.10, -.82, .49), (-.82, -.47, .49),
    (-.47, -.20, .47), (-.20, .04, .445),
    (.04, .35, .47), (.35, .72, .48), (.72, 1.10, .49)
]
for i, (a, b, bottom) in enumerate(apron_sections):
    top = .581 - .012 * ((a+b)/2 + 1.1)
    chaise.include("front solid apron %d" % i,
                   box((b-a+.006, .055, top-bottom),
                       center=((a+b)/2, -.438, (top+bottom)/2),
                       color=frame))

# Leg positions, seat placement and overall chaise rotation are unchanged.
for ix, x in enumerate((-1.00, 1.02)):
    for iy, y in enumerate((-.35, .34)):
        direction = -1 if x < 0 else 1
        tube(chaise, "cabriole leg %d %d" % (ix, iy),
             [(x,y,.59),(x+direction*.055,y,.46),
              (x+direction*.008,y,.29),(x-direction*.045,y,.10),
              (x+direction*.018,y,.055)], .037, frame)
        tube(chaise, "leg gilt edge %d %d" % (ix, iy),
             [(x,y-.031,.57),(x+direction*.035,y-.031,.43),
              (x-direction*.018,y-.031,.22),
              (x-direction*.025,y-.031,.095)], .009, edge)

head_outline = [
    (-1.16,-.40,.65),(-1.28,-.42,1.02),(-1.34,-.40,1.35),
    (-1.32,-.31,1.51),(-1.27,-.10,1.58),(-1.25,.16,1.57),
    (-1.18,.37,1.47),(-1.08,.43,1.20),(-1.00,.43,.76)
]
head = fillet_box((.15,.82,.88), radius=.072,
                  center=(-1.22,.015,1.10), color=(.65,.62,.53))
head.turn('y', -11)
chaise.include("padded head", head)
tube(chaise, "head outer carved frame", head_outline, .038, frame)
tube(chaise, "head pale inner beading",
     [(x+.014,y-.018,z-.016) for x,y,z in head_outline], .012, edge)

# Deeper front wing extends toward the head while retaining its seat-side end.
wing = fillet_box((.75,.10,.53), radius=.045,
                  center=(-1.065,-.415,.86), color=(.69,.65,.56))
wing.turn('y', 12)
chaise.include("front side upholstery", wing)
tube(chaise, "front sweeping arm",
     [(-1.32,-.415,1.36),(-1.21,-.46,1.21),(-1.06,-.47,1.13),
      (-.82,-.46,1.07),(-.70,-.44,1.045)], .034, frame)
tube(chaise, "front arm highlight",
     [(-1.32,-.448,1.38),(-1.20,-.49,1.23),(-1.05,-.50,1.15),
      (-.82,-.49,1.09),(-.70,-.47,1.065)], .009, edge)
tube(chaise, "front wing lower frame",
     [(-1.32,-.46,.86),(-1.26,-.47,.64),(-1.15,-.47,.57),
      (-.94,-.47,.56),(-.73,-.45,.62)], .030, frame)
tube(chaise, "far sloping arm",
     [(-1.22,.41,1.49),(-1.04,.44,1.26),(-.81,.44,1.15),
      (-.60,.43,1.13),(-.56,.42,.85)], .028, frame)
tube(chaise, "far arm highlight",
     [(-1.22,.397,1.51),(-1.04,.427,1.28),(-.81,.427,1.17),
      (-.60,.417,1.15)], .009, edge)

for i, (x,z,r) in enumerate([
    (-.15,.458,.045),(-.07,.446,.037),
    (.01,.457,.040),(-.22,.476,.027)
]):
    ornament = ball(r, center=(x,-.485,z), color=edge)
    ornament.resize((1,.35,.72))
    chaise.include("apron carving %d" % i, ornament)
for i in range(5):
    chaise.include("head crest %d" % i,
                   ball(.022,
                        center=(-1.31+.022*i,-.25+i*.07,
                                1.565+.025*math.sin(i)), color=edge))

pillow = fillet_box((.24,.74,.63), radius=.115,
                    center=(-.925,-.035,1.17), color=(.86,.81,.69))
pillow.turn('y', -24)
pillow.turn('x', -6)
pillow.turn('z', -45)
chaise.include("cream loose pillow", pillow)

label = box((.085,.155,.008), center=(.76,.12,.858),
            color=(.035,.20,.16))
label.turn('z', -5)
chaise.include("museum label", label)
for i in range(3):
    chaise.include("label marking %d" % i,
                   box((.035,.003,.002), center=(.76,.09+i*.013,.864),
                       color=(.63,.71,.59)))
chaise.turn('z', -11, pivot=(0,0,0))
scene.include("chaise", chaise)

chair = Asset("foreground cane chair")
chair.include("seat frame",
              fillet_box((.65,.64,.085), radius=.04,
                         center=(-1.48,-1.29,.43), color=frame))
chair.include("cane inset", box((.54,.53,.018),
                               center=(-1.48,-1.29,.482),
                               color=(.48,.35,.21)))
for i in range(18):
    x = -1.73 + i*.029
    beam(chair, "cane warp %d" % i,
         (x,-1.53,.496),(x,-1.05,.496), .0034, (.66,.52,.32))
for i in range(17):
    y = -1.52 + i*.029
    beam(chair, "cane weft %d" % i,
         (-1.73,y,.500),(-1.23,y,.500), .0034, (.66,.52,.32))
for i, x in enumerate((-1.75,-1.21)):
    beam(chair, "chair leg %d" % i,
         (x,-1.51,.05),(x,-1.51,.43), .028, frame)
chair.turn('z', 15, pivot=(-1.48,-1.29,0))
scene.include("foreground chair", chair)

realize(scene)

def material_nodes(mat):
    mat.use_nodes = True
    return (mat.node_tree.nodes, mat.node_tree.links,
            mat.node_tree.nodes.get("Principled BSDF"))

def fabric_finish(mat):
    nodes, links, bs = material_nodes(mat)
    bs.inputs["Roughness"].default_value = .88
    tex = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tex.outputs["Generated"], sep.inputs[0])
    mult = nodes.new("ShaderNodeMath")
    mult.operation = 'MULTIPLY'
    mult.inputs[1].default_value = 170
    links.new(sep.outputs["Y"], mult.inputs[0])
    sine = nodes.new("ShaderNodeMath")
    sine.operation = 'SINE'
    links.new(mult.outputs[0], sine.inputs[0])
    compare = nodes.new("ShaderNodeMath")
    compare.operation = 'GREATER_THAN'
    compare.inputs[1].default_value = .94
    links.new(sine.outputs[0], compare.inputs[0])
    mix = nodes.new("ShaderNodeMixRGB")
    mix.inputs[1].default_value = (.79,.74,.65,1)
    mix.inputs[2].default_value = (.52,.35,.31,1)
    links.new(compare.outputs[0], mix.inputs[0])
    links.new(mix.outputs[0], bs.inputs["Base Color"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 155
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .15
    bump.inputs["Distance"].default_value = .008
    links.new(tex.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs[0], bs.inputs["Normal"])

used = set()
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None or mat.name in used:
            continue
        used.add(mat.name)
        rgb = tuple(mat.diffuse_color[:3])
        nodes, links, bs = material_nodes(mat)
        if bs is None:
            continue
        bs.inputs["Roughness"].default_value = .76
        if sum(abs(rgb[i]-fabric[i]) for i in range(3)) < .035:
            fabric_finish(mat)
        elif sum(abs(rgb[i]-wood[i]) for i in range(3)) < .025:
            coord = nodes.new("ShaderNodeTexCoord")
            brick = nodes.new("ShaderNodeTexBrick")
            brick.inputs["Scale"].default_value = 3.4
            brick.inputs["Mortar Size"].default_value = .004
            brick.inputs["Mortar Smooth"].default_value = .002
            brick.inputs["Brick Width"].default_value = .85
            brick.inputs["Row Height"].default_value = .19
            brick.inputs["Color1"].default_value = (.12,.055,.03,1)
            brick.inputs["Color2"].default_value = (.22,.105,.055,1)
            brick.inputs["Mortar"].default_value = (.075,.035,.02,1)
            links.new(coord.outputs["Object"], brick.inputs["Vector"])
            links.new(brick.outputs["Color"], bs.inputs["Base Color"])
            bs.inputs["Roughness"].default_value = .40

set_view(CAMERA, TARGET, lens=LENS)
area_emitter((-3,-.7,3.0), power=650, size=3.0,
             target=(0,0,.6), color=(1,.93,.82))
area_emitter((1,-3,3.5), power=110, size=4,
             target=(0,0,.7), color=(.84,.89,1))
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("Room ambient")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.69,.73,.78,1)
world.node_tree.nodes["Background"].inputs[1].default_value = .28

# Source audit:
# Fillet radii: .11 <= .115; .045 <= .0525; .072 <= .075;
# wing .045 <= .05; pillow .115 <= .12; chair .04 <= .0425.
# All dimensions are positive; all rod endpoints and adjacent sweep points differ.
# Repeated include keys contain every loop index needed for uniqueness.
# Furniture transformations preserve meaningful multipart assemblies.
# realize precedes all Blender customization, camera creation and lighting.
# No external access, rendering, saving, or runner-setting changes.
