# Reference inventory: two tall white windows with green upper blinds occupy
# x=0-.44, y=.06-.64; oval gold portrait x=.13-.25,y=.16-.36.
# Small draped table and cropped cabinet sit below them. Painted blue/ochre
# screen x=.41-.61,y=.33-.64 stands behind the olive armchair.
# Armchair x=.28-.54,y=.50-.99 overlaps the bed's near foot.
# Bed x=.51-.99,y=.47-.98 has its head against the right wall; white pillows
# and duvet sit inside a dark wooden frame. Thin black chair is behind it.
# Small framed portraits, floor pot, two red rugs and cropped bedside table
# remain separate assets. Hidden furniture details are uncertain.
# Landmarks: central window top (.24,.08)-(.43,.10), sill (.27,.62)-(.44,.61);
# screen top (.415,.331)-(.609,.334); bed head rail (.72,.48)-(.97,.55);
# near foot post approximately (.58,.64)-(.57,.94).
#
# Revision ledger, comparing the supplied render to the photograph:
# Bed head/foot ordering is reversed: the rendered footboard faces the camera
# broadly on the right, while the reference shows the long side with its
# foot at the left. Rotate the complete bed about its center, preserving
# bedding membership and support heights.
# Armchair is too far right and faces almost straight forward. Move its
# complete group left and turn it to expose the right outer upholstered side.
# Windows and ceiling junction are too low/small together. A modest focal
# length increase with a small framing adjustment addresses these shared
# residuals; camera attribution remains nonunique.
# Wallpaper was absent on the rendered right wall because primitive Blender
# names do not preserve the semantic asset names. Assign its material by the
# deliberately unique wall finish instead. Preserve windows and trim.
# Expected effects: a left foot/right head bed silhouette, chair-screen
# overlap at center-left, less ceiling, and wallpaper on both wall planes.
# Expanded primitive estimate: about 330 meshes, including three rounded
# boxes (~78 primitives), ~65 screen/portrait forms and ~70 rug components.
import bpy, math
from sceneact import *

scene=Scene(name="Period bedroom")
white=(.92,.93,.89)
wood=(.075,.037,.021)
gold=(.52,.34,.09)
olive=(.25,.255,.065)
wallcolor=(.40,.31,.20)
black=(.023,.021,.016)

def asset(name):
    a=Asset(name=name);scene.include(name,a);return a
def bx(a,n,s,c,col):
    p=box(size=s,center=c,color=col);a.include(n,p);return p
def rd(a,n,r,p,q,col):
    t=rod(radius=r,start=p,end=q,color=col);a.include(n,t);return t
def ell(a,n,c,s,col):
    p=ball(radius=1,center=c,color=col)
    p.resize(s,pivot=c);a.include(n,p);return p
def soft(a,n,s,c,col):
    p=box(size=s,center=c,color=col);a.include(n,p);return p
def rounded(a,n,s,c,r,col):
    p=fillet_box(size=s,radius=r,center=c,color=col)
    a.include(n,p);return p

room=asset("Room architecture")
bx(room,"Floor",(8.2,10,.15),(-.9,-.2,-.09),(.48,.45,.39))
bx(room,"Back wallpaper",(7.2,.15,3.45),(-1.4,3.7,1.72),wallcolor)
bx(room,"Right wallpaper",(.15,9,3.45),(2.13,-.72,1.72),wallcolor)
bx(room,"Ceiling",(7.2,9,.12),(-1.4,-.72,3.48),(.88,.88,.84))
for z,d in [(3.32,.10),(3.38,.15),(3.43,.21)]:
    bx(room,"Back cornice "+str(z),(7.2,d,.075),(-1.4,3.55,z),white)
    bx(room,"Right cornice "+str(z),(d,9,.075),(1.98,-.72,z),white)
bx(room,"Back skirting",(7.2,.07,.18),(-1.4,3.57,.10),wood)
bx(room,"Right skirting",(.07,9,.18),(2.01,-.72,.10),wood)

def window(name,x,w):
    a=asset(name)
    bx(a,"Reveal",(w+.16,.13,2.66),(x,3.53,1.82),(.16,.18,.16))
    bx(a,"Bright lower glazing",(w,.08,2.51),(x,3.43,1.83),(.78,.91,.91))
    for xx in [x-w/2-.055,x+w/2+.055]:
        bx(a,"Outer jamb "+str(xx),(.10,.23,2.80),(xx,3.38,1.82),white)
    for z in [.43,3.20]:
        bx(a,"Horizontal frame "+str(z),(w+.21,.22,.10),(x,3.38,z),white)
    for xx in [x-w/2+.035,x+w/2-.035]:
        bx(a,"Inner stile "+str(xx),(.043,.07,2.58),(xx,3.28,1.82),white)
    bx(a,"Green roller blind",(w-.09,.055,1.34),(x,3.24,2.43),(.095,.29,.245))
    rd(a,"Blind lower bar",.018,(x-w/2+.04,3.20,1.76),(x+w/2-.04,3.20,1.76),(.30,.40,.32))
    bx(a,"Broad sill",(w+.34,.40,.09),(x,3.25,.44),white)
window("Central tall window",-1.53,1.13)
window("Cropped left window",-3.83,1.05)

door=asset("White door behind screen")
bx(door,"Door slab",(.60,.08,2.26),(.26,3.47,1.15),(.77,.80,.75))
for x in [-.08,.60]:
    bx(door,"Door casing "+str(x),(.075,.12,2.42),(x,3.39,1.21),white)
bx(door,"Top casing",(.75,.12,.08),(.26,3.39,2.40),white)
for z in [.72,1.72]:
    bx(door,"Panel "+str(z),(.44,.035,.72),(.26,3.40,z),(.84,.86,.81))

a=asset("Large oval oil portrait")
x,z=-2.74,2.40
ell(a,"Gold oval frame",(x,3.43,z),(.39,.055,.51),gold)
ell(a,"Dark canvas",(x,3.36,z),(.332,.027,.444),(.024,.025,.018))
ell(a,"Shoulders",(x,3.32,z-.17),(.19,.015,.14),(.055,.038,.025))
ell(a,"Face",(x,3.30,z+.075),(.082,.018,.107),(.36,.23,.13))
ell(a,"Hair",(x-.018,3.278,z+.13),(.078,.01,.063),(.035,.022,.015))

a=asset("Small back portrait")
bx(a,"Frame",(.46,.065,.64),(-.30,3.45,2.59),gold)
bx(a,"Ivory mount",(.415,.027,.595),(-.30,3.40,2.59),(.83,.82,.69))
ell(a,"Grey portrait",(-.30,3.375,2.59),(.11,.012,.20),(.34,.34,.29))
ell(a,"Face",(-.30,3.357,2.65),(.046,.009,.074),(.61,.59,.50))

a=asset("Right wall portrait")
bx(a,"Gold frame",(.065,.41,.62),(2.015,2.64,2.59),gold)
bx(a,"Cream mount",(.025,.37,.58),(1.97,2.64,2.59),(.83,.81,.69))
ell(a,"Oval portrait",(1.947,2.64,2.59),(.012,.105,.22),(.34,.32,.28))

cab=asset("Cropped left cabinet")
bx(cab,"Carcase",(1.04,.56,.67),(-3.78,2.91,.47),wood)
bx(cab,"Polished top",(1.13,.63,.075),(-3.78,2.89,.85),(.11,.065,.034))
for x in [-4.20,-3.37]:
    for y in [2.68,3.10]:
        rd(cab,"Leg "+str((x,y)),.037,(x,y,.04),(x,y,.50),wood)
for x in [-4.04,-3.56]:
    bx(cab,"Drawer "+str(x),(.44,.045,.23),(x,2.60,.62),(.105,.056,.028))
    ell(cab,"Brass knob "+str(x),(x,2.56,.62),(.025,.018,.025),gold)
bx(cab,"Standing frame",(.25,.045,.32),(-3.76,2.86,1.045),gold)
bx(cab,"Framed miniature",(.20,.025,.27),(-3.76,2.83,1.045),(.065,.075,.045))

table=asset("Draped side table")
bx(table,"Table top",(.68,.51,.065),(-2.65,2.85,.79),wood)
for x in [-2.91,-2.39]:
    for y in [2.64,3.03]:
        rd(table,"Leg "+str((x,y)),.025,(x,y,.05),(x,y,.78),wood)
bx(table,"Linen top",(.70,.54,.025),(-2.65,2.85,.838),white)
# Three overlapping flat tapered cloth strips approximate the pointed drape
# entirely within the editable SceneAct table asset.
for i,(w,z) in enumerate([(.61,.77),(.43,.66),(.22,.55)]):
    bx(table,"Hanging linen "+str(i),(w,.018,.15),(-2.65,2.565,z),white)
for i,x in enumerate([-2.82,-2.52]):
    ell(table,"Saucer "+str(i),(x,2.82,.87),(.075,.06,.012),(.71,.70,.58))
    ell(table,"Cup "+str(i),(x,2.82,.902),(.035,.035,.035),(.74,.71,.55))

pot=asset("Small floor pot")
rd(pot,"Terracotta vessel",.105,(-3.14,2.59,.02),(-3.14,2.59,.23),(.32,.16,.075))
rd(pot,"Rim",.119,(-3.14,2.59,.215),(-3.14,2.59,.25),(.40,.23,.11))

screen=asset("Decorative painted screen")
for i,x in enumerate([-.47,.12]):
    bx(screen,"Panel "+str(i),(.59,.065,1.68),(x,2.56,1.22),(.57,.40,.15))
    for xx in [x-.29,x+.29]:
        rd(screen,"Edging "+str((i,xx)),.017,(xx,2.51,.38),(xx,2.51,2.06),wood)
    for j,(dx,z,sx,sz) in enumerate([(-.13,1.73,.20,.19),(.11,1.20,.22,.35),(-.13,.65,.18,.25)]):
        ell(screen,"Cobalt painted form "+str((i,j)),(x+dx,2.516,z),(sx,.012,sz),(.025,.075,.43))
    for j in range(4):
        ell(screen,"Ochre leaf "+str((i,j)),(x+.12*math.sin(j*2),2.497,.64+j*.32),(.085,.009,.14),(.70,.33,.07))
    for j in range(5):
        ell(screen,"Green leaf "+str((i,j)),(x-.16+j*.065,2.486,1.73+.12*math.sin(j)),(.025,.006,.065),(.13,.32,.18))
        ell(screen,"Gold dot "+str((i,j)),(x-.23+j*.105,2.487,1.96),(.012,.006,.014),(.18,.14,.08))
screen.resize((1.20,1,1),pivot=(-.175,2.56,.38))

bed=asset("Dark wooden double bed")
bx(bed,"Bedstead base",(1.92,2.47,.25),(1.02,.79,.35),wood)
rounded(bed,"Mattress",(1.82,2.32,.25),(1.02,.78,.61),.10,(.75,.74,.64))
ell(bed,"Soft ivory duvet",(1.02,.68,.76),(.93,1.13,.20),(.79,.79,.70))
bx(bed,"Duvet central surface",(1.72,1.96,.11),(1.02,.68,.81),(.79,.79,.70))
ell(bed,"Duvet rounded foot",(1.02,-.38,.72),(.92,.28,.16),(.79,.79,.70))
for x in [.08,1.96]:
    bx(bed,"Side rail "+str(x),(.09,2.48,.18),(x,.78,.44),wood)
    for y in [-.47,2.04]:
        h=1.22 if y<0 else 1.40
        rd(bed,"Post "+str((x,y)),.063,(x,y,.04),(x,y,h),wood)
        ell(bed,"Finial "+str((x,y)),(x,y,h+.02),(.08,.08,.08),wood)
bx(bed,"Headboard panel",(1.90,.11,.53),(1.02,2.06,1.10),(.10,.052,.026))
rd(bed,"Headboard upper rail",.065,(.05,2.04,1.43),(1.99,2.04,1.43),wood)
bx(bed,"Footboard panel",(1.90,.105,.57),(1.02,-.48,.71),(.075,.040,.023))
rd(bed,"Footboard top rail",.055,(.06,-.49,1.04),(1.98,-.49,1.04),wood)
for z in [.52,.88]:
    bx(bed,"Footboard molding "+str(z),(1.76,.024,.027),(1.02,-.548,z),(.16,.086,.041))
for i,x in enumerate([.56,1.42]):
    p=rounded(bed,"Pillow "+str(i),(.81,.61,.20),(x,1.59,.99),.09,(.84,.85,.78))
    p.turn(axis='x',degrees=22,pivot=(x,1.59,.99))
    ell(bed,"Pillow crown "+str(i),(x,1.56,1.10),(.37,.26,.09),(.84,.85,.78))
# Head now faces the right wall; foot occupies the left foreground.
bed.turn(axis='z',degrees=-90,pivot=(1.02,.79,0))
bed.move((-.32,-.24,0))

chair=asset("Olive upholstered armchair")
cx,cy=-.83,-.12
ell(chair,"Seat cushion",(cx,cy,.53),(.47,.43,.12),olive)
bx(chair,"Lower apron",(.90,.79,.23),(cx,cy,.37),(.20,.20,.043))
ell(chair,"High rounded back",(cx,cy+.36,.99),(.49,.15,.57),(.24,.25,.060))
ell(chair,"Back crest",(cx+.03,cy+.34,1.37),(.30,.13,.25),(.25,.26,.065))
for x in [cx-.48,cx+.48]:
    ell(chair,"Upholstered arm "+str(x),(x,cy-.02,.79),(.13,.49,.33),(.22,.22,.050))
    rd(chair,"Arm piping "+str(x),.022,(x,cy-.43,.83),(x,cy+.30,1.20),(.34,.33,.10))
    for y in [cy-.32,cy+.28]:
        rd(chair,"Leg "+str((x,y)),.033,(x,y,.03),(x,y,.31),wood)
for row in range(3):
    for col in range(3):
        ell(chair,"Tuft "+str((row,col)),(cx-.23+col*.23,cy+.205,.91+row*.18),(.023,.012,.025),(.12,.14,.028))
chair.turn(axis='z',degrees=-39,pivot=(cx,cy,0))
chair.resize((1.08,1.08,1.03),pivot=(cx,cy,0))
chair.move((-1.04,.06,0))

thin=asset("Black spindle chair")
for x in [.39,.77]:
    for y in [2.55,2.93]:
        rd(thin,"Leg "+str((x,y)),.018,(x,y,.03),(x,y,.58),black)
bx(thin,"Seat",(.46,.44,.045),(.58,2.74,.59),(.10,.085,.047))
for x in [.37,.79]:
    rd(thin,"Upright "+str(x),.021,(x,2.96,.53),(x,2.96,1.30),black)
rd(thin,"Top rail",.026,(.37,2.96,1.30),(.79,2.96,1.30),black)
for x in [.45,.53,.61,.69]:
    rd(thin,"Spindle "+str(x),.010,(x,2.96,.67),(x,2.96,1.28),black)

night=asset("Cropped round bedside table")
rd(night,"Round top",.38,(2.05,-.65,.70),(2.05,-.65,.76),wood)
rd(night,"Pedestal",.07,(2.05,-.65,.06),(2.05,-.65,.70),wood)
rd(night,"Round base",.29,(2.05,-.65,.025),(2.05,-.65,.085),wood)

def rug(name,cx,cy,w,h):
    a=asset(name)
    bx(a,"Woven ground",(w,h,.012),(cx,cy,.012),(.32,.13,.09))
    for inset,col in [(.04,(.61,.48,.28)),(.085,(.12,.23,.25)),(.13,(.65,.47,.30)),(.17,(.43,.18,.13))]:
        for sign in [-1,1]:
            bx(a,"Long border "+str((inset,sign)),(.025,h-2*inset,.007),(cx+sign*(w/2-inset),cy,.022),col)
            bx(a,"Short border "+str((inset,sign)),(w-2*inset,.025,.007),(cx,cy+sign*(h/2-inset),.022),col)
    for i in range(4):
        for j in range(5):
            x=cx+(i-1.5)*(w-.42)/4
            y=cy+(j-2)*(h-.42)/5
            p=bx(a,"Woven diamond "+str((i,j)),(.065,.065,.006),(x,y,.027),(.69,.51,.30))
            p.turn(axis='z',degrees=45,pivot=(x,y,.027))
rug("Small back rug",-2.00,1.65,1.13,1.17)
rug("Foreground patterned rug",.15,-1.55,1.80,.95)

realize(scene)

# Match the unique finish, since emitted primitive names are generic.
wallmat=bpy.data.materials.new("Warm patterned wallpaper")
wallmat.use_nodes=True
n=wallmat.node_tree.nodes;l=wallmat.node_tree.links
bs=n.get("Principled BSDF")
bs.inputs["Roughness"].default_value=.94
tc=n.new("ShaderNodeTexCoord")
sep=n.new("ShaderNodeSeparateXYZ")
l.new(tc.outputs["Geometry"] if "Geometry" in tc.outputs else tc.outputs["Generated"],sep.inputs[0])
# World coordinates keep motif scale compatible on perpendicular walls.
geo=n.new("ShaderNodeNewGeometry")
noise=n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=31
noise.inputs["Detail"].default_value=2
noise.inputs["Roughness"].default_value=.65
l.new(geo.outputs["Position"],noise.inputs["Vector"])
r=n.new("ShaderNodeValToRGB")
r.color_ramp.elements[0].position=.24
r.color_ramp.elements[0].color=(.13,.17,.15,1)
r.color_ramp.elements[1].position=.76
r.color_ramp.elements[1].color=(.41,.28,.16,1)
e=r.color_ramp.elements.new(.45);e.color=(.30,.24,.16,1)
e=r.color_ramp.elements.new(.58);e.color=(.43,.32,.20,1)
l.new(noise.outputs["Fac"],r.inputs[0])
l.new(r.outputs[0],bs.inputs["Base Color"])
for ob in bpy.data.objects:
    if ob.type!='MESH':continue
    iswall=False
    for m in ob.data.materials:
        if m is None:continue
        c=m.diffuse_color[:3]
        if max(abs(c[k]-wallcolor[k]) for k in range(3))<.012:
            iswall=True
        if m.use_nodes:
            p=m.node_tree.nodes.get("Principled BSDF")
            if p:p.inputs["Roughness"].default_value=.82
    if iswall:
        ob.data.materials.clear();ob.data.materials.append(wallmat)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get("Background")
if background is None:background=nodes.new("ShaderNodeBackground")
output=nodes.get("World Output")
if output is None:output=nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.62,.69,.76,1)
background.inputs["Strength"].default_value=.20
set_view(position=(-3.65,-5.65,2.70),target=(-.83,1.63,1.36),lens=40,sensor=36)
area_emitter(position=(-1.55,3.05,2.35),power=350,size=1.6,target=(-.55,-.3,.7),color=(.83,.93,1))
area_emitter(position=(-3.65,2.95,2.3),power=190,size=1.5,target=(-1,-.8,.5),color=(.86,.94,1))
area_emitter(position=(-1.7,-3.2,3.1),power=35,size=4,target=(.2,1.5,.8),color=(1,.88,.73))
sc.view_settings.view_transform='AgX'
