from sceneact import *
import bpy
import math

# Reference inventory, normalized image bounds:
# Floor: (0,.75)-( .42,1), pale rectangular tiles with restrained joints.
# Back wall: (0,.11)-(.47,.76), closely spaced vertical walnut battens.
# White door: (.31,.29)-(.45,.77), thin casing, inset panel, silver lever.
# Low bench: (0,.65)-(.21,.81), black frame, white front, dark wood top.
# Kitchen: counter (.37,.59)-(1,1), pale veined stone, dark inset sink
# at (.46,.64)-(.62,.71), black hob (.40,.77)-(.81,1).
# Right backsplash: (.58,.28)-(1,1), glossy warm white.
# Upper cabinetry: (.46,0)-(1,.43), dark walnut, fine panel seams,
# stainless extractor underside and continuous warm under-cabinet light.
# Tall rear wood section overlaps the slat wall beside the door.
# Counter front and lower cabinetry continue beyond the bottom/right crop.
# Sink fittings and concealed cabinet interiors are uncertain.
#
# Expanded geometry estimate: approximately 310 meshes:
# 65 battens, 35 floor joints, 144 hob-ring segments, approximately
# 65 architectural/cabinet/sink/door/lighting components. One countertop
# Boolean with one cutter. No fillet_box or dense nested decorations.

scene = Scene("Walnut kitchen")

WALL = (.79, .77, .70)
WHITE = (.86, .86, .82)
WOOD = (.19, .075, .026)
SLAT = (.33, .145, .055)
STONE = (.74, .71, .63)
FLOOR = (.57, .55, .48)
BLACK = (.012, .014, .013)
METAL = (.46, .47, .43)
GROUT = (.34, .33, .29)
RING = (.105, .105, .085)
LED = (1.0, .79, .40)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Room architecture")
add(architecture, "Floor slab", (8, 11, .10), (-.5, .5, -.06), FLOOR)
add(architecture, "Rear plaster wall", (6.2, .13, 3.25), (-1.35, 3.75, 1.60), WALL)
add(architecture, "Right plaster wall", (.14, 9, 3.3), (1.54, -.2, 1.62), WALL)
add(architecture, "Ceiling", (6.2, 9, .10), (-1.4, -.2, 2.98), WHITE)
scene.include("Architecture", architecture)

floor = Asset("Large pale floor tiles")
for i in range(14):
    y = -4.0 + i * .59
    add(floor, "Horizontal joint %02d" % i, (6.1, .008, .002),
        (-1.4, y, -.007), GROUT)
    for j in range(2):
        x = -2.9 + j * 1.75 + (i % 2) * .70
        add(floor, "Staggered joint %02d %d" % (i,j),
            (.007, .59, .002), (x, y + .295, -.006), GROUT)
scene.include("Tile joints", floor)

wall = Asset("Walnut slatted feature wall")
add(wall, "Dark recess backing", (4.55, .06, 2.48),
    (-1.15, 3.64, 1.27), (.065, .035, .019))
for i in range(65):
    x = -3.40 + i * .070
    add(wall, "Vertical timber batten %02d" % i,
        (.045, .045, 2.48), (x, 3.586, 1.27), SLAT)
scene.include("Slatted wall", wall)

door = Asset("White interior door")
door_x = -.14
add(door, "Door slab", (.86, .055, 2.05), (door_x, 3.525, 1.025), WHITE)
add(door, "Left casing", (.055, .075, 2.12), (door_x-.465, 3.50, 1.06), WHITE)
add(door, "Right casing", (.055, .075, 2.12), (door_x+.465, 3.50, 1.06), WHITE)
add(door, "Top casing", (.985, .075, .065), (door_x, 3.50, 2.09), WHITE)
add(door, "Fine inset door panel", (.745, .012, 1.90),
    (door_x, 3.489, 1.025), (.80, .80, .77))
door.include("Handle escutcheon",
             rod(radius=.022, start=(door_x-.31,3.475,1.02),
                 end=(door_x-.31,3.450,1.02), color=METAL))
door.include("Silver lever",
             rod(radius=.012, start=(door_x-.31,3.437,1.025),
                 end=(door_x-.20,3.437,1.025), color=METAL))
door.include("Keyhole", rod(radius=.009, start=(door_x-.31,3.475,.94),
                            end=(door_x-.31,3.456,.94), color=METAL))
add(door, "Light switch", (.085,.018,.085), (door_x-.65,3.535,1.05), WHITE)
add(door, "Low wall outlet", (.07,.018,.08), (door_x-.64,3.535,.25), WHITE)
scene.include("Door and fittings", door)

bench = Asset("Low black and white bench")
add(bench, "Black cabinet body", (1.54,.43,.43), (-2.06,3.27,.215), BLACK)
add(bench, "White inset front", (1.40,.018,.29), (-2.06,3.043,.205), WHITE)
add(bench, "Dark timber top", (1.58,.46,.045), (-2.06,3.26,.45), WOOD)
add(bench, "Front upper rail", (1.53,.025,.045), (-2.06,3.026,.39), BLACK)
scene.include("Bench", bench)

kitchen = Asset("Right wall kitchen")
cx = 1.075
counter_width = .84
counter_back = 3.50
counter_front = -3.2
counter_len = counter_back-counter_front
counter_y = (counter_back+counter_front)/2
add(kitchen, "Base cabinet volume", (.81,counter_len,.84),
    (1.095,counter_y,.43), (.24,.13,.065))
add(kitchen, "Recessed plinth", (.70,counter_len,.10),
    (1.15,counter_y,.05), BLACK)
# Long front panels face the room.
for i in range(7):
    y = counter_front + .46 + .94*i
    add(kitchen, "Lower walnut front %d" % i, (.025,.925,.76),
        (.675,y,.47), WOOD)

sink_x, sink_y = 1.055, 2.47
counter = box((counter_width,counter_len,.055),
              center=(cx,counter_y,.9025), color=STONE)
opening = box((.51,.65,.15), center=(sink_x,sink_y,.90), color=STONE)
kitchen.include("Stone countertop with sink opening", subtract(counter, opening))

sink = Asset("Dark inset rectangular sink")
add(sink,"Recessed bowl bottom",(.49,.63,.025),(sink_x,sink_y,.735),BLACK)
for x in (sink_x-.255,sink_x+.255):
    add(sink,"Bowl side %.2f"%x,(.018,.65,.145),(x,sink_y,.81),BLACK)
for y in (sink_y-.325,sink_y+.325):
    add(sink,"Bowl end %.2f"%y,(.51,.018,.145),(sink_x,y,.81),BLACK)
for x in (sink_x-.285,sink_x+.285):
    add(sink,"Sink long rim %.2f"%x,(.035,.74,.014),(x,sink_y,.936),(.095,.077,.045))
for y in (sink_y-.355,sink_y+.355):
    add(sink,"Sink end rim %.2f"%y,(.59,.025,.014),(sink_x,y,.936),(.095,.077,.045))
add(sink,"Narrow draining ledge",(.115,.62,.012),(sink_x+.20,sink_y,.923),(.07,.065,.045))
for i in range(6):
    add(sink,"Draining groove %d"%i,(.09,.008,.006),
        (sink_x+.20,sink_y-.25+i*.095,.933),BLACK)
kitchen.include("Sink",sink)

hob = Asset("Black glass ceramic cooktop")
hob_y = .34
add(hob,"Glass hob",(.72,1.18,.018),(.999,hob_y,.943),BLACK)
# Four faint burner circles lie flush against the glossy glass.
for burner,(x,y,r) in enumerate([
    (.82,hob_y+.32,.145),(1.18,hob_y+.32,.123),
    (.82,hob_y-.27,.17),(1.18,hob_y-.27,.15)]):
    for i in range(36):
        a=2*math.pi*i/36
        b=2*math.pi*(i+1)/36
        hob.include("Burner %d ring %02d"%(burner,i),
                    rod(radius=.0017,
                        start=(x+r*math.cos(a),y+r*math.sin(a),.954),
                        end=(x+r*math.cos(b),y+r*math.sin(b),.954),
                        color=RING))
kitchen.include("Cooktop",hob)

add(kitchen,"Glossy ivory backsplash",(.025,6.85,1.02),
    (1.447,.10,1.43),(.84,.83,.77))
# Vertical glass joins are deliberately subtle.
for i,y in enumerate((-.6,1.25,2.9)):
    add(kitchen,"Backsplash joint %d"%i,(.002,.004,.97),
        (1.431,y,1.425),(.72,.71,.65))

upper = Asset("Walnut wall cupboards")
add(upper,"Continuous upper cabinet",(.49,6.9,.94),(1.22,.10,2.35),WOOD)
for i in range(8):
    y=-3.0+i*.88
    add(upper,"Walnut door panel %d"%i,(.022,.867,.87),
        (.963,y,2.36),WOOD)
    add(upper,"Thin lower edge %d"%i,(.045,.86,.025),
        (.945,y,1.904),(.10,.044,.019))
add(upper,"Underside dark panel",(.51,6.85,.028),(1.21,.1,1.875),WOOD)
add(upper,"Warm continuous light diffuser",(.018,6.6,.012),
    (1.39,.1,1.854),LED)
add(upper,"Front underside trim",(.018,6.85,.025),
    (.95,.1,1.86),(.33,.24,.12))
hood=Asset("Integrated stainless extractor")
add(hood,"Metal underside",(.48,1.35,.025),(1.19,.35,1.844),METAL)
for i,y in enumerate((.04,.62)):
    add(hood,"Inset filter %d"%i,(.30,.49,.008),(1.20,y,1.827),(.33,.34,.31))
add(hood,"Extractor front lip",(.035,1.38,.035),(.943,.35,1.835),METAL)
upper.include("Extractor",hood)
kitchen.include("Upper cabinets",upper)

rear = Asset("Rear walnut cabinet end")
add(rear,"Tall rear cabinet",(.75,.57,2.86),(1.10,3.30,1.45),WOOD)
add(rear,"Broad walnut side face",(.035,.59,2.81),(.707,3.29,1.455),WOOD)
add(rear,"Side panel upper seam",(.009,.004,2.72),(.684,3.15,1.47),(.075,.03,.012))
kitchen.include("Rear tall section",rear)
scene.include("Kitchen",kitchen)

realize(scene)

# Shared procedural finishes, without image textures.
def basic(name,color,rough=.45,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    return m

wood=basic("Walnut fine longitudinal grain",WOOD,.32)
n=wood.node_tree.nodes
l=wood.node_tree.links
tex=n.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value=3.8
tex.inputs["Detail"].default_value=2
coord=n.new("ShaderNodeTexCoord")
mapping=n.new("ShaderNodeVectorMath")
mapping.operation='MULTIPLY'
mapping.inputs[1].default_value=(9,9,.45)
l.new(coord.outputs["Generated"],mapping.inputs[0])
l.new(mapping.outputs[0],tex.inputs["Vector"])
r=n.new("ShaderNodeValToRGB")
r.color_ramp.elements[0].position=.16
r.color_ramp.elements[0].color=(.055,.018,.006,1)
r.color_ramp.elements[1].position=.85
r.color_ramp.elements[1].color=(.29,.13,.047,1)
l.new(tex.outputs["Fac"],r.inputs[0])
l.new(r.outputs["Color"],n.get("Principled BSDF").inputs["Base Color"])

slatmat=basic("Warm walnut battens",SLAT,.40)
stone=basic("Cream subtly veined stone",STONE,.31)
n=stone.node_tree.nodes
l=stone.node_tree.links
noise=n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=5.0
noise.inputs["Detail"].default_value=3
noise.inputs["Roughness"].default_value=.7
r=n.new("ShaderNodeValToRGB")
r.color_ramp.elements[0].position=.45
r.color_ramp.elements[0].color=(.71,.68,.58,1)
r.color_ramp.elements[1].position=.59
r.color_ramp.elements[1].color=(.87,.84,.74,1)
e=r.color_ramp.elements.new(.505)
e.color=(.23,.20,.15,1)
e=r.color_ramp.elements.new(.525)
e.color=(.78,.75,.65,1)
l.new(noise.outputs["Fac"],r.inputs[0])
l.new(r.outputs[0],n.get("Principled BSDF").inputs["Base Color"])

glass=basic("Black reflective ceramic",BLACK,.115,.12)
backsplash=basic("Glossy warm white glass",(.84,.83,.77),.12)
metalmat=basic("Brushed stainless steel",METAL,.28,.78)
floormat=basic("Light warm gray floor",FLOOR,.67)
ledmat=basic("Warm strip light",LED,.3)
p=ledmat.node_tree.nodes.get("Principled BSDF")
if "Emission Color" in p.inputs:
    p.inputs["Emission Color"].default_value=(1,.72,.32,1)
    p.inputs["Emission Strength"].default_value=5

palette=[(WOOD,wood),(SLAT,slatmat),(STONE,stone),(BLACK,glass),
         ((.84,.83,.77),backsplash),(METAL,metalmat),(FLOOR,floormat),(LED,ledmat)]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':
        continue
    for slot in obj.material_slots:
        if slot.material:
            c=slot.material.diffuse_color
            for target,material in palette:
                if sum((c[k]-target[k])**2 for k in range(3))<.00015:
                    slot.material=material
                    break

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get("Background")
if background is None:
    background=nodes.new("ShaderNodeBackground")
output=nodes.get("World Output")
if output is None:
    output=nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.78,.81,.86,1)
background.inputs["Strength"].default_value=.35

set_view(position=(-1.10,-3.65,1.62),
         target=(-.28,3.42,1.45),lens=31.5,sensor=36)
area_emitter(position=(-2.8,-1.1,2.65),power=650,size=4.0,
             target=(.0,2.1,1.0),color=(1,.94,.84))
area_emitter(position=(-1.7,2.0,2.8),power=180,size=2.0,
             target=(-.9,3.5,1.3),color=(1,.91,.78))
area_emitter(position=(1.14,1.3,1.81),power=65,size=2.1,
             target=(1.43,1.3,1.15),color=(1,.72,.35))
area_emitter(position=(1.15,-1.0,1.81),power=55,size=2.0,
             target=(1.43,-1.0,1.15),color=(1,.78,.45))
sc.view_settings.view_transform='AgX'
