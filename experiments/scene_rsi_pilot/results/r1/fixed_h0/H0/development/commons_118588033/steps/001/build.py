from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(8)

scene = Scene("Shipboard sleeping compartment")
cream=(.59,.59,.47)
wall=(.67,.68,.57)
iron=(.055,.073,.066)
green=(.065,.12,.105)
linen=(.66,.68,.60)
rust=(.31,.105,.057)

def add(name,node):
    scene.include(name,node)
    return node
def cube(name,size,pos,col):
    return add(name,box(size,center=pos,color=col))
def pipe(name,a,b,r=.025,col=cream):
    return add(name,rod(r,start=a,end=b,color=col))

# Painted steel compartment, with a deep, reddish deck.
cube("red brown deck",(4.2,10,.16),(0,4,-.08),(.29,.105,.064))
cube("port bulkhead",(.16,10,3.35),(-2.03,4,1.64),wall)
cube("starboard bulkhead",(.16,10,3.35),(2.03,4,1.64),(.71,.71,.60))
cube("aft bulkhead",(4.2,.16,3.35),(0,8.6,1.64),(.56,.59,.51))
cube("overhead",(4.2,10,.16),(0,4,3.35),(.39,.37,.28))
for y in [-.3,1.8,4.1,6.5,8.3]:
    cube("overhead transverse beam"+str(y),(4.1,.18,.28),(0,y,3.18),(.40,.29,.19))
for x in [-1.6,-.9,.1,1.25]:
    cube("longitudinal ceiling beam"+str(x),(.10,9.8,.19),(x,4,3.17),(.45,.38,.27))
for x in [-2.0,2.0]:
    cube("deck edge skirting"+str(x),(.05,9.5,.15),(x,4,.1),rust)

# Main support stanchion, cream above and red oxide below.
pipe("stanchion lower",(.83,1.82,.05),(.83,1.82,1.52),.105,(.28,.105,.055))
pipe("stanchion upper",(.83,1.82,1.52),(.83,1.82,3.4),.105,(.62,.47,.28))
pipe("stanchion foot",(.83,1.82,.01),(.83,1.82,.055),.14,(.39,.23,.13))
pipe("stanchion joint ring",(.83,1.82,1.5),(.83,1.82,1.55),.111,(.69,.61,.43))

# Port side three-tier pipe bunks.
for by in [1.35,3.65,5.95]:
    for x in [-1.88,-.80]:
        pipe("bunk upright", (x,by-1.07,.16),(x,by-1.07,2.50),.026,iron)
    for level,z in enumerate([.48,1.02,1.57]):
        cube("bunk dark support",(1.03,2.07,.065),(-1.36,by,z),iron)
        cube("rounded mattress",(1.00,2.04,.105),(-1.36,by,z+.08),linen)
        pillow=fillet_box((.72,.43,.14),radius=.065,center=(-1.37,by+.69,z+.17),color=(.72,.74,.66))
        add("bunk pillow",pillow)
        cube("folded pale blanket",(.98,.76,.035),(-1.36,by-.56,z+.151),(.57,.61,.55))
        pipe("outer bed edge",(-.82,by-1.02,z+.025),(-.82,by+1.02,z+.025),.025,iron)
        pipe("short end rail",(-1.88,by-1.04,z+.19),(-.80,by-1.04,z+.19),.018,iron)
    # Small brackets and bed fasteners.
    for z in [.47,1.01,1.56]:
        cube("bed mounting bracket",(.09,.09,.17),(-.80,by-1.07,z),(.12,.14,.12))

# Foreground locker and louvered cabinet faces.
for y in [.18,.82]:
    cube("green storage locker",(.48,.59,1.08),(-1.73,y,.91),(.095,.15,.135))
    cube("locker face",(.035,.54,1.00),(-1.475,y,.92),(.14,.20,.18))
    for i in range(17):
        z=.51+i*.045
        cube("locker ventilation black gap",(.015,.39,.016),(-1.451,y,z),(.035,.057,.05))
        cube("locker louver highlight",(.019,.39,.008),(-1.44,y,z+.009),(.25,.30,.26))
    cube("locker door handle",(.045,.035,.13),(-1.425,y-.21,1.13),(.50,.51,.42))
cube("long green bench along port",(.63,4.2,.085),(-1.69,1.8,.36),(.035,.105,.083))
for y in [.1,1.8,3.5]:
    for x in [-1.9,-1.43]:
        pipe("port bench foot",(x,y,.02),(x,y,.34),.018,iron)

# Wall mounted ventilation unit.
cube("vent housing",(.27,.67,.74),(-1.81,1.65,2.28),(.62,.62,.51))
cube("vent dark inset",(.021,.52,.48),(-1.663,1.65,2.29),(.06,.075,.065))
for z in [2.07,2.17,2.27,2.37,2.47]:
    sl=cube("vent broad horizontal blade",(.055,.50,.042),(-1.635,1.65,z),(.56,.59,.51))
    sl.turn('y',-12)
for y in [2.6,4.5]:
    cube("wall junction box",(.13,.24,.26),(-1.9,y,1.95),(.40,.43,.36))
    pipe("conduit drop",(-1.91,y,2.06),(-1.91,y,2.86),.016,(.4,.43,.36))

# Rear bank of steel lockers.
for x in [-.42,.12,.66]:
    cube("rear steel locker",(.51,.62,1.89),(x,6.55,1.03),(.43,.48,.44))
    cube("locker door recessed border",(.46,.019,1.77),(x,6.228,1.04),(.48,.53,.48))
    for z in [1.53,1.61,1.69,1.77]:
        cube("rear locker vent",(.25,.018,.018),(x,6.211,z),(.22,.28,.25))
    for z in [.41,.49,.57]:
        cube("low locker vent",(.25,.018,.018),(x,6.211,z),(.24,.29,.26))
    cube("silver locker latch",(.028,.05,.14),(x+.15,6.19,1.05),(.66,.67,.57))
    cube("locker label",(.16,.025,.05),(x,6.19,1.40),(.68,.70,.60))
    pipe("locker foot",(x-.17,6.37,.0),(x-.17,6.37,.10),.025,iron)

# Aft pipes, rails, and little machinery.
for x in [.78,1.05,1.40]:
    pipe("rear vertical service pipe",(x,7.8,.15),(x,7.8,3.17),.035,(.24,.28,.23))
    pipe("rear service elbow",(x,7.8,3.17),(x-.38,7.8,3.17),.035,(.24,.28,.23))
cube("aft dark machinery",(.80,.65,.93),(1.34,7.7,.51),(.24,.29,.26))
for y in [4.95,6.15]:
    pipe("equipment cage upright",(.92,y,.08),(.92,y,2.67),.026,iron)
    pipe("equipment cage back upright",(1.65,y,.08),(1.65,y,2.67),.026,iron)
for z in [.15,1.15,1.67,2.64]:
    pipe("equipment cage crossbar",(.92,4.95,z),(.92,6.15,z),.025,iron)
    pipe("equipment cage width",(.92,4.95,z),(1.65,4.95,z),.025,iron)
cube("small gray work cabinet",(.85,.66,.91),(1.18,5.40,.49),(.25,.29,.26))
cube("work cabinet lid",(.94,.73,.055),(1.18,5.40,.98),(.35,.38,.31))
cube("cabinet door",(.70,.025,.69),(1.18,5.052,.48),(.29,.33,.29))
pipe("cabinet handle",(1.43,5.02,.65),(1.43,5.02,.76),.018,(.13,.15,.13))
for i in range(4):
    pipe("small metal container",(1.0+i*.15,5.50,1.01),(1.0+i*.15,5.50,1.15),.045,(.44,.44,.34))

# Pale chair visible between the bunks and work cabinet.
cx,cy=.04,5.20
cube("chair seat",(.47,.46,.075),(cx,cy,.50),(.46,.48,.39))
for x in [cx-.205,cx+.205]:
    for y in [cy-.19,cy+.19]:
        pipe("chair metal leg",(x,y,.04),(x,y,.49),.022,(.49,.49,.39))
    pipe("chair back frame",(x,cy+.19,.45),(x,cy+.26,1.06),.022,(.56,.57,.46))
cube("chair back",(.43,.075,.28),(cx,cy+.24,.90),(.57,.58,.47))
pipe("chair arm left",(cx-.24,cy-.18,.69),(cx-.24,cy+.2,.72),.024,(.55,.56,.45))
pipe("chair arm right",(cx+.24,cy-.18,.69),(cx+.24,cy+.2,.72),.024,(.55,.56,.45))

# Right bulkhead blackboard and red emergency telephone.
cube("blackboard frame",(.055,1.13,.77),(1.924,4.14,1.95),(.33,.33,.26))
cube("blackboard surface",(.018,1.035,.675),(1.887,4.14,1.95),(.19,.25,.23))
cube("telephone red wall case",(.16,.35,.59),(1.86,2.94,1.20),(.72,.045,.025))
add("rounded telephone top",fillet_box((.18,.36,.29),radius=.10,center=(1.845,2.94,1.49),color=(.78,.055,.028)))
cube("telephone label",(.016,.15,.12),(1.756,2.91,1.32),(.77,.66,.48))
pipe("telephone receiver top",(1.72,2.83,1.57),(1.72,3.02,1.57),.044,(.91,.24,.13))
pipe("telephone receiver lower",(1.72,2.83,1.41),(1.72,2.83,1.57),.043,(.88,.19,.10))
pipe("telephone cord",(1.74,2.94,1.16),(1.74,3.04,1.38),.012,(.19,.12,.075))
cube("wall paper notice",(.018,.50,.57),(1.93,1.78,1.88),(.78,.78,.67))
for i in range(7):
    cube("notice printed line",(.012,.30,.007),(1.915,1.78,2.04-i*.045),(.47,.49,.43))

# Near starboard bench entering the lower right corner.
cube("right bench seat",(.60,2.02,.075),(1.67,.10,.46),(.035,.105,.083))
for y in [-.68,.83]:
    for x in [1.43,1.91]:
        pipe("right bench legs",(x,y,.015),(x,y,.43),.023,iron)
pipe("right bench brace",(1.44,-.70,.17),(1.44,.87,.17),.018,iron)

# Overhead network of exposed cream and black plumbing.
for x,z in [(-1.65,2.88),(-1.12,2.91),(.32,3.00),(1.45,3.02)]:
    pipe("lengthwise overhead pipe",(x,-.7,z),(x,8.5,z),.040, (.60,.61,.49))
    for y in [1.0,3.4,5.7,7.8]:
        pipe("pipe coupling",(x,y-.045,z),(x,y+.045,z),.054,(.66,.66,.54))
for y in [1.0,3.7,6.3]:
    pipe("black overhead transverse",(-1.85,y,2.73),(1.7,y,2.73),.024,iron)
pipe("cream diagonal downpipe",(-1.15,-.5,3.30),(-1.15,1.65,2.75),.045,(.72,.71,.58))
pipe("bend toward wall",(-1.15,1.65,2.75),(-1.82,1.65,2.75),.045,(.72,.71,.58))
for y in [.1,2.4,4.8]:
    pipe("ceiling pipe hanger",(-.68,y,2.84),(-.68,y,3.27),.016,(.64,.62,.49))
    pipe("thin white utility pipe",(-1.85,y,2.91),(-.62,y,2.91),.024,(.76,.77,.65))
pipe("rear black drop",(.49,6.1,1.86),(.49,6.1,2.85),.027,iron)
pipe("rear black top run",(.49,6.1,2.85),(-1.4,6.1,2.85),.027,iron)

# Enamel pendant lamps made from separate rounded shade elements.
lamp_positions=[(-.65,.45,2.82),(-.45,3.65,2.81),(-.32,6.10,2.77)]
for i,(x,y,z) in enumerate(lamp_positions):
    pipe("pendant stem",(x,y,z+.07),(x,y,3.30),.020,(.24,.26,.23))
    shade=ball(.25,center=(x,y,z),color=(.28,.31,.27))
    shade.resize((1,1,.32))
    add("gray enamel lamp shade",shade)
    pipe("shade lower lip",(x,y,z-.035),(x,y,z-.015),.252,(.62,.65,.58))
    pipe("white luminous lamp underside",(x,y,z-.047),(x,y,z-.036),.222,(.96,.98,.87))

realize(scene)
set_view((.48,-2.32,1.67),(-.02,5.5,1.69),lens=25.5,sensor=36)

# Soft, localized overhead illumination.
for x,y,z in lamp_positions:
    area_emitter((x,y,z-.09),power=105,size=.53,target=(x,y,.2),color=(.91,1.0,.92))
area_emitter((.1,-1.8,2.65),power=170,size=3,target=(0,3,1.1),color=(1,.84,.65))
area_emitter((.3,6.8,2.8),power=85,size=1.7,target=(0,4,1),color=(.88,.97,.88))
for mat in bpy.data.materials:
    if mat.use_nodes:
        bs=mat.node_tree.nodes.get("Principled BSDF")
        if bs:
            bs.inputs["Roughness"].default_value=.69
            c=bs.inputs["Base Color"].default_value
            if c[0]>.9 and c[1]>.9:
                bs.inputs["Emission Color"].default_value=(.83,1.0,.87,1)
                bs.inputs["Emission Strength"].default_value=3
# Slightly uneven painted steel deck.
for ob in bpy.data.objects:
    if "red brown deck" in ob.name.lower() and ob.type=="MESH":
        for mat in ob.data.materials:
            mat.use_nodes=True
            nt=mat.node_tree
            bs=nt.nodes.get("Principled BSDF")
            noise=nt.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value=65
            bump=nt.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value=.13
            bump.inputs["Distance"].default_value=.025
            nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
            nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
            bs.inputs["Roughness"].default_value=.38

world=bpy.context.scene.world
world.color=(.10,.11,.085)
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
