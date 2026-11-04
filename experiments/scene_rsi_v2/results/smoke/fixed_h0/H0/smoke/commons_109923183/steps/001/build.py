import bpy, math, random
from mathutils import Vector
from sceneact import *

random.seed(12)
scene = Scene("French chaise in paneled room")
ivory = (.74,.68,.56)
wood = (.30,.36,.29)
gold = (.57,.49,.32)
cream = (.69,.66,.56)

def add(name, node):
    scene.include(name, node)
    return node

def tube(name, pts, radius, color):
    return add(name, sweep_tube(points=pts, radius=radius, color=color))

# Dark parquet, laid in alternating blocks and turned diagonally.
add("floor foundation", box((12,12,.12), center=(0,0,-.08), color=(.16,.09,.055)))
a = math.radians(45)
for i in range(-7,8):
    for j in range(-7,8):
        for k in range(5):
            u = i*.65
            v = j*.65
            if (i+j)%2:
                u += (k+.5)*.13
                v += .325
                dims = (.127,.647,.022)
            else:
                u += .325
                v += (k+.5)*.13
                dims = (.647,.127,.022)
            x,y = u*math.cos(a)-v*math.sin(a), u*math.sin(a)+v*math.cos(a)
            tone = random.uniform(.78,1.18)
            p = box(dims, center=(x,y,-.009),
                    color=(.22*tone,.123*tone,.072*tone))
            p.turn('z',45)
            add(f"parquet {i} {j} {k}",p)

# Room joinery.
add("back wall",box((7,.16,3.8),center=(0,1.16,1.9),color=(.70,.68,.61)))
add("right return",box((.16,2.6,3.8),center=(2.0,2.34,1.9),color=(.73,.72,.66)))
for z,depth,h in [(.10,.12,.18),(.22,.055,.035),(1.70,.07,.045),
                  (1.77,.10,.045),(1.88,.065,.035),(2.15,.05,.025)]:
    add("horizontal molding "+str(z),box((6,depth,h),center=(0,1.035,z),color=cream))

def wall_frame(name,x,z,w,h):
    for inset,r in [(0,.016),(.036,.008),(.057,.006)]:
        xx=w/2-inset
        zz=h/2-inset
        for sx in [-1,1]:
            add(name+" vertical "+str(inset)+str(sx),
                box((r*1.6,.025,h-2*inset),center=(x+sx*xx,1.055,z),color=(.76,.73,.64)))
        for sz in [-1,1]:
            add(name+" horizontal "+str(inset)+str(sz),
                box((w-2*inset,.025,r*1.6),center=(x,1.055,z+sz*zz),color=(.76,.73,.64)))
wall_frame("large panel",.03,.98,3.20,1.12)
for x in [-1.16,.46,1.82]:
    add("door fine seam "+str(x),box((.008,.012,3),center=(x,1.065,1.65),color=(.30,.29,.25)))
for x in [-.97,-.88]:
    p=ball(.021,center=(x,1.005,1.91),color=(.16,.13,.085))
    p.resize((.65,.65,1.7))
    add("small antique latch "+str(x),p)

# Window and long curtains at the left margin.
add("window bright opening",box((.08,2.8,3.6),center=(-2.04,-.1,1.8),color=(.94,.94,.88)))
for j in range(17):
    y = -.74+j*.095
    p=rod(.055,start=(-1.94+math.sin(j*1.7)*.015,y,.03),
          end=(-1.94,y,3.25),color=(.78+.06*(j%2),.75+.06*(j%2),.66+.07*(j%2)))
    add("curtain fold "+str(j),p)
for j in range(6):
    add("near curtain fold "+str(j),
        rod(.045,start=(-1.91+j*.035,-1.13,.02),
            end=(-2.02+j*.035,-1.13,3.3),color=(.52,.45,.33)))

chaise=Asset("Louis XV chaise longue")
def ch(name,node):
    chaise.include(name,node)
def ct(name,pts,r=.025,c=wood):
    ch(name,sweep_tube(points=pts,radius=r,color=c))

# Upholstered long mattress.
ch("seat cushion",fillet_box((2.55,1.03,.29),radius=.145,
                           center=(.02,0,.665),color=ivory))
# Foundation rails curve down at the foot.
front=[(-1.27,-.49,.51),(-1.05,-.53,.48),(-.72,-.54,.475),
       (-.25,-.54,.46),(.30,-.54,.445),(.88,-.52,.44),(1.21,-.45,.43)]
back=[(x,-y,z) for x,y,z in front]
ct("front deep carved apron",front,.061)
ct("rear apron",back,.047)
ct("front gold upper edge",[(x,y-.045,z+.043) for x,y,z in front],.008,gold)
ct("front lower gold edge",[(x,y-.047,z-.043) for x,y,z in front],.007,gold)
for x in [-1.18,1.15]:
    ct("rounded end rail "+str(x),[(x,-.45,.46),(x+.055,-.26,.46),
         (x+.075,0,.47),(x+.055,.26,.46),(x,.45,.46)],.045)
# Mattress welt.
for y in [-.505,.505]:
    ct("seat piping "+str(y),[(-1.13,y,.66),(-.8,y,.573),(-.3,y,.568),
        (.3,y,.568),(.85,y,.57),(1.15,y*.92,.60)],.009,(.57,.51,.40))

# Tall upholstered head, with an arched outline.
head=fillet_box((.18,1.03,.87),radius=.085,
                center=(-1.19,0,1.045),color=ivory)
head.turn('y',-12)
ch("head upholstery",head)
head_outline=[(-1.105,-.48,.67),(-1.26,-.52,1.05),(-1.34,-.50,1.40),
              (-1.34,-.40,1.51),(-1.33,-.19,1.535),(-1.31,.06,1.52),
              (-1.28,.31,1.46),(-1.22,.48,1.36),(-1.12,.51,1.02)]
ct("arched head wooden border",head_outline,.035)
ct("arched head gilt bead",[(x+.025,y,z+.009) for x,y,z in head_outline],.008,gold)

# Sweeping upholstered arm panels at both sides.
for side in [-1,1]:
    y=side*.49
    # A broad padded wing whose crest falls toward the open seat.
    wing=fillet_box((.64,.095,.48),radius=.047,
                   center=(-.93,y,.865),color=ivory)
    wing.turn('y',17)
    ch("padded side wing "+str(side),wing)
    outline=[(-1.31,y,1.34),(-1.22,y,1.23),(-1.08,y,1.15),
             (-.90,y,1.095),(-.72,y,1.075),(-.60,y,1.105),
             (-.57,y,1.055),(-.59,y,.96),(-.54,y,.79),
             (-.48,y,.62),(-.55,y,.53),(-.78,y,.51),(-1.05,y,.56),(-1.18,y,.69)]
    ct("wing perimeter "+str(side),outline,.028)
    ct("wing gilt highlight "+str(side),
       [(x,y+side*.022,z+.008) for x,y,z in outline],.0065,gold)
    for x,z in [(-.61,1.085),(-1.26,1.33)]:
        for k in range(3):
            ch("arm scroll bead "+str((side,x,k)),
               ball(.022-k*.004,center=(x+k*.018,y+side*.012,z+k*.009),color=gold))

# Four cabriole legs.
for x in [-1.02,1.10]:
    for y in [-.43,.43]:
        s=-1 if x<0 else 1
        pts=[(x,y,.49),(x+s*.065,y,.40),(x+s*.025,y,.29),
             (x-s*.035,y,.15),(x-s*.025,y-.015,.055),
             (x+s*.015,y-.025,.035)]
        ct("cabriole leg "+str((x,y)),pts,.037)
        ct("leg gilded ridge "+str((x,y)),
           [(xx,yy-.029,zz) for xx,yy,zz in pts],.006,gold)
        ch("foot "+str((x,y)),fillet_box((.09,.075,.045),radius=.018,
           center=(x+s*.005,y-.025,.032),color=wood))
        # Small carved leaf at the knee.
        for k in range(3):
            leaf=ball(.024,center=(x+(k-1)*.022,y-.04,.43-abs(k-1)*.012),color=gold)
            leaf.resize((.55,.45,1.45))
            ch("knee leaf "+str((x,y,k)),leaf)

# Rococo central cartouche, with curling leaf motifs.
for k in range(7):
    t=k/6*math.pi
    ch("central carved crest "+str(k),
       ball(.024,center=(.12+.085*math.cos(t),-.605,.435-.055*math.sin(t)),color=gold))
for s in [-1,1]:
    pts=[]
    for k in range(24):
        t=k/23*math.pi*1.7
        r=.052*(1-k/30)
        pts.append((.12+s*(.09+r*math.sin(t)),-.596,.43+r*math.cos(t)))
    ct("apron scroll "+str(s),pts,.009,gold)
    for k in range(3):
        leaf=ball(.027,center=(.12+s*(.15+k*.038),-.585,.445+k*.006),color=gold)
        leaf.resize((1.55,.32,.42))
        ch("apron leaf "+str((s,k)),leaf)

# Large casually placed cream pillow.
pillow=fillet_box((.25,.70,.73),radius=.105,
                  center=(-.99,-.075,1.145),color=(.83,.77,.63))
pillow.turn('y',-21)
pillow.turn('z',-15)
ch("loose pillow",pillow)
# Pillow seam and small corner tips.
pts=[(-.905,-.43,.85),(-.83,-.44,1.00),(-.88,-.40,1.37),
     (-1.07,-.34,1.52),(-1.17,.24,1.43),(-1.10,.29,1.05),
     (-1.00,.24,.85),(-.905,-.43,.85)]
ct("pillow welt",pts,.0065,(.69,.61,.46))

# Small green museum label on the seat.
label=box((.105,.165,.004),center=(.79,.12,.816),color=(.055,.22,.17))
label.turn('z',-9)
ch("green museum label",label)
for i,w in enumerate([.045,.033,.05]):
    p=box((w,.003,.001),center=(.79,.15-i*.014,.819),color=(.70,.77,.63))
    p.turn('z',-9)
    ch("label lettering "+str(i),p)
scene.include("chaise",chaise)

# Partial cane chair in the lower-left corner.
chair=Asset("foreground cane chair")
for y in [-1.59,-2.12]:
    chair.include("rim "+str(y),rod(.026,start=(-1.65,y,.48),end=(-1.04,y,.48),color=wood))
for x in [-1.65,-1.04]:
    chair.include("side "+str(x),rod(.029,start=(x,-2.12,.48),end=(x,-1.59,.48),color=wood))
for i in range(25):
    x=-1.62+i*.023
    chair.include("cane warp "+str(i),rod(.003,start=(x,-2.09,.477),end=(x,-1.62,.477),color=(.53,.36,.21)))
for i in range(21):
    y=-2.09+i*.023
    chair.include("cane weft "+str(i),rod(.003,start=(-1.62,y,.480),end=(-1.07,y,.480),color=(.55,.39,.24)))
scene.include("partial foreground chair",chair)

realize(scene)

# Woven ivory upholstery with restrained pink floral stripes.
def fabric_material(name, pillow=False):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    n=m.node_tree.nodes
    l=m.node_tree.links
    bs=n.get("Principled BSDF")
    bs.inputs["Roughness"].default_value=.88
    tex=n.new("ShaderNodeTexCoord")
    sep=n.new("ShaderNodeSeparateXYZ")
    l.new(tex.outputs["Generated"],sep.inputs[0])
    noise=n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=165
    noise.inputs["Detail"].default_value=2
    l.new(tex.outputs["Generated"],noise.inputs["Vector"])
    bump=n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.19
    bump.inputs["Distance"].default_value=.012 if pillow else .006
    l.new(noise.outputs["Fac"],bump.inputs["Height"])
    l.new(bump.outputs["Normal"],bs.inputs["Normal"])
    if pillow:
        ramp=n.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color=(.57,.48,.33,1)
        ramp.color_ramp.elements[1].color=(.88,.80,.63,1)
        l.new(noise.outputs["Fac"],ramp.inputs[0])
        l.new(ramp.outputs[0],bs.inputs["Base Color"])
        return m
    def mathnode(op,a=None,b=None):
        q=n.new("ShaderNodeMath");q.operation=op
        if isinstance(a,(int,float)):q.inputs[0].default_value=a
        elif a is not None:l.new(a,q.inputs[0])
        if isinstance(b,(int,float)):q.inputs[1].default_value=b
        elif b is not None:l.new(b,q.inputs[1])
        return q.outputs[0]
    sy=mathnode("MULTIPLY",sep.outputs["Y"],17)
    fy=mathnode("FRACT",sy)
    line=mathnode("LESS_THAN",fy,.035)
    # Repeated tiny flower-like groups between the fine woven stripes.
    xx=mathnode("MULTIPLY",sep.outputs["X"],24)
    fx=mathnode("FRACT",xx)
    dx=mathnode("SUBTRACT",fx,.5)
    dy=mathnode("SUBTRACT",fy,.47)
    dx2=mathnode("MULTIPLY",dx,dx)
    dy2=mathnode("MULTIPLY",dy,dy)
    dist=mathnode("ADD",dx2,dy2)
    dots=mathnode("LESS_THAN",dist,.012)
    mask=mathnode("MAXIMUM",mathnode("MULTIPLY",line,.35),dots)
    mix=n.new("ShaderNodeMixRGB")
    mix.inputs[1].default_value=(.78,.725,.62,1)
    mix.inputs[2].default_value=(.49,.25,.245,1)
    l.new(mask,mix.inputs[0])
    l.new(mix.outputs[0],bs.inputs["Base Color"])
    return m

fabric=fabric_material("Antique ivory silk with faded rose sprigs")
pillmat=fabric_material("Cream damask pillow",True)
for obj in bpy.context.scene.objects:
    if obj.type=='MESH':
        nm=obj.name.lower()
        if any(s in nm for s in ["seat cushion","head upholstery","padded side wing"]):
            obj.data.materials.clear()
            obj.data.materials.append(fabric)
        elif "loose pillow" in nm:
            obj.data.materials.clear()
            obj.data.materials.append(pillmat)
        if any(s in nm for s in ["cushion","upholstery","padded","pillow","cabriole","scroll"]):
            for p in obj.data.polygons:
                p.use_smooth=True

set_view((3.05,-5.8,3.6),(-.04,.02,.91),lens=49,sensor=36)
area_emitter((-3,-1,3.1),power=550,size=2.7,target=(0,0,.65),color=(1,.92,.79))
area_emitter((1,-3,3.6),power=100,size=3.5,target=(0,0,.8),color=(.85,.90,1))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.57,.60,.64,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.26
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.15
sc.render.image_settings.file_format='PNG'
