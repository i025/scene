from sceneact import *
import bpy
import math
import random

random.seed(11)
scene = Scene("Historic workshop display")

ivory = (.64, .62, .46)
panel = (.69, .70, .57)
iron = (.105, .105, .078)
edge = (.18, .17, .125)
rust = (.23, .20, .135)
steel = (.32, .31, .24)
door_red = (.48, .19, .105)

def block(name, size, center, color):
    scene.include(name, box(size=size, center=center, color=color))

def bar(name, a, b, r=.012, color=iron):
    scene.include(name, rod(radius=r, start=a, end=b, color=color))

def disk(name, x, y, z, radius, thickness, color=iron):
    bar(name, (x,y-thickness/2,z), (x,y+thickness/2,z), radius, color)

def ring(name, x, y, z, radius, tube=.012, color=iron, segments=48):
    for i in range(segments):
        a = 2*math.pi*i/segments
        b = 2*math.pi*(i+1)/segments
        bar(name+str(i),
            (x+radius*math.cos(a),y,z+radius*math.sin(a)),
            (x+radius*math.cos(b),y,z+radius*math.sin(b)),tube,color)

def flatbar(name, x,y,z, length,width, angle, color=iron, depth=.018):
    node = box((width,depth,length),center=(x,y,z),color=color)
    node.turn('y',angle)
    scene.include(name,node)

# The plaster pier and the room beyond it.
block("stone floor",(10,9,.12),(0,2,-.065),(.43,.45,.40))
block("display pier",(2.78,.28,3.54),(-.55,.16,1.77),ivory)
block("right edge plaster",( .105,.40,3.53),(.855,.19,1.765),(.72,.70,.54))
block("upper plaster molding",(2.83,.38,.15),(-.55,.09,3.45),(.72,.69,.50))
block("plaster header seam",(2.83,.022,.015),(-.55,-.075,3.36),(.36,.34,.23))
block("rear wall",(4,.23,3.65),(2.6,1.50,1.825),(.72,.72,.59))
block("rear lower sill",(2.6,.32,.15),(1.9,1.29,1.15),(.75,.74,.64))

# Painted wooden door, partially cut off by the photograph.
block("door dark recess",(.91,.075,3.37),(-1.38,-.012,1.69),(.20,.13,.075))
block("red door",(.79,.06,3.29),(-1.40,-.067,1.65),door_red)
for x in (-1.76,-1.05):
    block("door vertical stile"+str(x),(.055,.035,3.27),(x,-.111,1.66),(.53,.225,.13))
for z in (.12,1.05,1.90,3.20):
    block("door rail"+str(z),(.70,.035,.075),(-1.40,-.112,z),(.54,.23,.14))
for z,h in ((.57,.73),(1.48,.65),(2.55,1.13)):
    block("recessed door panel"+str(z),(.54,.016,h),(-1.40,-.103,z),(.45,.17,.095))
    for x in (-1.69,-1.11):
        block("panel bead"+str((x,z)),(.018,.018,h+.06),(x,-.129,z),(.60,.27,.16))
    for zz in (z-h/2-.025,z+h/2+.025):
        block("panel horizontal bead"+str((z,zz)),(.59,.02,.019),(-1.40,-.129,zz),(.59,.26,.15))
block("door right jamb",(.065,.07,3.36),(-.98,-.06,1.68),(.37,.30,.17))

# Bright tall window in the adjoining room.
block("window dark surround",(1.27,.10,2.37),(1.65,1.335,2.33),(.16,.19,.16))
block("window pale glass",(1.08,.035,2.16),(1.65,1.265,2.33),(.77,.86,.84))
for x in (1.12,1.65,2.18):
    block("window frame"+str(x),(.055,.09,2.21),(x,1.218,2.33),(.20,.25,.23))
for z in (1.25,1.77,2.29,2.81,3.40):
    block("window crosspiece"+str(z),(1.13,.08,.035),(1.65,1.21,z),(.22,.27,.24))
block("window middle slender mullion",(.022,.04,2.15),(1.39,1.19,2.33),(.20,.24,.22))
block("window sill",(1.45,.42,.09),(1.65,1.13,1.18),(.48,.49,.39))

# Workbench visible through the opening.
block("bench top",(2.45,.67,.10),(1.91,.79,.93),(.34,.28,.20))
block("bench front apron",(2.39,.065,.18),(1.91,.445,.80),(.29,.24,.18))
block("bench lower shelf",(2.38,.59,.065),(1.91,.79,.46),(.37,.32,.25))
for x in (.87,2.85):
    for y in (.53,1.03):
        block("bench leg"+str((x,y)),(.085,.085,.90),(x,y,.46),(.26,.23,.18))
block("bench black rectangular recess",(.47,.02,.065),(1.55,.402,.80),(.055,.049,.035))

# Aged rectangular equipment board.
block("mounting board",(1.19,.057,1.99),(-.03,-.037,2.265),panel)
for x in (-.673,.612):
    block("heavy outer upright"+str(x),(.052,.065,2.13),(x,-.075,2.27),edge)
    block("inner upright highlight"+str(x),(.014,.018,2.04),(x+.016,-.116,2.27),(.30,.29,.22))
for z in (1.205,3.335):
    block("heavy horizontal frame"+str(z),(1.33,.065,.053),(-.03,-.076,z),edge)
for z in (1.25,3.29):
    block("thin inner horizontal frame"+str(z),(1.22,.017,.014),(-.03,-.119,z),(.32,.31,.23))
for x in (-.655,.594):
    for z in (1.245,3.29):
        disk("frame screw"+str((x,z)),x,-.118,z,.012,.009,(.12,.12,.09))

# Large five-spoke pulley at upper left.
wx,wz = -.412,3.045
ring("large pulley rim",wx,-.167,wz,.177,.016)
ring("large pulley inner edge",wx,-.171,wz,.153,.006,steel)
disk("large pulley hub",wx,-.181,wz,.036,.055,rust)
for i in range(5):
    a = .30+2*math.pi*i/5
    bar("pulley spoke"+str(i),(wx,-.181,wz),
        (wx+.163*math.cos(a),-.181,wz+.163*math.sin(a)),.014,iron)
disk("large pulley axle",wx,-.218,wz,.013,.018,steel)

# Four small cup-shaped pulleys along the top.
for i,(x,r) in enumerate(((-.075,.069),(.125,.057),(.307,.056),(.476,.050))):
    disk("small pulley back"+str(i),x,-.125,3.042,r,.031,rust)
    ring("small pulley raised lip"+str(i),x,-.164,3.042,r*.86,.009,iron,32)
    disk("small pulley inset"+str(i),x,-.172,3.042,r*.50,.009,(.28,.27,.19))
    disk("small pulley center"+str(i),x,-.187,3.042,.017,.024,iron)
    disk("small pulley bolt"+str(i),x,-.202,3.042,.008,.012,(.44,.42,.31))

# Rack of narrow horizontal tools.
block("long upper rack",(.96,.036,.037),(-.095,-.134,2.692),(.18,.16,.105))
for i,x in enumerate((-.54,-.31,-.085,.16,.39)):
    bar("rack screw"+str(i),(x,-.156,2.667),(x,-.156,2.720),.008,steel)
block("wide dark hanging blade",(.34,.025,.060),(.299,-.159,2.667),iron)
bar("right dangling pin",(.485,-.163,2.690),(.493,-.17,2.453),.009,iron)
bar("left rack extension",(-.606,-.142,2.691),(-.51,-.142,2.691),.009)

# Slender pointed tool below the rack.
bar("horizontal spindle",(-.386,-.164,2.278),(.151,-.164,2.278),.009,rust)
bar("spindle tip",(.151,-.164,2.278),(.196,-.164,2.285),.004,steel)
disk("spindle collar",-.11,-.167,2.278,.022,.038,steel)
bar("spindle vertical drop",(-.113,-.167,2.29),(-.112,-.167,2.15),.009,iron)
flatbar("spindle pointed pendant",-.085,-.16,2.22,.13,.012,-7,steel)
for i,x in enumerate((-.563,-.435,.24,.366)):
    block("small mounting block"+str(i),(.075,.026,.083),(x,-.13,2.169),iron)
bar("small left hook",(-.548,-.162,2.17),(-.56,-.18,2.10),.008,steel)

# Ring and pair of tongs on the lower half.
ring("hanging circular tool",-.492,-.171,1.754,.055,.012,rust,36)
bar("ring upper tang",(-.49,-.17,1.80),(-.475,-.17,1.84),.009,rust)
disk("tongs pivot",-.134,-.17,1.86,.022,.023,iron)
bar("tongs left handle",(-.139,-.174,1.85),(-.157,-.18,1.666),.014,iron)
bar("tongs right handle",(-.12,-.174,1.85),(-.077,-.18,1.70),.012,iron)
bar("tongs upper left jaw",(-.139,-.17,1.855),(-.159,-.17,1.905),.013,iron)
bar("tongs upper right jaw",(-.12,-.17,1.855),(-.096,-.17,1.914),.012,iron)

# Heavy cast-iron mechanism at lower right: base, arch, jaws and handles.
block("machine foot",(.40,.19,.055),(.297,-.20,1.365),iron)
block("machine base upper",(.30,.16,.055),(.297,-.21,1.409),rust)
for x in (.164,.431):
    bar("machine rising arch"+str(x),(x,-.232,1.43),(x+(.035 if x<.3 else -.035),-.232,1.585),.028,iron)
ring("machine arch",.298,-.235,1.526,.105,.025,iron,36)
block("arch lower opening cover",(.17,.055,.06),(.298,-.276,1.397),iron)
block("machine main body",(.22,.16,.13),(.305,-.226,1.704),iron)
block("machine side block",(.07,.12,.19),(.202,-.228,1.702),rust)
bar("machine central vertical shaft",(.313,-.202,1.74),(.313,-.202,2.045),.026,steel)
block("machine upper jaw",(.10,.11,.067),(.339,-.20,2.045),iron)
block("machine jaw backing",(.08,.07,.12),(.371,-.136,2.02),rust)
disk("machine face hub",.31,-.334,1.725,.063,.052,rust)
disk("machine face center",.31,-.371,1.725,.025,.022,iron)
bar("machine cross handle",(.115,-.352,1.64),(.486,-.352,1.827),.012,steel)
disk("machine handle knob",.486,-.352,1.827,.022,.038,iron)
bar("machine right lever",(.382,-.28,1.73),(.501,-.30,1.62),.016,iron)
bar("machine upright small lever",(.38,-.22,2.06),(.412,-.22,2.17),.013,iron)
disk("machine lever cap",.412,-.22,2.17,.021,.024,iron)

# Loose components resting on the bottom edge.
block("little bottom tray",(.17,.065,.025),(-.366,-.163,1.307),iron)
block("little tray lip",(.135,.015,.022),(-.366,-.197,1.328),rust)
bar("little left pin",(-.586,-.145,1.322),(-.553,-.175,1.345),.013,rust)

# Exterior straps and projecting pegs below the framed display.
block("middle wall iron strap",(1.48,.028,.11),(-.02,-.041,1.018),iron)
bar("left projecting peg",(-.352,-.064,1.032),(-.352,-.265,1.032),.024,steel)
bar("right projecting peg",(.364,-.064,1.023),(.364,-.258,1.023),.026,iron)
block("yellow exhibit label",(.228,.018,.151),(.015,-.084,1.102),(.68,.49,.08))
for i in range(5):
    block("faint label text"+str(i),(.155-.015*(i%2),.003,.003),(.015,-.095,1.145-i*.021),(.37,.29,.11))

# Two large circular chucks mounted near the floor.
block("lower mounting strap",(1.46,.035,.103),(-.005,-.045,.485),iron)
disk("left large chuck",-.356,-.135,.548,.268,.084,(.235,.218,.163))
ring("left chuck edge",-.356,-.181,.548,.254,.007,(.17,.16,.12))
disk("left chuck hub",-.356,-.198,.548,.047,.033,(.30,.29,.22))
for i in range(6):
    a = math.radians(13+i*60)
    x=-.356+.168*math.sin(a)
    z=.548+.168*math.cos(a)
    flatbar("left radial slot"+str(i),x,-.184,z,.113,.014,math.degrees(a),(.075,.075,.055),.009)
block("left chuck central square",(.047,.018,.059),(-.356,-.224,.548),(.41,.41,.32))
block("left chuck square hole",(.018,.008,.023),(-.356,-.237,.548),(.10,.11,.08))

disk("right large chuck",.348,-.139,.592,.243,.092,(.20,.19,.14))
ring("right chuck rim",.348,-.193,.592,.229,.008,rust)
disk("right chuck center",.348,-.22,.592,.069,.058,(.28,.27,.20))
for i in range(6):
    a=math.radians(i*60+12)
    x=.348+.159*math.sin(a)
    z=.592+.159*math.cos(a)
    flatbar("right chuck radial recess"+str(i),x,-.196,z,.125,.025,math.degrees(a),(.085,.083,.058),.012)
    jaw=box((.064,.088,.103),center=(x,-.239,z),color=(.23,.23,.18))
    jaw.turn('y',math.degrees(a)+25)
    scene.include("right chuck jaw"+str(i),jaw)
disk("chuck center bolt",.348,-.267,.592,.025,.027,steel)
bar("lower hanging shaft",(.349,-.09,.37),(.349,-.09,.102),.018,steel)
ring("shaft lower collar",.349,-.095,.19,.026,.008,rust,24)
bar("floor wall bracket",(.18,-.075,.071),(.56,-.075,.071),.014,iron)
bar("bracket upturn",(.56,-.075,.071),(.56,-.075,.118),.012,iron)
block("bottom wall strap",(1.20,.03,.055),(.01,-.04,.018),iron)

# Hinges and latches on the right edge of the wall.
for z in (2.32,2.83,2.98):
    block("right edge hinge"+str(z),(.15,.075,.048),(.886,-.045,z),iron)
bar("edge upright hinge pin",(.889,-.1,2.66),(.889,-.1,3.07),.018,iron)

# Painted service pipe across the top of the photograph.
sweep = sweep_tube(points=[(-.30,-.16,3.55),(.03,-.16,3.53),(.31,-.13,3.55),
                          (.72,-.01,3.65),(1.24,.05,3.77)],
                   radius=.037,color=(.20,.31,.31))
scene.include("overhead blue pipe",sweep)
for x,z in ((-.26,3.55),(.02,3.53)):
    bar("pipe collar"+str(x),(x-.022,-.16,z),(x+.022,-.16,z),.045,(.24,.32,.31))

realize(scene)

# Soft daylight and warm room illumination retain the muted museum colors.
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.61,.65,.59,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.38
area_emitter((1.7,.75,3.0),power=230,size=1.5,target=(-.2,-.2,1.6),color=(.83,.91,1.0))
area_emitter((-2.6,-3.8,4.7),power=390,size=4.0,target=(-.1,0,1.6),color=(1.0,.88,.65))

set_view((2.05,-7.6,2.62),(-.14,0,1.76),lens=118,sensor=36)
cam=bpy.context.scene.camera
cam.data.sensor_fit='HORIZONTAL'
bpy.context.scene.render.resolution_x=341
bpy.context.scene.render.resolution_y=512
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=48
bpy.context.scene.view_settings.view_transform='AgX'
bpy.context.scene.view_settings.exposure=.15
bpy.context.scene.render.image_settings.file_format='PNG'
