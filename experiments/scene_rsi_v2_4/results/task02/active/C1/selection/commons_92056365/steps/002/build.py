import bpy, math, random
from sceneact import *

# Inventory estimates: ceiling (0,0)-(1,.33); tiled floor (0,.60)-(1,1);
# rear glazing (0,.31)-(.72,.58), right glazing (.68,.22)-(1,.59).
# Left booths (0,.53)-(.34,.90), cropped foreground table (0,.85)-(.46,1);
# staggered pedestal tables and armchairs (.33,.52)-(.88,.99).
# Large left bell pendant (.02,.11)-(.24,.41); smaller hanging bells
# across the middle and rear; palm (.77,.40)-(1,1) overlaps right furniture.
# Hidden room extents, foliage and absolute scale remain uncertain.
#
# Execution review: previous execution failed before realization because rod
# endpoints and colors were passed positionally. All rod calls now use named
# arguments. No rendered image was returned; appearance and camera matching
# remain unverified. Geometry, placement and lighting families are retained.
# Checks by inspection: positive primitive dimensions, distinct rod endpoints,
# keyword-only rod arguments, world initialization after realize.
# Estimated expansion: about 510 primitive meshes plus 8 Boolean cutters.
random.seed(12)
scene = Scene("Windowed cafeteria")

ivory = (.76,.77,.73)
ceiling_color = (.86,.87,.82)
frame = (.23,.25,.22)
upholstery = (.28,.31,.27)
upholstery_light = (.35,.38,.33)
table_color = (.66,.68,.62)
metal = (.42,.45,.41)
dark = (.055,.075,.055)
floor_color = (.19,.22,.19)

def add(parent, name, node):
    parent.include(name, node)
    return node

def cylinder(radius, height, center, color):
    return rod(radius=radius, length=height, center=center,
               axis='+z', color=color)

def line(radius, start, end, color):
    return rod(radius=radius, start=start, end=end, color=color)

architecture = Asset("Architecture")
scene.include("architecture", architecture)
add(architecture, "tiled_floor",
    box(size=(11,18,.12), center=(0,2,-.08), color=floor_color))
add(architecture, "ceiling",
    box(size=(11,18,.12), center=(0,2,3.52), color=ceiling_color))
add(architecture, "left_wall",
    box(size=(.15,18,3.5), center=(-5.5,2,1.72), color=ivory))
add(architecture, "rear_sill_wall",
    box(size=(11,.16,.88), center=(0,9,.44), color=ivory))
add(architecture, "right_sill_wall",
    box(size=(.16,18,.88), center=(5.5,2,.44), color=ivory))

for j in range(38):
    add(architecture, "ceiling_seam_%02d" % j,
        box(size=(10.95,.012,.008), center=(0,-6.3+j*.42,3.452),
            color=(.57,.59,.55)))
for i in range(20):
    add(architecture, "floor_long_joint_%02d" % i,
        box(size=(.012,17.8,.004), center=(-5.2+i*.55,2,-.015),
            color=(.32,.34,.30)))
for j in range(28):
    add(architecture, "floor_cross_joint_%02d" % j,
        box(size=(10.95,.009,.004), center=(0,-6.5+j*.62,-.014),
            color=(.30,.32,.28)))

windows = Asset("Window framing and outdoor view")
scene.include("windows", windows)
add(windows, "rear_bright_exterior",
    box(size=(17,.12,5), center=(0,11.8,2.5), color=(.87,.90,.84)))
add(windows, "right_bright_exterior",
    box(size=(.12,24,5), center=(8,2,2.5), color=(.88,.91,.86)))
for z in [.89,3.18]:
    add(windows, "rear_horizontal_%.2f" % z,
        box(size=(11,.11,.07), center=(0,8.91,z), color=frame))
    add(windows, "right_horizontal_%.2f" % z,
        box(size=(.11,18,.07), center=(5.41,2,z), color=frame))
for i,x in enumerate([-5.4,-3.55,-1.65,.3,2.25,4.15,5.4]):
    add(windows, "rear_mullion_%d" % i,
        box(size=(.065,.12,2.3), center=(x,8.9,2.035), color=frame))
for i,y in enumerate([-6,-3.2,-.3,2.6,5.5,8.9]):
    add(windows, "right_mullion_%d" % i,
        box(size=(.12,.065,2.3), center=(5.4,y,2.035), color=frame))
add(windows, "rear_upper_fascia",
    box(size=(11,.22,.26), center=(0,8.91,3.34), color=ivory))
add(windows, "right_upper_fascia",
    box(size=(.22,18,.26), center=(5.4,2,3.34), color=ivory))
for i in range(24):
    x = random.uniform(-7,7)
    y = random.uniform(10,11.5)
    z = random.uniform(.8,2.3)
    bush = ball(radius=random.uniform(.30,.65), center=(x,y,z),
                color=(.55,.61,.51))
    bush.resize((1,.7,1.1))
    add(windows, "distant_foliage_%02d" % i, bush)

def table(name, x, y, w=1.22, d=.93):
    a = Asset(name)
    add(a, "dark_edge",
        box(size=(w,d,.065), center=(x,y,.785), color=(.18,.21,.18)))
    add(a, "laminate_surface",
        box(size=(w-.025,d-.025,.025), center=(x,y,.83), color=table_color))
    add(a, "pedestal", cylinder(.055,.69,(x,y,.385),metal))
    add(a, "foot", cylinder(.29,.045,(x,y,.045),metal))
    add(a, "ashtray", cylinder(.065,.024,(x+.19,y+.09,.856),(.64,.67,.60)))
    scene.include(name, a)
    return a

def chair(name, x, y, angle=0, shade=upholstery):
    a = Asset(name)
    add(a, "seat", box(size=(.72,.67,.13), center=(x,y,.49), color=shade))
    add(a, "padded_back",
        box(size=(.77,.105,.69), center=(x,y-.30,.82), color=shade))
    add(a, "left_arm_panel",
        box(size=(.09,.66,.39), center=(x-.36,y,.66), color=shade))
    add(a, "right_arm_panel",
        box(size=(.09,.66,.39), center=(x+.36,y,.66), color=shade))
    add(a, "swivel_stem", cylinder(.057,.38,(x,y,.245),metal))
    add(a, "round_base", cylinder(.255,.042,(x,y,.045),metal))
    a.turn("z", angle, pivot=(x,y,0))
    scene.include(name, a)
    return a

for i,y in enumerate([-3.05,-.30,2.35,5.0,7.4]):
    a = Asset("Left booth %d" % i)
    x = -3.47
    add(a, "wide_seat",
        box(size=(2.28,.66,.16), center=(x,y,.48), color=upholstery_light))
    add(a, "broad_back",
        box(size=(2.32,.15,.78), center=(x,y+.29,.86), color=upholstery))
    add(a, "left_end",
        box(size=(.12,.68,.53), center=(x-1.12,y,.67), color=upholstery))
    add(a, "plinth",
        box(size=(1.88,.43,.36), center=(x,y,.22), color=(.14,.17,.14)))
    scene.include("booth_%d" % i, a)
    table("Left table %d" % i, x, y-.81, 2.16, 1.06)

for row,y in enumerate([-.55,2.25,4.85,7.1]):
    for col,x in enumerate([-.55,2.20]):
        table("Dining table %d %d" % (row,col), x,y,1.35,.98)
        chair("Near chair %d %d" % (row,col), x+.12,y-.96,0,
              upholstery if row % 2 == 0 else upholstery_light)
        chair("Far chair %d %d" % (row,col), x-.12,y+.90,180,
              upholstery_light)
        if row in [1,2]:
            chair("Side chair %d %d" % (row,col), x-.98,y,90,upholstery)
table("Right foreground table",3.35,-2.53,1.40,1.04)
chair("Right foreground armchair",3.42,-3.47,-5)
chair("Right foreground far armchair",3.45,-1.58,180,upholstery_light)

lamps = Asset("Suspended industrial lights")
scene.include("pendant_lights", lamps)

def pendant(name, x, y, r, bottom):
    a = Asset(name)
    h = r*.86
    shell = ball(radius=r, center=(x,y,bottom+.025), color=dark)
    shell.resize((1,1,.86))
    cutter = box(size=(r*2.5,r*2.5,r*2),
                 center=(x,y,bottom-r), color=dark)
    add(a, "bell_shade", subtract(shell,cutter))
    add(a, "pale_open_underside",
        cylinder(r*.985,.018,(x,y,bottom+.003),(.81,.83,.75)))
    add(a, "neck", cylinder(r*.34,r*.61,(x,y,bottom+h*.94),dark))
    add(a, "neck_band",
        cylinder(r*.345,.055,(x,y,bottom+h*.99),(.38,.41,.34)))
    top = bottom+h*.94+r*.305
    if top < 3.45:
        add(a, "suspension_cord",
            line(.009,(x,y,top),(x,y,3.46),dark))
    add(a, "ceiling_rose", cylinder(.075,.022,(x,y,3.438),dark))
    lamps.include(name,a)

pendant("Large left foreground pendant",-3.50,-2.45,.66,2.51)
pendant("Central pendant",.55,2.15,.36,2.43)
pendant("Right middle pendant",3.42,1.0,.45,2.52)
pendant("Rear left pendant",-2.8,6.25,.23,2.36)
pendant("Rear middle pendant",-.48,6.4,.25,2.39)
pendant("Rear right pendant",3.6,5.55,.23,2.4)
pendant("Distant right pendant",4.83,7.65,.21,2.40)
pendant("Left distant pendant",-4.4,5.2,.22,2.4)

plant = Asset("Foreground palm")
scene.include("foreground_palm",plant)
px,py = 4.85,-2.8
add(plant, "planter", cylinder(.31,.48,(px,py,.25),(.12,.16,.11)))
add(plant, "soil", cylinder(.285,.025,(px,py,.50),(.07,.08,.05)))
for k in range(7):
    az = math.radians(35+k*48)
    origin = (px+random.uniform(-.13,.13),
              py+random.uniform(-.13,.13),.44)
    tip = (px+math.cos(az)*.53,py+math.sin(az)*.53,
           1.65+random.uniform(.05,.48))
    add(plant, "stem_%d" % k, line(.015,origin,tip,(.18,.23,.13)))
    end = (tip[0]+math.cos(az)*.87,
           tip[1]+math.sin(az)*.87,tip[2]-.12)
    add(plant, "frond_spine_%d" % k, line(.009,tip,end,(.14,.20,.10)))
    for j in range(5):
        t = .10+j*.17
        cx = tip[0]+(end[0]-tip[0])*t
        cy = tip[1]+(end[1]-tip[1])*t
        cz = tip[2]+(end[2]-tip[2])*t
        for side in [-1,1]:
            length = .35*(1-t*.62)
            vx = math.cos(az+.85*side)
            vy = math.sin(az+.85*side)
            leaf = ball(radius=1,
                        center=(cx+vx*length*.45,cy+vy*length*.45,cz+.07),
                        color=(.095+.015*(j%2),.16,.085))
            leaf.resize((length,.026,.045))
            leaf.turn("z",math.degrees(az+.85*side))
            add(plant, "leaf_%d_%d_%d" % (k,j,side),leaf)

rearplants = Asset("Rear low planters")
scene.include("rear_planters",rearplants)
for i,x in enumerate([-2.0,-.9,.1]):
    add(rearplants, "container_%d" % i,
        box(size=(.75,.30,.23), center=(x,6.7,1.0), color=(.20,.24,.18)))
    for j in range(4):
        foliage = ball(radius=.22,
                       center=(x+random.uniform(-.3,.3),6.7,
                               1.23+random.uniform(0,.13)),
                       color=(.22,.29,.19))
        foliage.resize((1,.7,.8))
        add(rearplants,"foliage_%d_%d" % (i,j),foliage)

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
sc.world.node_tree.links.new(background.outputs["Background"],
                             output.inputs["Surface"])
background.inputs["Color"].default_value = (.78,.82,.75,1)
background.inputs["Strength"].default_value = .65

set_view(position=(-2.15,-7.1,1.90),target=(.10,5.3,1.73),
         lens=24,sensor=36)
area_emitter(position=(0,8.4,2.8),power=1100,size=8,target=(0,0,.5))
area_emitter(position=(5.0,1.5,2.65),power=1000,size=7,target=(-2,1,.4))
area_emitter(position=(-1,-3,3.25),power=350,size=6,target=(0,2,0))

for mat in bpy.data.materials:
    if mat.use_nodes:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value = .67
sc.render.resolution_x = 512
sc.render.resolution_y = 379
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = .25
