from sceneact import *
import bpy, math, random
from mathutils import Vector

# Reference inventory (normalized image bounds):
# Architecture: pale floor (0,.63)-(1,1), patterned warm walls, ceiling and white cornice.
# Back wall: two tall white windows at (0,.07)-(.13,.59) and (.24,.08)-(.44,.62),
# green roller blinds, bright lower glazing; oval portrait between them.
# Right wall: small framed portraits and narrow white door near the corner.
# Bed (.53,.47)-(1,.98): dark timber frame, headboard, tall near foot posts,
# ivory mattress, rumpled cover and two large pillows; its foot overlaps the chair.
# Olive chair (.28,.50)-(.54,.95): curved tall back, seat, broad arms and dark feet.
# Painted folding panel (.41,.33)-(.61,.65), partially hidden by chair and bed.
# Left furniture: cropped dark chest, small draped table and terracotta pot.
# Small spindle chair behind bed, bedside round cabinet, two patterned rugs.
# Depth and concealed furniture surfaces are uncertain; only simple support geometry is used.
# Anchors: back/right ceiling corner near (.57,.07), window top corners (.25,.08),
# (.43,.10), window sill (.43,.61), bed headboard top (.72,.47)-( .97,.54),
# chair floor contacts around (.34,.91), (.45,.96). Scale is arbitrary.
# Estimate: about 240 primitive meshes, including roughly 90 picture/panel details
# and rug borders. No booleans, fillets, or densely sampled curve expansions.

S = Scene('Historic bedroom')
random.seed(8)
ivory=(.86,.84,.73); white=(.91,.92,.88)
wood=(.075,.035,.019); gold=(.48,.31,.10)
olive=(.24,.24,.055)

def asset(name):
    a=Asset(name); S.include(name,a); return a
def B(a,n,sz,c,col):
    p=box(size=sz,center=c,color=col); a.include(n,p); return p
def E(a,n,sz,c,col):
    p=ball(1,center=c,color=col); p.resize(sz,pivot=c); a.include(n,p); return p
def R(a,n,r,p,q,col):
    o=rod(radius=r,start=p,end=q,color=col); a.include(n,o); return o

room=asset('Room architecture')
B(room,'stone floor',(8,9,.12),(0,0,-.07),(.59,.57,.49))
B(room,'back wallpaper',(6.9,.12,3.45),(0,3.45,1.72),(.47,.34,.23))
B(room,'right wallpaper',(.12,8,3.45),(3.45,-.5,1.72),(.47,.35,.25))
B(room,'ceiling',(7,8,.10),(0,-.5,3.49),(.86,.88,.85))
for z,w,h in [(3.31,.12,.09),(3.39,.21,.07),(3.44,.28,.055)]:
    B(room,'back cornice '+str(z),(6.9,w,h),(0,3.31,z),white)
    B(room,'side cornice '+str(z),(w,8,h),(3.31,-.5,z),white)
B(room,'back baseboard',(6.9,.075,.16),(0,3.35,.08),wood)
B(room,'side baseboard',(.075,8,.16),(3.35,-.5,.08),wood)

# Windows are layered opaque luminous planes, with modelled trim and deep sills.
for i,x in enumerate([-2.80,-.78]):
    a=asset('Window '+str(i+1))
    B(a,'recess shadow',(1.44,.10,2.79),(x,3.355,1.88),(.24,.22,.17))
    B(a,'glazing',(1.24,.045,2.55),(x,3.275,1.91),(.79,.92,.92))
    B(a,'green blind',(1.15,.045,1.40),(x,3.23,2.39),(.14,.31,.28))
    for j,xx in enumerate([x-.68,x+.68]):
        B(a,'white jamb '+str(j),(.105,.20,2.82),(xx,3.20,1.88),white)
        B(a,'inner jamb '+str(j),(.032,.06,2.6),(xx+(.075 if j==0 else -.075),3.09,1.9),(.68,.72,.70))
    for n,z in [('lintel',3.27),('lower frame',.53)]:
        B(a,n,(1.47,.21,.10),(x,3.18,z),white)
    B(a,'sill',(1.57,.33,.07),(x,3.10,.51),white)
    B(a,'blind bottom',(1.16,.06,.035),(x,3.19,1.70),(.28,.43,.38))
    R(a,'blind cord',.006,(x+.56,3.12,2.9),(x+.56,3.12,1.5),(.7,.7,.6))

door=asset('Narrow white door')
B(door,'door leaf',(.68,.06,2.48),(1.13,3.32,1.24),(.84,.85,.80))
for x in [.75,1.51]:
    B(door,'door casing '+str(x),(.065,.15,2.61),(x,3.23,1.30),white)
B(door,'door top',(.84,.15,.07),(1.13,3.23,2.61),white)
for z in [.75,1.98]:
    B(door,'panel '+str(z),(.51,.035,.96),(1.13,3.27,z),(.78,.80,.75))
E(door,'handle',(.035,.035,.035),(1.4,3.17,1.16),gold)

# Oval painting between windows, concentric oval solids form the visible frame.
a=asset('Oval ancestor portrait')
for n,sz,y,col in [
    ('outer gilt',(.45,.055,.59),3.22,gold),
    ('bright ridge',(.414,.058,.555),3.15,(.68,.48,.19)),
    ('inner dark oval',(.365,.06,.505),3.085,(.07,.055,.035))]:
    E(a,n,sz,(-1.82,y,2.36),col)
E(a,'black coat',(.20,.025,.24),(-1.82,3.012,2.18),(.025,.02,.015))
E(a,'face',(.085,.025,.123),(-1.82,2.997,2.49),(.43,.25,.13))
E(a,'hair',(.09,.024,.055),(-1.82,2.982,2.59),(.045,.025,.015))
B(a,'shirt',(.09,.015,.075),(-1.82,2.968,2.34),(.57,.51,.35))

def framed_back(name,x,z,w,h):
    a=asset(name)
    B(a,'frame',(w,.085,h),(x,3.20,z),gold)
    B(a,'mount',(w-.045,.02,h-.045),(x,3.145,z),(.80,.78,.65))
    B(a,'image',(w*.64,.02,h*.71),(x,3.125,z),(.44,.44,.38))
    E(a,'portrait head',(w*.15,.016,h*.19),(x,3.104,z+.07),(.59,.59,.52))
    E(a,'portrait shoulders',(w*.25,.016,h*.17),(x,3.10,z-.13),(.28,.28,.25))
framed_back('Small rectangular portrait',.49,2.70,.46,.63)
a=asset('Right wall miniature')
B(a,'gilt frame',(.065,.38,.59),(3.31,2.43,2.60),gold)
B(a,'cream mount',(.025,.33,.54),(3.267,2.43,2.60),ivory)
E(a,'oval image',(.016,.105,.20),(3.245,2.43,2.60),(.44,.40,.36))

panel=asset('Decorative painted folding screen')
for j in range(2):
    x=.10+j*.69
    B(panel,'panel timber '+str(j),(.70,.075,1.67),(x,2.18,1.32),wood)
    B(panel,'ochre ground '+str(j),(.675,.025,1.62),(x,2.13,1.32),(.58,.43,.20))
    # Broad blue, curving patches and stylized leaves describe the visible decorative painting.
    for k in range(5):
        cx=x+random.uniform(-.24,.24); z=.65+k*.29
        E(panel,'blue silhouette %d %d'%(j,k),(.27,.018,.21),(cx,2.105,z),(.035,.12,.42))
    for k in range(9):
        cx=x+random.uniform(-.28,.28); z=random.uniform(.58,2.04)
        leaf=E(panel,'leaf %d %d'%(j,k),(.045,.012,.12),(cx,2.077,z),
               [(.58,.29,.08),(.26,.38,.22),(.72,.58,.31)][k%3])
        leaf.turn('y',random.uniform(-50,50),pivot=(cx,2.077,z))
    for k in range(6):
        E(panel,'small gilded motif %d %d'%(j,k),(.018,.012,.025),
          (x+random.uniform(-.29,.29),2.066,random.uniform(.6,2.05)),(.20,.16,.09))

# Bed runs from a near foot at x=.2 toward the right wall at x=3.2.
bed=asset('Dark wooden bed')
B(bed,'main bed frame',(2.65,1.84,.25),(1.78,.23,.49),wood)
B(bed,'mattress',(2.58,1.76,.32),(1.76,.23,.77),ivory)
B(bed,'soft cover',(2.55,1.79,.16),(1.72,.23,.94),(.76,.75,.64))
# Gentle irregularities form the broad linen contour.
for k in range(6):
    E(bed,'cover fold '+str(k),(.55,.18,.055),
      (.70+k*.35,-.45+random.uniform(-.13,.13),.985),(.78,.77,.67))
B(bed,'near side rail',(2.69,.09,.27),(1.77,-.73,.48),wood)
B(bed,'far side rail',(2.69,.09,.27),(1.77,1.19,.48),wood)
B(bed,'headboard panel',(.12,1.93,.72),(3.12,.23,1.13),wood)
R(bed,'headboard top rail',.055,(3.105,-.78,1.55),(3.105,1.24,1.55),wood)
for xx,n in [(.37,'foot'),(3.12,'head')]:
    for yy in [-.75,1.21]:
        B(bed,n+' post '+str(yy),(.105,.105,1.27),(xx,yy,.69),wood)
        E(bed,n+' finial '+str(yy),(.082,.082,.085),(xx,yy,1.36),wood)
B(bed,'footboard',(.12,1.86,.62),(.38,.23,.76),wood)
R(bed,'footboard crown',.055,(.36,-.74,1.12),(.36,1.20,1.12),wood)
for i,y in enumerate([-.26,.64]):
    p=E(bed,'large ivory pillow '+str(i),(.45,.43,.16),(2.63,y,1.19),(.84,.84,.75))
    p.turn('y',-26,pivot=(2.63,y,1.19))
    E(bed,'pillow lower crease '+str(i),(.34,.35,.045),(2.38,y,1.04),(.71,.72,.64))

chair=asset('Olive upholstered armchair')
# The chair is modelled locally, then rotated as a complete semantic group.
cx=-.50; cy=.10
B(chair,'seat base',(1.22,1.03,.24),(cx,cy,.47),olive)
E(chair,'rounded seat cushion',(.61,.52,.15),(cx,cy-.04,.64),(.29,.29,.07))
E(chair,'high curved back',(.61,.17,.55),(cx,cy+.44,1.04),(.23,.25,.055))
E(chair,'back central cushion',(.45,.12,.45),(cx,cy+.29,1.07),(.28,.29,.067))
for i,dx in enumerate([-.59,.59]):
    E(chair,'sweeping arm '+str(i),(.14,.61,.35),(cx+dx,cy,.79),(.23,.24,.052))
    R(chair,'arm piping '+str(i),.023,(cx+dx,cy-.43,.94),(cx+dx,cy+.37,1.22),(.34,.34,.09))
for dx in [-.45,.45]:
    for dy in [-.37,.37]:
        R(chair,'wood foot '+str((dx,dy)),.035,(cx+dx,cy+dy,.06),(cx+dx,cy+dy,.41),wood)
for i,(dx,z) in enumerate([(-.22,1.0),(0,1.14),(.22,1.0),(0,.87)]):
    E(chair,'tuft '+str(i),(.033,.018,.038),(cx+dx,cy+.168,z),(.14,.16,.028))
chair.turn('z',-25,pivot=(cx,cy,0))

table=asset('Small draped table')
B(table,'top',(.80,.58,.07),(-1.70,2.64,.75),wood)
for dx in [-.31,.31]:
    for dy in [-.20,.20]:
        R(table,'leg '+str((dx,dy)),.035,(-1.70+dx,2.64+dy,.05),(-1.70+dx,2.64+dy,.74),wood)
B(table,'white linen top',(.82,.59,.02),(-1.70,2.64,.80),white)
d=B(table,'hanging triangular cloth',(.51,.035,.45),(-1.70,2.32,.60),ivory)
d.turn('y',45,pivot=(-1.70,2.32,.60))
for i,x in enumerate([-1.94,-1.61,-1.43]):
    E(table,'small porcelain '+str(i),(.06,.055,.022),(x,2.59,.83),(.73,.70,.55))
    R(table,'goblet stem '+str(i),.012,(x,2.59,.83),(x,2.59,.90),gold)
    E(table,'goblet bowl '+str(i),(.032,.032,.034),(x,2.59,.92),gold)

chest=asset('Cropped left chest')
B(chest,'body',(.98,.57,.66),(-3.05,2.77,.42),wood)
B(chest,'top',(1.08,.65,.075),(-3.05,2.77,.79),wood)
for z in [.22,.47,.66]:
    B(chest,'drawer '+str(z),(.90,.035,.17),(-3.05,2.466,z),(.11,.065,.035))
    for x in [-3.28,-2.84]:
        E(chest,'brass pull '+str((x,z)),(.024,.016,.022),(x,2.438,z),gold)
for x in [-3.46,-2.64]:
    R(chest,'foot '+str(x),.045,(x,2.60,.04),(x,2.60,.27),wood)
B(chest,'little picture frame',(.24,.065,.33),(-3.15,2.70,.99),gold)
B(chest,'little picture',(.19,.025,.28),(-3.15,2.66,.99),(.08,.10,.065))
pot=asset('Terracotta floor pot')
R(pot,'pot',.14,(-2.28,2.89,.03),(-2.28,2.89,.25),(.36,.18,.10))
R(pot,'rim',.16,(-2.28,2.89,.23),(-2.28,2.89,.27),(.42,.24,.13))

sp=asset('Small spindle chair behind bed')
B(sp,'seat',(.43,.43,.07),(2.12,2.46,.51),wood)
for x in [1.94,2.30]:
    for y in [2.28,2.64]:
        R(sp,'leg '+str((x,y)),.022,(x,y,.02),(x,y,.53),wood)
for x in [1.93,2.31]:
    R(sp,'back upright '+str(x),.022,(x,2.66,.48),(x,2.66,1.21),wood)
R(sp,'back top',.035,(1.91,2.66,1.20),(2.33,2.66,1.20),wood)
for i in range(4):
    x=1.98+i*.09
    R(sp,'spindle '+str(i),.012,(x,2.66,.61),(x,2.66,1.18),wood)

night=asset('Round bedside cabinet')
R(night,'round cabinet',.37,(3.0,-1.18,.05),(3.0,-1.18,.72),wood)
R(night,'top lip',.40,(3.0,-1.18,.72),(3.0,-1.18,.77),(.11,.06,.035))
for z in [.12,.42]:
    R(night,'rim '+str(z),.375,(3.0,-1.18,z),(3.0,-1.18,z+.025),(.19,.12,.065))

def rug(name,cx,cy,w,d):
    a=asset(name)
    B(a,'red ground',(w,d,.014),(cx,cy,.009),(.31,.12,.08))
    for k,col in enumerate([(.65,.52,.32),(.20,.27,.29),(.67,.57,.40),(.30,.15,.10)]):
        inset=.035+k*.055
        for y in [cy-d/2+inset,cy+d/2-inset]:
            B(a,'horizontal border '+str((k,y)),(w-2*inset,.027,.006),(cx,y,.019),col)
        for x in [cx-w/2+inset,cx+w/2-inset]:
            B(a,'vertical border '+str((k,x)),(.027,d-2*inset,.006),(x,cy,.019),col)
    for k in range(7):
        x=cx-w*.35+k*w*.115
        b=B(a,'geometric motif '+str(k),(.105,.105,.006),(x,cy,.022),(.62,.47,.29))
        b.turn('z',45,pivot=(x,cy,.022))
rug('Small rug behind armchair',-1.06,1.50,1.65,.95)
rug('Foreground carpet',1.28,-1.72,2.48,1.30)

realize(S)
# Restrained procedural wall motifs use a repeating floral-like grid rather than noise.
for obj in bpy.data.objects:
    if obj.type!='MESH': continue
    if 'wallpaper' in obj.name:
        mat=bpy.data.materials.new('Muted ochre floral wallpaper')
        mat.diffuse_color=(.45,.33,.23,1); mat.use_nodes=True
        nt=mat.node_tree; nd=nt.nodes; lk=nt.links
        bs=nd.get('Principled BSDF')
        tex=nd.new('ShaderNodeTexCoord')
        sep=nd.new('ShaderNodeSeparateXYZ')
        lk.new(tex.outputs['Generated'],sep.inputs[0])
        # Object dimensions determine repeat counts; both planes carry small vertical motifs.
        axes=('X','Z') if 'back' in obj.name else ('Y','Z')
        vals=[]
        for ax,freq in [(axes[0],155),(axes[1],110)]:
            mul=nd.new('ShaderNodeMath'); mul.operation='MULTIPLY'
            lk.new(sep.outputs[ax],mul.inputs[0]); mul.inputs[1].default_value=freq
            sn=nd.new('ShaderNodeMath'); sn.operation='SINE'; lk.new(mul.outputs[0],sn.inputs[0])
            vals.append(sn)
        prod=nd.new('ShaderNodeMath'); prod.operation='MULTIPLY'
        lk.new(vals[0].outputs[0],prod.inputs[0]); lk.new(vals[1].outputs[0],prod.inputs[1])
        ramp=nd.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(.29,.25,.18,1)
        ramp.color_ramp.elements[1].position=.74
        ramp.color_ramp.elements[1].color=(.52,.36,.23,1)
        lk.new(prod.outputs[0],ramp.inputs[0]); lk.new(ramp.outputs[0],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=.87
        obj.data.materials.clear(); obj.data.materials.append(mat)
    elif 'glazing' in obj.name:
        for mat in obj.data.materials:
            mat.use_nodes=True
            bs=mat.node_tree.nodes.get('Principled BSDF')
            if bs:
                bs.inputs['Emission Color'].default_value=(.72,.88,.93,1)
                bs.inputs['Emission Strength'].default_value=1.5
    else:
        for mat in obj.data.materials:
            mat.use_nodes=True
            bs=mat.node_tree.nodes.get('Principled BSDF')
            if bs: bs.inputs['Roughness'].default_value=.76

sc=bpy.context.scene
if sc.world is None: sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
bg=nodes.get('Background')
if bg is None: bg=nodes.new('ShaderNodeBackground')
out=nodes.get('World Output')
if out is None: out=nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(bg.outputs['Background'],out.inputs['Surface'])
bg.inputs['Color'].default_value=(.61,.68,.73,1)
bg.inputs['Strength'].default_value=.28

set_view(position=(-4.65,-6.8,2.92),target=(.05,1.47,1.46),lens=42,sensor=36)
area_emitter(position=(-.85,2.96,2.25),power=650,size=1.5,target=(.2,-.3,.5),color=(.82,.91,1))
area_emitter(position=(-3.0,2.92,2.2),power=350,size=1.3,target=(-1,0,.7),color=(.84,.93,1))
area_emitter(position=(-2,-3,3.1),power=100,size=4,target=(1,1,.8),color=(1,.87,.71))
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
