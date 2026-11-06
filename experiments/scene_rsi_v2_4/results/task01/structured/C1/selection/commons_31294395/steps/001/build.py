import bpy, math, random
from mathutils import Vector
from sceneact import *

# Reference inventory (normalized image bounds):
# Architecture: pale floor [0,.59,1,1], patterned brown rear/right walls,
# white cornice [0,0,1,.11]. Rear wall meets right wall near (.57,.08).
# Two tall white windows: [-.03,.07,.13,.55], [.24,.08,.44,.57];
# dark green roller blinds, brilliant lower glass, deep white reveals.
# Bed [.49,.47,.99,.98]: dark wood head at right, foot toward lower center;
# long rails rise rightward, white bedding, two pillows, tall foot posts.
# Olive upholstered chair [.28,.50,.54,.96]: high rounded back, sloping
# padded arms, visible seat opening, near arm obscures bed's left foot.
# Painted folding screen [.41,.33,.62,.65], behind chair and bed.
# Oval gold portrait [.13,.16,.24,.36], two smaller pale framed portraits
# [.47,.15,.54,.28] and [.66,.16,.71,.29].
# Rear left dresser [0,.47,.12,.67], miniature framed picture on its top.
# Cloth-covered table [.15,.48,.26,.64], brass tabletop objects; waste pot.
# Thin dark chair [.61,.46,.71,.65] behind bed; cropped round bedside table.
# Red patterned rug [.20,.64,.33,.76] and cropped foreground rug.
# Hidden furniture backs and bed underside remain simple.
#
# Parent parameters control coherent dimensions and placement. Bed axis is X,
# head on right wall; its head/foot boards span Y. Chair front is local -Y.
# Estimated expanded mesh count: architecture 65, bed 75, chair 45,
# screen 65, portraits 35, tables/chair 65, rugs 95 = about 445 meshes.
# Rounded boxes add about 26 primitives each; use only three below.

random.seed(7)
scene = Scene("Historic bedroom")
WHITE=(.83,.82,.75)
TRIM=(.9,.9,.85)
WOOD=(.065,.035,.023)
WALL=(.36,.285,.20)
GOLD=(.52,.34,.105)
OLIVE=(.255,.25,.055)

def asset(name):
    a=Asset(name)
    scene.include(name,a)
    return a

def block(a,name,size,center,color):
    n=box(size=size,center=center,color=color)
    a.include(name,n)
    return n

def ell(a,name,center,size,color):
    n=ball(1,center=center,color=color)
    n.resize(size,pivot=center)
    a.include(name,n)
    return n

def stick(a,name,p,q,r,color):
    n=rod(radius=r,start=p,end=q,color=color)
    a.include(name,n)
    return n

def place(a,origin,angle=0):
    if angle:
        a.turn('z',angle,pivot=(0,0,0))
    a.move(origin)
    return a

room=asset("Room architecture")
block(room,"Stone floor",(9,12,.14),(0,0,-.08),(.57,.55,.49))
block(room,"Rear wallpaper",(7.4,.16,4.05),(-.3,4.48,2.025),WALL)
block(room,"Right wallpaper",(.16,10,4.05),(3.48,-.5,2.025),WALL)
block(room,"Ceiling",(7.5,10,.12),(-.2,-.5,4.09),(.82,.83,.81))
for z,d,h in [(3.94,.16,.12),(3.85,.1,.08),(4.015,.24,.055)]:
    block(room,"Rear crown "+str(z),(7.4,d,h),(-.3,4.32,z),TRIM)
    block(room,"Right crown "+str(z),(d,10,h),(3.32,-.5,z),TRIM)
block(room,"Rear skirting",(7.3,.09,.17),(-.25,4.34,.09),(.14,.085,.047))
block(room,"Right skirting",(.09,10,.17),(3.34,-.5,.09),(.14,.085,.047))

# Window planes cover the wall, with bright recesses and distinct frame strips.
def window(name,cx,width):
    a=asset(name)
    y=4.30
    bot,top=1.06,3.83
    block(a,"Bright window recess",(width,.045,top-bot),(cx,y,(top+bot)/2),(.94,.99,1))
    block(a,"Blue green lower glass",(width-.16,.025,1.12),(cx,y-.033,1.68),(.72,.87,.86))
    block(a,"Green roller blind",(width-.15,.035,1.52),(cx,y-.075,2.98),(.145,.32,.28))
    block(a,"Blind bottom rail",(width-.14,.045,.025),(cx,y-.09,2.22),(.27,.42,.35))
    for side in [-1,1]:
        block(a,"Outer upright "+str(side),(.12,.15,top-bot+.2),(cx+side*(width/2+.035),y-.09,(top+bot)/2),TRIM)
        block(a,"Inner upright "+str(side),(.045,.17,top-bot),(cx+side*(width/2-.065),y-.13,(top+bot)/2),(.76,.79,.75))
    for zz in [bot,top]:
        block(a,"Horizontal surround "+str(zz),(width+.2,.15,.11),(cx,y-.09,zz),TRIM)
    block(a,"Deep sill",(width+.28,.32,.085),(cx,y-.15,bot-.05),TRIM)
    block(a,"Upper reveal",(width-.12,.13,.06),(cx,y-.12,top-.09),(.68,.72,.69))
    # A faint central frame on the exposed lower pane.
    block(a,"Lower sash rail",(width-.14,.055,.045),(cx,y-.12,1.20),(.91,.93,.89))
    return a

window("Left cropped window",-2.72,1.43)
window("Central tall window",.03,1.54)

door=asset("Narrow white rear door")
block(door,"Door frame",(.80,.13,2.65),(2.20,4.27,1.325),(.88,.88,.82))
block(door,"Door leaf",(.66,.055,2.47),(2.20,4.18,1.26),(.73,.76,.72))
for z,h in [(1.95,.79),(.77,1.08)]:
    block(door,"Inset panel "+str(z),(.51,.022,h),(2.20,4.14,z),(.80,.82,.77))
ell(door,"Brass handle",(1.98,4.08,1.16),(.035,.025,.035),GOLD)

# Bed: explicit local frame, x=0 at the foot, x=L at the head.
bed=asset("Dark mahogany bed")
L,W=2.83,1.96
for x in [0,L]:
    for y in [-W/2,W/2]:
        block(bed,"Square bedpost %.1f %.1f"%(x,y),(.115,.115,1.12 if x==0 else 1.48),
              (x,y,.56 if x==0 else .74),WOOD)
        ell(bed,"Post finial %.1f %.1f"%(x,y),(x,y,1.16 if x==0 else 1.52),(.085,.085,.085),WOOD)
for y in [-W/2,W/2]:
    block(bed,"Long side rail "+str(y),(L,.105,.31),(L/2,y,.42),WOOD)
    block(bed,"Side rail top lip "+str(y),(L,.135,.055),(L/2,y,.60),(.10,.052,.028))
block(bed,"Footboard lower panel",(.105,W,.51),(0,0,.56),WOOD)
block(bed,"Footboard raised panel",(.04,W-.24,.35),(-.067,0,.59),(.092,.049,.027))
block(bed,"Footboard upper rail",(.15,W+.05,.11),(0,0,.91),WOOD)
block(bed,"Headboard broad panel",(.11,W,1.03),(L,0,.94),WOOD)
block(bed,"Headboard inset",(.035,W-.20,.66),(L-.073,0,1.06),(.10,.052,.029))
block(bed,"Headboard crown",(.15,W+.08,.10),(L,0,1.48),WOOD)
m=fillet_box(size=(L-.09,W-.10,.27),radius=.10,
             center=(L/2,0,.67),color=(.72,.71,.64))
bed.include("Mattress",m)
m=fillet_box(size=(L-.14,W-.08,.19),radius=.07,
             center=(L/2-.045,0,.82),color=(.83,.82,.74))
bed.include("Ivory quilt",m)
# The near edge hangs lower than the sleeping surface.
block(bed,"Hanging quilt near edge",(L-.25,.10,.26),(L/2-.02,-W/2+.045,.67),(.79,.78,.70))
for i in range(9):
    x=.26+i*.26
    ell(bed,"Soft quilt edge fold "+str(i),(x,-.946,.69),
        (.17,.065,.14),(.80+.013*(i%3),.79+.013*(i%3),.72+.01*(i%3)))
for j,y in enumerate([-.49,.47]):
    p=ell(bed,"Large linen pillow "+str(j),(L-.53,y,1.02),
          (.47,.43,.16),(.87,.86,.79))
    p.turn('y',-16,pivot=(L-.53,y,1.02))
    p.turn('z',(-5 if j==0 else 5),pivot=(L-.53,y,1.02))
    for k in range(3):
        ell(bed,"Pillow soft crease %d %d"%(j,k),(L-.28,y-.22+k*.21,1.04),
            (.095,.028,.045),(.78,.78,.71))
for i in range(6):
    ell(bed,"Quilt shallow fold "+str(i),(.40+i*.29,-.23+(.13 if i%2 else -.09),.921),
        (.24,.033,.014),(.76,.76,.69))
place(bed,(.23,.52,0))

# Small olive velvet settee. Broad arched back and swept enclosing arms.
chair=asset("Olive upholstered settee")
cw,cd=1.38,1.02
block(chair,"Upholstered base",(cw-.10,cd-.07,.32),(0,0,.40),(.23,.23,.047))
ell(chair,"Seat cushion",(0,-.12,.65),(.64,.48,.115),(.31,.30,.066))
ell(chair,"Arched upholstered back",(0,.36,1.08),(.67,.17,.63),OLIVE)
ell(chair,"Back central crest",(-.02,.36,1.49),(.37,.15,.23),(.28,.28,.065))
for side in [-1,1]:
    # Side panels remain substantial at the lower front, with rounded top rolls.
    ell(chair,"Swept side panel "+str(side),(side*.64,-.04,.72),(.14,.54,.44),(.215,.215,.045))
    stick(chair,"Sloping padded arm "+str(side),(side*.64,-.43,.95),
          (side*.64,.36,1.22),.105,(.29,.285,.061))
    ell(chair,"Arm front end "+str(side),(side*.64,-.44,.94),(.115,.12,.17),(.27,.265,.052))
    for yy in [-.36,.32]:
        stick(chair,"Short dark foot %.1f %.1f"%(side,yy),(side*.52,yy,.08),
              (side*.54,yy,.33),.043,WOOD)
# Low contrast buttons and tuft valleys on the visible front of the back.
for row in range(3):
    for col in range(4):
        x=(col-1.5)*.23 + (.055 if row%2 else 0)
        z=.94+row*.19
        ell(chair,"Tuft button %d %d"%(row,col),(x,.184,z),(.027,.014,.027),(.18,.18,.035))
        stick(chair,"Tuft shadow %d %d"%(row,col),(x-.038,.186,z-.065),
              (x+.025,.186,z+.065),.012,(.235,.235,.045))
place(chair,(-1.28,.17,0),-19)

# Two hinged painted screen leaves; predominantly cobalt and aged ochre.
screen=asset("Decorative painted folding screen")
def screen_leaf(name,w,h,origin,angle):
    a=Asset(name)
    block(a,"Ochre painted panel",(w,.065,h),(0,0,h/2),(.52,.40,.18))
    for xx in [-w/2,w/2]:
        block(a,"Dark narrow edge "+str(xx),(.024,.083,h),(xx,0,h/2),(.15,.10,.045))
    for zz in [.025,h-.025]:
        block(a,"Panel cross edge "+str(zz),(w,.083,.025),(0,0,zz),(.17,.11,.04))
    # Flat organic blue areas are built from shallow ellipsoids on the front.
    for i,(x,z,sx,sz) in enumerate([
        (-.34,1.82,.30,.16),(-.20,1.65,.38,.21),(.13,1.40,.28,.17),
        (.32,1.17,.28,.27),(.13,.93,.37,.22),(-.20,.64,.32,.27),
        (-.34,.28,.22,.30)]):
        ell(a,"Cobalt painted cloud "+str(i),(x,-.041,z),(sx,.009,sz),(.025,.10,.43))
    for k,(x,z) in enumerate([(-.13,1.30),(.22,.73),(-.29,.45)]):
        # Stylized fans with radiating ribs and small warm floral marks.
        ell(a,"Fan ochre field "+str(k),(x,-.055,z),(.21,.009,.14),(.65,.48,.20))
        for j in range(4):
            th=.3+j*.52
            stick(a,"Fan rib %d %d"%(k,j),(x-.12,-.068,z-.10),
                  (x-.12+.29*math.cos(th),-.068,z-.10+.25*math.sin(th)),
                  .008,(.27,.22,.12))
        ell(a,"Coral flower "+str(k),(x+.08,-.073,z+.035),(.055,.009,.038),(.61,.23,.13))
    for i in range(8):
        x=random.uniform(-w*.43,w*.43)
        z=random.uniform(.2,h-.1)
        ell(a,"Sparse painted leaf "+str(i),(x,-.056,z),(.018,.008,.035),(.24,.29,.13))
    place(a,origin,angle)
    screen.include(name,a)
screen_leaf("Left screen leaf",.92,2.05,(-.47,0,0),0)
screen_leaf("Right folded leaf",.80,2.05,(.38,.10,0),-19)
place(screen,(1.16,3.32,.12))

# Rear-wall portrait, flattened ellipsoids preserve the oval silhouette.
portrait=asset("Gilt oval gentleman portrait")
px,py,pz=-1.55,4.23,2.90
ell(portrait,"Outer oval gold frame",(px,py,pz),(.43,.065,.57),(.56,.38,.12))
ell(portrait,"Dark beaded rim",(px,py-.057,pz),(.386,.025,.526),(.28,.18,.06))
ell(portrait,"Inner gilt lip",(px,py-.08,pz),(.365,.018,.503),(.65,.46,.17))
ell(portrait,"Dark portrait canvas",(px,py-.102,pz),(.329,.013,.46),(.048,.042,.031))
ell(portrait,"Painted dark coat",(px,py-.12,pz-.18),(.22,.008,.22),(.025,.023,.021))
ell(portrait,"Painted gentleman head",(px-.015,py-.125,pz+.12),(.083,.009,.12),(.41,.28,.16))
ell(portrait,"Painted dark hair",(px-.024,py-.135,pz+.20),(.078,.008,.055),(.085,.064,.035))
ell(portrait,"White shirt collar",(px+.005,py-.14,pz-.01),(.048,.008,.032),(.64,.60,.46))
# A restrained row of raised gilded beads.
for i in range(24):
    t=2*math.pi*i/24
    ell(portrait,"Frame bead "+str(i),(px+.407*math.cos(t),py-.058,pz+.548*math.sin(t)),
        (.014,.014,.014),(.65,.46,.19))

def rear_print():
    a=asset("Rear monochrome framed print")
    x,y,z=1.43,4.24,3.02
    block(a,"Gold thin rectangular frame",(.56,.065,.75),(x,y,z),(.48,.37,.20))
    block(a,"Ivory mat",(.50,.035,.69),(x,y-.046,z),(.82,.80,.69))
    block(a,"Gray print rectangle",(.30,.015,.48),(x,y-.072,z),(.44,.45,.39))
    ell(a,"Printed head",(x,y-.086,z+.09),(.085,.008,.115),(.25,.27,.24))
    ell(a,"Printed shoulders",(x,y-.088,z-.12),(.12,.008,.12),(.32,.34,.30))
rear_print()

a=asset("Right wall small oval print")
x,y,z=3.365,3.43,3.03
block(a,"Rectangular gilded outer frame",(.055,.49,.74),(x,y,z),(.52,.39,.19))
block(a,"Cream paper mat",(.025,.43,.68),(x-.04,y,z),(.84,.81,.70))
ell(a,"Gray oval print",(x-.059,y,z),(.013,.14,.25),(.48,.47,.40))
ell(a,"Faded portrait head",(x-.075,y,z+.055),(.008,.061,.091),(.33,.34,.30))
ell(a,"Faded portrait bust",(x-.076,y,z-.11),(.008,.088,.09),(.39,.39,.34))

dresser=asset("Cropped left mahogany dresser")
block(dresser,"Dresser body",(1.12,.48,.53),(0,0,.69),WOOD)
block(dresser,"Polished top",(1.24,.56,.075),(0,0,.995),(.105,.058,.029))
for z in [.55,.77]:
    block(dresser,"Drawer "+str(z),(1.04,.035,.18),(0,-.255,z),(.13,.073,.037))
    for xx in [-.28,.28]:
        ell(dresser,"Drawer brass pull %.1f %.1f"%(z,xx),(xx,-.289,z),(.029,.015,.021),GOLD)
for xx in [-.47,.47]:
    for yy in [-.17,.17]:
        stick(dresser,"Turned leg %.1f %.1f"%(xx,yy),(xx,yy,.06),(xx,yy,.45),.045,WOOD)
        ell(dresser,"Leg collar %.1f %.1f"%(xx,yy),(xx,yy,.27),(.064,.064,.055),WOOD)
block(dresser,"Small picture gilt frame",(.34,.05,.43),(-.23,.10,1.23),GOLD)
block(dresser,"Small picture dark painting",(.28,.017,.36),(-.23,.067,1.23),(.10,.12,.08))
ell(dresser,"Small painted vase",(-.23,.051,1.20),(.06,.008,.095),(.28,.25,.13))
place(dresser,(-3.03,3.92,0))

table=asset("Cloth covered rear table")
for xx in [-.34,.34]:
    for yy in [-.22,.22]:
        stick(table,"Mahogany table leg %.1f %.1f"%(xx,yy),(xx,yy,.06),(xx,yy,1.06),.035,WOOD)
block(table,"Small table top",(.91,.64,.07),(0,0,1.10),WOOD)
block(table,"White linen top",(.94,.67,.025),(0,0,1.148),(.85,.84,.76))
# The pointed hanging cloth is a shallow triangular mesh after realization.
# Retain the corresponding SceneAct asset and supporting hem.
stick(table,"Front cloth hem",(-.44,-.345,1.13),(.42,-.345,1.13),.015,WHITE)
for i,x in enumerate([-.24,.21]):
    ell(table,"Brass saucer "+str(i),(x,-.05,1.18),(.12,.095,.018),GOLD)
    ell(table,"Small cup "+str(i),(x,-.05,1.22),(.045,.045,.044),(.73,.68,.47))
stick(table,"Slender brass candlestick",(.04,.14,1.17),(.04,.14,1.39),.018,GOLD)
ell(table,"Candlestick foot",(.04,.14,1.18),(.065,.065,.015),GOLD)
place(table,(-1.45,3.68,0))

pot=asset("Small brown wastepaper pot")
stick(pot,"Cylindrical body",(-2.18,3.55,.035),(-2.18,3.55,.29),.13,(.25,.12,.057))
ell(pot,"Dark open mouth",(-2.18,3.55,.302),(.126,.126,.012),(.075,.047,.025))

spindle=asset("Black spindle chair behind bed")
for x in [-.23,.23]:
    for y in [-.23,.23]:
        stick(spindle,"Thin leg %.1f %.1f"%(x,y),(x,y,.05),(x,y,.64),.022,WOOD)
block(spindle,"Cane seat",(.53,.52,.055),(0,0,.64),(.32,.28,.17))
for x in [-.25,.25]:
    stick(spindle,"Back upright "+str(x),(x,.22,.61),(x,.22,1.37),.026,WOOD)
stick(spindle,"Curved top rail",(-.25,.22,1.37),(.25,.22,1.37),.039,WOOD)
for x in [-.15,-.05,.05,.15]:
    stick(spindle,"Back spindle "+str(x),(x,.22,.77),(x,.22,1.34),.012,WOOD)
place(spindle,(2.56,2.60,0),-8)

roundtable=asset("Cropped round bedside table")
stick(roundtable,"Drum cabinet",(3.31,-1.02,.09),(3.31,-1.02,.69),.37,(.07,.039,.025))
stick(roundtable,"Circular top",(3.31,-1.02,.70),(3.31,-1.02,.75),.43,(.105,.056,.031))
stick(roundtable,"Base molding",(3.31,-1.02,.08),(3.31,-1.02,.13),.40,(.10,.055,.03))
ell(roundtable,"Small drawer knob",(3.0,-1.23,.49),(.035,.025,.025),GOLD)

def rug(name,w,d,origin,angle):
    a=asset(name)
    block(a,"Rust outer field",(w,d,.018),(0,0,.012),(.34,.115,.075))
    block(a,"Ivory border",(w-.09,d-.09,.009),(0,0,.025),(.58,.49,.33))
    block(a,"Blue inner border",(w-.17,d-.17,.008),(0,0,.032),(.17,.24,.25))
    block(a,"Red central field",(w-.29,d-.29,.008),(0,0,.039),(.38,.14,.10))
    for i in range(11):
        xx=-w/2+.12+(w-.24)*i/10
        for side in [-1,1]:
            block(a,"Border lozenge %d %d"%(i,side),(.045,.065,.007),(xx,side*(d/2-.10),.042),(.60,.48,.29))
    for i in range(5):
        for j in range(3):
            xx=(i-2)*(w-.5)/5
            yy=(j-1)*(d-.45)/3
            n=block(a,"Woven motif %d %d"%(i,j),(.075,.075,.006),(xx,yy,.048),(.64,.51,.31))
            n.turn('z',45,pivot=(xx,yy,.048))
    place(a,origin,angle)
rug("Small rear Persian rug",1.55,.94,(-1.35,2.23,0),-3)
rug("Foreground cropped Persian rug",2.35,1.53,(1.05,-2.06,0),-4)

realize(scene)

# A simple cloth mesh supplies the visible triangular drop without thick solids.
verts=[(-1.91,3.333,1.145),(-.99,3.333,1.145),(-1.45,3.27,.69)]
mesh=bpy.data.meshes.new("Linen triangular drape mesh")
mesh.from_pydata(verts,[],[(0,1,2)])
mesh.update()
cloth=bpy.data.objects.new("Cloth covered rear table - pointed linen drop",mesh)
bpy.context.collection.objects.link(cloth)
mat=bpy.data.materials.new("Warm white linen")
mat.diffuse_color=(.84,.83,.76,1)
mat.use_nodes=True
mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.84,.83,.76,1)
mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.96
cloth.data.materials.append(mat)

# Wallpaper: subdued fine olive/rust ornament, scaled in world coordinates.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs is None:
        continue
    bs.inputs["Roughness"].default_value=.78
    c=bs.inputs['Base Color'].default_value
    if abs(c[0]-WALL[0])<.015 and abs(c[1]-WALL[1])<.015 and abs(c[2]-WALL[2])<.015:
        nt=mat.node_tree
        tex=nt.nodes.new('ShaderNodeTexCoord')
        noise=nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=49
        noise.inputs['Detail'].default_value=3
        noise.inputs['Roughness'].default_value=.72
        nt.links.new(tex.outputs['Object'],noise.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.24
        ramp.color_ramp.elements[0].color=(.12,.16,.12,1)
        ramp.color_ramp.elements[1].position=.76
        ramp.color_ramp.elements[1].color=(.46,.32,.20,1)
        e=ramp.color_ramp.elements.new(.49)
        e.color=(.29,.23,.15,1)
        e=ramp.color_ramp.elements.new(.60)
        e.color=(.39,.29,.18,1)
        nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.15
        bump.inputs['Distance'].default_value=.015
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])
    # Bright daylight visible through both lower panes.
    if c[0]>.9 and c[1]>.95 and c[2]>.95:
        if 'Emission Color' in bs.inputs:
            bs.inputs['Emission Color'].default_value=(.78,.91,1,1)
            bs.inputs['Emission Strength'].default_value=.9

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.55,.60,.65,1)
background.inputs['Strength'].default_value=.28

set_view(position=(-4.8,-6.5,3.6),target=(.6,2.0,1.50),lens=42,sensor=36)
area_emitter(position=(-.03,3.94,2.43),power=700,size=2.1,target=(-.4,.1,.6),color=(.84,.94,1.0))
area_emitter(position=(-2.7,3.98,2.5),power=420,size=1.8,target=(-1.2,.3,.8),color=(.86,.94,1.0))
area_emitter(position=(-2,-3.1,3.5),power=95,size=4,target=(1,1,1),color=(1,.90,.75))
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.25
# No rendering or saving: the external runner handles both.
