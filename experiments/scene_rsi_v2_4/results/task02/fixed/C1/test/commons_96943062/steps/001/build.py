from sceneact import *
import bpy
import math
import random

# Reference inventory (normalized image bounds, approximate):
# Room: pale cream back wall (.12,.38)-(.53,.60); right wall (.52,.00)-(1,.78).
# Dark carpet covers lower .40 of image, with right wall black baseboard.
# Large right-wall whiteboard (.59,.26)-(.91,.58), aluminum border and two panels.
# Left luminous windows (.00,.33)-(.12,.67), cropped by image left.
# Suspended ceiling fills upper left; rectangular tiles, lights and missing edge tiles.
# Hanging US flag (.45,.33)-(.51,.43), diagonal pole toward right wall.
# Back wall vent, open electrical enclosure, dangling cover and small wall plates.
# Floor debris: gray torn panels left/center, yellow layered sheets at lower right,
# and long aluminum ceiling rails cropped by the bottom-right edge.
# Shared observed anchors: back floor corners near (.12,.61),(.52,.59);
# back ceiling line near y=.38; right board verticals and receding top/bottom edges;
# right baseboard runs from (.52,.59) to (1,.78). Hidden room extent is inferred.
# Editable parameter families: camera, room dimensions, board, ceiling grid, debris.
# Expanded primitive estimate: about 200 boxes/rods, plus 13 flag stripes.
# No rendered feedback is available at this initial build.

random.seed(12)
scene = Scene(name="Vacant classroom")
W, D, H = 4.65, 7.6, 2.95
cream = (.69,.675,.60)
ceiling_col = (.65,.67,.66)
metal = (.48,.52,.52)
dark = (.055,.065,.058)

def asset(name):
    a = Asset(name=name)
    scene.include(name, a)
    return a

def bx(parent, name, size, center, color, rotation=None):
    obj = box(size=size, center=center, color=color)
    if rotation:
        obj.turn(euler=rotation, pivot=center)
    parent.include(name, obj)
    return obj

def rd(parent, name, a, b, radius, color):
    obj = rod(radius=radius, start=a, end=b, color=color)
    parent.include(name, obj)
    return obj

architecture = asset("Room shell")
bx(architecture,"Carpet",(W+1,D+3,.12),(W/2,D/2-.8,-.07),(.16,.17,.145))
bx(architecture,"Right plaster wall",(.12,D+2,H),(W+.06,D/2-.7,H/2),cream)
bx(architecture,"Back plaster wall",(W,.12,H),(W/2,D+.06,H/2),cream)
bx(architecture,"Left wall",(.12,D,H),(-.06,D/2,H/2),(.73,.74,.70))
bx(architecture,"Right black skirting",(.035,D+.5,.115),(W-.025,D/2-.25,.057),dark)
bx(architecture,"Back black skirting",(W,.035,.115),(W/2,D-.025,.057),dark)
bx(architecture,"Left black skirting",(.035,D,.1),(.02,D/2,.05),dark)

windows = asset("Left translucent window wall")
for j in range(4):
    yy = .78+j*1.38
    bx(windows,"Opaque glowing pane %d"%j,(.025,1.34,2.56),(.022,yy,1.49),(.86,.90,.90))
    bx(windows,"Window mullion %d"%j,(.052,.022,2.65),(.043,yy+.68,1.48),(.70,.75,.75))
for zz in (.2,1.52,2.77):
    bx(windows,"Window horizontal rail %.2f"%zz,(.055,5.65,.024),(.05,2.82,zz),(.72,.77,.77))

ceiling = asset("Suspended acoustic ceiling")
bx(ceiling,"Dark plenum",(W+.2,D+.5,.055),(W/2,D/2,H+.19),(.095,.115,.11))
sx, sy = .79, 1.22
for i in range(6):
    for j in range(7):
        xx, yy = (i+.5)*sx, (j+.5)*sy-.6
        if xx>W or yy>D:
            continue
        # Missing tiles along the left side expose a dark ceiling cavity.
        if i==0 and j in (0,1,3,4):
            continue
        c=ceiling_col
        if (i,j) in ((1,2),(1,3),(2,5)):
            c=(.77,.79,.77)
        bx(ceiling,"Acoustic tile %d %d"%(i,j),(sx-.022,sy-.022,.025),(xx,yy,H),c)
for i in range(7):
    xx=i*sx
    if xx<=W:
        bx(ceiling,"Long grid runner %d"%i,(.018,D+.8,.025),(xx,D/2-.3,H-.016),(.55,.59,.58))
for j in range(8):
    yy=j*sy-.6
    if yy<=D:
        bx(ceiling,"Cross grid runner %d"%j,(W,.018,.025),(W/2,yy,H-.016),(.56,.60,.59))
for j in (2,4):
    bx(ceiling,"Recessed fluorescent frame %d"%j,(.68,1.12,.025),(1.185,j*sy+.01,H-.033),(.52,.56,.56))
    bx(ceiling,"Fluorescent diffuser %d"%j,(.62,1.06,.012),(1.185,j*sy+.01,H-.051),(.78,.82,.81))
rd(ceiling,"Loose ceiling wire",(.18,4.8,H+.02),(.24,4.66,2.48),.008,(.12,.14,.14))

board = asset("Right wall whiteboard")
board_y, board_len = 4.95, 3.12
board_z, board_h = 1.77, 1.36
bx(board,"Board backing",(.035,board_len,board_h),(W-.045,board_y,board_z),(.68,.70,.68))
bx(board,"White writing surface",(.012,board_len-.065,board_h-.065),(W-.069,board_y,board_z),(.78,.80,.79))
for zz, nm in ((board_z-board_h/2,"Bottom frame"),(board_z+board_h/2,"Top frame")):
    bx(board,nm,(.052,board_len+.035,.025),(W-.08,board_y,zz),(.57,.61,.62))
for yy, nm in ((board_y-board_len/2,"Near end frame"),(board_y+board_len/2,"Far end frame")):
    bx(board,nm,(.052,.023,board_h+.03),(W-.08,yy,board_z),(.55,.59,.61))
bx(board,"Center divider",(.021,.012,board_h-.04),(W-.082,board_y+.28,board_z),(.63,.66,.65))
bx(board,"Narrow marker tray",(.085,board_len,.025),(W-.095,board_y,board_z-board_h/2-.025),(.54,.58,.58))
for yy in (board_y-board_len/2+.08,board_y+board_len/2-.08):
    bx(board,"Top mounting clip %.1f"%yy,(.027,.055,.08),(W-.08,yy,board_z+board_h/2+.025),(.47,.50,.49))

fixtures = asset("Back wall fixtures")
bx(fixtures,"Vent dark opening",(.91,.025,.37),(.93,D-.03,2.13),(.24,.29,.29))
for k in range(9):
    bx(fixtures,"Vent horizontal louver %d"%k,(.85,.028,.013),(.93,D-.051,1.98+k*.036),(.32,.37,.36))
bx(fixtures,"Electrical panel surround",(.28,.035,.41),(2.08,D-.035,1.89),(.49,.53,.51))
bx(fixtures,"Electrical panel black cavity",(.22,.016,.32),(2.08,D-.063,1.9),(.11,.14,.13))
for k in range(4):
    bx(fixtures,"Breaker %d"%k,(.06,.025,.037),(2.06+(k%2)*.075,D-.083,1.82+(k//2)*.10),(.47,.49,.45))
cover=bx(fixtures,"Loose hanging panel cover",(.43,.035,.34),(2.25,D-.13,1.58),(.43,.49,.47))
cover.turn(axis="+y",degrees=39,pivot=(2.25,D-.13,1.58))
for xx,zz in ((2.69,1.64),(2.88,1.69)):
    bx(fixtures,"Small wall plate %.2f"%xx,(.13,.02,.18),(xx,D-.035,zz),(.75,.75,.68))
    bx(fixtures,"Plate inset %.2f"%xx,(.05,.012,.045),(xx,D-.05,zz+.02),(.43,.46,.42))
bx(fixtures,"Right wall outlet",(.018,.085,.135),(W-.065,5.8,.50),(.64,.63,.53))

flag = asset("American flag and diagonal bracket")
rd(flag,"Flagpole",(W-.03,6.49,2.60),(3.23,6.68,2.97),.012,(.28,.29,.26))
# Hanging cloth is constructed in narrow vertical folds, with horizontal stripes.
flag_x, flag_y, flag_top = 3.25,6.64,2.94
fw, fh = .36,.76
for k in range(13):
    ztop=flag_top-k*fh/13
    col=(.56,.055,.055) if k%2==0 else (.83,.82,.73)
    for q in range(4):
        xx=flag_x+q*fw/4+fw/8
        yy=flag_y+.030*math.sin(q*2.1+k*.27)
        bx(flag,"Cloth stripe %d fold %d"%(k,q),(fw/4+.004,.014,fh/13+.002),(xx,yy,ztop-fh/26),col)
bx(flag,"Blue canton",(.185,.018,.36),(flag_x+.09,flag_y-.022,flag_top-.18),(.09,.14,.23))
for r in range(5):
    for c in range(4):
        bx(flag,"Small star %d %d"%(r,c),(.009,.006,.011),(flag_x+.025+c*.041,flag_y-.034,flag_top-.038-r*.064),(.81,.82,.75))

debris = asset("Scattered ceiling debris")
# Assemblies use explicit centers and pivots to retain editable whole-object placement.
def fragment(name, center, size, angle, color):
    p=Asset(name=name)
    debris.include(name,p)
    slab=bx(p,"Broken panel",size,center,color)
    slab.turn(axis="+z",degrees=angle,pivot=center)
    return p
fragment("Foreground torn panel",(.93,1.7,.025),(1.28,.56,.028),-12,(.32,.34,.29))
fragment("Foreground overlapping piece",(1.29,1.86,.047),(.90,.34,.022),17,(.37,.38,.32))
fragment("Left middle panel",(.42,3.28,.022),(.96,.38,.025),-8,(.36,.37,.31))
fragment("Back scattered panel",(1.36,4.86,.025),(1.12,.35,.026),9,(.28,.30,.25))
fragment("Small back panel",(1.08,5.02,.046),(.55,.26,.018),-19,(.42,.43,.36))
for k in range(13):
    xx=random.uniform(.4,2.0)
    yy=random.uniform(1.5,5.1)
    rd(debris,"Torn dark edging %d"%k,(xx,yy,.045),(xx+random.uniform(.15,.48),yy+random.uniform(-.2,.2),.047),.009,(.10,.13,.11))
for k in range(23):
    xx=random.uniform(.2,4.4)
    yy=random.uniform(1.1,6.8)
    s=random.uniform(.012,.045)
    bx(debris,"Small plaster chip %d"%k,(s,s*.65,.008),(xx,yy,.012),(.50,.49,.39))

yellow = asset("Collapsed yellow ceiling panels")
for k in range(4):
    ctr=(3.83-.09*k,2.65+.10*k,.075+.023*k)
    obj=bx(yellow,"Layered yellow sheet %d"%k,(1.24,.95,.028),ctr,(.59+.035*k,.45+.035*k,.15+.018*k))
    obj.turn(euler=(2, -4, -7),pivot=ctr)
# A raised, sloping front sheet gives the distinctive bent, broad yellow silhouette.
ctr=(4.00,2.49,.19)
obj=bx(yellow,"Bent raised yellow panel",(.92,1.10,.035),ctr,(.71,.56,.21))
obj.turn(euler=(-13,7,-7),pivot=ctr)
for k in range(4):
    rd(yellow,"Exposed layered edge %d"%k,(3.16,2.27+.05*k,.08+.022*k),(3.21,3.03+.05*k,.11+.022*k),.012,(.55,.44,.19))

rails = asset("Fallen metal ceiling runners")
rd(rails,"Long silver foreground rail",(3.94,1.85,.035),(4.79,-.70,.035),.024,(.59,.62,.59))
rd(rails,"Second silver foreground rail",(4.39,2.10,.03),(5.32,-.30,.03),.018,(.68,.69,.63))
rd(rails,"Left pale cross rail",(.74,2.99,.045),(2.17,2.69,.045),.017,(.57,.64,.64))
rd(rails,"Left rail dark flange",(.77,3.015,.027),(2.19,2.715,.027),.012,(.24,.29,.28))

realize(scene)

# Restrained procedural finishes retain the large observed tonal regions.
for obj in bpy.data.objects:
    if obj.type!='MESH' or not obj.data.materials:
        continue
    mat=obj.data.materials[0]
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Roughness"].default_value=.86

# Carpet variation is surface shading, not geometry.
for obj in bpy.data.objects:
    if obj.type=='MESH' and "Carpet" in obj.name and obj.data.materials:
        mat=obj.data.materials[0]
        nt=mat.node_tree
        bs=nt.nodes.get("Principled BSDF")
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=185
        noise.inputs["Detail"].default_value=2
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.20
        ramp.color_ramp.elements[0].color=(.065,.075,.065,1)
        ramp.color_ramp.elements[1].position=.80
        ramp.color_ramp.elements[1].color=(.21,.22,.18,1)
        nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
nt=sc.world.node_tree
background=nt.nodes.get("Background")
if background is None:
    background=nt.nodes.new("ShaderNodeBackground")
output=nt.nodes.get("World Output")
if output is None:
    output=nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.64,.70,.76,1)
background.inputs["Strength"].default_value=.32
area_emitter(position=(.22,3.4,2.12),power=420,size=4.6,target=(3.4,4.0,1.0),color=(.88,.94,1.0))
area_emitter(position=(2.2,3.8,2.78),power=100,size=3.7,target=(2.4,4,0),color=(1.0,.94,.81))
set_view(position=(.88,-.42,1.64),target=(2.35,7.25,1.60),lens=24,sensor=32)
sc.camera.data.clip_start=.05
sc.camera.data.clip_end=100
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='Standard'
sc.view_settings.exposure=0
sc.view_settings.gamma=1
