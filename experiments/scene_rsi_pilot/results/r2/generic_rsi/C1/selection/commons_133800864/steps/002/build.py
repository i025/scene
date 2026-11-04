from sceneact import *
import bpy, math

# Largest mismatch in step 1: the camera viewed the exterior of the
# overextended left wall, hiding the entire kitchen.
# Correct the camera into the room and limit that wall to the window bay.
# Reference anchors: window ends near x=.29; cabinet lower edge y=.52;
# roll bounds (.61,.08)-(.84,.42); towel (.25,.48)-(.46,.83);
# jug (.59,.65)-(.79,.89); pitcher (.74,.60)-(.97,.85).
# Cabinet side recedes rightward; jug overlaps pitcher and blender.
scene = Scene("Kitchen corner")
CAMERA = (-.91, -2.35, 2.10)
TARGET = (-.03, .32, 1.63)
LENS = 55
C = {
    "wall": (.70,.65,.52), "cabinet": (.76,.71,.58),
    "trim": (.82,.77,.65), "paper": (.91,.88,.78),
    "chrome": (.48,.49,.45), "blue": (.035,.075,.16),
    "plastic": (.57,.59,.51), "granite": (.30,.29,.24),
    "cloth": (.84,.81,.71)
}

def add(parent, name, node):
    parent.include(name, node)
    return node

def oval(radius, center, scale, color):
    return resized(ball(radius, center=center, color=color), scale)

room = Asset("Architecture")
add(room, "rear plaster wall",
    box((4,.12,3.6), center=(.25,.94,1.8), color=C["wall"]))
# The previous 3.5 m wall projected in front of the camera.
add(room, "left window wall",
    box((.12,1.82,3.6), center=(-1.12,-.02,1.8), color=C["trim"]))
add(room, "counter slab",
    box((2.8,1.75,.065), center=(.15,.065,.8275), color=C["granite"]))
add(room, "rear granite upstand",
    box((2.8,.045,.12), center=(.15,.86,.91), color=C["granite"]))
add(room, "left granite upstand",
    box((.045,1.73,.13), center=(-1.045,.06,.915), color=C["granite"]))
scene.include("Architecture", room)

window = Asset("Window and blinds")
add(window, "daylit glass",
    box((.025,1.55,2.02), center=(-1.042,-.02,1.97), color=(.67,.80,.81)))
for i,y in enumerate((-.81,.77)):
    add(window, f"vertical frame {i}",
        box((.09,.075,2.20), center=(-.997,y,1.97), color=C["trim"]))
for i,z in enumerate((.91,2.00,3.04)):
    add(window, f"cross frame {i}",
        box((.10,1.65,.065), center=(-.99,-.02,z), color=C["trim"]))
for i in range(32):
    slat = box((.115,1.60,.018), center=(-.942,-.02,.96+i*.065),
               color=(.78,.79,.71))
    slat.turn("y",-12)
    add(window, f"blind slat {i}", slat)
for i,y in enumerate((-.54,.47)):
    add(window, f"blind tape {i}",
        box((.012,.023,2.08), center=(-.873,y,2), color=(.80,.79,.69)))
add(window, "sill",
    box((.23,1.77,.075), center=(-.98,-.02,.915), color=C["trim"]))
scene.include("Window", window)

cab = Asset("Upper cream cabinet")
add(cab, "case",
    box((1.16,.56,1.46), center=(.28,.55,2.21), color=C["cabinet"]))
add(cab, "bottom lip",
    box((1.20,.60,.045), center=(.28,.54,1.48), color=C["trim"]))
add(cab, "door",
    box((1.045,.035,1.38), center=(.29,.245,2.22), color=C["trim"]))
add(cab, "recessed panel",
    box((.83,.018,1.16), center=(.29,.219,2.22), color=C["cabinet"]))
for i,x in enumerate((-.16,.74)):
    add(cab, f"door stile {i}",
        box((.065,.025,1.29), center=(x,.200,2.22), color=C["trim"]))
for i,z in enumerate((1.59,2.85)):
    add(cab, f"door rail {i}",
        box((.94,.025,.055), center=(.29,.20,z), color=C["trim"]))
add(cab, "knob", ball(.025, center=(.746,.157,1.79), color=(.37,.33,.22)))
add(cab, "knob stem",
    rod(.012, start=(.746,.18,1.79), end=(.746,.14,1.79), color=C["chrome"]))
scene.include("Cabinet", cab)

paper = Asset("Wall mounted paper towel roll")
add(paper, "lower bracket",
    rod(.024, start=(.41,.19,1.76), end=(.41,.027,1.76), color=(.25,.25,.20)))
add(paper, "spindle",
    rod(.018, start=(.41,.020,1.75), end=(.41,.020,2.53), color=C["chrome"]))
add(paper, "paper cylinder",
    rod(.145, length=.67, center=(.41,.012,2.11), color=C["paper"]))
add(paper, "metal finial",
    oval(.033, (.41,.012,2.49), (.75,.75,1.45), C["chrome"]))
add(paper, "loose paper edge",
    box((.021,.10,.61), center=(.548,-.012,2.09), color=C["paper"]))
scene.include("Paper towels", paper)

towel = Asset("Towel ring and hanging towel")
add(towel, "wall plate",
    rod(.052, start=(-.302,.43,1.83), end=(-.33,.43,1.83), color=C["chrome"]))
add(towel, "mounting post",
    rod(.017, start=(-.33,.43,1.83), end=(-.40,.36,1.83), color=C["chrome"]))
points = [
    (-.409, .30+.112*math.cos(2*math.pi*i/16),
     1.665+.155*math.sin(2*math.pi*i/16))
    for i in range(17)
]
add(towel, "oval chrome ring", sweep_tube(points=points, radius=.008, color=C["chrome"]))
for i in range(7):
    bottom = 1.01+.045*math.sin(i*1.9)
    top = 1.58-.022*abs(i-3)
    add(towel, f"soft hanging fold {i}",
        fillet_box((.043,.046,top-bottom), radius=.018,
                   center=(-.444-.013*math.cos(i),.225+i*.025,(top+bottom)/2),
                   color=C["cloth"]))
add(towel, "fold over ring",
    oval(.10, (-.442,.30,1.57), (.35,1,.40), C["cloth"]))
add(towel, "rear cloth flap",
    box((.025,.19,.38), center=(-.385,.38,1.31), color=C["cloth"]))
scene.include("Hand towel", towel)

sink = Asset("Sink and faucet")
add(sink, "dark basin",
    box((.68,.55,.035), center=(-.63,-.48,.865), color=(.045,.055,.047)))
for i,x in enumerate((-.99,-.27)):
    add(sink, f"side rim {i}",
        box((.035,.61,.018), center=(x,-.48,.88), color=C["chrome"]))
for i,y in enumerate((-.78,-.18)):
    add(sink, f"cross rim {i}",
        box((.75,.025,.018), center=(-.63,y,.88), color=C["chrome"]))
add(sink, "faucet base",
    rod(.055, length=.025, center=(-.61,-.09,.889), color=C["chrome"]))
add(sink, "faucet upright",
    rod(.019, start=(-.61,-.09,.90), end=(-.61,-.09,1.15), color=C["chrome"]))
add(sink, "bent spout",
    sweep_tube(points=[(-.61,-.09,1.14),(-.61,-.09,1.29),
                       (-.61,-.14,1.32),(-.61,-.24,1.30),
                       (-.61,-.27,1.24)], radius=.014, color=C["chrome"]))
for i,x in enumerate((-.76,-.46)):
    add(sink, f"tap foot {i}",
        rod(.032, length=.035, center=(x,-.09,.90), color=C["chrome"]))
    add(sink, f"tap lever {i}",
        rod(.009, start=(x,-.09,.92), end=(x+.03,-.12,.98), color=C["chrome"]))
scene.include("Sink and faucet", sink)

jug = Asset("Filtered water gallon")
jx,jy = .40,-.31
add(jug, "rounded body",
    fillet_box((.29,.245,.34), radius=.065, center=(jx,jy,1.045), color=C["plastic"]))
add(jug, "shoulders",
    oval(.155, (jx,jy,1.205), (1,.80,.88), C["plastic"]))
add(jug, "neck",
    rod(.040, length=.065, center=(jx,jy,1.325), color=(.66,.67,.59)))
add(jug, "screw cap",
    rod(.042, length=.036, center=(jx,jy,1.367), color=(.83,.82,.71)))
add(jug, "handle",
    sweep_tube(points=[(jx-.10,jy+.012,1.28),(jx-.16,jy+.012,1.24),
                       (jx-.17,jy+.012,1.14),(jx-.11,jy+.012,1.12)],
               radius=.018, color=(.66,.67,.59)))
scene.include("Water gallon", jug)

pitcher = Asset("Blue water filter pitcher")
px,py = .78,.19
add(pitcher, "blue vessel",
    oval(.18, (px,py,1.065), (1,.76,1.50), C["blue"]))
add(pitcher, "flat base",
    rod(.135, length=.035, center=(px,py,.895), color=(.05,.09,.16)))
add(pitcher, "upper rim",
    rod(.172, length=.04, center=(px,py,1.30), color=(.20,.24,.24)))
add(pitcher, "lid",
    oval(.172, (px-.008,py-.003,1.327), (1,.78,.18), (.36,.37,.32)))
add(pitcher, "pouring lip",
    box((.075,.075,.045), center=(px-.15,py-.03,1.32), color=(.31,.33,.30)))
add(pitcher, "clear handle",
    sweep_tube(points=[(px+.15,py,1.27),(px+.24,py,1.23),
                       (px+.28,py,1.12),(px+.25,py,.98),
                       (px+.15,py,.95)], radius=.023, color=(.44,.48,.43)))
scene.include("Filter pitcher", pitcher)

blender = Asset("Blender")
add(blender, "black base",
    fillet_box((.18,.18,.15), radius=.025, center=(.10,.48,.955), color=(.025,.029,.024)))
add(blender, "collar",
    rod(.075, length=.08, center=(.10,.48,1.065), color=(.045,.045,.035)))
cup = rod(.062, length=.28, center=(.10,.48,1.235), color=(.29,.32,.28), opacity=.55)
cup.turn("x",9)
add(blender, "clear blending cup", cup)
add(blender, "cup rim",
    rod(.065, length=.012, center=(.10,.459,1.374), color=(.51,.53,.46)))
scene.include("Blender", blender)

can = Asset("Green canister")
add(can, "body",
    rod(.058, length=.25, center=(-.15,.49,.985), color=(.24,.27,.14)))
add(can, "lid",
    rod(.064, length=.022, center=(-.15,.49,1.122), color=(.44,.43,.27)))
scene.include("Canister", can)

accessories = Asset("Countertop accessories")
add(accessories, "small steel cup",
    rod(.042, length=.065, center=(-.30,-.04,.895), color=C["chrome"]))
add(accessories, "cup dark opening",
    rod(.033, length=.004, center=(-.30,-.04,.93), color=(.04,.043,.03)))
add(accessories, "soap dish",
    box((.16,.11,.018), center=(-.91,-.14,.88), color=(.52,.49,.33)))
add(accessories, "cream soap",
    fillet_box((.12,.075,.025), radius=.011, center=(-.91,-.14,.902), color=(.78,.74,.57)))
scene.include("Accessories", accessories)

print("Primitive count:", sum(n.solid is not None for n in scene.traverse()))
realize(scene)

# Match materials by their finish, since realized primitives have generic names.
def close_color(a,b):
    return max(abs(a[i]-b[i]) for i in range(3)) < .002

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bs = nodes.get("Principled BSDF")
    if bs is None:
        continue
    rgb = tuple(bs.inputs["Base Color"].default_value[:3])
    if close_color(rgb,C["chrome"]):
        bs.inputs["Metallic"].default_value = .72
        bs.inputs["Roughness"].default_value = .25
    elif close_color(rgb,C["blue"]):
        bs.inputs["Roughness"].default_value = .21
    elif close_color(rgb,C["plastic"]):
        bs.inputs["Roughness"].default_value = .32
        bs.inputs["Subsurface Weight"].default_value = .08
    elif close_color(rgb,(.67,.80,.81)):
        bs.inputs["Emission Color"].default_value = (.48,.66,.72,1)
        bs.inputs["Emission Strength"].default_value = .7
    if close_color(rgb,C["granite"]):
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 150
        tex.inputs["Detail"].default_value = 2.5
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .25
        ramp.color_ramp.elements[0].color = (.075,.075,.055,1)
        ramp.color_ramp.elements[1].position = .77
        ramp.color_ramp.elements[1].color = (.61,.56,.43,1)
        links.new(tex.outputs["Fac"],ramp.inputs[0])
        links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .23
        bump.inputs["Distance"].default_value = .012
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bs.inputs["Normal"])
        bs.inputs["Roughness"].default_value = .39
    elif close_color(rgb,C["cloth"]) or close_color(rgb,C["paper"]):
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 230
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .15
        bump.inputs["Distance"].default_value = .006
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bs.inputs["Normal"])
        bs.inputs["Roughness"].default_value = .9

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (.67,.69,.66,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = .35

set_view(position=CAMERA, target=TARGET, lens=LENS, sensor=36)
area_emitter(position=(-1.0,-.35,2.35), power=170, size=1.65,
             target=(.35,.35,1.35), color=(.82,.91,1))
area_emitter(position=(.4,-1.9,2.8), power=65, size=2,
             target=(.1,.35,1.4), color=(1,.84,.64))
sc.view_settings.view_transform = "AgX"
