from sceneact import *
import bpy
import math
import random

random.seed(18)
scene = Scene("Montessori classroom")
wood = (.53, .35, .17)
lightwood = (.64, .46, .24)
edgewood = (.71, .53, .29)
cream = (.78, .77, .65)
darkwood = (.34, .23, .11)

def add(name, node):
    scene.include(name, node)
    return node

def cube(name, size, center, color):
    return add(name, box(size, center=center, color=color))

# Full-size architecture extends beyond the camera frame.
cube("floor", (9.4, 11.5, .15), (0, -.8, -.075), (.49, .34, .20))
cube("back wall", (9.4, .18, 3.65), (0, 4.65, 1.825), cream)
cube("left wall", (.16, 11.4, 3.65), (-4.65, -.8, 1.825), cream)
cube("right wall", (.16, 11.4, 3.65), (4.65, -.8, 1.825), cream)
cube("ceiling", (9.4, 11.4, .12), (0, -.8, 3.72), (.85, .84, .75))
cube("back skirting", (9.2, .06, .13), (0, 4.53, .065), lightwood)
cube("left skirting", (.06, 11.2, .13), (-4.53, -.8, .065), lightwood)

for i in range(39):
    x = -4.56 + i*.24
    for j in range(7):
        y = -5.75+j*1.64+(.38 if i%2 else 0)
        if y > 4.6:
            continue
        v = random.uniform(-.025, .025)
        cube("floorboard", (.237, 1.631, .015), (x, y, .009),
             (.51+v, .365+v, .22+v))

# Large windows with quiet, layered exterior greenery.
for i, x in enumerate([-3.70, -2.14, -.58, .98, 2.54]):
    cube("window sky", (1.31, .035, 2.02), (x, 4.535, 2.27),
         (.63, .74, .73))
    for k in range(12):
        xx = x+random.uniform(-.57, .57)
        zz = random.uniform(1.35, 3.20)
        add("exterior foliage", ball(random.uniform(.08, .23),
            center=(xx, 4.49, zz),
            color=random.choice([(.27,.39,.20), (.39,.48,.25),
                                 (.50,.56,.34), (.35,.46,.30)])))
    for k in range(2):
        xx = x-.35+k*.66
        add("distant tree trunk", rod(radius=.022,
            start=(xx,4.455,1.30), end=(xx+.12,4.455,3.23),
            color=(.43,.43,.33)))
    for dx in [-.66, .66]:
        cube("window upright", (.072, .14, 2.10),
             (x+dx, 4.39, 2.27), (.84, .85, .76))
    for z in [1.23, 3.31]:
        cube("window horizontal frame", (1.39, .14, .075),
             (x, 4.39, z), (.85, .85, .77))
    cube("window mullion", (.043, .08, 2.02),
         (x+.20, 4.36, 2.27), (.82, .84, .76))
    cube("window crossbar", (1.29, .08, .043),
         (x, 4.35, 2.17), (.83, .84, .76))
    cube("window sill", (1.48, .34, .075),
         (x, 4.30, 1.20), edgewood)

def shelf(name, x, y, width=2.1, depth=.65, height=1.05,
          angle=0, columns=3, levels=2):
    a = Asset(name)
    def panel(n, size, pos, col=lightwood):
        a.include(n, box(size, center=pos, color=col))
    panel("back", (width, .045, height-.10),
          (0, depth/2-.025, height/2), wood)
    for i, xx in enumerate([-width/2+.035, width/2-.035]):
        panel("side%d"%i, (.07,depth,height), (xx,0,height/2))
    for j in range(levels+1):
        zz=.11+j*(height-.15)/levels
        panel("shelf%d"%j, (width,depth,.065), (0,0,zz), edgewood)
    for j in range(1,columns):
        xx=-width/2+width*j/columns
        panel("divider%d"%j, (.045,depth-.05,height-.15),
              (xx,0,height/2+.025))
    for i,xx in enumerate([-width/2+.12,width/2-.12]):
        for j,yy in enumerate([-depth/2+.10,depth/2-.10]):
            panel("foot%d%d"%(i,j),(.10,.10,.12),(xx,yy,.06),darkwood)
    a.turn('z',angle,pivot=(0,0,0))
    a.move((x,y,0))
    add(name,a)
    return a

shelf("back left cabinet",-3.05,3.91,2.35,.58,.89,columns=3)
shelf("back middle cabinet",-.53,3.91,2.35,.58,.89,columns=4)
shelf("back right cabinet",2.02,3.91,2.35,.58,.89,columns=3)
shelf("left rear shelves",-4.04,1.65,2.80,.66,1.03,angle=90,columns=4)
shelf("left foreground shelves",-3.95,-1.15,2.30,.66,1.04,angle=90)
shelf("left freestanding partition",-2.45,1.39,1.76,.65,.98)
shelf("right rear shelves",4.02,2.25,2.30,.58,.94,angle=-90)
shelf("right middle shelves",3.70,.05,1.47,.62,.96,angle=-90,columns=2)

add("round red rug",rod(radius=1.65,length=.018,
    center=(.75,-1.48,.027),color=(.32,.055,.035)))
add("rug inner field",rod(radius=1.51,length=.020,
    center=(.75,-1.48,.029),color=(.40,.10,.055)))
shelf("foreground material island",.65,-1.35,2.65,1.05,1.12)

def tray(name,x,y,z,w=.43,d=.30):
    cube(name+" base",(w,d,.025),(x,y,z+.0125),edgewood)
    for yy in [-d/2,d/2]:
        cube(name+" rim",(w,.022,.045),(x,y+yy,z+.035),lightwood)
    for xx in [-w/2,w/2]:
        cube(name+" end",(.022,d,.045),(x+xx,y,z+.035),lightwood)

def bowl(name,x,y,z,r=.07,col=(.71,.68,.49)):
    add(name+" base",rod(radius=r*.86,length=.025,
        center=(x,y,z+.0125),color=col))
    points=[(x+r*math.cos(k*math.tau/24),
             y+r*math.sin(k*math.tau/24),z+.05) for k in range(25)]
    add(name+" rim",sweep_tube(points=points,radius=.013,color=col))

for j,x in enumerate([-.32,.32,.98,1.62]):
    tray("island activity",x,-1.34,1.112,.46,.35)
    if j==0:
        for k in range(4):
            bowl("sorting cup",x-.15+k*.10,-1.34,1.14,.035,
                 [(.52,.16,.08),(.68,.48,.13),
                  (.22,.38,.21),(.22,.32,.46)][k])
    elif j==1:
        for k in range(3):
            cube("geometric block",(.075,.075,.09+k*.03),
                 (x-.13+k*.12,-1.34,1.19+k*.015),(.66,.45,.21))
    elif j==2:
        add("small pitcher",rod(radius=.065,length=.16,
            center=(x,-1.34,1.23),color=(.82,.81,.69)))
        add("pitcher handle",sweep_tube(
            points=[(x+.04,-1.34,1.28),(x+.11,-1.34,1.28),
                    (x+.12,-1.34,1.20),(x+.05,-1.34,1.19)],
            radius=.014,color=(.82,.81,.69)))
        bowl("receiving bowl",x+.16,-1.34,1.145,.06)
    else:
        for k in range(5):
            h=.08+k*.025
            add("cylinder material",rod(radius=.023+k*.004,length=h,
                center=(x-.16+k*.08,-1.34,1.145+h/2),
                color=(.49,.29,.12)))

for z in [.15,.64]:
    for x in [-.22,.65,1.52]:
        tray("stored tray",x,-1.55,z,.58,.33)
        for k in range(3):
            cube("stored wood blocks",(.12,.14,.065),
                 (x-.17+k*.17,-1.55,z+.071),(.53,.35,.15))

for i,x in enumerate([-3.8,-2.9,-1.8,-.7,.5,1.6,2.6]):
    tray("back cabinet tray",x,3.87,.885,.49,.30)
    for k in range(3):
        cube("back material",(.07,.09,.08+.025*k),
             (x-.13+k*.12,3.88,.955+.013*k),
             [(.58,.37,.14),(.48,.17,.08),(.43,.48,.25)][k])
    for z in [.16,.54]:
        tray("back stored tray",x,3.76,z,.42,.30)

def table(name,x,y,w=1.36,d=.8,h=.69):
    a=Asset(name)
    a.include("top",box((w,d,.065),center=(x,y,h),color=edgewood))
    for i,xx in enumerate([-w/2+.10,w/2-.10]):
        for j,yy in enumerate([-d/2+.10,d/2-.10]):
            a.include("leg%d%d"%(i,j),box((.06,.06,h-.03),
                center=(x+xx,y+yy,(h-.03)/2),color=wood))
    a.include("apron",box((w-.12,.05,.12),
        center=(x,y-d/2+.07,h-.09),color=lightwood))
    add(name,a)

def stool(name,x,y):
    a=Asset(name)
    a.include("seat",box((.35,.34,.05),center=(x,y,.34),color=edgewood))
    for i,dx in enumerate([-.12,.12]):
        for j,dy in enumerate([-.11,.11]):
            a.include("leg%d%d"%(i,j),box((.042,.042,.32),
                center=(x+dx,y+dy,.16),color=wood))
    add(name,a)

table("central activity table",.15,1.60,1.65,.90)
stool("central left stool",-.94,1.55)
stool("central right stool",1.25,1.59)
stool("central rear stool",.17,2.27)
table("rear right table",2.72,2.37,1.12,.72)
stool("rear stool",2.67,1.71)
table("left work table",-2.52,2.79,1.05,.72)
stool("left work stool",-2.51,2.17)
tray("table work",.20,1.62,.725,.54,.33)
for k in range(5):
    cube("table puzzle",(.07,.07,.04),(-.01+k*.10,1.62,.78),(.57,.33,.14))

def chair(name,x,y,angle=0):
    a=Asset(name)
    a.include("seat",box((.43,.43,.055),center=(0,0,.37),color=lightwood))
    for i,xx in enumerate([-.16,.16]):
        for j,yy in enumerate([-.16,.16]):
            a.include("leg%d%d"%(i,j),box((.05,.05,.37),
                center=(xx,yy,.185),color=wood))
    for i,xx in enumerate([-.17,.17]):
        a.include("back post%d"%i,box((.045,.045,.70),
            center=(xx,.18,.35),color=wood))
    a.include("backrest",box((.38,.05,.18),
        center=(0,.18,.63),color=lightwood))
    a.turn('z',angle,pivot=(0,0,0))
    a.move((x,y,0))
    add(name,a)

chair("chair beside island",2.30,-1.15,-17)
chair("rear child chair",3.54,2.75)
for i in range(7):
    cube("side shelf box",(.31,.35,.18),
         (-3.98,-1.8+i*.60,.25 if i%2 else .70),(.53,.35,.16))
for i in range(5):
    cube("book",(.045,.20,.25+random.random()*.05),
         (3.75+i*.055,1.72,1.07),
         [(.40,.17,.08),(.49,.47,.27),(.26,.35,.27)][i%3])

for x,y,z in [(-3.95,3.90,.94),(3.,3.90,.94),(-3.98,.8,1.08)]:
    add("plant pot",rod(radius=.10,length=.15,
        center=(x,y,z+.075),color=(.45,.23,.11)))
    for k in range(6):
        a=k*2.4
        add("plant foliage",ball(.095,
            center=(x+math.cos(a)*.10,y+math.sin(a)*.07,z+.23+k*.018),
            color=(.19,.32,.10)))

cube("wall picture frame",(.45,.045,.56),(3.93,4.51,2.55),lightwood)
cube("wall picture paper",(.36,.025,.47),(3.93,4.475,2.55),(.83,.80,.64))
cube("picture motif",(.20,.015,.22),(3.93,4.452,2.57),(.34,.43,.26))

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if not bs:
        continue
    bs.inputs["Roughness"].default_value=.78
    c=bs.inputs["Base Color"].default_value
    if c[0]>c[1]*1.12 and c[1]>c[2]*1.20:
        nodes=mat.node_tree.nodes
        links=mat.node_tree.links
        coord=nodes.new("ShaderNodeTexCoord")
        mapping=nodes.new("ShaderNodeVectorMath")
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(3,48,5)
        tex=nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=4
        tex.inputs["Detail"].default_value=2
        links.new(coord.outputs["Generated"],mapping.inputs[0])
        links.new(mapping.outputs[0],tex.inputs["Vector"])
        bump=nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.08
        bump.inputs["Distance"].default_value=.012
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bs.inputs["Normal"])

# Interior corner viewpoint, cropping the room boundaries.
set_view((3.5,-5.5,2.75),(-.20,1.75,1.20),lens=27,sensor=36)
area_emitter((-1.3,4.05,3.05),power=700,size=4.5,
             target=(0,-1,.3),color=(1.,.94,.82))
area_emitter((.5,-3,3.35),power=160,size=4.5,
             target=(0,1,.5),color=(1.,.96,.87))

sc=bpy.context.scene
world=bpy.data.worlds.new("Soft daylight")
sc.world=world
world.use_nodes=True
background=world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value=(.70,.77,.83,1)
background.inputs["Strength"].default_value=.23
sc.render.engine='CYCLES'
sc.cycles.samples=64
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.15
sc.render.resolution_x=1920
sc.render.resolution_y=1080
sc.render.resolution_percentage=100
