# Reference inventory (normalized image coordinates, approximate):
# Foreground folding bench: (.07,.33)-(.91,.98). Long tan dog-hole top,
# pale apron, yellow blocks, splayed plywood legs, blue front vise, handle,
# hanging clamps, perforated end panels and two upright stops.
# Rear workbench: (0,.23)-(.88,.70). Honey-colored top, dark front densely
# covered in irregular pale log cross sections; foreground bench occludes it.
# On rear bench: track saw and rail (.05,.27)-(.23,.38), blue drill press
# (.27,.20)-(.37,.36), CNC router (.46,.16)-(.84,.32), task lamp.
# Background: lumber shelving (0,0)-(.43,.30), dark stove and metal wall
# behind CNC, right-hand clamps and shelves (.79,0)-(1,.35). Concrete floor.
# Back and lower portions of equipment, shelving and stove are uncertain.
#
# Comparison with the first render: the whole scene was much too small in
# frame, the camera looked from the opposite end of the long benches, and
# empty room boundaries were visible. The revised camera moves closer and
# to the other side. Foreground top, leg structure and vise are emphasized;
# the existing equipment layout and log mosaic remain.
# Approximate primitive count: 440: architecture 30, log bench 193,
# foreground bench 120, machines and lamp 50, background storage 47.
# Each box or rod is one primitive; no fillets, sweeps or booleans.

from sceneact import *
import bpy
import random

random.seed(11)
scene = Scene("Woodworking shop")

ply = (0.79, 0.77, 0.69)
ply_light = (0.90, 0.88, 0.80)
edge = (0.56, 0.43, 0.29)
hardboard = (0.59, 0.39, 0.23)
benchwood = (0.66, 0.39, 0.16)
black = (0.055, 0.06, 0.058)
steel = (0.37, 0.39, 0.37)
blue = (0.025, 0.21, 0.42)
yellow = (0.95, 0.62, 0.025)
red = (0.48, 0.055, 0.035)
logcolors = [(0.66,0.52,0.35), (0.75,0.64,0.46),
             (0.52,0.39,0.27), (0.83,0.73,0.56)]

def B(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

def R(asset, name, radius, start, end, color):
    asset.include(name, rod(radius=radius, start=start, end=end, color=color))

architecture = Asset("Architecture")
B(architecture, "concrete floor", (30,30,.12), (0,1,-.07), (.34,.34,.32))
B(architecture, "rear wall", (30,.12,7), (0,4.0,3.4), (.20,.19,.17))
B(architecture, "corrugated backing", (3.8,.035,3.5), (.9,3.91,2.7), (.25,.27,.26))
for i in range(26):
    x = -.95 + i*.15
    B(architecture, "wall rib %02d"%i, (.018,.025,3.5),
      (x,3.875,2.7), (.13,.15,.14))
scene.include("architecture", architecture)

rear = Asset("Rear log faced workbench")
B(rear, "worktop", (6.8,1.05,.12), (-.45,2.18,1.22), benchwood)
B(rear, "front dark substrate", (6.8,.10,1.16), (-.45,1.70,.60), (.12,.085,.055))
B(rear, "front top edging", (6.8,.06,.07), (-.45,1.63,1.18), (.33,.21,.12))
for row in range(5):
    for col in range(19):
        x = -3.50 + col*.34 + (row%2)*.16 + random.uniform(-.025,.025)
        z = .12 + row*.235 + random.uniform(-.025,.025)
        rad = random.uniform(.075,.14)
        R(rear, "log bark %d %d"%(row,col), rad,
          (x,1.625,z), (x,1.59,z), (.16,.105,.06))
        R(rear, "log end %d %d"%(row,col), rad*.78,
          (x,1.585,z), (x,1.57,z), random.choice(logcolors))
scene.include("rear workbench", rear)

hero = Asset("Folding birch plywood workbench")
B(hero, "hardboard top", (3.72,1.08,.095), (0,-.48,1.05), hardboard)
B(hero, "front laminated edge", (3.72,.025,.085), (0,-1.032,1.045), edge)
B(hero, "front apron", (3.36,.10,.28), (0,-.87,.86), ply_light)
B(hero, "rear apron", (3.36,.10,.24), (0,-.08,.87), ply)
B(hero, "left end frame", (.12,.90,.24), (-1.65,-.48,.88), ply_light)
B(hero, "right end frame", (.12,.90,.24), (1.65,-.48,.88), ply_light)
for side in (-1,1):
    for y in (-.84,-.10):
        leg = box(size=(.27,.12,1.05), center=(side*1.48,y,.48), color=ply_light)
        leg.turn(axis="y", degrees=side*9)
        hero.include("splayed leg %s %s"%(side,y), leg)
    B(hero, "end perforated panel %s"%side, (.62,.07,.54),
      (side*1.44,-.09,.46), ply)
    for j in range(5):
        z = .24+j*.105
        R(hero, "front leg hole %s %s"%(side,j), .018,
          (side*(1.52+(0.5-z)*.14),-.906,z),
          (side*(1.52+(0.5-z)*.14),-.92,z), (.24,.22,.18))
    for j in range(4):
        for k in range(3):
            x = side*1.24 + side*k*.12
            z = .26+j*.11
            R(hero, "end panel hole %s %s %s"%(side,j,k), .014,
              (x,-.13,z), (x,-.145,z), (.30,.27,.21))
for i in range(14):
    x = -1.45+i*.225
    R(hero, "apron dog hole %02d"%i, .016,
      (x,-.927,.87),(x,-.945,.87),(.27,.25,.20))
for i in range(12):
    for j in range(4):
        x = -1.58+i*.285
        y = -.85+j*.23
        R(hero, "top dog hole %d %d"%(i,j), .012,
          (x,y,1.099),(x,y,1.105),(.28,.19,.12))
for i,x in enumerate((-1.35,-1.17,-.29,.60)):
    B(hero, "yellow bench block %d"%i, (.13,.18,.18), (x,-.68,.88), yellow)
B(hero, "vise wooden jaw", (.56,.10,.15), (-1.03,-1.07,.91), ply_light)
B(hero, "blue vise plate", (.42,.045,.11), (-1.03,-1.14,.91), blue)
for x in (-1.17,-.90):
    R(hero, "vise bolt %s"%x, .027, (x,-1.17,.91),(x,-1.20,.91), steel)
R(hero, "vise screw", .026, (-1.03,-1.17,.91),(-1.03,-1.33,.91), steel)
R(hero, "vise handle", .022, (-1.32,-1.35,1.10),(-.74,-1.35,.70), steel)
R(hero, "vise handle red end", .035, (-.78,-1.35,.73),(-.71,-1.35,.68), red)
for i in range(3):
    x = -1.77+i*.095
    R(hero, "hanging clamp bar %d"%i, .015,(x,-.73,.18),(x,-.73,.80),steel)
    B(hero, "clamp head %d"%i, (.09,.08,.07),(x,-.73,.76),red if i==0 else black)
    B(hero, "clamp handle %d"%i, (.07,.07,.14),(x,-.73,.29),(.95,.32,.035))
for i in range(2):
    R(hero, "bench stop %d"%i, .012,
      (1.61+i*.10,-.18,1.07),(1.61+i*.10,-.18,1.43),(.73,.66,.50))
scene.include("foreground folding bench", hero)

saw = Asset("Track saw and rail")
B(saw,"guide rail",(1.62,.10,.025),(-2.15,1.97,1.30),(.66,.69,.66))
B(saw,"saw base",(.55,.31,.045),(-2.40,1.98,1.34),(.42,.44,.42))
B(saw,"saw motor body",(.31,.24,.24),(-2.41,1.98,1.48),(.67,.70,.68))
B(saw,"black saw motor",(.17,.20,.20),(-2.23,1.98,1.48),(.16,.18,.17))
R(saw,"handle left",.025,(-2.54,1.99,1.53),(-2.52,1.99,1.70),black)
R(saw,"handle top",.025,(-2.52,1.99,1.70),(-2.34,1.99,1.70),black)
R(saw,"handle right",.025,(-2.34,1.99,1.70),(-2.30,1.99,1.57),black)
scene.include("track saw",saw)

drill = Asset("Blue drill press")
B(drill,"base",(.43,.32,.05),(-1.20,2.07,1.32),blue)
R(drill,"column",.035,(-1.20,2.12,1.34),(-1.20,2.12,1.98),steel)
B(drill,"drill table",(.30,.24,.035),(-1.20,2.05,1.56),blue)
B(drill,"head housing",(.32,.22,.16),(-1.20,2.09,1.93),blue)
B(drill,"black motor",(.14,.19,.19),(-1.20,2.22,1.96),black)
R(drill,"chuck",.035,(-1.20,2.02,1.82),(-1.20,2.02,1.70),steel)
R(drill,"bit",.009,(-1.20,2.02,1.70),(-1.20,2.02,1.60),steel)
R(drill,"feed handle",.012,(-1.04,2.07,1.92),(-.92,2.07,2.05),black)
scene.include("drill press",drill)

cnc = Asset("CNC gantry router")
B(cnc,"black machine base",(1.85,.78,.12),(.90,2.20,1.35),black)
B(cnc,"pale spoilboard",(1.42,.62,.055),(.93,2.18,1.43),(.72,.63,.48))
for y in (1.86,2.53):
    B(cnc,"side rail %s"%y,(1.9,.075,.10),(.90,y,1.47),(.20,.21,.20))
for x in (.25,1.50):
    B(cnc,"gantry upright %s"%x,(.09,.09,.46),(x,2.25,1.67),black)
B(cnc,"gantry beam",(1.45,.11,.14),(.875,2.25,1.88),(.60,.62,.59))
B(cnc,"gantry dark rail",(1.43,.05,.05),(.875,2.18,1.88),black)
B(cnc,"router carriage",(.23,.16,.25),(.94,2.15,1.73),(.18,.19,.18))
R(cnc,"router spindle",.07,(.94,2.05,1.48),(.94,2.05,1.77),(.25,.25,.23))
B(cnc,"yellow router cap",(.17,.15,.08),(.94,2.05,1.80),yellow)
R(cnc,"router bit",.012,(.94,2.05,1.42),(.94,2.05,1.50),steel)
B(cnc,"controller box",(.45,.28,.26),(2.13,2.43,1.46),black)
scene.include("CNC router",cnc)

lamp = Asset("Articulated task lamp")
R(lamp,"lamp stem",.015,(-.66,2.42,1.28),(-.66,2.42,1.85),steel)
R(lamp,"lower arm",.015,(-.66,2.42,1.85),(-.45,2.42,2.18),steel)
R(lamp,"upper arm",.015,(-.45,2.42,2.18),(-.13,2.42,2.29),steel)
R(lamp,"shade",.10,(-.13,2.42,2.23),(-.13,2.42,2.33),(.70,.68,.58))
scene.include("work lamp",lamp)

rack = Asset("Wall lumber rack")
for z in (1.55,2.12,2.68,3.18):
    B(rack,"shelf %s"%z,(2.85,.52,.065),(-2.42,3.57,z),(.15,.11,.08))
for x in (-3.65,-2.72,-1.65,-1.06):
    B(rack,"rack upright %s"%x,(.065,.07,2.8),(x,3.80,2.05),(.10,.09,.08))
for row in range(4):
    for i in range(5):
        x = -2.50 + random.uniform(-.30,.30)
        z = 1.62+row*.54+i*.06
        length = random.uniform(1.65,2.65)
        B(rack,"stored board %d %d"%(row,i),(length,.24,.055),
          (x,3.48-random.uniform(0,.16),z),
          random.choice([(0.48,.29,.14),(.64,.42,.23),(.36,.22,.12)]))
scene.include("lumber rack",rack)

stove = Asset("Cast iron stove")
B(stove,"stove body",(.65,.52,.76),(-.22,3.36,1.03),(.10,.105,.10))
B(stove,"stove top",(.76,.60,.075),(-.22,3.36,1.45),(.08,.085,.08))
B(stove,"fire door",(.40,.035,.40),(-.22,3.08,1.03),(.16,.16,.15))
R(stove,"stove flue",.13,(-.22,3.40,1.49),(-.22,3.40,3.55),(.11,.11,.10))
scene.include("stove",stove)

storage = Asset("Right wall storage")
for z in (.75,1.35,1.95,2.55):
    B(storage,"shelf %s"%z,(1.45,.48,.06),(3.48,3.52,z),(.16,.14,.11))
for x in (2.79,4.17):
    B(storage,"upright %s"%x,(.07,.07,2.6),(x,3.70,1.55),(.12,.12,.11))
for i in range(7):
    x = 2.91+i*.18
    B(storage,"red parts bin %d"%i,(.15,.25,.13),(x,3.35,2.04),(.43,.08,.045))
for i in range(9):
    x = 2.65+i*.10
    R(storage,"upright stock %d"%i,.018,(x,3.05,1.25),(x,3.05,2.84),(.22,.22,.20))
    if i%2 == 0:
        B(storage,"clamp jaw %d"%i,(.10,.08,.09),(x,3.05,2.28),black)
scene.include("wall storage",storage)

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
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.29,0.27,0.23,1)
background.inputs["Strength"].default_value = .28

set_view((-4.4,-7.3,3.65), (0,.72,1.25), lens=50)
area_emitter((0,-3,6), power=1000, size=5, target=(0,1,0.8), color=(1.0,.85,.68))
area_emitter((-3,1,4.5), power=650, size=3.5, target=(-1,2,1), color=(1.0,.76,.53))
area_emitter((3,3,4.5), power=400, size=3, target=(1,2,1), color=(.82,.87,1.0))
area_emitter((-.13,2.35,2.24), power=40, size=.25, target=(.1,2,1.2), color=(1,.82,.57))
