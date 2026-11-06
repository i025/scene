# Reference inventory (normalized image coordinates):
# Architecture: patterned back wall (0,.03)-(.58,.64), patterned right wall
# (.56,0)-(1,.73), pale floor (0,.61)-(1,1), white cornice across upper edge.
# Two tall windows: cropped left (0,.06)-(.13,.62), central (.24,.08)-(.44,.64).
# Dark green roller blinds, bright lower glazing, thick white frames and reveals.
# Bed (.51,.47)-(.99,.98): dark wood headboard, tall footboard, white bedding,
# two pillows; right edge partly cropped. Armchair (.28,.50)-(.54,.97) overlaps
# bed foot and painted screen (.41,.33)-(.61,.64).
# Left furniture: cropped dark cabinet, small draped table, terracotta pot.
# Pictures: gold oval portrait (.13,.16)-(.25,.36), small pale rectangular
# portrait (.47,.15)-(.54,.28), narrow oval picture (.66,.16)-(.71,.30).
# Thin black chair (.61,.47)-(.70,.65) is partly hidden behind the bed.
# Rugs: small red patterned runner (.20,.64)-(.36,.77), cropped foreground rug.
# Landmarks: central window upper corners (.25,.09),(.42,.10); window sill
# (.27,.62)-(.44,.61); screen upper edge (.415,.331)-(.609,.334);
# headboard rail (.72,.48)-(.97,.55); footboard post (.58,.64)-(.57,.94).
# Wall corner location is uncertain behind the screen and doorway.
# Coarse geometry is established before decoration; bed/chair overlap is deliberate.
# Primitive estimate: approximately 240 meshes, including ~70 rug details,
# ~30 screen ornaments, 30 chair components, and architectural trim.
import bpy, math, random
from mathutils import Vector
from sceneact import *

random.seed(8)
scene = Scene(name="Period bedroom")
cream=(.86,.85,.78)
white=(.92,.93,.89)
wood=(.075,.037,.021)
gold=(.52,.34,.09)
olive=(.25,.255,.065)
black=(.023,.021,.016)

def asset(name):
    a=Asset(name=name)
    scene.include(name,a)
    return a
def bx(a,n,s,c,col):
    p=box(size=s,center=c,color=col); a.include(n,p); return p
def rd(a,n,r,p,q,col):
    t=rod(radius=r,start=p,end=q,color=col);a.include(n,t);return t
def ell(a,n,c,s,col):
    p=ball(radius=1,center=c,color=col)
    p.resize(s,pivot=c);a.include(n,p);return p
def fb(a,n,s,c,r,col):
    p=fillet_box(size=s,radius=r,center=c,color=col);a.include(n,p);return p

room=asset("Room architecture")
bx(room,"Floor",(8.2,10,.15),(-.9,-.2,-.09),(.48,.45,.39))
bx(room,"Back patterned wall",(7.2,.15,3.45),(-1.4,3.7,1.72),(.40,.31,.20))
bx(room,"Right patterned wall",(.15,9,3.45),(2.13,-.72,1.72),(.40,.31,.20))
bx(room,"Ceiling",(7.2,9,.12),(-1.4,-.72,3.48),(.88,.88,.84))
for z,d in [(3.32,.10),(3.38,.15),(3.43,.21)]:
    bx(room,"Back cornice "+str(z),(7.2,d,.075),(-1.4,3.55,z),white)
    bx(room,"Right cornice "+str(z),(d,9,.075),(1.98,-.72,z),white)
bx(room,"Back skirting",(7.2,.07,.18),(-1.4,3.57,.10),(.36,.28,.20))
bx(room,"Right skirting",(.07,9,.18),(2.01,-.72,.10),(.36,.28,.20))

# Window assemblies sit in front of the wall, with bright glazing and white reveals.
def window(name,x,w):
    a=asset(name)
    bx(a,"Dark reveal",(w+.16,.13,2.66),(x,3.53,1.82),(.16,.18,.16))
    bx(a,"Daylit glazing",(w,.08,2.51),(x,3.43,1.83),(.78,.91,.91))
    for xx in [x-w/2-.055,x+w/2+.055]:
        bx(a,"Outer jamb "+str(xx),(.10,.23,2.80),(xx,3.38,1.82),white)
    for z in [.43,3.20]:
        bx(a,"Frame lintel "+str(z),(w+.21,.22,.10),(x,3.38,z),white)
    bx(a,"Inner left stile",(.043,.07,2.58),(x-w/2+.035,3.28,1.82),(.74,.78,.74))
    bx(a,"Inner right stile",(.043,.07,2.58),(x+w/2-.035,3.28,1.82),white)
    bx(a,"Green roller blind",(w-.09,.055,1.34),(x,3.24,2.43),(.095,.29,.245))
    rd(a,"Blind lower bar",.018,(x-w/2+.04,3.20,1.76),(x+w/2-.04,3.20,1.76),(.30,.40,.32))
    bx(a,"Broad sill",(w+.34,.40,.09),(x,3.25,.44),white)
    return a
window("Central tall window",-1.53,1.13)
window("Cropped left window",-3.83,1.05)

door=asset("White door behind screen")
bx(door,"Door slab",(.60,.08,2.26),(.26,3.47,1.15),(.77,.80,.75))
for x in [-.08,.60]:
    bx(door,"Door casing"+str(x),(.075,.12,2.42),(x,3.39,1.21),white)
bx(door,"Door top casing",(.75,.12,.08),(.26,3.39,2.40),white)
for z in [.72,1.72]:
    bx(door,"Inset panel"+str(z),(.44,.035,.72),(.26,3.40,z),(.84,.86,.81))

def oval_picture(name,x,z,w,h):
    a=asset(name)
    # Ellipsoids face toward the room; gold outer silhouette surrounds dark canvas.
    ell(a,"Gold oval frame",(x,3.43,z),(w/2,.055,h/2),gold)
    ell(a,"Inset dark canvas",(x,3.36,z),(w*.425,.027,h*.435),(.034,.035,.025))
    ell(a,"Portrait shoulders",(x,3.32,z-h*.17),(w*.24,.015,h*.14),(.075,.055,.037))
    ell(a,"Portrait head",(x,3.30,z+h*.075),(w*.105,.018,h*.105),(.42,.28,.16))
    ell(a,"Dark hair",(x-.018,3.287,z+h*.13),(w*.10,.01,h*.062),(.055,.036,.021))
    return a
oval_picture("Large oval oil portrait",-2.74,2.40,.78,1.02)
def small_picture(name,x,z,w,h):
    a=asset(name)
    bx(a,"Gold frame",(w,.065,h),(x,3.45,z),gold)
    bx(a,"Ivory mount",(w-.045,.027,h-.045),(x,3.40,z),(.83,.82,.69))
    ell(a,"Grey portrait",(x,3.375,z),(w*.24,.012,h*.31),(.34,.34,.29))
    ell(a,"Pale face",(x,3.357,z+h*.09),(w*.10,.009,h*.115),(.61,.59,.50))
small_picture("Small back portrait",-.30,2.59,.46,.64)

# A small framed oval hangs on the right wall.
a=asset("Right wall portrait")
bx(a,"Slim gold rectangular frame",(.065,.41,.62),(2.015,2.64,2.59),gold)
bx(a,"Cream mount",(.025,.37,.58),(1.97,2.64,2.59),(.83,.81,.69))
ell(a,"Oval portrait",(1.947,2.64,2.59),(.012,.105,.22),(.34,.32,.28))

cab=asset("Cropped left cabinet")
bx(cab,"Carcase",(1.04,.56,.67),(-3.78,2.91,.47),wood)
bx(cab,"Polished top",(1.13,.63,.075),(-3.78,2.89,.85),(.11,.065,.034))
for x in [-4.20,-3.37]:
    for y in [2.68,3.10]:
        rd(cab,"Leg"+str((x,y)),.037,(x,y,.04),(x,y,.50),wood)
for x in [-4.04,-3.56]:
    bx(cab,"Drawer"+str(x),(.44,.045,.23),(x,2.60,.62),(.105,.056,.028))
    ell(cab,"Brass knob"+str(x),(x,2.56,.62),(.025,.018,.025),gold)
bx(cab,"Small standing frame",(.25,.045,.32),(-3.76,2.86,1.045),gold)
bx(cab,"Small framed image",(.20,.025,.27),(-3.76,2.83,1.045),(.065,.075,.045))

table=asset("Draped side table")
bx(table,"Table top",(.68,.51,.065),(-2.65,2.85,.79),wood)
for x in [-2.91,-2.39]:
    for y in [2.64,3.03]:
        rd(table,"Slender leg"+str((x,y)),.025,(x,y,.05),(x,y,.78),wood)
# White cloth has a broad top and hanging triangular front.
bx(table,"Linen top",(.70,.54,.025),(-2.65,2.85,.838),white)
# Use a tapered flat mesh for the visible pointed cloth.
verts=[(-3.01,2.56,.84),(-2.29,2.56,.84),(-2.65,2.54,.43)]
mesh=bpy.data.meshes.new("Cloth pending")
# Mesh creation is deferred until after realize, which clears Blender.
for i,x in enumerate([-2.82,-2.52]):
    ell(table,"Tea saucer"+str(i),(x,2.82,.87),(.075,.06,.012),(.71,.70,.58))
    ell(table,"Teacup"+str(i),(x,2.82,.902),(.035,.035,.035),(.74,.71,.55))
pot=asset("Small floor pot")
rd(pot,"Terracotta vessel",.105,(-3.14,2.59,.02),(-3.14,2.59,.23),(.32,.16,.075))
rd(pot,"Rim",.119,(-3.14,2.59,.215),(-3.14,2.59,.25),(.40,.23,.11))

# Painted two-panel screen, partly behind the chair and beside the bed.
screen=asset("Decorative painted screen")
for i,x in enumerate([-.47,.12]):
    bx(screen,"Panel "+str(i),(.59,.065,1.68),(x,2.56,1.22),(.57,.40,.15))
    for xx in [x-.29,x+.29]:
        rd(screen,"Panel edging"+str((i,xx)),.017,(xx,2.51,.38),(xx,2.51,2.06),wood)
    # Large organized cobalt shapes and stylized orange/green motifs.
    for j,(dx,z,sx,sz) in enumerate([(-.13,1.73,.20,.19),(.11,1.20,.22,.35),(-.13,.65,.18,.25)]):
        ell(screen,"Blue painted form"+str((i,j)),(x+dx,2.516,z),(sx,.012,sz),(.025,.075,.43))
    for j in range(4):
        zz=.64+j*.32
        ell(screen,"Ochre leaf"+str((i,j)),(x+.12*math.sin(j*2),2.497,zz),(.085,.009,.14),(.70,.33,.07))
    for j in range(5):
        ell(screen,"Small leaf"+str((i,j)),(x-.16+j*.065,2.486,1.73+.12*math.sin(j)),(.025,.006,.065),(.13,.32,.18))
    for j in range(5):
        ell(screen,"Gold dot"+str((i,j)),(x-.23+j*.105,2.487,1.96),(.012,.006,.014),(.18,.14,.08))

# Bed: longitudinal axis points from the head at y=2.4 toward the foreground.
bed=asset("Dark wooden double bed")
bx(bed,"Bedstead base",(1.92,2.47,.25),(1.02,.79,.35),wood)
fb(bed,"Mattress",(1.82,2.32,.25),(1.02,.78,.61),.10,(.75,.74,.64))
fb(bed,"Ivory coverlet",(1.86,2.25,.19),(1.02,.68,.78),.075,(.83,.83,.74))
# Thick hanging sides are soft forms rather than a rigid white block.
ell(bed,"Duvet rounded foot",(1.02,-.38,.72),(.92,.28,.16),(.83,.83,.74))
for x in [.08,1.96]:
    bx(bed,"Side rail"+str(x),(.09,2.48,.18),(x,.78,.44),wood)
    for y in [-.47,2.04]:
        rd(bed,"Bed post"+str((x,y)),.063,(x,y,.04),(x,y,1.22 if y<0 else 1.40),wood)
        ell(bed,"Post finial"+str((x,y)),(x,y,1.24 if y<0 else 1.42),(.08,.08,.08),wood)
bx(bed,"Headboard solid panel",(1.90,.11,.53),(1.02,2.06,1.10),(.10,.052,.026))
rd(bed,"Headboard upper rail",.065,(.05,2.04,1.43),(1.99,2.04,1.43),wood)
bx(bed,"Footboard panel",(1.90,.105,.57),(1.02,-.48,.71),(.075,.040,.023))
rd(bed,"Footboard top rail",.055,(.06,-.49,1.04),(1.98,-.49,1.04),wood)
for z in [.52,.88]:
    bx(bed,"Footboard carved horizontal"+str(z),(1.76,.024,.027),(1.02,-.548,z),(.16,.086,.041))
for i,x in enumerate([.56,1.42]):
    p=fb(bed,"Large pillow"+str(i),(.81,.61,.20),(x,1.59,.99),.09,(.86,.87,.80))
    p.turn(axis='x',degrees=22,pivot=(x,1.59,.99))
    ell(bed,"Pillow crown"+str(i),(x,1.56,1.10),(.37,.26,.09),(.86,.87,.80))

# Upholstered olive armchair, rotated slightly so the open seat faces the viewer.
chair=asset("Olive upholstered armchair")
cx,cy=-.83,-.12
fb(chair,"Seat cushion",(.91,.86,.20),(cx,cy,.52),.09,olive)
fb(chair,"Lower upholstered apron",(.94,.83,.23),(cx,cy,.37),.08,(.20,.20,.043))
# Broad scalloped back and side wings.
ell(chair,"High rounded back",(cx,cy+.36,.99),(.49,.15,.57),(.26,.27,.075))
ell(chair,"Back crest",(cx+.03,cy+.34,1.37),(.30,.13,.25),(.27,.28,.077))
for x in [cx-.48,cx+.48]:
    ell(chair,"Arm body"+str(x),(x,cy-.02,.79),(.13,.49,.33),(.24,.24,.060))
    rd(chair,"Upholstered arm piping"+str(x),.025,(x,cy-.43,.83),(x,cy+.30,1.20),(.38,.36,.12))
    for y in [cy-.32,cy+.28]:
        rd(chair,"Short wood leg"+str((x,y)),.033,(x,y,.03),(x,y,.31),wood)
for row in range(3):
    for col in range(3):
        x=cx-.23+col*.23
        z=.91+row*.18
        ell(chair,"Back tuft"+str((row,col)),(x,cy+.205,z),(.023,.012,.025),(.13,.15,.032))
chair.turn(axis='z',degrees=-13,pivot=(cx,cy,.0))

thin=asset("Black spindle chair")
for x in [.39,.77]:
    for y in [2.55,2.93]:
        rd(thin,"Leg"+str((x,y)),.018,(x,y,.03),(x,y,.58),black)
bx(thin,"Seat",(.46,.44,.045),(.58,2.74,.59),(.10,.085,.047))
for x in [.37,.79]:
    rd(thin,"Back upright"+str(x),.021,(x,2.96,.53),(x,2.96,1.30),black)
rd(thin,"Top rail",.026,(.37,2.96,1.30),(.79,2.96,1.30),black)
for x in [.45,.53,.61,.69]:
    rd(thin,"Back spindle"+str(x),.010,(x,2.96,.67),(x,2.96,1.28),black)

night=asset("Cropped round bedside table")
rd(night,"Round dark top",.38,(2.26,.15,.70),(2.26,.15,.76),wood)
rd(night,"Pedestal",.07,(2.26,.15,.06),(2.26,.15,.70),wood)
rd(night,"Round base",.29,(2.26,.15,.025),(2.26,.15,.085),wood)

def rug(name,cx,cy,w,h):
    a=asset(name)
    bx(a,"Woven ground",(w,h,.012),(cx,cy,.012),(.32,.13,.09))
    for inset,col in [(.04,(.61,.48,.28)),(.085,(.12,.23,.25)),(.13,(.65,.47,.30)),(.17,(.43,.18,.13))]:
        bx(a,"Long border left"+str(inset),(.025,h-2*inset,.007),(cx-w/2+inset,cy,.022),col)
        bx(a,"Long border right"+str(inset),(.025,h-2*inset,.007),(cx+w/2-inset,cy,.022),col)
        bx(a,"Short border near"+str(inset),(w-2*inset,.025,.007),(cx,cy-h/2+inset,.022),col)
        bx(a,"Short border far"+str(inset),(w-2*inset,.025,.007),(cx,cy+h/2-inset,.022),col)
    for i in range(4):
        for j in range(5):
            x=cx+(i-1.5)*(w-.42)/4
            y=cy+(j-2)*(h-.42)/5
            p=bx(a,"Woven diamond"+str((i,j)),(.065,.065,.006),(x,y,.027),(.69,.51,.30))
            p.turn(axis='z',degrees=45,pivot=(x,y,.027))
rug("Small back rug",-1.77,1.33,1.13,1.17)
rug("Foreground patterned rug",.65,-1.55,1.80,.95)

realize(scene)

# Complete the small cloth as a separate semantic Blender object after realization.
me=bpy.data.meshes.new("Pointed linen mesh")
me.from_pydata(verts,[],[(0,1,2)])
me.update()
ob=bpy.data.objects.new("Draped side table - pointed linen",me)
bpy.context.collection.objects.link(ob)
mat=bpy.data.materials.new("White linen")
mat.diffuse_color=(*white,1)
ob.data.materials.append(mat)
sol=ob.modifiers.new("Linen thickness",'SOLIDIFY');sol.thickness=.006

# Restrained procedural wallpaper: warm ground with small organized faded motifs.
wallmat=bpy.data.materials.new("Faded ochre and blue floral wallpaper")
wallmat.use_nodes=True
n=wallmat.node_tree.nodes; l=wallmat.node_tree.links
bs=n.get("Principled BSDF")
bs.inputs["Roughness"].default_value=.93
tex=n.new("ShaderNodeTexCoord")
mapping=n.new("ShaderNodeVectorMath");mapping.operation='MULTIPLY'
mapping.inputs[1].default_value=(15,15,20)
l.new(tex.outputs["Generated"],mapping.inputs[0])
noise=n.new("ShaderNodeTexNoise");noise.inputs["Scale"].default_value=5
noise.inputs["Detail"].default_value=2
l.new(mapping.outputs[0],noise.inputs["Vector"])
r=n.new("ShaderNodeValToRGB")
r.color_ramp.elements.remove(r.color_ramp.elements[1])
for pos,col in [(0,(.10,.16,.15,1)),(.33,(.24,.25,.18,1)),(.48,(.43,.30,.17,1)),(.62,(.49,.36,.22,1)),(.77,(.25,.29,.24,1)),(1,(.58,.43,.26,1))]:
    e=r.color_ramp.elements[0] if pos==0 else r.color_ramp.elements.new(pos)
    e.color=col
l.new(noise.outputs["Fac"],r.inputs[0]);l.new(r.outputs[0],bs.inputs["Base Color"])
for ob in bpy.data.objects:
    if ob.type=='MESH' and ("patterned wall" in ob.name.lower()):
        ob.data.materials.clear();ob.data.materials.append(wallmat)

# Fabric roughness and gentle geometric irregularity preserve broad silhouettes.
for ob in bpy.data.objects:
    if ob.type!='MESH': continue
    for m in ob.data.materials:
        if m and m.use_nodes:
            p=m.node_tree.nodes.get('Principled BSDF')
            if p:p.inputs['Roughness'].default_value=.77
    if any(s in ob.name.lower() for s in ['pillow','coverlet','duvet']):
        sub=ob.modifiers.new("Soft fabric surface",'SUBSURF');sub.levels=2
        t=bpy.data.textures.new(ob.name+" subtle folds",type='CLOUDS')
        t.noise_scale=.16;t.noise_depth=1
        dis=ob.modifiers.new("Gentle bedding folds",'DISPLACE')
        dis.texture=t;dis.strength=.018;dis.texture_coords='GLOBAL'

sc=bpy.context.scene
if sc.world is None:sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get('Background')
if background is None:background=nodes.new('ShaderNodeBackground')
output=nodes.get('World Output')
if output is None:output=nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.62,.69,.76,1)
background.inputs['Strength'].default_value=.32
set_view(position=(-3.65,-5.65,2.70),target=(-.55,1.63,1.44),lens=36,sensor=36)
area_emitter(position=(-1.55,3.05,2.35),power=430,size=1.6,target=(-.55,-.3,.7),color=(.83,.93,1))
area_emitter(position=(-3.65,2.95,2.3),power=230,size=1.5,target=(-1,-.8,.5),color=(.86,.94,1))
area_emitter(position=(-1.7,-3.2,3.1),power=75,size=4,target=(.2,1.5,.8),color=(1,.88,.73))
sc.view_settings.view_transform='AgX'
