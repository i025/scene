from sceneact import *
import bpy
import math

# Inventory: cream wall cabinet, paper roll with brackets, towel ring and towel,
# window and horizontal blinds, granite counter, cropped sink and faucet,
# canister, blender, blue filter pitcher, and labeled gallon jug.
# Near anchors: cropped sink and faucet. Middle: towel and jug.
# Far anchors: cabinet underside, window jambs, pitcher and rear wall.
# Jug occludes pitcher; towel occludes canister. Hidden geometry is hypothetical.
#
# Revision family: CAMERA.
# Visual observation: step 2 shows the outside of the window filling the left
# half, hiding towel, faucet and blender. The paper roll and jug remain visible.
# Hypothesis: the camera crossed the window plane, producing architectural
# occlusion; this is not evidence that those objects are missing.
# Move camera inside the window plane and closer to the counter, with a wider
# lens to retain cabinet, window and counter anchors in the portrait frame.
# Affected module: camera only. All assemblies, fittings, support heights,
# geometry and lighting remain as before. Risk: perspective enlargement near
# the foreground sink. Runtime fact: both previous builds executed successfully.
CAMERA = (-.82, -1.25, 1.80)
TARGET = (-.14, .28, 1.50)
LENS = 32
COUNTER_Z = .81
CAB_BOTTOM = 1.37
CREAM = (.79, .75, .63)
DOOR = (.86, .82, .70)
WHITE = (.91, .89, .81)
METAL = (.47, .47, .40)
scene = Scene("Kitchen corner")

def add(parent, key, node):
    return parent.include(key, node)

def ellipse(parent, key, center, radii, color, opacity=1):
    n = ball(1, center=center, color=color, opacity=opacity)
    n.resize(radii, pivot=center)
    return add(parent, key, n)

def tube(parent, key, points, radius, color):
    return add(parent, key, sweep_tube(points=points, radius=radius, color=color))

def loop_points(center, r1, r2, plane="xz", count=24):
    pts = []
    for i in range(count + 1):
        a = 2 * math.pi * i / count
        if plane == "xz":
            pts.append((center[0]+r1*math.cos(a), center[1],
                        center[2]+r2*math.sin(a)))
        else:
            pts.append((center[0], center[1]+r1*math.cos(a),
                        center[2]+r2*math.sin(a)))
    return pts

# Architecture stays outside movable semantic groups.
add(scene, "rear_wall", box((3.4,.10,3.0), center=(0,.76,1.5),
                           color=(.75,.70,.57)))
add(scene, "left_wall_upper", box((.09,1.6,.30),
    center=(-1.04,.05,2.56), color=CREAM))
add(scene, "window_sill", box((.22,1.52,.055),
    center=(-.96,.02,.91), color=(.86,.84,.74)))

window = Asset("Window and blinds")
add(window, "daylight_glass", box((.018,1.47,1.62),
    center=(-1.065,.01,1.75), color=(.62,.78,.82)))
for y in (-.73,.75):
    add(window, "jamb_%s" % y, box((.13,.055,1.72),
        center=(-1.005,y,1.76), color=WHITE))
for z in (.92,1.55,2.58):
    add(window, "cross_frame_%s" % z, box((.13,1.48,.045),
        center=(-1.005,.01,z), color=WHITE))
for i in range(31):
    slat = box((.115,1.44,.012), center=(-.936,.01,.96+i*.052),
               color=(.83,.85,.79))
    slat.turn("y", -9)
    add(window, "blind_slat_%02d" % i, slat)
for y in (-.42,.40):
    add(window, "blind_tape_%s" % y, box((.012,.016,1.60),
        center=(-.866,y,1.75), color=(.81,.79,.68)))
add(window, "pull_cord", rod(.0025, start=(-.86,-.53,1.89),
    end=(-.86,-.53,1.56), color=(.84,.80,.67)))
add(window, "cord_weight", rod(.009, length=.047,
    center=(-.86,-.53,1.55), color=(.85,.79,.65)))
add(scene, "window", window)

counter = Asset("Granite counter")
slab = box((2.36,1.65,.075), center=(.05,-.065,COUNTER_Z-.0375),
           color=(.34,.31,.25))
cut = box((.57,.49,.30), center=(-.67,-.47,COUNTER_Z), color=(0,0,0))
add(counter, "stone_slab", subtract(slab, cut))
add(counter, "rear_upstand", box((2.3,.045,.12),
    center=(.05,.685,COUNTER_Z+.06), color=(.34,.31,.25)))
add(counter, "window_upstand", box((.045,1.45,.10),
    center=(-1.0,-.03,COUNTER_Z+.05), color=(.34,.31,.25)))
add(scene, "counter", counter)

sink = Asset("Cropped stainless sink")
outer = fillet_box((.61,.53,.19), .045,
    center=(-.67,-.47,COUNTER_Z-.08), color=(.19,.21,.19))
inner = fillet_box((.55,.47,.21), .04,
    center=(-.67,-.47,COUNTER_Z-.025), color=(.08,.10,.09))
add(sink, "basin", subtract(outer, inner))
for x in (-.975,-.365):
    add(sink, "rim_side_%s" % x, box((.028,.55,.017),
        center=(x,-.47,COUNTER_Z+.006), color=METAL))
for y in (-.735,-.205):
    add(sink, "rim_end_%s" % y, box((.63,.028,.017),
        center=(-.67,y,COUNTER_Z+.006), color=METAL))
add(scene, "sink", sink)

faucet = Asset("Chrome faucet")
add(faucet, "mount", rod(.037, length=.027,
    center=(-.69,-.11,COUNTER_Z+.014), color=METAL))
tube(faucet, "neck", [(-.69,-.11,.83),(-.69,-.11,.99),
    (-.69,-.11,1.12),(-.69,-.135,1.15),(-.69,-.18,1.15),
    (-.69,-.23,1.11),(-.69,-.23,1.065)], .012, (.60,.61,.56))
add(faucet, "tap_base", rod(.026, length=.035,
    center=(-.54,-.13,.837), color=METAL))
add(faucet, "tap_lever", rod(.008, start=(-.54,-.13,.85),
    end=(-.50,-.12,.91), color=(.65,.65,.59)))
add(scene, "faucet", faucet)

cabinet = Asset("Cream upper cabinet")
add(cabinet, "carcass", box((1.00,.43,1.23),
    center=(.10,.49,CAB_BOTTOM+.615), color=CREAM))
add(cabinet, "door_panel", box((.93,.027,1.16),
    center=(.115,.259,2.005), color=DOOR))
for x in (-.33,.56):
    add(cabinet, "door_stile_%s" % x, box((.045,.024,1.17),
        center=(x,.238,2.005), color=(.83,.79,.67)))
for z in (1.435,2.57):
    add(cabinet, "door_rail_%s" % z, box((.92,.024,.045),
        center=(.115,.238,z), color=(.83,.79,.67)))
add(cabinet, "recessed_field", box((.77,.012,1.01),
    center=(.115,.239,2.005), color=(.85,.81,.69)))
add(cabinet, "knob_stem", rod(.012, start=(.535,.215,1.59),
    end=(.535,.182,1.59), color=(.39,.35,.23)))
ellipse(cabinet, "door_knob", (.535,.174,1.59),
        (.022,.017,.024), (.43,.38,.24))
add(scene, "cabinet", cabinet)

paper = Asset("Paper towel and vertical holder")
add(paper, "roll", rod(.142, length=.65,
    center=(.295,.073,1.94), color=(.94,.92,.83)))
add(paper, "bottom_core", rod(.025, length=.008,
    center=(.295,.073,1.611), color=(.41,.32,.20)))
add(paper, "spindle", rod(.014, start=(.295,.073,1.56),
    end=(.295,.073,2.325), color=METAL))
ellipse(paper, "top_finial", (.295,.073,2.315),
        (.031,.031,.045), (.42,.43,.37))
for z in (1.57,2.29):
    add(paper, "wall_bracket_%s" % z, rod(.014,
        start=(.295,.245,z), end=(.295,.073,z), color=METAL))
sheet = box((.245,.008,.60), center=(.30,-.067,1.935), color=WHITE)
sheet.turn("z", -3)
add(paper, "loose_sheet", sheet)
add(scene, "paper_holder", paper)

ring = Asset("Towel ring and wall fitting")
add(ring, "wall_rosette", rod(.045, length=.019,
    center=(-.415,.40,1.75), axis="+x", color=(.50,.49,.40)))
add(ring, "projecting_stem", rod(.014,
    start=(-.425,.40,1.75), end=(-.47,.33,1.75), color=METAL))
tube(ring, "ring", loop_points((-.473,.287,1.60),.119,.158,"yz"),
     .008, (.58,.59,.53))
add(scene, "towel_ring", ring)

towel = Asset("Ivory hanging hand towel")
add(towel, "rear_fold", fillet_box((.035,.235,.45), .016,
    center=(-.473,.335,1.165), color=(.82,.80,.72)))
for i in range(6):
    y = .137+i*.044
    bottom = .855+(.020 if i in (0,5) else 0)+.009*math.sin(i*1.8)
    top = 1.455-.018*abs(i-2.5)
    strip = fillet_box((.047,.059,top-bottom), .022,
        center=(-.501-.009*math.sin(i*1.5),y,(top+bottom)/2),
        color=(.89,.87,.79))
    strip.turn("x", -3+i*.7)
    add(towel, "hanging_fold_%02d" % i, strip)
add(scene, "hand_towel", towel)

canister = Asset("Partly hidden kitchen canister")
add(canister, "body", rod(.071, length=.24,
    center=(-.265,.43,COUNTER_Z+.12), color=(.37,.39,.22)))
add(canister, "lid", rod(.077, length=.023,
    center=(-.265,.43,1.061), color=(.48,.48,.33)))
add(canister, "rim", rod(.076, length=.008,
    center=(-.265,.43,1.045), color=METAL))
add(scene, "canister", canister)

blender = Asset("Compact blender")
add(blender, "motor_base", fillet_box((.18,.19,.205), .035,
    center=(-.035,.43,COUNTER_Z+.1025), color=(.035,.041,.034)))
add(blender, "top_collar", rod(.072, length=.045,
    center=(-.035,.43,1.027), color=(.09,.10,.083)))
add(blender, "clear_cup", rod(.054,
    start=(-.035,.43,1.045), end=(-.092,.43,1.37), color=(.65,.68,.62)))
add(blender, "cup_bottom", rod(.056, length=.018,
    center=(-.035,.43,1.053), color=(.28,.30,.26)))
tube(blender, "cup_lip", loop_points((-.092,.43,1.37),.054,.054,"xz"),
     .003, (.60,.62,.58))
add(scene, "blender", blender)

pitcher = Asset("Blue water filter pitcher")
ellipse(pitcher, "outer_body", (.575,.385,1.035),
        (.148,.119,.223), (.28,.36,.43), .68)
add(pitcher, "blue_reservoir", fillet_box((.205,.174,.265), .035,
    center=(.562,.395,1.091), color=(.025,.067,.145)))
ellipse(pitcher, "rounded_base", (.575,.385,.839),
        (.123,.097,.026), (.15,.20,.24))
lid = fillet_box((.315,.248,.041), .018,
    center=(.567,.378,1.264), color=(.43,.45,.42))
lid.turn("y", 12)
add(pitcher, "sloping_lid", lid)
add(pitcher, "pouring_spout", fillet_box((.085,.12,.038), .013,
    center=(.421,.37,1.291), color=(.44,.46,.43)))
tube(pitcher, "clear_handle", loop_points((.713,.39,1.055),.078,.151),
     .018, (.46,.50,.47))
add(scene, "water_pitcher", pitcher)

jug = Asset("Translucent gallon jug")
add(jug, "bottle_body", fillet_box((.263,.222,.265), .055,
    center=(.215,.025,COUNTER_Z+.137), color=(.76,.79,.73)))
ellipse(jug, "sloping_shoulders", (.215,.025,1.078),
        (.126,.106,.139), (.79,.81,.75))
add(jug, "neck", rod(.037, length=.06,
    center=(.215,.025,1.213), color=(.82,.83,.76)))
add(jug, "screw_cap", rod(.040, length=.025,
    center=(.215,.025,1.247), color=(.88,.87,.78)))
tube(jug, "molded_handle", loop_points((.295,.031,1.105),.043,.078),
     .013, (.78,.80,.73))
strokes = {
    "F":[[(0,0),(0,1)],[(0,1),(.6,1)],[(0,.55),(.48,.55)]],
    "I":[[(.3,0),(.3,1)]],
    "L":[[(0,1),(0,0),(.6,0)]],
    "T":[[(0,1),(.7,1)],[(.35,1),(.35,0)]],
    "E":[[(.6,1),(0,1),(0,0),(.6,0)],[(0,.5),(.5,.5)]],
    "R":[[(0,0),(0,1),(.5,1),(.6,.75),(.45,.53),(0,.53)],
         [(.3,.53),(.65,0)]]
}
for i, ch in enumerate("FILTER"):
    for j, path in enumerate(strokes[ch]):
        pts = [(.143+i*.021+u*.019,-.089,.912+v*.031) for u,v in path]
        tube(jug, "label_%d_%d" % (i,j), pts, .0009, (.31,.32,.29))
add(scene, "gallon_jug", jug)

# Source preflight: positive finite dimensions and radii; fillet bounds valid.
# Rod endpoints and consecutive sweep points differ; loops close once.
# Repeated parts have unique keys. All composite parts precede group placement.
# Camera changes leave every support, attachment and descendant unchanged.
realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.68,.72,.74,1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .45

def material(name, color, roughness=.5, metallic=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color,1)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic
    return m

stone = material("Granite warm salt and pepper",(.37,.34,.27),.73)
nt = stone.node_tree
p = nt.nodes.get("Principled BSDF")
tex = nt.nodes.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value = 155
tex.inputs["Detail"].default_value = 3
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .27
ramp.color_ramp.elements[0].color = (.065,.061,.048,1)
ramp.color_ramp.elements[1].position = .73
ramp.color_ramp.elements[1].color = (.61,.57,.45,1)
nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .23
bump.inputs["Distance"].default_value = .003
nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])

cloth = material("Ivory terry fabric",(.86,.835,.75),.95)
nt = cloth.node_tree
n = nt.nodes.new("ShaderNodeTexNoise")
n.inputs["Scale"].default_value = 230
n.inputs["Detail"].default_value = 2
b = nt.nodes.new("ShaderNodeBump")
b.inputs["Strength"].default_value = .35
b.inputs["Distance"].default_value = .002
nt.links.new(n.outputs["Fac"], b.inputs["Height"])
nt.links.new(b.outputs["Normal"], nt.nodes.get("Principled BSDF").inputs["Normal"])
chrome = material("Brushed nickel",(.53,.54,.48),.24,.82)
glass = material("Blender transparent plastic",(.60,.65,.61),.16)
pg = glass.node_tree.nodes.get("Principled BSDF")
pg.inputs["Transmission Weight"].default_value = .72
pg.inputs["IOR"].default_value = 1.46

# Preserve the preceding appearance pass and semantic selectors.
for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    name = obj.name.lower()
    chosen = None
    if any(k in name for k in ("stone_slab","rear_upstand","window_upstand")):
        chosen = stone
    elif any(k in name for k in ("hanging_fold","rear_fold")):
        chosen = cloth
    elif any(k in name for k in ("wall_rosette","projecting_stem","faucet",
                                 "top_finial","spindle","wall_bracket",
                                 "rim_side","rim_end")):
        chosen = chrome
    elif "clear_cup" in name:
        chosen = glass
    if chosen is not None:
        obj.data.materials.clear()
        obj.data.materials.append(chosen)

set_view(CAMERA, TARGET, lens=LENS, sensor=36)
area_emitter((-1.35,-.15,2.08), power=190, size=1.55,
             target=(.15,.25,1.12), color=(.83,.92,1.0))
area_emitter((-.1,-1.8,2.65), power=80, size=2.2,
             target=(.1,.3,1.35), color=(1.0,.85,.66))
sc.view_settings.view_transform = "AgX"
