import bpy, math, random
from sceneact import *

# Reference inventory, normalized image bounds:
# Room: gray floor [0,.60,1,1], brown patterned walls, white cornice [0,0,1,.09].
# Windows: cropped left [0,.07,.13,.56], central [.24,.08,.44,.58],
# with white reveals, green upper blinds and bright lower panes.
# Bed [.49,.47,.99,.98]: mahogany headboard, footboard and four posts,
# cream quilt and two large pillows; chair overlaps its left foot.
# Olive chair [.28,.51,.54,.98]: arched tufted back, low seat opening,
# swept arms; broad right outer side is prominent.
# Folding screen [.41,.33,.62,.65]: ochre panels and cobalt painted fans.
# Oval portrait [.13,.16,.24,.36], rear print [.47,.15,.54,.28],
# right print [.66,.16,.71,.29].
# Cropped dresser [0,.47,.12,.67] supports a small framed painting.
# Linen-covered table [.15,.48,.26,.64] supports brass objects.
# Waste pot, thin spindle chair behind bed, cropped round bedside cabinet.
# Rear rug [.20,.64,.33,.76], foreground rug cropped at lower edge.
# Hidden regions remain simple; all named composites retain semantic children.
#
# Revision observations ranked:
# 1. Chair is nearly frontal in feedback; reference shows a broad right side,
#    oblique seat and a narrower visible back. Change parent orientation only.
# 2. Bed footboard exposes too much broad face and ends too far left/high.
#    Rotate the whole bed around its head anchor; retain attached bedding.
#    Slightly widen the bed to match headboard span and pillow spacing.
# 3. Screen top is too low and right edge too far left. Increase panel height,
#    shift whole screen right; preserve bottom support and hinge arrangement.
# 4. Feedback floor and right wall are too bright; reference has dark wood,
#    muted floor and stronger wallpaper ornament. Adjust lighting/materials.
# 5. Rear cornice is too level. A small camera roll addresses its direction;
#    camera position/lens stay fixed because window and portrait sizes broadly
#    agree. This explanation is uncertain, not a calibrated camera solution.
# Estimated expanded primitives: architecture 55, bed 95 (two fillet boxes),
# chair 45, screen 75, portraits 45, furniture 65, rugs 80: about 460.
# No Boolean operations or external resources.

random.seed(7)
scene=Scene("Historic bedroom revised")
WHITE=(.83,.82,.75)
TRIM=(.9,.9,.85)
WOOD=(.052,.027,.016)
WALL=(.36,.285,.20)
GOLD=(.52,.34,.105)
OLIVE=(.22,.215,.043)

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
block(room,"Stone floor",(9,12,.14),(0,0,-.08),(.41,.40,.355))
block(room,"Rear wallpaper",(7.4,.16,4.05),(-.3,4.48,2.025),WALL)
block(room,"Right wallpaper",(.16,10,4.05),(3.48,-.5,2.025),WALL)
block(room,"Ceiling",(7.5,10,.12),(-.2,-.5,4.09),(.82,.83,.81))
for z,d,h in [(3.94,.16,.12),(3.85,.1,.08),(4.015,.24,.055)]:
    block(room,"Rear crown "+str(z),(7.4,d,h),(-.3,4.32,z),TRIM)
    block(room,"Right crown "+str(z),(d,10,h),(3.32,-.5,z),TRIM)
block(room,"Rear skirting",(7.3,.09,.17),(-.25,4.34,.09),(.14,.085,.047))
block(room,"Right skirting",(.09,10,.17),(3.34,-.5,.09),(.14,.085,.047))

def window(name,cx,width):
    a=asset(name)
    y,bot,top=4.30,1.06,3.83
    block(a,"Bright recess",(width,.045,top-bot),(cx,y,(top+bot)/2),(.94,.99,1))
    block(a,"Lower glass",(width-.16,.025,1.12),(cx,y-.033,1.68),(.72,.87,.86))
    block(a,"Green blind",(width-.15,.035,1.52),(cx,y-.075,2.98),(.10,.255,.215))
    block(a,"Blind hem",(width-.14,.045,.025),(cx,y-.09,2.22),(.24,.36,.29))
    for s in [-1,1]:
        block(a,"Outer upright "+str(s),(.12,.15,top-bot+.2),
              (cx+s*(width/2+.035),y-.09,(top+bot)/2),TRIM)
        block(a,"Inner upright "+str(s),(.045,.17,top-bot),
              (cx+s*(width/2-.065),y-.13,(top+bot)/2),(.76,.79,.75))
    for z in [bot,top]:
        block(a,"Horizontal surround "+str(z),(width+.2,.15,.11),(cx,y-.09,z),TRIM)
    block(a,"Deep sill",(width+.28,.32,.085),(cx,y-.15,bot-.05),TRIM)
    block(a,"Upper reveal",(width-.12,.13,.06),(cx,y-.12,top-.09),(.68,.72,.69))
    block(a,"Lower sash rail",(width-.14,.055,.045),(cx,y-.12,1.20),(.91,.93,.89))
window("Left cropped window",-2.72,1.43)
window("Central tall window",.03,1.62)

door=asset("Narrow white rear door")
block(door,"Frame",(.80,.13,2.65),(2.20,4.27,1.325),(.88,.88,.82))
block(door,"Leaf",(.66,.055,2.47),(2.20,4.18,1.26),(.73,.76,.72))
for z,h in [(1.95,.79),(.77,1.08)]:
    block(door,"Inset panel "+str(z),(.51,.022,h),(2.20,4.14,z),(.80,.82,.77))
ell(door,"Brass handle",(1.98,4.08,1.16),(.035,.025,.035),GOLD)

# Bed local principal axis +X, head at x=L. Head anchor remains fixed.
bed=asset("Dark mahogany bed")
L,W=2.83,2.20
for x in [0,L]:
    for y in [-W/2,W/2]:
        block(bed,"Bedpost %.2f %.2f"%(x,y),(.115,.115,1.12 if x==0 else 1.48),
              (x,y,.56 if x==0 else .74),WOOD)
        ell(bed,"Finial %.2f %.2f"%(x,y),(x,y,1.16 if x==0 else 1.52),
            (.075,.075,.075),WOOD)
for y in [-W/2,W/2]:
    block(bed,"Long side rail "+str(y),(L,.105,.31),(L/2,y,.42),WOOD)
    block(bed,"Rail top lip "+str(y),(L,.135,.055),(L/2,y,.60),(.075,.038,.02))
block(bed,"Footboard lower panel",(.105,W,.51),(0,0,.56),WOOD)
block(bed,"Footboard raised panel",(.04,W-.24,.35),(-.067,0,.59),(.07,.035,.019))
block(bed,"Footboard upper rail",(.15,W+.05,.11),(0,0,.91),WOOD)
block(bed,"Headboard broad panel",(.11,W,1.03),(L,0,.94),WOOD)
block(bed,"Headboard inset",(.035,W-.20,.66),(L-.073,0,1.06),(.075,.039,.021))
block(bed,"Headboard crown",(.15,W+.08,.10),(L,0,1.48),WOOD)
bed.include("Mattress",fillet_box(size=(L-.09,W-.10,.27),radius=.10,
            center=(L/2,0,.67),color=(.69,.68,.61)))
bed.include("Ivory quilt",fillet_box(size=(L-.14,W-.08,.19),radius=.07,
            center=(L/2-.045,0,.82),color=(.78,.77,.69)))
block(bed,"Hanging quilt near edge",(L-.25,.10,.26),
      (L/2-.02,-W/2+.045,.67),(.74,.73,.65))
for i in range(9):
    ell(bed,"Soft quilt edge fold "+str(i),(.26+i*.26,-W/2+.034,.69),
        (.17,.065,.14),(.75+.012*(i%3),.74+.012*(i%3),.67+.01*(i%3)))
for j,y in enumerate([-W*.25,W*.25]):
    p=ell(bed,"Large linen pillow "+str(j),(L-.53,y,1.05),
          (.49,.48,.185),(.84,.83,.75))
    p.turn('y',-21,pivot=(L-.53,y,1.05))
    p.turn('z',-5 if j==0 else 5,pivot=(L-.53,y,1.05))
    for k in range(3):
        ell(bed,"Pillow crease %d %d"%(j,k),(L-.28,y-.24+k*.23,1.055),
            (.09,.022,.035),(.74,.74,.66))
for i in range(6):
    ell(bed,"Quilt shallow fold "+str(i),(.40+i*.29,-.23+(.13 if i%2 else -.09),.921),
        (.24,.026,.011),(.72,.72,.64))
bed.turn('z',17,pivot=(L,0,0))
place(bed,(.23,.52,0))

# Chair local front is -Y. Positive yaw exposes the right outer arm and side.
chair=asset("Olive upholstered settee")
cw,cd=1.38,1.02
block(chair,"Upholstered base",(cw-.10,cd-.07,.32),(0,0,.40),(.19,.19,.034))
ell(chair,"Seat cushion",(0,-.12,.65),(.64,.48,.115),(.27,.26,.048))
ell(chair,"Arched upholstered back",(0,.36,1.08),(.67,.17,.63),OLIVE)
ell(chair,"Back crest",(-.02,.36,1.49),(.37,.15,.23),(.24,.235,.046))
for s in [-1,1]:
    ell(chair,"Swept side panel "+str(s),(s*.64,-.04,.72),(.14,.54,.44),(.18,.18,.031))
    stick(chair,"Sloping padded arm "+str(s),(s*.64,-.43,.95),
          (s*.64,.36,1.22),.105,(.25,.245,.045))
    ell(chair,"Arm front end "+str(s),(s*.64,-.44,.94),(.115,.12,.17),(.23,.225,.038))
    for y in [-.36,.32]:
        stick(chair,"Dark foot %.1f %.2f"%(s,y),(s*.52,y,.08),(s*.54,y,.33),.043,WOOD)
for row in range(3):
    for col in range(4):
        x=(col-1.5)*.23+(.055 if row%2 else 0)
        z=.94+row*.19
        ell(chair,"Tuft button %d %d"%(row,col),(x,.184,z),(.027,.014,.027),(.135,.14,.023))
        stick(chair,"Tuft valley %d %d"%(row,col),(x-.038,.186,z-.065),
              (x+.025,.186,z+.065),.012,(.19,.19,.032))
place(chair,(-1.18,.17,0),27)

screen=asset("Decorative painted folding screen")
def screen_leaf(name,w,h,origin,angle):
    a=Asset(name)
    block(a,"Ochre panel",(w,.065,h),(0,0,h/2),(.47,.35,.15))
    for x in [-w/2,w/2]:
        block(a,"Narrow vertical edge "+str(x),(.024,.083,h),(x,0,h/2),(.12,.075,.031))
    for z in [.025,h-.025]:
        block(a,"Cross edge "+str(z),(w,.083,.025),(0,0,z),(.14,.09,.035))
    for i,(x,z,sx,sz) in enumerate([
        (-.34,1.82,.30,.16),(-.20,1.65,.38,.21),(.13,1.40,.28,.17),
        (.32,1.17,.28,.27),(.13,.93,.37,.22),(-.20,.64,.32,.27),
        (-.34,.28,.22,.30)]):
        ell(a,"Cobalt cloud "+str(i),(x,-.041,z*h/2.05),(sx,.009,sz*h/2.05),(.018,.055,.32))
    for k,(x,z) in enumerate([(-.13,1.30),(.22,.73),(-.29,.45)]):
        z*=h/2.05
        ell(a,"Fan field "+str(k),(x,-.055,z),(.21,.009,.14),(.61,.43,.16))
        for j in range(5):
            t=.2+j*.44
            stick(a,"Fan rib %d %d"%(k,j),(x-.12,-.068,z-.10),
                  (x-.12+.29*math.cos(t),-.068,z-.10+.25*math.sin(t)),
                  .007,(.23,.17,.08))
        ell(a,"Coral flower "+str(k),(x+.08,-.073,z+.035),(.055,.009,.038),(.56,.18,.085))
    for i in range(10):
        x=random.uniform(-w*.43,w*.43)
        z=random.uniform(.2,h-.1)
        ell(a,"Painted leaf "+str(i),(x,-.056,z),(.018,.008,.035),(.18,.24,.08))
    place(a,origin,angle)
    screen.include(name,a)
screen_leaf("Left screen leaf",.92,2.29,(-.47,0,0),0)
screen_leaf("Right folded leaf",.80,2.29,(.38,.10,0),-19)
place(screen,(1.53,3.32,.12))

portrait=asset("Gilt oval gentleman portrait")
px,py,pz=-1.55,4.23,2.90
for name,cy,sx,sz,col in [
    ("Outer gold frame",py,.43,.57,(.56,.38,.12)),
    ("Dark frame rim",py-.057,.386,.526,(.28,.18,.06)),
    ("Inner gilt lip",py-.08,.365,.503,(.65,.46,.17)),
    ("Portrait canvas",py-.102,.329,.46,(.035,.029,.021))]:
    ell(portrait,name,(px,cy,pz),(sx,.018 if cy!=py else .065,sz),col)
ell(portrait,"Painted coat",(px,py-.12,pz-.18),(.22,.008,.22),(.018,.017,.016))
ell(portrait,"Painted head",(px-.015,py-.125,pz+.12),(.083,.009,.12),(.41,.28,.16))
ell(portrait,"Painted hair",(px-.024,py-.135,pz+.20),(.078,.008,.055),(.065,.045,.024))
ell(portrait,"Shirt collar",(px+.005,py-.14,pz-.01),(.048,.008,.032),(.64,.60,.46))
for i in range(24):
    t=2*math.pi*i/24
    ell(portrait,"Gilded bead "+str(i),(px+.407*math.cos(t),py-.058,pz+.548*math.sin(t)),
        (.014,.014,.014),(.65,.46,.19))

a=asset("Rear monochrome framed print")
x,y,z=1.43,4.24,3.02
block(a,"Gold frame",(.56,.065,.75),(x,y,z),(.48,.37,.20))
block(a,"Ivory mat",(.50,.035,.69),(x,y-.046,z),(.82,.80,.69))
block(a,"Gray print",(.30,.015,.48),(x,y-.072,z),(.44,.45,.39))
ell(a,"Printed head",(x,y-.086,z+.09),(.085,.008,.115),(.25,.27,.24))
ell(a,"Printed shoulders",(x,y-.088,z-.12),(.12,.008,.12),(.32,.34,.30))

a=asset("Right wall small oval print")
x,y,z=3.365,3.43,3.03
block(a,"Gilded frame",(.055,.49,.74),(x,y,z),(.52,.39,.19))
block(a,"Cream mat",(.025,.43,.68),(x-.04,y,z),(.84,.81,.70))
ell(a,"Gray oval",(x-.059,y,z),(.013,.14,.25),(.48,.47,.40))
ell(a,"Portrait head",(x-.075,y,z+.055),(.008,.061,.091),(.33,.34,.30))
ell(a,"Portrait bust",(x-.076,y,z-.11),(.008,.088,.09),(.39,.39,.34))

dresser=asset("Cropped left mahogany dresser")
block(dresser,"Cabinet body",(1.12,.48,.53),(0,0,.69),WOOD)
block(dresser,"Polished top",(1.24,.56,.075),(0,0,.995),(.085,.042,.02))
for z in [.55,.77]:
    block(dresser,"Drawer "+str(z),(1.04,.035,.18),(0,-.255,z),(.10,.051,.024))
    for x in [-.28,.28]:
        ell(dresser,"Brass pull %.2f %.2f"%(z,x),(x,-.289,z),(.029,.015,.021),GOLD)
for x in [-.47,.47]:
    for y in [-.17,.17]:
        stick(dresser,"Turned leg %.2f %.2f"%(x,y),(x,y,.06),(x,y,.45),.045,WOOD)
        ell(dresser,"Leg collar %.2f %.2f"%(x,y),(x,y,.27),(.064,.064,.055),WOOD)
block(dresser,"Small picture frame",(.34,.05,.43),(-.23,.10,1.23),GOLD)
block(dresser,"Small painting",(.28,.017,.36),(-.23,.067,1.23),(.07,.085,.045))
ell(dresser,"Painted vase",(-.23,.051,1.20),(.06,.008,.095),(.28,.25,.13))
place(dresser,(-3.03,3.92,0))

table=asset("Cloth covered rear table")
for x in [-.34,.34]:
    for y in [-.22,.22]:
        stick(table,"Leg %.2f %.2f"%(x,y),(x,y,.06),(x,y,1.06),.035,WOOD)
block(table,"Table top",(.91,.64,.07),(0,0,1.10),WOOD)
block(table,"White linen top",(.94,.67,.025),(0,0,1.148),(.85,.84,.76))
# Sloping thin strips form the hanging triangular cloth inside its named asset.
for i in range(12):
    u=(i+.5)/12
    width=.94/12
    drop=.43*(1-abs(2*u-1))
    block(table,"Linen hanging strip "+str(i),(width+.003,.018,max(.018,drop)),
          (-.47+u*.94,-.342,1.14-drop/2),(.83,.82,.74))
for i,x in enumerate([-.24,.21]):
    ell(table,"Brass saucer "+str(i),(x,-.05,1.18),(.12,.095,.018),GOLD)
    ell(table,"Small cup "+str(i),(x,-.05,1.22),(.045,.045,.044),(.73,.68,.47))
stick(table,"Candlestick",(.04,.14,1.17),(.04,.14,1.39),.018,GOLD)
ell(table,"Candlestick foot",(.04,.14,1.18),(.065,.065,.015),GOLD)
place(table,(-1.45,3.68,0))

pot=asset("Small brown wastepaper pot")
stick(pot,"Cylindrical body",(-2.18,3.55,.035),(-2.18,3.55,.29),.13,(.25,.12,.057))
ell(pot,"Dark mouth",(-2.18,3.55,.302),(.126,.126,.012),(.055,.032,.015))

spindle=asset("Black spindle chair behind bed")
for x in [-.23,.23]:
    for y in [-.23,.23]:
        stick(spindle,"Leg %.2f %.2f"%(x,y),(x,y,.05),(x,y,.64),.022,WOOD)
block(spindle,"Cane seat",(.53,.52,.055),(0,0,.64),(.32,.28,.17))
for x in [-.25,.25]:
    stick(spindle,"Back upright "+str(x),(x,.22,.61),(x,.22,1.37),.026,WOOD)
stick(spindle,"Top rail",(-.25,.22,1.37),(.25,.22,1.37),.039,WOOD)
for x in [-.15,-.05,.05,.15]:
    stick(spindle,"Back spindle "+str(x),(x,.22,.77),(x,.22,1.34),.012,WOOD)
place(spindle,(2.56,2.60,0),-8)

a=asset("Cropped round bedside table")
stick(a,"Drum cabinet",(3.31,-1.02,.09),(3.31,-1.02,.69),.37,(.052,.027,.015))
stick(a,"Circular top",(3.31,-1.02,.70),(3.31,-1.02,.75),.43,(.08,.038,.018))
stick(a,"Base molding",(3.31,-1.02,.08),(3.31,-1.02,.13),.40,(.075,.036,.018))
ell(a,"Drawer knob",(3.0,-1.23,.49),(.035,.025,.025),GOLD)

def rug(name,w,d,origin,angle):
    a=asset(name)
    block(a,"Rust outer field",(w,d,.018),(0,0,.012),(.30,.085,.049))
    block(a,"Ivory border",(w-.09,d-.09,.009),(0,0,.025),(.55,.45,.29))
    block(a,"Blue inner border",(w-.17,d-.17,.008),(0,0,.032),(.12,.19,.20))
    block(a,"Red central field",(w-.29,d-.29,.008),(0,0,.039),(.33,.095,.060))
    for i in range(11):
        x=-w/2+.12+(w-.24)*i/10
        for s in [-1,1]:
            block(a,"Border lozenge %d %d"%(i,s),(.045,.065,.007),
                  (x,s*(d/2-.10),.042),(.60,.48,.29))
    for i in range(5):
        for j in range(3):
            x,y=(i-2)*(w-.5)/5,(j-1)*(d-.45)/3
            n=block(a,"Woven motif %d %d"%(i,j),(.075,.075,.006),(x,y,.048),(.60,.47,.27))
            n.turn('z',45,pivot=(x,y,.048))
    place(a,origin,angle)
rug("Small rear Persian rug",1.55,.94,(-1.35,2.23,0),-3)
rug("Foreground cropped Persian rug",2.35,1.53,(1.05,-2.06,0),-4)

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    bs.inputs['Roughness'].default_value=.82
    c=tuple(bs.inputs['Base Color'].default_value)
    if all(abs(c[i]-WALL[i])<.015 for i in range(3)):
        nt=mat.node_tree
        geo=nt.nodes.new('ShaderNodeNewGeometry')
        sep=nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(geo.outputs['Position'],sep.inputs[0])
        def mathnode(op,a=None,b=None):
            n=nt.nodes.new('ShaderNodeMath')
            n.operation=op
            if hasattr(a,'node'):
                nt.links.new(a,n.inputs[0])
            elif a is not None:
                n.inputs[0].default_value=a
            if hasattr(b,'node'):
                nt.links.new(b,n.inputs[1])
            elif b is not None:
                n.inputs[1].default_value=b
            return n.outputs[0]
        horizontal=mathnode('ADD',sep.outputs['X'],sep.outputs['Y'])
        hphase=mathnode('MULTIPLY',horizontal,57)
        vphase=mathnode('MULTIPLY',sep.outputs['Z'],68)
        hs=mathnode('SINE',hphase)
        vs=mathnode('SINE',vphase)
        lattice=mathnode('MULTIPLY',hs,vs)
        lattice=mathnode('ABSOLUTE',lattice)
        noise=nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=95
        noise.inputs['Detail'].default_value=2
        nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
        fine=mathnode('MULTIPLY',noise.outputs['Fac'],.30)
        pattern=mathnode('ADD',mathnode('MULTIPLY',lattice,.7),fine)
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.20
        ramp.color_ramp.elements[0].color=(.12,.14,.095,1)
        ramp.color_ramp.elements[1].position=.73
        ramp.color_ramp.elements[1].color=(.37,.245,.135,1)
        e=ramp.color_ramp.elements.new(.46)
        e.color=(.245,.18,.105,1)
        nt.links.new(pattern,ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.10
        bump.inputs['Distance'].default_value=.008
        nt.links.new(pattern,bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])
    if c[0]>.9 and c[1]>.95 and c[2]>.95 and 'Emission Color' in bs.inputs:
        bs.inputs['Emission Color'].default_value=(.78,.91,1,1)
        bs.inputs['Emission Strength'].default_value=1.1

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.55,.60,.65,1)
background.inputs['Strength'].default_value=.17

set_view(position=(-4.8,-6.5,3.6),target=(.6,2.0,1.50),lens=42,sensor=36)
sc.camera.rotation_euler.rotate_axis('Z',math.radians(3))
area_emitter(position=(-.03,3.94,2.43),power=470,size=2.1,
             target=(-.4,.1,.6),color=(.84,.94,1))
area_emitter(position=(-2.7,3.98,2.5),power=300,size=1.8,
             target=(-1.2,.3,.8),color=(.86,.94,1))
area_emitter(position=(-2,-3.1,3.5),power=42,size=4,
             target=(1,1,1),color=(1,.90,.75))
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.35
# External runner saves and renders once.
