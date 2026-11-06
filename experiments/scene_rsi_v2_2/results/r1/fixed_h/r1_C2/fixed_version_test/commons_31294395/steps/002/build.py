from sceneact import *
import bpy
import math

# Reference inventory (estimated normalized image bounds):
# Room: brown patterned walls, pale floor below .62, white cornice near .03.
# Cropped left window (0,.07)-(.13,.59); main window (.24,.08)-(.44,.62).
# Oval gilt portrait (.13,.16)-(.25,.37); small prints (.47,.15)-(.54,.28)
# and (.66,.16)-(.71,.29). Console (0,.47)-(.12,.67), cloth table
# (.14,.48)-(.27,.65), waste pot beside table.
# Gold/blue folding screen (.41,.33)-(.62,.66), partly behind chair and bed.
# Olive chair (.28,.50)-(.54,.98): tall scalloped back, tufting, curved
# arms, broad seat, substantial outside side panels, short dark feet.
# Bed (.52,.47)-(1,.98): head toward right wall, foot toward viewer-left,
# dark timber boards/posts, cream cover, two sloping pillows.
# Thin black chair (.61,.47)-(.70,.63), round cabinet at right edge,
# small rug behind chair and partial rug at bottom.
# Hidden furniture backs and bed supports remain uncertain.
#
# Feedback comparison: previous bed ran in the opposite image direction,
# chair was too far right and too bulbous, framing included excessive floor
# and ceiling, and illumination flattened the dark timber/wallpaper.
# This revision preserves the inventory and changes those supported errors.
#
# Expanded cost estimate: approximately 235 simple meshes, 104 primitives
# from four fillet boxes, and about 65 tube components: about 404 total.
# Wallpaper and fabric microstructure use shared procedural materials.

scene = Scene("Historic bedroom revised")
C = {
    "wall": (.26,.18,.11), "wood": (.045,.021,.012),
    "gold": (.52,.35,.10), "white": (.83,.84,.79),
    "linen": (.68,.68,.57), "green": (.18,.19,.035),
    "blue": (.015,.045,.29), "glass": (.76,.90,.88),
    "floor": (.43,.41,.36), "black": (.016,.018,.013)
}

def asset(name):
    a = Asset(name)
    scene.include(name,a)
    return a

def bx(a,n,s,p,c):
    q=box(s,center=p,color=c)
    a.include(n,q)
    return q

def ell(a,n,p,s,c):
    q=ball(1,center=p,color=c)
    q.resize(s)
    a.include(n,q)
    return q

def rd(a,n,p,q,r,c):
    t=rod(r,start=p,end=q,color=c)
    a.include(n,t)
    return t

def curve(a,n,pts,r,c):
    q=sweep_tube(points=pts,radius=r,color=c)
    a.include(n,q)
    return q

room=asset("Room architecture")
bx(room,"pale floor",(8.9,11,.12),(-.6,.1,-.06),C["floor"])
bx(room,"back patterned wall",(8.4,.16,3.75),(-1.3,4.2,1.875),C["wall"])
bx(room,"right patterned wall",(.16,10,3.75),(2.88,-.72,1.875),C["wall"])
bx(room,"ceiling",(8.4,10,.12),(-1.3,-.72,3.81),(.83,.85,.83))
for z,d,h in [(3.59,.10,.10),(3.68,.18,.10),(3.75,.25,.08)]:
    bx(room,"back cornice "+str(z),(8.4,d,h),(-1.3,4.06,z),(.85,.87,.84))
    bx(room,"right cornice "+str(z),(d,10,h),(2.75,-.72,z),(.85,.87,.84))
bx(room,"rear skirting",(8.4,.09,.16),(-1.3,4.07,.08),(.19,.15,.10))
bx(room,"side skirting",(.10,10,.16),(2.75,-.72,.08),(.19,.15,.10))

def window(name,x,w):
    a=asset(name)
    y=4.065
    bx(a,"luminous lower glazing",(w,.035,2.88),(x,y,1.82),C["glass"])
    for dx in [-w/2,w/2]:
        bx(a,"outer jamb "+str(dx),(.13,.18,3.02),(x+dx,y-.06,1.82),C["white"])
        bx(a,"inner sash "+str(dx),(.035,.23,2.78),(x+dx*.91,y-.10,1.82),(.94,.95,.90))
    for z in [.34,3.30]:
        bx(a,"horizontal trim "+str(z),(w+.21,.19,.13),(x,y-.055,z),C["white"])
    bx(a,"deep sill",(w+.25,.36,.075),(x,y-.16,.31),(.90,.91,.85))
    bx(a,"green roller blind",(w-.16,.025,1.47),(x,y-.13,2.40),(.10,.26,.21))
    bx(a,"blind bottom",(w-.14,.04,.035),(x,y-.16,1.665),(.20,.34,.28))
    bx(a,"lower sash rail",(w-.12,.055,.055),(x,y-.15,.65),(.91,.93,.87))
window("Left cropped window",-4.10,1.40)
window("Main tall window",-1.77,1.43)

door=asset("Rear white door")
bx(door,"door leaf",(.70,.07,2.47),(.52,4.02,1.265),(.73,.76,.69))
for x in [.13,.91]:
    bx(door,"jamb "+str(x),(.055,.10,2.58),(x,3.95,1.31),C["white"])
bx(door,"lintel",(.83,.10,.07),(.52,3.95,2.61),C["white"])
bx(door,"upper inset",(.51,.035,1.44),(.52,3.965,1.70),(.79,.81,.74))

portrait=asset("Large oval portrait")
ell(portrait,"gilt outer oval",(-2.94,3.91,2.49),(.43,.065,.57),C["gold"])
ell(portrait,"raised gold rim",(-2.94,3.835,2.49),(.385,.035,.52),(.71,.50,.17))
ell(portrait,"dark painted canvas",(-2.94,3.79,2.49),(.335,.025,.465),(.018,.015,.010))
ell(portrait,"dark shoulders",(-2.94,3.755,2.28),(.23,.018,.17),(.035,.025,.018))
ell(portrait,"face",(-2.94,3.745,2.57),(.087,.018,.125),(.34,.19,.095))
ell(portrait,"hair",(-2.95,3.72,2.64),(.089,.016,.06),(.026,.018,.010))
bx(portrait,"collar",(.08,.018,.055),(-2.94,3.72,2.44),(.57,.53,.39))

p=asset("Small rear portrait")
bx(p,"gilt rectangular frame",(.43,.065,.61),(-.30,3.97,2.83),(.55,.41,.21))
bx(p,"ivory mount",(.385,.025,.565),(-.30,3.925,2.83),(.82,.80,.68))
ell(p,"oval gray print",(-.30,3.90,2.83),(.15,.016,.23),(.31,.32,.28))
ell(p,"head",(-.30,3.875,2.885),(.057,.012,.089),(.50,.49,.42))
ell(p,"bust",(-.30,3.87,2.73),(.095,.012,.08),(.22,.24,.20))

p=asset("Right wall miniature")
bx(p,"gilt frame",(.065,.43,.65),(2.755,3.12,2.77),(.53,.37,.18))
bx(p,"pale mount",(.025,.39,.61),(2.71,3.12,2.77),(.81,.78,.65))
ell(p,"oval print",(2.69,3.12,2.77),(.015,.125,.24),(.34,.33,.28))
ell(p,"head",(2.67,3.12,2.84),(.013,.052,.08),(.53,.49,.40))

console=asset("Dark console under left window")
bx(console,"top",(1.20,.49,.075),(-4.05,3.69,.83),C["wood"])
bx(console,"drawer apron",(1.12,.40,.27),(-4.05,3.70,.665),(.064,.029,.014))
for x in [-4.55,-3.55]:
    for y in [3.52,3.87]:
        rd(console,"turned leg "+str((x,y)),(x,y,.12),(x,y,.64),.043,C["wood"])
        ell(console,"leg bead "+str((x,y)),(x,y,.31),(.065,.065,.07),C["wood"])
        ell(console,"foot "+str((x,y)),(x,y,.10),(.075,.07,.06),C["wood"])
bx(console,"low stretcher",(1.07,.32,.045),(-4.05,3.70,.20),C["wood"])
for x in [-4.28,-3.82]:
    ell(console,"drawer pull "+str(x),(x,3.477,.70),(.025,.018,.025),C["gold"])
bx(console,"little picture frame",(.27,.045,.36),(-4.20,3.59,1.055),C["gold"])
bx(console,"little picture",(.22,.025,.30),(-4.20,3.56,1.055),(.055,.06,.035))

table=asset("Small cloth covered table")
bx(table,"timber top",(.77,.65,.065),(-2.78,3.44,.79),C["wood"])
for x in [-3.06,-2.50]:
    for y in [3.20,3.67]:
        rd(table,"leg "+str((x,y)),(x,y,.10),(x,y,.76),.035,C["wood"])
bx(table,"white cloth top",(.83,.68,.025),(-2.78,3.42,.84),(.83,.82,.74))
cloth=bx(table,"diagonal hanging cloth",(.72,.025,.39),(-2.78,3.075,.66),(.79,.78,.70))
cloth.turn("y",32)
ell(table,"small dish",(-2.79,3.39,.872),(.16,.11,.015),(.68,.62,.44))
ell(table,"small vessel",(-2.55,3.38,.91),(.043,.043,.075),(.48,.40,.21))
pot=asset("Small floor waste pot")
bx(pot,"basket body",(.23,.23,.27),(-3.30,3.50,.135),(.23,.105,.040))
bx(pot,"dark opening",(.19,.19,.018),(-3.30,3.50,.279),(.035,.021,.010))

screen=asset("Painted folding screen")
for i,(x,y,ang) in enumerate([(-.94,3.18,-6),(-.37,3.15,3),(.20,3.19,-7)]):
    panel=Asset("Screen leaf "+str(i))
    bx(panel,"gold panel",(.59,.065,1.69),(x,y,1.23),(.48,.35,.14))
    for xx in [x-.29,x+.29]:
        bx(panel,"dark edge "+str(xx),(.018,.075,1.72),(xx,y-.005,1.23),(.11,.066,.025))
    # Unequal patches retain open gold ground rather than identical blue disks.
    if i==0:
        ell(panel,"upper blue sweep",(x-.12,y-.045,1.57),(.29,.012,.23),C["blue"])
        ell(panel,"lower blue sweep",(x+.12,y-.045,.77),(.24,.012,.29),C["blue"])
    elif i==1:
        ell(panel,"central blue field",(x+.08,y-.045,1.12),(.27,.012,.45),C["blue"])
        ell(panel,"gold opening",(x-.035,y-.067,1.21),(.20,.012,.14),(.54,.40,.19))
    else:
        ell(panel,"upper blue field",(x+.10,y-.045,1.71),(.22,.012,.32),C["blue"])
        ell(panel,"lower blue field",(x-.12,y-.045,.77),(.25,.012,.31),C["blue"])
    curve(panel,"painted blue current",[(x-.23,y-.052,1.49),(x+.08,y-.052,1.39),
          (x+.19,y-.052,1.19),(x-.10,y-.052,1.01)],.070,C["blue"])
    ell(panel,"ochre island",(x+.03,y-.075,.85),(.12,.012,.07),(.59,.33,.10))
    rd(panel,"painted branch",(x-.17,y-.080,.93),(x+.17,y-.080,1.34),.012,(.19,.20,.08))
    for j in range(3):
        ell(panel,"green leaf "+str(j),(x-.10+j*.075,y-.095,1.10+j*.065),
            (.055,.012,.025),(.23,.34,.17))
    panel.turn("z",ang,pivot=(x,y,1.2))
    screen.include("leaf "+str(i),panel)
screen.move((.28,0,0))

bed=asset("Dark wooden double bed")
bed_x=1.38
bed_width=2.08
head_y=2.46
foot_y=-.39
bx(bed,"bed base",(bed_width,2.85,.29),(bed_x,1.03,.40),C["wood"])
for x in [bed_x-bed_width/2,bed_x+bed_width/2]:
    bx(bed,"side rail "+str(x),(.10,2.87,.24),(x,1.02,.50),(.055,.026,.014))
    for y in [head_y,foot_y]:
        bx(bed,"square post "+str((x,y)),(.125,.13,1.00),(x,y,.54),C["wood"])
        ell(bed,"post cap "+str((x,y)),(x,y,1.065),(.095,.095,.055),(.067,.032,.016))
bx(bed,"headboard broad panel",(2.14,.13,.65),(bed_x,head_y,1.12),(.051,.024,.014))
rd(bed,"headboard top rail",(bed_x-1.11,head_y,1.49),(bed_x+1.11,head_y,1.49),.052,C["wood"])
bx(bed,"headboard inset",(1.87,.035,.36),(bed_x,head_y-.085,1.12),(.078,.040,.022))
bx(bed,"footboard solid panel",(2.14,.14,.66),(bed_x,foot_y,.70),(.040,.019,.011))
rd(bed,"footboard top rail",(bed_x-1.10,foot_y,1.08),(bed_x+1.10,foot_y,1.08),.055,C["wood"])
bx(bed,"footboard inset",(1.83,.025,.40),(bed_x,foot_y-.085,.70),(.060,.029,.015))
bed.include("cream mattress",fillet_box((1.99,2.66,.28),radius=.10,
            center=(bed_x,1.03,.68),color=(.74,.74,.64)))
bed.include("soft duvet",fillet_box((2.02,2.13,.24),radius=.10,
            center=(bed_x,.73,.85),color=C["linen"]))
for i,(xx,yy,zz,sx,sy) in enumerate([
    (-.69,.18,.947,.23,.68),(.60,.42,.945,.29,.70),
    (-.35,1.33,.966,.42,.15),(.30,1.40,.957,.41,.17),
    (-.77,.91,.935,.12,.47)]):
    e=ell(bed,"cover fold "+str(i),(bed_x+xx,yy,zz),(sx,sy,.032),(.70,.70,.60))
    e.turn("z",-15+i*9)
for i,x in enumerate([bed_x-.51,bed_x+.49]):
    pillow=fillet_box((.98,.65,.28),radius=.12,
                     center=(x,1.99,1.16),color=(.79,.79,.69))
    pillow.turn("x",46)
    pillow.turn("z",-7 if i==0 else 9)
    bed.include("large sloping pillow "+str(i),pillow)
    ell(bed,"pillow crease "+str(i),(x+.27,1.76,1.16),(.08,.17,.025),(.66,.67,.57))
# Turn the entire editable bed so the head is at image right and foot at left.
bed.turn("z",-65,pivot=(bed_x,1.03,0))
bed.move((.55-bed_x,1.30-1.03,0))

chair=asset("Olive upholstered armchair")
cx=-2.43
cy=.19
for x in [cx-.43,cx+.43]:
    for y in [cy-.43,cy+.37]:
        rd(chair,"short foot "+str((x,y)),(x,y,.045),(x,y,.25),.035,(.065,.042,.015))
ell(chair,"lower upholstered body",(cx,cy,.39),(.60,.55,.30),(.14,.15,.025))
ell(chair,"seat cushion",(cx,cy-.18,.64),(.53,.47,.12),(.25,.26,.045))
back=ell(chair,"tall curved back",(cx,cy+.37,1.04),(.56,.145,.64),C["green"])
back.turn("x",-12)
ell(chair,"back interior",(cx,cy+.245,1.05),(.45,.085,.47),(.22,.23,.040))
for side in [-1,1]:
    x=cx+side*.52
    # Tall side upholstery creates a continuous wing-to-front silhouette.
    sidepart=ell(chair,"deep upholstered side "+str(side),(x,cy-.03,.67),
                 (.105,.57,.38),(.15,.16,.025))
    sidepart.turn("x",-13)
    curve(chair,"curved arm rim "+str(side),[
        (x,cy-.56,.58),(x,cy-.50,.82),(x,cy-.12,.96),
        (x,cy+.25,1.24),(x,cy+.34,1.37)],.035,(.25,.26,.05))
for i,(dx,z) in enumerate([(-.23,1.12),(0,1.26),(.23,1.11),(-.13,.91),(.14,.92)]):
    ell(chair,"recessed tuft "+str(i),(cx+dx,cy+.145,z),(.025,.014,.035),(.09,.11,.014))
    curve(chair,"tuft fold "+str(i),[(cx+dx-.06,cy+.15,z+.08),
          (cx+dx,cy+.13,z),(cx+dx+.04,cy+.15,z-.065)],.012,(.26,.27,.045))
chair.turn("z",-65,pivot=(cx,cy,0))

thin=asset("Slender black side chair")
tx=.18
ty=2.64
bx(thin,"seat",(.43,.43,.045),(tx,ty,.55),(.055,.048,.025))
for x in [tx-.19,tx+.19]:
    for y in [ty-.18,ty+.18]:
        rd(thin,"leg "+str((x,y)),(x,y,.05),(x,y,.57),.018,C["black"])
    rd(thin,"back upright "+str(x),(x,ty+.18,.52),(x,ty+.18,1.20),.019,C["black"])
rd(thin,"back top",(tx-.21,ty+.18,1.20),(tx+.21,ty+.18,1.20),.025,C["black"])
for dx in [-.12,0,.12]:
    rd(thin,"back spindle "+str(dx),(tx+dx,ty+.18,.74),(tx+dx,ty+.18,1.17),.012,C["black"])
rd(thin,"front stretcher",(tx-.19,ty-.18,.23),(tx+.19,ty-.18,.23),.015,C["black"])

side=asset("Round bedside cabinet")
ell(side,"round top",(2.35,-.02,.76),(.43,.43,.055),(.043,.020,.010))
ell(side,"cabinet body",(2.35,-.02,.42),(.38,.38,.34),(.050,.024,.012))
ell(side,"base molding",(2.35,-.02,.12),(.42,.42,.055),(.029,.015,.009))

def rug(name,x,y,w,h):
    a=asset(name)
    bx(a,"red field",(w,h,.012),(x,y,.012),(.25,.085,.052))
    for inset,col in [(.04,(.57,.46,.28)),(.075,(.12,.20,.20)),
                      (.12,(.43,.25,.12)),(.16,(.58,.51,.34))]:
        for sy in [-1,1]:
            bx(a,"long border "+str((inset,sy)),(w-2*inset,.028,.006),
               (x,y+sy*(h/2-inset),.022),col)
        for sx in [-1,1]:
            bx(a,"short border "+str((inset,sx)),(.028,h-2*inset,.006),
               (x+sx*(w/2-inset),y,.022),col)
    for j in range(5):
        q=bx(a,"woven medallion "+str(j),(.16,.16,.007),
             (x,y-h*.31+j*h*.155,.026),(.33,.34,.20))
        q.turn("z",45)
    return a
rug("Small rug behind armchair",-2.25,1.68,1.13,1.45)
rug("Partial foreground rug",-.10,-1.35,1.72,1.15)

realize(scene)

def material(name,color,rough=.7):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    return m

wallpaper=material("Faded ochre teal wallpaper",C["wall"],.95)
nd=wallpaper.node_tree.nodes
lk=wallpaper.node_tree.links
geo=nd.new("ShaderNodeNewGeometry")
noise=nd.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=37
noise.inputs["Detail"].default_value=2.4
noise.inputs["Roughness"].default_value=.72
lk.new(geo.outputs["Position"],noise.inputs["Vector"])
ramp=nd.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.27
ramp.color_ramp.elements[0].color=(.040,.070,.059,1)
ramp.color_ramp.elements[1].position=.72
ramp.color_ramp.elements[1].color=(.32,.20,.095,1)
mid=ramp.color_ramp.elements.new(.47)
mid.color=(.16,.105,.052,1)
mid=ramp.color_ramp.elements.new(.56)
mid.color=(.25,.145,.067,1)
lk.new(noise.outputs["Fac"],ramp.inputs[0])
bs=nd.get("Principled BSDF")
lk.new(ramp.outputs[0],bs.inputs["Base Color"])
bump=nd.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.12
bump.inputs["Distance"].default_value=.008
lk.new(noise.outputs["Fac"],bump.inputs["Height"])
lk.new(bump.outputs[0],bs.inputs["Normal"])

linen=material("Woven cream linen",C["linen"],.96)
n=linen.node_tree.nodes
l=linen.node_tree.links
t=n.new("ShaderNodeTexNoise")
t.inputs["Scale"].default_value=165
t.inputs["Detail"].default_value=2
b=n.new("ShaderNodeBump")
b.inputs["Strength"].default_value=.12
b.inputs["Distance"].default_value=.009
l.new(t.outputs["Fac"],b.inputs["Height"])
l.new(b.outputs[0],n.get("Principled BSDF").inputs["Normal"])

glass=material("Bright window daylight",C["glass"])
pbs=glass.node_tree.nodes.get("Principled BSDF")
pbs.inputs["Emission Color"].default_value=(.77,.90,.89,1)
pbs.inputs["Emission Strength"].default_value=2.8

wood=material("Dark polished walnut",C["wood"],.30)
n=wood.node_tree.nodes
l=wood.node_tree.links
no=n.new("ShaderNodeTexNoise")
no.inputs["Scale"].default_value=5
no.inputs["Detail"].default_value=3
b=n.new("ShaderNodeBump")
b.inputs["Strength"].default_value=.12
b.inputs["Distance"].default_value=.012
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
            return sum((rgb[k]-c[k])**2 for k in range(3))<.00012
        if close(C["wall"]):
            obj.data.materials[i]=wallpaper
        elif close(C["linen"]):
            obj.data.materials[i]=linen
        elif close(C["glass"]):
            obj.data.materials[i]=glass
        elif close(C["wood"]):
            obj.data.materials[i]=wood
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
background.inputs["Color"].default_value=(.43,.49,.53,1)
background.inputs["Strength"].default_value=.15

set_view(position=(-4.65,-6.45,2.70),target=(-1.15,1.65,1.30),lens=44,sensor=36)
area_emitter(position=(-1.75,3.55,2.30),power=310,size=1.65,
             target=(-.70,-.50,.45),color=(.85,.94,1))
area_emitter(position=(-4.0,3.50,2.20),power=190,size=1.45,
             target=(-1.5,-1,.6),color=(.84,.93,1))
area_emitter(position=(-2,-2.1,3.4),power=42,size=4,
             target=(.3,1,.3),color=(1,.92,.81))
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=-.55
sc.camera.data.clip_start=.05
sc.camera.data.clip_end=100
