from sceneact import *
import bpy
import math
import random

random.seed(18)
scene = Scene("Montessori classroom")

wood = (0.64, 0.46, 0.24)
lightwood = (0.73, 0.57, 0.34)
edgewood = (0.79, 0.64, 0.40)
cream = (0.84, 0.82, 0.70)
darkwood = (0.39, 0.29, 0.16)

def add(name, node):
    scene.include(name, node)
    return node

def cube(name, size, center, color):
    return add(name, box(size, center=center, color=color))

# Open-front room, with a high ceiling and generous daylight.
cube("floor", (9.4, 9.5, .16), (0, 0, -.08), (.67, .48, .29))
cube("back cream wall", (9.4, .18, 3.65), (0, 4.65, 1.82), cream)
cube("left cream wall", (.16, 9.4, 3.65), (-4.65, 0, 1.82), cream)
cube("right rear wall", (.16, 3.8, 3.65), (4.65, 2.75, 1.82), cream)
cube("back skirting", (9.2, .06, .13), (0, 4.53, .065), lightwood)
cube("left skirting", (.06, 9.2, .13), (-4.53, 0, .065), lightwood)

# Narrow, lightly varied floorboards.
for i in range(37):
    x = -4.5 + i * .25
    for j in range(5):
        y = -3.9 + j * 1.95 + (.45 if i % 2 else 0)
        if y > 4.4:
            continue
        c = (.67 + random.uniform(-.035, .035),
             .49 + random.uniform(-.025, .025),
             .30 + random.uniform(-.02, .02))
        cube("floorboard_%d_%d" % (i, j), (.246, 1.936, .018),
             (x, y, .011), c)

# Five tall windows across the back wall.
for i, x in enumerate([-3.70, -2.14, -.58, .98, 2.54]):
    cube("window recess %d" % i, (1.30, .045, 2.02),
         (x, 4.535, 2.27), (.80, .88, .85))
    cube("window daylight %d" % i, (1.16, .035, 1.88),
         (x, 4.49, 2.28), (.81, .89, .85))
    for dx in [-.66, .66]:
        cube("window upright", (.075, .14, 2.10),
             (x + dx, 4.43, 2.27), (.90, .90, .82))
    for z in [1.23, 3.31]:
        cube("window horizontal frame", (1.39, .14, .075),
             (x, 4.43, z), (.92, .91, .83))
    cube("window mullion", (.045, .08, 2.02),
         (x + .20, 4.40, 2.27), (.89, .90, .83))
    cube("window crossbar", (1.29, .08, .045),
         (x, 4.39, 2.17), (.89, .90, .83))
    cube("broad wood sill", (1.48, .34, .075),
         (x, 4.36, 1.20), edgewood)
    # Muted exterior shapes visible through the glazing.
    for k in range(5):
        xx = x + random.uniform(-.52, .52)
        zz = random.uniform(1.43, 3.05)
        add("distant foliage", ball(random.uniform(.09, .22),
            center=(xx, 4.46, zz), color=(.48, .62, .43)))

def shelf(name, x, y, width=2.1, depth=.65, height=1.05,
          angle=0, columns=3, levels=2):
    a = Asset(name)
    def panel(n, size, p, col=lightwood):
        a.include(n, box(size, center=p, color=col))
    panel("back", (width, .045, height-.10), (0, depth/2-.025, height/2), wood)
    for xx in [-width/2+.035, width/2-.035]:
        panel("side"+str(xx), (.07, depth, height), (xx, 0, height/2))
    for j in range(levels+1):
        zz = .11 + j*(height-.15)/levels
        panel("horizontal"+str(j), (width, depth, .065), (0, 0, zz), edgewood)
    for j in range(1, columns):
        xx = -width/2 + width*j/columns
        panel("divider"+str(j), (.045, depth-.05, height-.15),
              (xx, 0, height/2+.025))
    for xx in [-width/2+.12, width/2-.12]:
        for yy in [-depth/2+.10, depth/2-.10]:
            panel("foot"+str((xx, yy)), (.10, .10, .12), (xx, yy, .06), darkwood)
    a.turn('z', angle, pivot=(0, 0, 0))
    a.move((x, y, 0))
    add(name, a)
    return a

# Cabinets run beneath the windows and along the side walls.
shelf("back left cabinet", -3.05, 3.91, 2.35, .58, .89, columns=3)
shelf("back middle cabinet", -.53, 3.91, 2.35, .58, .89, columns=4)
shelf("back right cabinet", 2.02, 3.91, 2.35, .58, .89, columns=3)
shelf("left long shelves", -4.04, 1.65, 2.80, .66, 1.03, angle=90, columns=4)
shelf("left foreground shelves", -3.95, -1.15, 2.30, .66, 1.04, angle=90, columns=3)
shelf("left short partition", -2.45, 1.39, 1.76, .65, .98, columns=3)
shelf("right wall shelves", 4.02, 2.25, 2.30, .58, .94, angle=-90, columns=3)
shelf("right middle shelves", 3.70, .05, 1.47, .62, .96, angle=-90, columns=2)

# Large open island in the foreground, on a red circular mat.
add("round burgundy classroom rug",
    rod(radius=1.72, length=.026, center=(.67, -1.73, .038),
        axis='+z', color=(.43, .095, .065)))
add("rug inset border",
    rod(radius=1.58, length=.029, center=(.67, -1.73, .04),
        axis='+z', color=(.50, .17, .10)))
shelf("main foreground material island", .55, -1.49,
      2.85, 1.06, 1.16, columns=3, levels=2)

# Trays and practical-life materials are small and loosely spaced.
def tray(name, x, y, z, w=.43, d=.30):
    cube(name+" base", (w, d, .032), (x, y, z+.016), edgewood)
    for yy in [-d/2, d/2]:
        cube(name+" rim", (w, .023, .055), (x, y+yy, z+.045), lightwood)
    for xx in [-w/2, w/2]:
        cube(name+" end", (.023, d, .055), (x+xx, y, z+.045), lightwood)

def bowl(name, x, y, z, radius=.085, color=(.75, .70, .48)):
    add(name, rod(radius=radius, length=.065,
        center=(x, y, z+.032), color=color))

for j, x in enumerate([-.48, .20, .94, 1.61]):
    tray("island activity tray "+str(j), x, -1.48, 1.195, .48, .36)
    if j == 0:
        for k in range(4):
            bowl("sorting cup", x-.15+k*.10, -1.48, 1.23, .036,
                 [(.66,.24,.15),(.84,.69,.26),(.31,.49,.36),(.34,.44,.60)][k])
    elif j == 1:
        for k in range(3):
            cube("wood geometric block", (.075,.075,.09+k*.03),
                 (x-.13+k*.12, -1.47, 1.27+k*.015), (.77,.61,.35))
    elif j == 2:
        add("small white pitcher", rod(radius=.068, length=.16,
            center=(x,-1.48,1.32), color=(.87,.86,.73)))
        bowl("pitcher receiving bowl", x+.15,-1.47,1.23,.065)
    else:
        for k in range(5):
            add("upright cylinder", rod(radius=.025+k*.005,
                length=.09+k*.027, center=(x-.16+k*.08,-1.49,1.28+k*.013),
                color=(.61,.40,.19)))

# Contents inside the island cubbies.
for z in [.18, .70]:
    for x in [-.40, .55, 1.48]:
        tray("stored tray", x, -1.69, z, .61, .36)
        for k in range(3):
            cube("stored wood material", (.12,.16,.065),
                 (x-.18+k*.17,-1.70,z+.075), (.62,.45,.24))

for i, x in enumerate([-3.8,-2.9,-1.8,-.7,.5,1.6,2.6]):
    tray("window cabinet tray"+str(i), x, 3.87, .94, .49, .30)
    for k in range(3):
        cube("back shelf material", (.07,.09,.08+.025*k),
             (x-.13+k*.12,3.88,1.00+.013*k),
             [(.69,.48,.23),(.61,.25,.15),(.62,.66,.43)][k])

# Child-scale work tables and stools.
def table(name, x, y, w=1.36, d=.80, h=.69):
    a = Asset(name)
    a.include("top", box((w,d,.075), center=(x,y,h), color=edgewood))
    for xx in [-w/2+.10,w/2-.10]:
        for yy in [-d/2+.10,d/2-.10]:
            a.include("leg"+str((xx,yy)),
                box((.065,.065,h-.04),center=(x+xx,y+yy,(h-.04)/2),color=wood))
    a.include("apron",box((w-.12,.06,.15),center=(x,y-d/2+.07,h-.10),color=lightwood))
    add(name,a)

def stool(name,x,y):
    a=Asset(name)
    a.include("seat",box((.37,.36,.055),center=(x,y,.36),color=edgewood))
    for dx in [-.13,.13]:
        for dy in [-.12,.12]:
            a.include(str((dx,dy)),box((.045,.045,.34),
                center=(x+dx,y+dy,.17),color=wood))
    add(name,a)

table("central activity table", .15, 1.60, 1.65, .90)
stool("central stool left",-.94,1.55)
stool("central stool right",1.25,1.59)
stool("central rear stool",.17,2.27)
table("rear right work table",2.72,2.37,1.12,.72)
stool("rear table stool",2.67,1.71)
table("left small work table",-2.52,2.79,1.05,.72)
stool("left work stool",-2.51,2.17)
tray("table work", .20,1.62,.73,.54,.33)
for k in range(5):
    cube("table wooden puzzle",(.07,.07,.04),
         (-.01+k*.10,1.62,.79),(.69,.42,.23))

# A little chair beside the front island.
def chair(name,x,y,angle=0):
    a=Asset(name)
    a.include("seat",box((.43,.43,.06),center=(0,0,.39),color=lightwood))
    for xx in [-.16,.16]:
        for yy in [-.16,.16]:
            a.include("leg"+str((xx,yy)),box((.055,.055,.39),
                center=(xx,yy,.195),color=wood))
    for xx in [-.17,.17]:
        a.include("back post"+str(xx),box((.05,.05,.70),
            center=(xx,.18,.36),color=wood))
    a.include("backrest",box((.38,.055,.19),center=(0,.18,.65),color=lightwood))
    a.turn('z',angle,pivot=(0,0,0))
    a.move((x,y,0))
    add(name,a)

chair("chair by island",2.35,-1.18,-17)
chair("distant child chair",3.54,2.75,0)

# A few orderly boxes and books on the side shelves.
for i in range(7):
    y=-1.8+i*.60
    cube("left shelf storage box",(.31,.35,.18),
         (-3.98,y,.25 if i%2 else .70),(.65,.48,.27))
for i in range(5):
    cube("upright books",(.045,.20,.24+random.random()*.06),
         (3.75+i*.055,1.72,1.08),
         [(.49,.24,.14),(.64,.62,.40),(.40,.48,.42)][i%3])

# Small green plants and classroom wall details.
for x,y,z in [(-3.95,3.90,.94),(3.0,3.90,.94),(-3.98,.8,1.08)]:
    add("terracotta plant pot",rod(radius=.105,length=.16,
        center=(x,y,z+.08),color=(.54,.30,.16)))
    for k in range(5):
        a=k*2.4
        add("plant leaves",ball(.10,
            center=(x+math.cos(a)*.10,y+math.sin(a)*.07,z+.25+k*.018),
            color=(.27,.40,.18)))
cube("small framed wall picture",(.45,.045,.56),(3.93,4.51,2.55),lightwood)
cube("picture cream paper",(.36,.022,.47),(3.93,4.47,2.55),(.88,.85,.70))
cube("picture colored center",(.20,.015,.22),(3.93,4.45,2.57),(.46,.54,.40))

realize(scene)

# Fine matte grain gives all timber a consistent natural finish.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Roughness"].default_value=.76
        c=bs.inputs["Base Color"].default_value
        if c[0] > c[1]*1.12 and c[1] > c[2]*1.20:
            nodes=mat.node_tree.nodes
            links=mat.node_tree.links
            tex=nodes.new("ShaderNodeTexNoise")
            tex.inputs["Scale"].default_value=5
            tex.inputs["Detail"].default_value=2
            mapping=nodes.new("ShaderNodeVectorMath")
            mapping.operation='MULTIPLY'
            mapping.inputs[1].default_value=(3,45,5)
            coord=nodes.new("ShaderNodeTexCoord")
            links.new(coord.outputs["Generated"],mapping.inputs[0])
            links.new(mapping.outputs[0],tex.inputs["Vector"])
            bump=nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value=.12
            bump.inputs["Distance"].default_value=.025
            links.new(tex.outputs["Fac"],bump.inputs["Height"])
            links.new(bump.outputs["Normal"],bs.inputs["Normal"])

set_view((7.8,-10.7,6.2),(-.15,1.05,1.05),lens=40,sensor=36)
area_emitter((-1.3,3.8,4.5),power=1250,size=5.5,target=(0,-1,0),
             color=(1.0,.94,.80))
area_emitter((1,-3,6.0),power=650,size=6,target=(0,1,.2),
             color=(1.0,.97,.90))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.72,.79,.86,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.45
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=64
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.render.resolution_x=1920
sc.render.resolution_y=1080
sc.render.resolution_percentage=100
