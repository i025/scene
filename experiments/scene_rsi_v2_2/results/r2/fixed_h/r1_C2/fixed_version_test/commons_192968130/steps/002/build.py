from sceneact import *
import bpy
import math

# Reference inventory (estimated normalized image bounds):
# Slatted walnut wall: (0,.11)-(.47,.76); dark narrow gaps, tall battens.
# White door: (.31,.29)-(.45,.77); casing, subtle panel, silver lever/keyhole.
# Bench: (0,.65)-(.21,.81); dark top/frame and broad white inset front.
# Tiled floor: (0,.76)-(.39,1); pale gray-beige rectangular tiles.
# Kitchen countertop: (.37,.59)-(1,1); thin cream stone with fine dark veins.
# Sink: (.46,.64)-(.62,.71); black recessed bowl and narrow draining ledge.
# Hob: (.40,.77)-(.81,1); glossy black glass, four faint circular burners.
# Backsplash: (.58,.29)-(1,1); glossy ivory, subtle panel joins/reflections.
# Walnut upper cabinets: (.46,0)-(1,.43); broad dark panels, underside trim,
# stainless extractor, warm linear light. Tall rear wood end beside door.
# Cabinet interiors and cropped lower fronts are uncertain and kept simple.
#
# Review of first render:
# Door and wall were too small, too far right; excessive ceiling and floor.
# Counter approached from too far to the side; hob and sink were too distant.
# Slat wall was too short vertically; timber and lighting were too pale.
# Correct camera proximity/lateral position, slat height, local appliance
# positions and upper-cabinet underside height while preserving hierarchy.
#
# Expanded primitive estimate: approximately 285 meshes:
# 54 battens, 42 tile joints, 112 burner segments, approximately 75 other
# architecture/furniture/fitting parts; one counter Boolean and one cutter.
# No fillet_box expansion or dense decorative geometry.

scene = Scene("Walnut kitchen revised")

WHITE = (.83, .83, .79)
WALL = (.76, .75, .69)
WOOD = (.115, .043, .015)
SLAT = (.255, .105, .034)
STONE = (.74, .71, .63)
FLOOR = (.56, .54, .49)
BLACK = (.009, .011, .010)
METAL = (.43, .45, .42)
GROUT = (.38, .365, .33)
RING = (.065, .062, .046)
LED = (1.0, .79, .40)
BACKSPLASH = (.82, .815, .765)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Room architecture")
add(architecture, "Floor slab", (8, 11, .10), (-.5, .5, -.06), FLOOR)
add(architecture, "Rear plaster wall", (6.2, .13, 3.55),
    (-1.35, 3.75, 1.755), WALL)
add(architecture, "Right plaster wall", (.14, 9, 3.55),
    (1.31, -.2, 1.755), WALL)
add(architecture, "Ceiling", (6.2, 9, .10),
    (-1.4, -.2, 3.39), WHITE)
scene.include("Architecture", architecture)

floor = Asset("Large pale floor tiles")
for i in range(14):
    y = -4.0 + i * .59
    add(floor, "Horizontal joint %02d" % i, (6.1, .006, .002),
        (-1.4, y, -.007), GROUT)
    for j in range(2):
        x = -2.9 + j * 1.75 + (i % 2) * .70
        add(floor, "Staggered joint %02d %d" % (i, j),
            (.005, .59, .002), (x, y + .295, -.006), GROUT)
scene.include("Tile joints", floor)

wall = Asset("Walnut slatted feature wall")
add(wall, "Dark recess backing", (4.58, .06, 2.88),
    (-1.14, 3.64, 1.46), (.035, .018, .009))
for i in range(54):
    x = -3.40 + i * .085
    add(wall, "Vertical timber batten %02d" % i,
        (.060, .050, 2.88), (x, 3.58, 1.46), SLAT)
scene.include("Slatted wall", wall)

door = Asset("White interior door")
door_x = -.14
add(door, "Door slab", (.86, .055, 2.05),
    (door_x, 3.525, 1.025), WHITE)
add(door, "Left casing", (.055, .075, 2.12),
    (door_x - .465, 3.50, 1.06), WHITE)
add(door, "Right casing", (.055, .075, 2.12),
    (door_x + .465, 3.50, 1.06), WHITE)
add(door, "Top casing", (.985, .075, .065),
    (door_x, 3.50, 2.09), WHITE)
add(door, "Subtle inset panel", (.745, .008, 1.90),
    (door_x, 3.493, 1.025), (.805, .807, .778))
door.include("Handle escutcheon",
    rod(radius=.022, start=(door_x-.31, 3.475, 1.02),
        end=(door_x-.31, 3.450, 1.02), color=METAL))
door.include("Silver lever",
    rod(radius=.010, start=(door_x-.31, 3.437, 1.025),
        end=(door_x-.20, 3.437, 1.025), color=METAL))
door.include("Keyhole",
    rod(radius=.008, start=(door_x-.31, 3.475, .94),
        end=(door_x-.31, 3.456, .94), color=METAL))
add(door, "Light switch", (.085, .018, .085),
    (door_x-.65, 3.535, 1.05), WHITE)
add(door, "Low wall outlet", (.07, .018, .08),
    (door_x-.64, 3.535, .25), WHITE)
scene.include("Door and fittings", door)

bench = Asset("Low black and white bench")
add(bench, "Black cabinet body", (1.54, .43, .43),
    (-2.06, 3.27, .215), BLACK)
add(bench, "White inset front", (1.40, .018, .29),
    (-2.06, 3.043, .205), WHITE)
add(bench, "Dark timber top", (1.58, .46, .045),
    (-2.06, 3.26, .45), WOOD)
add(bench, "Front upper rail", (1.53, .025, .045),
    (-2.06, 3.026, .39), BLACK)
scene.include("Bench", bench)

# All kitchen parts retain a shared editable parent and lateral adjustment.
kitchen = Asset("Right wall kitchen")
cx = 1.075
counter_width = .84
counter_back = 3.50
counter_front = -3.2
counter_len = counter_back - counter_front
counter_y = (counter_back + counter_front) / 2
add(kitchen, "Base cabinet volume", (.81, counter_len, .84),
    (1.095, counter_y, .43), WOOD)
add(kitchen, "Recessed plinth", (.70, counter_len, .10),
    (1.15, counter_y, .05), BLACK)
for i in range(7):
    y = counter_front + .46 + .94 * i
    add(kitchen, "Lower walnut front %d" % i, (.025, .925, .76),
        (.675, y, .47), WOOD)

sink_x, sink_y = 1.055, 1.42
counter = box((counter_width, counter_len, .055),
              center=(cx, counter_y, .9025), color=STONE)
opening = box((.51, .65, .19),
              center=(sink_x, sink_y, .88), color=STONE)
kitchen.include("Stone countertop with sink opening",
                subtract(counter, opening))

sink = Asset("Dark inset rectangular sink")
add(sink, "Recessed bowl bottom", (.49, .63, .025),
    (sink_x, sink_y, .735), BLACK)
for i, x in enumerate((sink_x-.255, sink_x+.255)):
    add(sink, "Bowl side %d" % i, (.018, .65, .145),
        (x, sink_y, .81), BLACK)
for i, y in enumerate((sink_y-.325, sink_y+.325)):
    add(sink, "Bowl end %d" % i, (.51, .018, .145),
        (sink_x, y, .81), BLACK)
for i, x in enumerate((sink_x-.285, sink_x+.285)):
    add(sink, "Sink long rim %d" % i, (.030, .74, .014),
        (x, sink_y, .936), (.075, .062, .035))
for i, y in enumerate((sink_y-.355, sink_y+.355)):
    add(sink, "Sink end rim %d" % i, (.59, .025, .014),
        (sink_x, y, .936), (.075, .062, .035))
add(sink, "Narrow draining ledge", (.115, .62, .012),
    (sink_x+.20, sink_y, .923), (.055, .050, .031))
for i in range(6):
    add(sink, "Draining groove %d" % i, (.09, .008, .006),
        (sink_x+.20, sink_y-.25+i*.095, .933), BLACK)
kitchen.include("Sink", sink)

hob = Asset("Black glass ceramic cooktop")
hob_y = -.35
add(hob, "Glass hob", (.72, 1.18, .018),
    (.999, hob_y, .943), BLACK)
for burner, (x, y, r) in enumerate([
    (.82, hob_y+.32, .145),
    (1.18, hob_y+.32, .123),
    (.82, hob_y-.27, .17),
    (1.18, hob_y-.27, .15)
]):
    for i in range(28):
        a = 2 * math.pi * i / 28
        b = 2 * math.pi * (i+1) / 28
        hob.include("Burner %d ring %02d" % (burner, i),
            rod(radius=.0014,
                start=(x+r*math.cos(a), y+r*math.sin(a), .954),
                end=(x+r*math.cos(b), y+r*math.sin(b), .954),
                color=RING))
kitchen.include("Cooktop", hob)

add(kitchen, "Glossy ivory backsplash", (.025, 6.85, .78),
    (1.447, .10, 1.31), BACKSPLASH)
for i, y in enumerate((-.6, 1.25, 2.9)):
    add(kitchen, "Backsplash joint %d" % i, (.002, .003, .73),
        (1.431, y, 1.305), (.76, .75, .70))

upper = Asset("Walnut wall cupboards")
upper_bottom = 1.65
upper_top = 3.35
add(upper, "Continuous upper cabinet", (.49, 6.9, upper_top-upper_bottom),
    (1.22, .10, (upper_top+upper_bottom)/2), WOOD)
for i in range(8):
    y = -3.0 + i * .88
    add(upper, "Walnut door panel %d" % i, (.022, .867, 1.64),
        (.963, y, 2.51), WOOD)
    add(upper, "Thin lower edge %d" % i, (.045, .86, .025),
        (.945, y, 1.679), (.052, .020, .007))
add(upper, "Underside dark panel", (.51, 6.85, .028),
    (1.21, .1, 1.65), WOOD)
add(upper, "Warm continuous light diffuser", (.018, 6.6, .012),
    (1.39, .1, 1.629), LED)
add(upper, "Front underside trim", (.018, 6.85, .025),
    (.95, .1, 1.635), (.19, .115, .045))
hood = Asset("Integrated stainless extractor")
add(hood, "Metal underside", (.48, 1.35, .025),
    (1.19, -.33, 1.619), METAL)
for i, y in enumerate((-.64, -.06)):
    add(hood, "Inset filter %d" % i, (.30, .49, .008),
        (1.20, y, 1.602), (.27, .28, .25))
add(hood, "Extractor front lip", (.035, 1.38, .035),
    (.943, -.33, 1.610), METAL)
upper.include("Extractor", hood)
kitchen.include("Upper cabinets", upper)

rear = Asset("Rear walnut cabinet end")
add(rear, "Tall rear cabinet", (.75, .57, 3.34),
    (1.10, 3.30, 1.69), WOOD)
add(rear, "Broad walnut side face", (.035, .59, 3.30),
    (.707, 3.29, 1.69), WOOD)
add(rear, "Side panel fine seam", (.009, .004, 3.20),
    (.684, 3.15, 1.69), (.040, .014, .005))
kitchen.include("Rear tall section", rear)
kitchen.move((-.23, 0, 0))
scene.include("Kitchen", kitchen)

realize(scene)

def basic(name, color, rough=.45, metal=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    return m

wood = basic("Dark walnut longitudinal grain", WOOD, .31)
n = wood.node_tree.nodes
l = wood.node_tree.links
coord = n.new("ShaderNodeTexCoord")
mapping = n.new("ShaderNodeVectorMath")
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (14, 14, .5)
noise = n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 3.8
noise.inputs["Detail"].default_value = 2
l.new(coord.outputs["Generated"], mapping.inputs[0])
l.new(mapping.outputs[0], noise.inputs["Vector"])
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .12
ramp.color_ramp.elements[0].color = (.025, .008, .003, 1)
ramp.color_ramp.elements[1].position = .88
ramp.color_ramp.elements[1].color = (.145, .057, .019, 1)
l.new(noise.outputs["Fac"], ramp.inputs[0])
l.new(ramp.outputs["Color"], n.get("Principled BSDF").inputs["Base Color"])

slatmat = basic("Warm walnut battens", SLAT, .38)

stone = basic("Cream fine veined stone", STONE, .28)
n = stone.node_tree.nodes
l = stone.node_tree.links
coord = n.new("ShaderNodeTexCoord")
mapping = n.new("ShaderNodeVectorMath")
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (1.8, .65, 2)
noise = n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 8
noise.inputs["Detail"].default_value = 3
noise.inputs["Roughness"].default_value = .65
l.new(coord.outputs["Object"], mapping.inputs[0])
l.new(mapping.outputs[0], noise.inputs["Vector"])
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .37
ramp.color_ramp.elements[0].color = (.77, .73, .63, 1)
ramp.color_ramp.elements[1].position = .66
ramp.color_ramp.elements[1].color = (.83, .79, .69, 1)
e = ramp.color_ramp.elements.new(.505)
e.color = (.78, .74, .64, 1)
e = ramp.color_ramp.elements.new(.519)
e.color = (.18, .15, .10, 1)
e = ramp.color_ramp.elements.new(.531)
e.color = (.79, .75, .65, 1)
l.new(noise.outputs["Fac"], ramp.inputs[0])
l.new(ramp.outputs[0], n.get("Principled BSDF").inputs["Base Color"])

glass = basic("Black reflective ceramic", BLACK, .09, .12)
backsplash = basic("Glossy warm white glass", BACKSPLASH, .10)
metalmat = basic("Brushed stainless steel", METAL, .25, .8)
floormat = basic("Pale warm gray floor", FLOOR, .65)
ledmat = basic("Warm strip light", LED, .3)
p = ledmat.node_tree.nodes.get("Principled BSDF")
if "Emission Color" in p.inputs:
    p.inputs["Emission Color"].default_value = (1, .77, .40, 1)
    p.inputs["Emission Strength"].default_value = 6

palette = [
    (WOOD, wood), (SLAT, slatmat), (STONE, stone), (BLACK, glass),
    (BACKSPLASH, backsplash), (METAL, metalmat), (FLOOR, floormat),
    (LED, ledmat)
]
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for slot in obj.material_slots:
        if slot.material:
            c = slot.material.diffuse_color
            for target, material in palette:
                if sum((c[k]-target[k])**2 for k in range(3)) < .0001:
                    slot.material = material
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
background.inputs["Color"].default_value = (.78, .81, .86, 1)
background.inputs["Strength"].default_value = .22

set_view(position=(.70, -2.20, 1.62),
         target=(.60, 3.50, 1.235),
         lens=31.5, sensor=36)
area_emitter(position=(-2.9, -.9, 2.8), power=430, size=4,
             target=(-.1, 2.2, 1), color=(1, .95, .87))
area_emitter(position=(-1.9, 2.1, 3.12), power=110, size=2.5,
             target=(-1, 3.5, 1.4), color=(1, .92, .81))
area_emitter(position=(.96, 1.15, 1.59), power=38, size=1.8,
             target=(1.20, 1.15, 1.12), color=(1, .77, .43))
area_emitter(position=(.96, -.85, 1.59), power=34, size=1.8,
             target=(1.20, -.85, 1.12), color=(1, .80, .50))
sc.view_settings.view_transform = 'AgX'
