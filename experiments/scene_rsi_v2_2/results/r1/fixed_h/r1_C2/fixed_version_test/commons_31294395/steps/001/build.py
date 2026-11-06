from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory, normalized image coordinates:
# Architecture: pale floor (0,.60)-(1,1), patterned brown walls, white ceiling cornice.
# Left window (0,.07)-(.13,.57), main window (.24,.08)-(.44,.62):
# white deep frames, green upper blinds, very bright lower glazing.
# Oval portrait (.13,.16)-(.25,.37), two small pale framed portraits
# (.47,.15)-(.54,.28) and (.66,.16)-(.71,.29).
# Left console (0,.47)-(.12,.67), cloth-covered table (.14,.48)-(.27,.65).
# Folding screen (.41,.33)-(.62,.66), gold ground and large blue painted shapes.
# Green upholstered chair (.28,.50)-(.54,.96), curved back, thick seat and arms.
# Bed (.52,.47)-(.99,.97), dark timber head and foot boards, cream bedding,
# two large rumpled pillows; chair overlaps its left foot corner.
# Slender black chair behind bed (.61,.47)-(.70,.63), bedside round table
# at right edge (.93,.70)-(1,.93). Two partial patterned rugs.
# Hidden bed supports, screen reverse, and objects beyond the frame are uncertain.
#
# Named assets below preserve these inventory groups and their meaningful parts.
# Cost estimate: approximately 255 ordinary primitives, 4 fillet boxes (~104
# expanded primitives), and short curved paths (~45 primitives): about 400 meshes.
# Wallpaper and textile detail use shared procedural shaders, not microgeometry.

scene = Scene("Historic bedroom")
C = {
    "wall": (.36,.285,.205), "wood": (.065,.033,.019),
    "gold": (.56,.39,.12), "white": (.86,.85,.79),
    "linen": (.72,.72,.62), "green": (.22,.235,.055),
    "blue": (.025,.075,.36), "glass": (.76,.90,.88),
    "floor": (.57,.55,.49), "black": (.022,.023,.018)
}
def asset(name):
    a=Asset(name)
    scene.include(name,a)
    return a
def bx(a,n,s,p,c):
    q=box(s,center=p,color=c); a.include(n,q); return q
def ell(a,n,p,s,c):
    q=ball(1,center=p,color=c)
    q.resize(s)
    a.include(n,q)
    return q
def rd(a,n,p,q,r,c):
    t=rod(r,start=p,end=q,color=c); a.include(n,t); return t
def curve(a,n,pts,r,c):
    q=sweep_tube(points=pts,radius=r,color=c); a.include(n,q); return q

room=asset("Room architecture")
bx(room,"stone floor",(8.9,11,.12),(-.6,.1,-.06),C["floor"])
bx(room,"back wallpaper",(8.4,.16,3.75),(-1.3,4.2,1.875),C["wall"])
bx(room,"right wallpaper",(.16,10,3.75),(2.88,-.72,1.875),C["wall"])
bx(room,"ceiling",(8.4,10,.12),(-1.3,-.72,3.81),(.88,.89,.87))
for z,d,h in [(3.59,.10,.10),(3.68,.18,.10),(3.75,.25,.08)]:
    bx(room,"back cornice "+str(z),(8.4,d,h),(-1.3,4.06,z),(.87,.88,.85))
    bx(room,"right cornice "+str(z),(d,10,h),(2.75,-.72,z),(.87,.88,.85))
bx(room,"back skirting",(8.4,.09,.16),(-1.3,4.07,.08),(.25,.21,.16))
bx(room,"right skirting",(.10,10,.16),(2.75,-.72,.08),(.25,.21,.16))

def window(name,x,w):
    a=asset(name)
    y=4.065
    bx(a,"bright opening",(w,.035,2.88),(x,y,1.82),C["glass"])
    # Deep white jambs and nested trim.
    for dx in [-w/2,w/2]:
        bx(a,"outer vertical "+str(dx),(.13,.18,3.02),(x+dx,y-.06,1.82),C["white"])
        bx(a,"inner vertical "+str(dx),(.035,.23,2.78),(x+dx*.91,y-.10,1.82),(.96,.96,.91))
    for z in [.34,3.30]:
        bx(a,"horizontal trim "+str(z),(w+.21,.19,.13),(x,y-.055,z),C["white"])
    bx(a,"projecting sill",(w+.25,.36,.075),(x,y-.16,.31),(.91,.91,.86))
    bx(a,"green roller blind",(w-.16,.025,1.47),(x,y-.13,2.40),(.19,.39,.34))
    bx(a,"blind bottom rail",(w-.14,.04,.035),(x,y-.16,1.665),(.30,.46,.40))
    bx(a,"lower sash rail",(w-.12,.055,.055),(x,y-.15,.65),(.92,.94,.89))
    return a
window("Left cropped window",-4.10,1.40)
window("Main tall window",-1.77,1.43)

# Small door near the room corner, mostly obscured by the screen.
door=asset("Rear white door")
bx(door,"door leaf",(.70,.07,2.47),(.52,4.02,1.265),(.81,.83,.77))
for x in [.13,.91]:
    bx(door,"jamb "+str(x),(.055,.10,2.58),(x,3.95,1.31),(.92,.92,.86))
bx(door,"lintel",(.83,.10,.07),(.52,3.95,2.61),C["white"])
bx(door,"upper inset",(.51,.035,1.44),(.52,3.965,1.70),(.86,.87,.81))

portrait=asset("Large oval portrait")
# Flattened concentric ellipsoids provide an oval gilt frame with an open dark center.
ell(portrait,"outer gold oval",(-2.94,3.91,2.49),(.43,.065,.57),C["gold"])
ell(portrait,"raised rim",(-2.94,3.835,2.49),(.385,.035,.52),(.77,.58,.23))
ell(portrait,"dark canvas",(-2.94,3.79,2.49),(.335,.025,.465),(.035,.029,.022))
ell(portrait,"painted shoulders",(-2.94,3.755,2.28),(.23,.018,.17),(.065,.051,.041))
ell(portrait,"painted head",(-2.94,3.745,2.57),(.087,.018,.125),(.40,.25,.135))
ell(portrait,"painted hair",(-2.95,3.72,2.64),(.089,.016,.06),(.055,.038,.025))
bx(portrait,"collar",(.08,.018,.055),(-2.94,3.72,2.44),(.65,.61,.46))

def small_picture(name,x,z,w=.43,h=.61):
    a=asset(name)
    bx(a,"gold frame",(w,.065,h),(x,3.97,z),(.62,.47,.25))
    bx(a,"ivory mount",(w-.045,.025,h-.045),(x,3.925,z),(.88,.86,.74))
    ell(a,"oval gray print",(x,3.90,z),((w-.13)/2,.016,(h-.15)/2),(.43,.44,.39))
    ell(a,"portrait head",(x,3.875,z+.055),(.057,.012,.089),(.59,.58,.51))
    ell(a,"portrait bust",(x,3.87,z-.10),(.095,.012,.08),(.33,.34,.31))
small_picture("Small rear portrait",-.30,2.83)

# Right-wall oval print, with frame parallel to the side wall.
p=asset("Right wall miniature")
bx(p,"frame",(.065,.43,.65),(2.755,3.12,2.77),(.59,.43,.22))
bx(p,"pale mount",(.025,.39,.61),(2.71,3.12,2.77),(.86,.83,.71))
ell(p,"oval print",(2.69,3.12,2.77),(.015,.125,.24),(.45,.44,.39))
ell(p,"head",(2.67,3.12,2.84),(.013,.052,.08),(.62,.59,.50))

console=asset("Dark console under left window")
bx(console,"top",(1.20,.49,.075),(-4.05,3.69,.83),C["wood"])
bx(console,"drawer apron",(1.12,.40,.27),(-4.05,3.70,.665),(.095,.047,.024))
for x in [-4.55,-3.55]:
    for y in [3.52,3.87]:
        rd(console,"turned leg "+str((x,y)),(x,y,.12),(x,y,.64),.043,C["wood"])
        ell(console,"leg bead "+str((x,y)),(x,y,.31),(.065,.065,.07),C["wood"])
        ell(console,"foot "+str((x,y)),(x,y,.10),(.075,.07,.06),C["wood"])
bx(console,"lower stretcher",(1.07,.32,.045),(-4.05,3.70,.20),C["wood"])
for x in [-4.28,-3.82]:
    ell(console,"drawer pull "+str(x),(x,3.477,.70),(.025,.018,.025),C["gold"])
bx(console,"little framed picture",(.27,.045,.36),(-4.20,3.59,1.055),C["gold"])
bx(console,"little picture center",(.22,.025,.30),(-4.20,3.56,1.055),(.09,.095,.062))

table=asset("Small cloth covered table")
bx(table,"table top",(.77,.65,.065),(-2.78,3.44,.79),C["wood"])
for x in [-3.06,-2.50]:
    for y in [3.20,3.67]:
        rd(table,"leg "+str((x,y)),(x,y,.10),(x,y,.76),.035,C["wood"])
bx(table,"white cloth top",(.83,.68,.025),(-2.78,3.42,.84),(.88,.87,.79))
cloth=bx(table,"hanging front cloth",(.72,.025,.39),(-2.78,3.075,.66),(.84,.83,.75))
cloth.turn("y",32)
ell(table,"small dish",(-2.79,3.39,.872),(.16,.11,.015),(.75,.70,.52))
ell(table,"small vessel",(-2.55,3.38,.91),(.043,.043,.075),(.58,.50,.28))
pot=asset("Small floor waste pot")
bx(pot,"tapered basket body",(.23,.23,.27),(-3.30,3.50,.135),(.28,.15,.065))
bx(pot,"dark opening",(.19,.19,.018),(-3.30,3.50,.279),(.07,.045,.025))

screen=asset("Painted folding screen")
# Three articulated leaves; painted motifs are shallow colored forms on the front.
for i,(x,y,ang) in enumerate([(-.94,3.18,-6),(-.37,3.15,3),(.20,3.19,-7)]):
    panel=Asset("Screen leaf "+str(i))
    bx(panel,"gold leaf",(.59,.065,1.69),(x,y,1.23),(.55,.43,.20))
    for xx in [x-.29,x+.29]:
        bx(panel,"dark edging "+str(xx),(.018,.075,1.72),(xx,y-.005,1.23),(.16,.105,.045))
    # Unequal blue pools and curling streams leave large gold openings.
    ell(panel,"upper blue pool",(x-.14,y-.045,1.72),(.23,.012,.14),C["blue"])
    ell(panel,"lower blue pool",(x+.11,y-.045,.73),(.24,.012,.28),C["blue"])
    curve(panel,"blue painted current",[(x-.23,y-.052,1.49),(x+.08,y-.052,1.39),
        (x+.19,y-.052,1.19),(x-.10,y-.052,1.01)],.075,C["blue"])
    ell(panel,"ochre island",(x+.03,y-.071,.85),(.12,.012,.07),(.66,.40,.13))
    rd(panel,"painted branch",(x-.17,y-.075,.93),(x+.17,y-.075,1.34),.012,(.23,.24,.12))
    for j in range(3):
        ell(panel,"leaf motif "+str(j),(x-.10+j*.075,y-.085,1.10+j*.065),
            (.055,.012,.025),(.28,.40,.25))
    panel.turn("z",ang,pivot=(x,y,1.2))
    screen.include("leaf "+str(i),panel)

# Bed parameters control silhouette and bedding coverage.
bed=asset("Dark wooden double bed")
bed_x=1.38
bed_width=1.98
head_y=2.46
foot_y=-.39
bx(bed,"bed base",(bed_width,2.85,.29),(bed_x,1.03,.40),C["wood"])
for x in [bed_x-bed_width/2,bed_x+bed_width/2]:
    bx(bed,"side rail "+str(x),(.10,2.87,.24),(x,1.02,.50),(.075,.039,.023))
    for y in [head_y,foot_y]:
        bx(bed,"square post "+str((x,y)),(.125,.13,1.00),(x,y,.54),C["wood"])
        ell(bed,"post cap "+str((x,y)),(x,y,1.065),(.095,.095,.055),(.095,.052,.029))
bx(bed,"headboard broad panel",(2.04,.13,.65),(bed_x,head_y,1.12),(.075,.039,.025))
rd(bed,"headboard top rail",(bed_x-1.06,head_y,1.49),(bed_x+1.06,head_y,1.49),.052,C["wood"])
bx(bed,"headboard inset",(1.77,.035,.36),(bed_x,head_y-.085,1.12),(.12,.071,.043))
bx(bed,"footboard solid panel",(2.04,.14,.54),(bed_x,foot_y,.66),(.061,.032,.021))
rd(bed,"footboard top rail",(bed_x-1.05,foot_y,.98),(bed_x+1.05,foot_y,.98),.055,C["wood"])
bx(bed,"footboard inset",(1.73,.025,.30),(bed_x,foot_y-.085,.66),(.085,.046,.028))
m=fillet_box((1.89,2.66,.28),radius=.10,center=(bed_x,1.03,.68),color=(.79,.79,.70))
bed.include("cream mattress",m)
q=fillet_box((1.94,2.13,.24),radius=.10,center=(bed_x,.73,.85),color=C["linen"])
bed.include("soft cream duvet",q)
# Low irregular folds along the cover, concentrated at pillow and side boundaries.
for i,(xx,yy,zz,sx,sy) in enumerate([
    (-.64,.18,.947,.23,.68),(.55,.42,.945,.29,.70),
    (-.35,1.33,.966,.42,.15),(.30,1.40,.957,.41,.17),
    (-.72,.91,.935,.12,.47)]):
    e=ell(bed,"bedding fold "+str(i),(bed_x+xx,yy,zz),(sx,sy,.032),(.76,.76,.67))
    e.turn("z",(-15+i*9))
# Pillows are broad, flattened and lean against the headboard.
for i,x in enumerate([bed_x-.48,bed_x+.46]):
    pillow=fillet_box((.92,.62,.25),radius=.115,center=(x,1.99,1.115),color=(.83,.83,.75))
    pillow.turn("x",42)
    pillow.turn("z",-6 if i==0 else 8)
    bed.include("large pillow "+str(i),pillow)
    ell(bed,"pillow crease "+str(i),(x+.27,1.76,1.12),(.08,.17,.025),(.73,.74,.66))

chair=asset("Olive upholstered armchair")
cx=-.84
cy=.19
# Thick tub silhouette: scooped tall back, seat and two forward rolling arms.
for x in [cx-.43,cx+.43]:
    for y in [cy-.43,cy+.37]:
        rd(chair,"short foot "+str((x,y)),(x,y,.045),(x,y,.28),.035,(.09,.063,.025))
ell(chair,"lower upholstered body",(cx,cy,.39),(.65,.58,.31),(.17,.18,.038))
seat=ell(chair,"broad seat cushion",(cx,cy-.16,.64),(.56,.49,.13),(.29,.30,.065))
back=ell(chair,"rounded high back",(cx,cy+.36,1.05),(.60,.19,.66),C["green"])
back.turn("x",-12)
ell(chair,"back interior",(cx,cy+.235,1.07),(.47,.115,.49),(.27,.28,.062))
for side in [-1,1]:
    x=cx+side*.55
    arm=ell(chair,"swept arm "+str(side),(x,cy-.04,.77),(.155,.63,.33),(.20,.215,.043))
    arm.turn("x",-14)
    curve(chair,"arm piping "+str(side),[
        (x,cy-.57,.65),(x,cy-.48,.88),(x,cy-.05,1.02),
        (x,cy+.36,1.31)],.022,(.34,.34,.085))
# Tufting is sparse and visible on the upper back.
for i,(dx,z) in enumerate([(-.23,1.12),(0,1.26),(.23,1.11),(-.13,.91),(.14,.92)]):
    ell(chair,"recessed tuft "+str(i),(cx+dx,cy+.105,z),(.032,.016,.044),(.13,.15,.025))
    curve(chair,"tuft fold "+str(i),[(cx+dx-.06,cy+.111,z+.08),
        (cx+dx,cy+.09,z),(cx+dx+.04,cy+.11,z-.065)],.014,(.31,.31,.07))

thin=asset("Slender black side chair")
tx=.20
ty=2.54
bx(thin,"seat",(.43,.43,.045),(tx,ty,.55),(.085,.075,.045))
for x in [tx-.19,tx+.19]:
    for y in [ty-.18,ty+.18]:
        rd(thin,"leg "+str((x,y)),(x,y,.05),(x,y,.57),.018,C["black"])
    rd(thin,"back upright "+str(x),(x,ty+.18,.52),(x,ty+.18,1.20),.019,C["black"])
rd(thin,"back top",(tx-.21,ty+.18,1.20),(tx+.21,ty+.18,1.20),.025,C["black"])
for dx in [-.12,0,.12]:
    rd(thin,"back spindle "+str(dx),(tx+dx,ty+.18,.74),(tx+dx,ty+.18,1.17),.012,C["black"])
rd(thin,"front stretcher",(tx-.19,ty-.18,.23),(tx+.19,ty-.18,.23),.015,C["black"])

side=asset("Round bedside cabinet")
ell(side,"round top",(2.72,.07,.76),(.43,.43,.055),(.065,.033,.020))
ell(side,"cylindrical cabinet",(2.72,.07,.42),(.38,.38,.34),(.074,.039,.023))
ell(side,"base molding",(2.72,.07,.12),(.42,.42,.055),(.045,.026,.017))

# Rugs have geometric border bands with a compact motif count.
def rug(name,x,y,w,h):
    a=asset(name)
    bx(a,"outer red field",(w,h,.012),(x,y,.012),(.32,.14,.095))
    for inset,col in [(.04,(.69,.59,.39)),(.075,(.20,.27,.28)),(.12,(.56,.38,.22)),(.16,(.70,.63,.46))]:
        for sy in [-1,1]:
            bx(a,"long border "+str((inset,sy)),(w-2*inset,.028,.006),(x,y+sy*(h/2-inset),.022),col)
        for sx in [-1,1]:
            bx(a,"short border "+str((inset,sx)),(.028,h-2*inset,.006),(x+sx*(w/2-inset),y,.022),col)
    for j in range(5):
        p=bx(a,"woven medallion "+str(j),(.16,.16,.007),(x,y-h*.31+j*h*.155,.026),(.44,.44,.29))
        p.turn("z",45)
    return a
rug("Small rug beside armchair",-1.82,1.39,1.13,1.45)
rug("Foreground rug",1.18,-1.25,1.56,1.13)

realize(scene)

# Shared materials are replaced by source color to keep surface families editable.
def material(name,color,rough=.7):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    return m

wallpaper=material("Dense faded ochre and teal floral wallpaper",C["wall"])
nd=wallpaper.node_tree.nodes
lk=wallpaper.node_tree.links
tex=nd.new("ShaderNodeTexCoord")
noise=nd.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=67
noise.inputs["Detail"].default_value=2.5
noise.inputs["Roughness"].default_value=.78
lk.new(tex.outputs["Generated"],noise.inputs["Vector"])
ramp=nd.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.25
ramp.color_ramp.elements[0].color=(.095,.13,.115,1)
ramp.color_ramp.elements[1].position=.75
ramp.color_ramp.elements[1].color=(.48,.34,.20,1)
mid=ramp.color_ramp.elements.new(.48)
mid.color=(.30,.225,.15,1)
lk.new(noise.outputs["Fac"],ramp.inputs[0])
bs=nd.get("Principled BSDF")
lk.new(ramp.outputs[0],bs.inputs["Base Color"])
bump=nd.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.15
bump.inputs["Distance"].default_value=.018
lk.new(noise.outputs["Fac"],bump.inputs["Height"])
lk.new(bump.outputs[0],bs.inputs["Normal"])

linen=material("Woven cream linen",C["linen"],.95)
n=linen.node_tree.nodes
l=linen.node_tree.links
t=n.new("ShaderNodeTexNoise")
t.inputs["Scale"].default_value=185
t.inputs["Detail"].default_value=2
b=n.new("ShaderNodeBump")
b.inputs["Strength"].default_value=.16
b.inputs["Distance"].default_value=.014
l.new(t.outputs["Fac"],b.inputs["Height"])
l.new(b.outputs[0],n.get("Principled BSDF").inputs["Normal"])

glass=material("Luminous daylight window",C["glass"])
pbs=glass.node_tree.nodes.get("Principled BSDF")
pbs.inputs["Emission Color"].default_value=(.76,.89,.87,1)
pbs.inputs["Emission Strength"].default_value=2.2

wood=material("Dark polished walnut",C["wood"],.31)
n=wood.node_tree.nodes
l=wood.node_tree.links
no=n.new("ShaderNodeTexNoise")
no.inputs["Scale"].default_value=5
no.inputs["Detail"].default_value=3
b=n.new("ShaderNodeBump")
b.inputs["Strength"].default_value=.14
b.inputs["Distance"].default_value=.018
l.new(no.outputs["Fac"],b.inputs["Height"])
l.new(b.outputs[0],n.get("Principled BSDF").inputs["Normal"])

for obj in bpy.context.scene.objects:
    if obj.type!="MESH":
        continue
    for i,ma in enumerate(obj.data.materials):
        if ma is None:
            continue
        rgb=tuple(ma.diffuse_color[:3])
        def close(c):
            return sum((rgb[k]-c[k])**2 for k in range(3))<.00015
        if close(C["wall"]):
            obj.data.materials[i]=wallpaper
        elif close(C["linen"]):
            obj.data.materials[i]=linen
        elif close(C["glass"]):
            obj.data.materials[i]=glass
        elif close(C["wood"]):
            obj.data.materials[i]=wood
    # Smooth curved upholstery, frame ovals, and turned timber.
    if len(obj.data.polygons)>12:
        for poly in obj.data.polygons:
            poly.use_smooth=True

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
if background is None:
    background=sc.world.node_tree.nodes.new("ShaderNodeBackground")
output=sc.world.node_tree.nodes.get("World Output")
if output is None:
    output=sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.50,.56,.60,1)
background.inputs["Strength"].default_value=.32

set_view(position=(-4.65,-6.45,3.05),target=(-.52,1.65,1.40),lens=36,sensor=36)
area_emitter(position=(-1.75,3.55,2.30),power=650,size=1.65,
             target=(-.40,-.50,.45),color=(.85,.94,1))
area_emitter(position=(-4.0,3.50,2.20),power=430,size=1.45,
             target=(-1,-1,.6),color=(.84,.93,1))
area_emitter(position=(-1.5,-2.1,3.4),power=155,size=4,
             target=(.3,1,.3),color=(1,.92,.81))
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=-.25
sc.camera.data.clip_start=.05
sc.camera.data.clip_end=100
