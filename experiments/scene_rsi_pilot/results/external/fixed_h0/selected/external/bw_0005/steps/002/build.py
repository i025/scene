from sceneact import *
import bpy
import math
import random

random.seed(18)
scene = Scene("Montessori classroom")
wood = (.64, .46, .24)
lightwood = (.73, .57, .34)
edgewood = (.79, .64, .40)
cream = (.84, .82, .70)
darkwood = (.39, .29, .16)

def add(name, node):
    scene.include(name, node)
    return node

def cube(name, size, center, color):
    return add(name, box(size, center=center, color=color))

cube("floor", (9.4, 9.5, .16), (0, 0, -.08), (.67, .48, .29))
cube("back cream wall", (9.4, .18, 3.65), (0, 4.65, 1.825), cream)
cube("left cream wall", (.16, 9.4, 3.65), (-4.65, 0, 1.825), cream)
cube("right rear wall", (.16, 3.8, 3.65), (4.65, 2.75, 1.825), cream)
cube("back skirting", (9.2, .06, .13), (0, 4.53, .065), lightwood)
cube("left skirting", (.06, 9.2, .13), (-4.53, 0, .065), lightwood)

for i in range(37):
    x = -4.5 + i * .25
    for j in range(5):
        y = -3.9 + j * 1.95 + (.45 if i % 2 else 0)
        if y > 4.4:
            continue
        col = (.67 + random.uniform(-.035, .035),
               .49 + random.uniform(-.025, .025),
               .30 + random.uniform(-.02, .02))
        cube("floorboard_%d_%d" % (i, j), (.246, 1.936, .018),
             (x, y, .011), col)

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
    for k in range(7):
        add("distant foliage", ball(random.uniform(.08, .20),
            center=(x + random.uniform(-.52, .52), 4.46,
                    random.uniform(1.43, 3.05)),
            color=(.48, .62, .43)))

def shelf(name, x, y, width=2.1, depth=.65, height=1.05,
          angle=0, columns=3, levels=2):
    a = Asset(name)
    def panel(n, size, pos, col=lightwood):
        a.include(n, box(size, center=pos, color=col))
    panel("back", (width, .045, height-.10),
          (0, depth/2-.025, height/2), wood)
    for i, xx in enumerate([-width/2+.035, width/2-.035]):
        panel("side%d" % i, (.07, depth, height), (xx, 0, height/2))
    for j in range(levels+1):
        zz = .11 + j*(height-.15)/levels
        panel("horizontal%d" % j, (width, depth, .065), (0, 0, zz), edgewood)
    for j in range(1, columns):
        xx = -width/2 + width*j/columns
        panel("divider%d" % j, (.045, depth-.05, height-.15),
              (xx, 0, height/2+.025))
    for i, xx in enumerate([-width/2+.12, width/2-.12]):
        for j, yy in enumerate([-depth/2+.10, depth/2-.10]):
            panel("foot%d%d" % (i,j), (.10, .10, .12),
                  (xx, yy, .06), darkwood)
    a.turn('z', angle, pivot=(0, 0, 0))
    a.move((x, y, 0))
    add(name, a)
    return a

shelf("back left cabinet", -3.05, 3.91, 2.35, .58, .89, columns=3)
shelf("back middle cabinet", -.53, 3.91, 2.35, .58, .89, columns=4)
shelf("back right cabinet", 2.02, 3.91, 2.35, .58, .89, columns=3)
shelf("left long shelves", -4.04, 1.65, 2.80, .66, 1.03, angle=90, columns=4)
shelf("left foreground shelves", -3.95, -1.15, 2.30, .66, 1.04,
      angle=90, columns=3)
shelf("left short partition", -2.45, 1.39, 1.76, .65, .98, columns=3)
shelf("right wall shelves", 4.02, 2.25, 2.30, .58, .94,
      angle=-90, columns=3)
shelf("right middle shelves", 3.70, .05, 1.47, .62, .96,
      angle=-90, columns=2)

add("round burgundy rug", rod(radius=1.72, length=.026,
    center=(.67, -1.73, .038), axis='+z', color=(.43, .095, .065)))
add("rug inset", rod(radius=1.58, length=.029,
    center=(.67, -1.73, .04), axis='+z', color=(.50, .17, .10)))
shelf("main foreground material island", .55, -1.49,
      2.85, 1.06, 1.16, columns=3, levels=2)

def tray(name, x, y, z, w=.43, d=.30):
    cube(name+" base", (w, d, .032), (x, y, z+.016), edgewood)
    for yy in [-d/2, d/2]:
        cube(name+" rim", (w, .023, .055), (x, y+yy, z+.045), lightwood)
    for xx in [-w/2, w/2]:
        cube(name+" end", (.023, d, .055), (x+xx, y, z+.045), lightwood)

def bowl(name, x, y, z, radius=.085, color=(.75, .70, .48)):
    a = Asset(name)
    a.include("base", rod(radius=radius*.86, length=.025,
              center=(x,y,z+.0125), color=color))
    points = [(x+radius*math.cos(k*math.tau/32),
               y+radius*math.sin(k*math.tau/32),z+.055) for k in range(33)]
    a.include("rim", sweep_tube(points=points, radius=.014, color=color))
    add(name,a)

for j, x in enumerate([-.48, .20, .94, 1.61]):
    tray("island tray "+str(j), x, -1.48, 1.155, .48, .36)
    if j == 0:
        for k in range(4):
            bowl("sorting cup", x-.15+k*.10, -1.48, 1.19, .036,
                 [(.66,.24,.15),(.84,.69,.26),
                  (.31,.49,.36),(.34,.44,.60)][k])
    elif j == 1:
        for k in range(3):
            cube("geometric block", (.075,.075,.09+k*.03),
                 (x-.13+k*.12,-1.47,1.23+k*.015), (.77,.61,.35))
    elif j == 2:
        add("white pitcher", rod(radius=.068,length=.16,
            center=(x,-1.48,1.28),color=(.87,.86,.73)))
        add("pitcher handle", sweep_tube(
            points=[(x+.04,-1.48,1.33),(x+.11,-1.48,1.33),
                    (x+.12,-1.48,1.25),(x+.05,-1.48,1.24)],
            radius=.014,color=(.87,.86,.73)))
        bowl("receiving bowl",x+.17,-1.47,1.19,.065)
    else:
        for k in range(5):
            add("upright cylinder",rod(radius=.025+k*.005,
                length=.09+k*.027,
                center=(x-.16+k*.08,-1.49,1.24+k*.0135),
                color=(.61,.40,.19)))

for z in [.15,.66]:
    for x in [-.40,.55,1.48]:
        tray("stored tray",x,-1.69,z,.61,.36)
        for k in range(3):
            cube("stored material",(.12,.16,.065),
                 (x-.18+k*.17,-1.70,z+.075),(.62,.45,.24))

for i,x in enumerate([-3.8,-2.9,-1.8,-.7,.5,1.6,2.6]):
    tray("window cabinet tray"+str(i),x,3.87,.885,.49,.30)
    for k in range(3):
        cube("back shelf material",(.07,.09,.08+.025*k),
             (x-.13+k*.12,3.88,.965+.013*k),
             [(.69,.48,.23),(.61,.25,.15),(.62,.66,.43)][k])

def table(name,x,y,w=1.36,d=.80,h=.69):
    a=Asset(name)
    a.include("top",box((w,d,.075),center=(x,y,h),color=edgewood))
    for i,xx in enumerate([-w/2+.10,w/2-.10]):
        for j,yy in enumerate([-d/2+.10,d/2-.10]):
            a.include("leg%d%d"%(i,j),box((.065,.065,h-.04),
                center=(x+xx,y+yy,(h-.04)/2),color=wood))
    a.include("apron",box((w-.12,.06,.15),
        center=(x,y-d/2+.07,h-.10),color=lightwood))
    add(name,a)

def stool(name,x,y):
    a=Asset(name)
    a.include("seat",box((.37,.36,.055),center=(x,y,.36),color=edgewood))
    for i,dx in enumerate([-.13,.13]):
        for j,dy in enumerate([-.12,.12]):
            a.include("leg%d%d"%(i,j),box((.045,.045,.34),
                center=(x+dx,y+dy,.17),color=wood))
    add(name,a)

table("central activity table",.15,1.60,1.65,.90)
stool("central stool left",-.94,1.55)
stool("central stool right",1.25,1.59)
stool("central rear stool",.17,2.27)
table("rear right work table",2.72,2.37,1.12,.72)
stool("rear table stool",2.67,1.71)
table("left work table",-2.52,2.79,1.05,.72)
stool("left work stool",-2.51,2.17)
tray("table work",.20,1.62,.73,.54,.33)
for k in range(5):
    cube("table puzzle",(.07,.07,.04),
         (-.01+k*.10,1.62,.79),(.69,.42,.23))

def chair(name,x,y,angle=0):
    a=Asset(name)
    a.include("seat",box((.43,.43,.06),center=(0,0,.39),color=lightwood))
    for i,xx in enumerate([-.16,.16]):
        for j,yy in enumerate([-.16,.16]):
            a.include("leg%d%d"%(i,j),box((.055,.055,.39),
                center=(xx,yy,.195),color=wood))
    for i,xx in enumerate([-.17,.17]):
        a.include("back post%d"%i,box((.05,.05,.70),
            center=(xx,.18,.36),color=wood))
    a.include("backrest",box((.38,.055,.19),
        center=(0,.18,.65),color=lightwood))
    a.turn('z',angle,pivot=(0,0,0))
    a.move((x,y,0))
    add(name,a)

chair("chair by island",2.35,-1.18,-17)
chair("distant chair",3.54,2.75)
for i in range(7):
    cube("left storage box",(.31,.35,.18),
         (-3.98,-1.8+i*.60,.25 if i%2 else .70),(.65,.48,.27))
for i in range(5):
    cube("upright book",(.045,.20,.24+random.random()*.06),
         (3.75+i*.055,1.72,1.08),
         [(.49,.24,.14),(.64,.62,.40),(.40,.48,.42)][i%3])

for x,y,z in [(-3.95,3.90,.94),(3.,3.90,.94),(-3.98,.8,1.08)]:
    add("plant pot",rod(radius=.105,length=.16,
        center=(x,y,z+.08),color=(.54,.30,.16)))
    for k in range(5):
        a=k*2.4
        add("plant leaves",ball(.10,
            center=(x+math.cos(a)*.10,y+math.sin(a)*.07,z+.25+k*.018),
            color=(.27,.40,.18)))

cube("framed wall picture",(.45,.045,.56),(3.93,4.51,2.55),lightwood)
cube("picture paper",(.36,.022,.47),(3.93,4.47,2.55),(.88,.85,.70))
cube("picture center",(.20,.015,.22),(3.93,4.45,2.57),(.46,.54,.40))

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if not bs:
        continue
    bs.inputs["Roughness"].default_value=.76
    c=bs.inputs["Base Color"].default_value
    if c[0]>c[1]*1.12 and c[1]>c[2]*1.20:
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
        bump.inputs["Strength"].default_value=.09
        bump.inputs["Distance"].default_value=.018
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bs.inputs["Normal"])

set_view((6.6,-10.4,5.0),(-.15,1.05,1.05),lens=40,sensor=36)
area_emitter((-1.3,3.8,4.5),power=1250,size=5.5,
             target=(0,-1,0),color=(1.,.94,.80))
area_emitter((1,-3,6),power=650,size=6,
             target=(0,1,.2),color=(1.,.97,.90))

sc=bpy.context.scene
world=sc.world
if world is None:
    world=bpy.data.worlds.new("Classroom daylight world")
    sc.world=world
world.use_nodes=True
background=world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value=(.72,.79,.86,1)
background.inputs["Strength"].default_value=.45
sc.render.engine='CYCLES'
sc.cycles.samples=64
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.render.resolution_x=1920
sc.render.resolution_y=1080
sc.render.resolution_percentage=100
