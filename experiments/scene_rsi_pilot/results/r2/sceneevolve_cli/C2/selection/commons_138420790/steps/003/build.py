from sceneact import *
import bpy

# Clearing the wall worked. Hood bottom ref (.57,.43), render (.54,.55): lens 52 and lower aim enlarge and raise the kitchen, preserving its assembly.
# Post bottom ref (.24,.99), render (.52,.94): move the post left across the view at similar depth, preserving foreground overlap.
# Cabinetry and ceiling render pale versus near-black reference: lower their reflectance while preserving the light floor and plaster hood.

scene = Scene("Industrial kitchen")
CAMERA = (-6.9, -4.5, 3.05)
TARGET = (-.16, .67, 1.63)
LENS = 52
ISLAND_W, ISLAND_D = 2.35, 1.12
COUNTER_Z, CEILING_Z = 1.02, 3.85
POST_X, POST_Y = -2.67, -.22

cabinet = (.023, .027, .025)
stone = (.58, .60, .58)
hood_color = (.76, .75, .69)
wood = (.37, .235, .125)
floor_color = (.68, .675, .63)

architecture = Asset("Room architecture")
architecture.include("floor", box((12,12,.12), (0,0,-.065), floor_color))
architecture.include("rear wall", box((8,.16,3.9), (0,2.35,1.95), (.36,.38,.35)))
architecture.include("left wall", box((.16,7,3.9), (-8,.2,1.95), (.37,.38,.35)))
architecture.include("ceiling", box((9,9,.14), (0,.4,CEILING_Z+.07), (.012,.016,.015)))
for i in range(13):
    architecture.include(
        "ceiling joist %02d" % i,
        box((.055,8,.11), (-4+i*.62,.3,3.77), (.012,.016,.015)))
for i,y in enumerate((-1.8,.55,2.6)):
    architecture.include(
        "main ceiling beam %d" % i,
        box((8,.22,.30), (0,y,3.64), (.018,.024,.022)))
architecture.include("right header", box((.25,4.2,.32), (2.85,.7,3.47), (.035,.045,.04)))
for i in range(-5,7):
    architecture.include(
        "floor x joint %d" % i,
        box((.009,11,.002), (i*.95,0,.0005), (.49,.49,.46)))
    architecture.include(
        "floor y joint %d" % i,
        box((11,.009,.002), (0,i*.95,.001), (.49,.49,.46)))
scene.include("architecture", architecture)

timbers = Asset("Exposed timber posts")
timbers.include("foreground post", box((.34,.35,4.25), (POST_X,POST_Y,2.125), wood))
timbers.include("far right post", box((.17,.20,3.55), (2.78,1.90,1.775), wood))
for z in (.16,1.4,2.7):
    timbers.include(
        "post peg %.2f" % z,
        rod(.012, start=(POST_X-.177,POST_Y-.08,z),
            end=(POST_X-.185,POST_Y-.08,z), color=(.15,.12,.075)))
scene.include("timbers", timbers)

island = Asset("Stone kitchen island")
island.include("body", box((ISLAND_W,ISLAND_D,.96), (0,0,.50), stone))
island.include(
    "countertop", box((ISLAND_W+.025,ISLAND_D+.025,.045),
                      (0,0,COUNTER_Z), (.70,.72,.69)))
island.include(
    "left end slab", box((.055,ISLAND_D+.015,1.025),
                         (-ISLAND_W/2-.015,0,.5125), stone))
island.include(
    "recessed toe", box((ISLAND_W-.10,.09,.095),
                        (0,-ISLAND_D/2+.025,.0475), (.20,.22,.21)))
for i in range(3):
    z = .235+i*.262
    island.include(
        "drawer %d" % i,
        box((ISLAND_W-.075,.025,.245),
            (.015,-ISLAND_D/2-.016,z), (.59,.61,.59)))
    island.include(
        "drawer upper groove %d" % i,
        box((ISLAND_W-.075,.014,.012),
            (.015,-ISLAND_D/2-.032,z+.124), (.29,.32,.30)))
scene.include("island", island)

sink = Asset("Inset sink and tap")
sx,sy = .38,.19
sink.include("sink rim", box((.61,.43,.010), (sx,sy,1.049), (.57,.61,.58)))
sink.include("sink shadow", box((.54,.36,.007), (sx,sy,1.055), (.29,.34,.32)))
sink.include("sink basin", box((.48,.30,.009), (sx,sy,1.060), (.54,.59,.56)))
sink.include("drain", rod(.026,length=.005,center=(sx+.13,sy,1.068),color=(.25,.28,.27)))
sink.include("tap base", rod(.032,length=.025,center=(sx,sy+.28,1.065),color=(.62,.67,.66)))
sink.include(
    "tap", sweep_tube(points=[
        (sx,sy+.28,1.07), (sx,sy+.28,1.30),
        (sx,sy+.23,1.35), (sx,sy+.08,1.35),
        (sx,sy+.04,1.30)], radius=.014, color=(.66,.71,.70)))
sink.include(
    "lever", rod(.009,start=(sx+.035,sy+.28,1.10),
                 end=(sx+.095,sy+.28,1.17),color=(.64,.69,.68)))
scene.include("sink", sink)

hood = Asset("Large suspended plaster hood")
hood.include("rectangular volume", box((1.13,.93,2.12), (-.05,.17,2.83), hood_color))
hood.include("lower edge", box((1.145,.945,.025), (-.05,.17,1.777), (.63,.64,.59)))
hood.include("underside inset", box((.76,.60,.008), (-.05,.17,1.761), (.16,.18,.16)))
hood.include("small control", box((.055,.009,.016), (-.35,-.305,1.80), (.39,.41,.36)))
scene.include("hood", hood)

rear = Asset("Black fitted kitchen")
rear.include("base units", box((4.30,.65,.91), (-.18,1.90,.455), cabinet))
rear.include("rear worktop", box((4.36,.69,.045), (-.18,1.88,.94), (.030,.035,.030)))
rear.include("backsplash", box((4.4,.035,.63), (-.16,2.005,1.285), (.022,.029,.024)))
for i in range(7):
    rear.include(
        "backsplash vertical seam %d" % i,
        box((.008,.008,.63), (-2.25+i*.65,1.982,1.285), (.012,.015,.013)))
for i in range(6):
    rear.include(
        "base door seam %d" % i,
        box((.008,.012,.83), (-2.1+i*.72,1.568,.48), (.009,.012,.010)))
rear.include("upper cabinets", box((3.32,.42,.53), (-.55,2.02,1.91), cabinet))
rear.include("under cabinet recess", box((3.25,.025,.035), (-.55,1.80,1.635), (.16,.13,.10)))
rear.include("lit backsplash panel", box((2.05,.020,.35), (-.82,1.976,1.19), (.25,.23,.20)))
rear.include("left tall cabinet", box((.88,.78,2.43), (-2.50,1.83,1.215), cabinet))
rear.include("left tall door", box((.82,.025,2.32), (-2.50,1.425,1.20), (.029,.033,.030)))
rear.include("left top seam", box((.82,.012,.008), (-2.50,1.405,2.12), (.012,.016,.014)))
rear.include("right tall cabinet", box((1.08,.78,2.52), (1.98,1.87,1.26), (.017,.023,.019)))
rear.include("right door", box((.49,.025,2.35), (2.25,1.465,1.24), (.022,.028,.024)))
rear.include("oven tower", box((.61,.80,2.38), (1.35,1.83,1.19), (.029,.035,.030)))
for i,z in enumerate((1.20,1.70)):
    rear.include(
        "oven steel surround %d" % i,
        box((.55,.035,.39), (1.35,1.410,z), (.27,.29,.28)))
    rear.include(
        "oven black glass %d" % i,
        box((.47,.012,.27), (1.35,1.386,z+.018), (.022,.035,.038)))
    rear.include(
        "oven handle %d" % i,
        rod(.012,start=(1.13,1.36,z-.11),end=(1.57,1.36,z-.11),color=(.48,.50,.48)))
scene.include("rear cabinetry", rear)

objects = Asset("Worktop objects")
objects.include(
    "red coffee machine",
    fillet_box((.19,.18,.22),.035,(-1.12,1.75,1.071),(.66,.008,.025)))
objects.include(
    "coffee machine black face",
    box((.125,.014,.14),(-1.12,1.650,1.07),(.018,.022,.020)))
objects.include(
    "coffee machine base",
    box((.20,.22,.025),(-1.12,1.72,.963),(.025,.028,.026)))
scene.include("small appliances", objects)

realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.30,.34,.36,1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .35

for material in bpy.data.materials:
    c = material.diffuse_color
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bs = nodes.get("Principled BSDF")
    if not bs:
        continue
    bs.inputs["Roughness"].default_value = .68
    if abs(c[0]-wood[0]) < .015 and abs(c[1]-wood[1]) < .015:
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 4
        tex.inputs["Detail"].default_value = 3
        coord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeVectorMath")
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (6,6,.25)
        links.new(coord.outputs["Generated"],mapping.inputs[0])
        links.new(mapping.outputs["Vector"],tex.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .20
        ramp.color_ramp.elements[0].color = (.19,.105,.045,1)
        ramp.color_ramp.elements[1].position = .82
        ramp.color_ramp.elements[1].color = (.52,.35,.19,1)
        links.new(tex.outputs["Fac"],ramp.inputs[0])
        links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .20
        bump.inputs["Distance"].default_value = .035
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    elif abs(c[0]-hood_color[0]) < .012:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 95
        noise.inputs["Detail"].default_value = 2
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .16
        bump.inputs["Distance"].default_value = .012
        links.new(noise.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bs.inputs["Normal"])

set_view(CAMERA,TARGET,lens=LENS,sensor=36)
area_emitter((-3.7,-3.6,3.35),power=1100,size=4.0,
             target=(0,.2,1.1),color=(1,.94,.83))
area_emitter((1.2,-.9,3.55),power=350,size=2.4,
             target=(0,0,.8),color=(.86,.91,1))
area_emitter((-.8,1.75,1.63),power=45,size=1.8,
             target=(-.8,1.95,1.12),color=(1,.75,.57))
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = .15
