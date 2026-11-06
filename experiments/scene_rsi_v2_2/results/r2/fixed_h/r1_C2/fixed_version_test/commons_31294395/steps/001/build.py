from sceneact import *
import bpy, math, random
from mathutils import Vector

# Reference inventory, estimated normalized image bounds:
# Architecture: pale floor (0,.60)-(1,1); brown patterned back/right walls;
# two bright white windows (0,.07)-(.12,.59), (.24,.08)-(.43,.60),
# green upper blinds; white ceiling cornice. Room extent behind camera is uncertain.
# Bed (.48,.47)-(.99,.99): dark timber head/foot boards, white bedding,
# two large pillows; foreground footboard overlaps mattress.
# Olive settee (.28,.50)-(.54,.98): curved tufted back, seat, two high arms,
# short dark feet; overlaps bed and decorative screen.
# Painted folding screen (.41,.33)-(.61,.65): ochre/blue panels and bird motifs.
# Left cabinet (0,.47)-(.12,.68), small framed pictures; cloth-topped table
# (.14,.48)-(.26,.65), oval gold portrait (.13,.16)-(.25,.37).
# Small wall pictures (.47,.15)-(.54,.28), (.66,.16)-(.71,.30);
# white door (.56,.20)-(.63,.52); thin chair (.62,.46)-(.70,.62).
# Rugs near windows and cropped foreground; round bedside table at right edge.
# Estimated expanded primitives: about 285, including 52 from two fillet boxes,
# approximately 70 screen/art parts and 45 furniture rods. No Boolean operations.
# Each inventory item maps to a named Asset below; hidden construction is simplified.

scene = Scene('Historic bedroom')
random.seed(11)
wallcol=(.39,.29,.20)
wood=(.065,.033,.020)
gold=(.53,.34,.105)
olive=(.24,.245,.065)
ivory=(.83,.82,.72)
white=(.91,.92,.87)

def asset(name):
    a=Asset(name); scene.include(name,a); return a
def B(a,n,s,c,col):
    a.include(n,box(s,center=c,color=col))
def E(a,n,c,s,col):
    a.include(n,ball(1,center=c,color=col).resize(s))
def R(a,n,p,q,r,col):
    a.include(n,rod(r,start=p,end=q,color=col))

room=asset('Room architecture')
B(room,'limestone floor',(8,10,.12),(-.7,-.6,-.08),(.63,.61,.55))
# Back wall segments leave two actual window openings.
back=3.25
for i,(l,r) in enumerate([(-4.5,-3.65),(-2.65,-1.65),(-.45,2.85)]):
    B(room,'back wall pier '+str(i),(r-l,.15,3.4),((l+r)/2,back,1.7),wallcol)
for i,(l,r) in enumerate([(-3.65,-2.65),(-1.65,-.45)]):
    B(room,'wall below window '+str(i),(r-l,.15,.48),((l+r)/2,back,.24),wallcol)
    B(room,'wall above window '+str(i),(r-l,.15,.30),((l+r)/2,back,3.25),wallcol)
B(room,'right patterned wall',(.16,9,3.4),(2.85,-1.17,1.7),wallcol)
B(room,'ceiling',(7.5,9,.12),(-.85,-1.15,3.45),white)
for z,dep,h in [(3.25,.08,.09),(3.32,.13,.08),(3.38,.19,.055)]:
    B(room,'back cornice '+str(z),(7.4,dep,h),(-.8,3.12,z),white)
    B(room,'right cornice '+str(z),(dep,8.8,h),(2.74,-1.1,z),white)
B(room,'back skirting',(7.3,.06,.17),(-.8,3.13,.085),(.33,.27,.21))
B(room,'right skirting',(.06,8.8,.17),(2.73,-1.1,.085),(.33,.27,.21))

for k,(xc,w) in enumerate([(-3.15,1.0),(-1.05,1.2)]):
    a=asset('Window '+str(k+1))
    B(a,'luminous glass',(w-.10,.025,2.48),(xc,3.255,1.77),(.83,.97,.98))
    for xx in [xc-w/2,xc+w/2]:
        B(a,'outer jamb '+str(xx),(.10,.23,2.72),(xx,3.10,1.77),white)
        B(a,'inner jamb '+str(xx),(.035,.27,2.54),(xx+(.07 if xx<xc else -.07),3.085,1.77),(.72,.74,.69))
    for z in [.42,3.12]:
        B(a,'horizontal frame '+str(z),(w+.16,.24,.11),(xc,3.095,z),white)
    B(a,'sill',(w+.25,.37,.075),(xc,3.015,.47),white)
    B(a,'green roller blind',(w-.14,.035,1.30),(xc,3.075,2.36),(.19,.40,.36))
    R(a,'blind bottom rail',(xc-w/2+.07,3.035,1.70),(xc+w/2-.07,3.035,1.70),.015,(.43,.57,.51))
    R(a,'blind cord',(xc+w/2-.02,2.98,2.98),(xc+w/2-.02,2.98,1.15),.006,(.65,.61,.46))

door=asset('White door by corner')
B(door,'door leaf',(.055,.78,2.23),(2.742,2.69,1.115),(.78,.80,.74))
for y in [2.27,3.10]:
    B(door,'door jamb '+str(y),(.11,.07,2.34),(2.70,y,1.17),white)
B(door,'door lintel',(.11,.91,.09),(2.70,2.69,2.34),white)
for z in [.68,1.65]:
    B(door,'recessed panel '+str(z),(.018,.61,.72),(2.703,2.69,z),(.72,.75,.69))
E(door,'brass handle',(2.65,2.36,1.06),(.025,.035,.025),gold)

bed=asset('Dark wood double bed')
# Long axis is perpendicular to the right wall.
bx,by=1.34,.65
B(bed,'bed base',(2.48,1.72,.29),(bx,by,.34),wood)
bed.include('rounded mattress',fillet_box((2.34,1.65,.24),radius=.09,center=(bx,by,.59),color=ivory))
bed.include('duvet body',fillet_box((2.15,1.64,.20),radius=.085,center=(1.19,by,.77),color=(.80,.80,.71)))
E(bed,'soft duvet crown',(1.17,by,.85),(1.03,.78,.095),(.85,.85,.77))
# Head and foot panels, with taller square posts and turned caps.
for tag,x,height in [('head',2.60,1.29),('foot',.08,.97)]:
    B(bed,tag+' board',(.10,1.76,height-.30),(x,by,(height+.30)/2),wood)
    R(bed,tag+' top rail',(x,by-.88,height),(x,by+.88,height),.047,(.09,.045,.025))
    for y in [by-.91,by+.91]:
        B(bed,tag+' post '+str(y),(.12,.12,height+.02),(x,y,(height+.02)/2),wood)
        E(bed,tag+' finial '+str(y),(x,y,height+.07),(.075,.075,.075),wood)
for y in [by-.87,by+.87]:
    B(bed,'side rail '+str(y),(2.45,.09,.22),(bx,y,.40),wood)
for j,y in enumerate([.23,1.07]):
    p=ball(1,center=(2.18,y,1.03),color=(.89,.89,.81)).resize((.34,.40,.145))
    p.turn('y',-35)
    bed.include('large white pillow '+str(j),p)
    q=ball(1,center=(2.37,y,.99),color=(.77,.78,.71)).resize((.19,.43,.13))
    q.turn('y',-40)
    bed.include('pillow behind '+str(j),q)
for j in range(7):
    y=by-.66+j*.21
    R(bed,'duvet soft fold '+str(j),(.25,y,.83),(.70,y+.06,.87),.008,(.75,.76,.68))

sofa=asset('Olive upholstered settee')
sx,sy=-.90,.12
B(sofa,'seat foundation',(1.28,.88,.23),(sx,sy,.45),(.18,.18,.045))
E(sofa,'single seat cushion',(sx,sy-.06,.61),(.63,.44,.16),(.30,.30,.075))
# Tall curved back, shoulder bulges, and near arms establish the silhouette.
E(sofa,'curved upholstered back',(sx,sy+.34,.96),(.64,.16,.52),olive)
E(sofa,'raised back crown',(sx-.08,sy+.35,1.27),(.31,.15,.30),olive)
for i,x in enumerate([sx-.64,sx+.64]):
    E(sofa,'solid arm side '+str(i),(x,sy-.03,.76),(.135,.51,.47),(.24,.24,.055))
    E(sofa,'rolled arm top '+str(i),(x,sy+.02,1.04),(.14,.53,.13),(.29,.29,.075))
    for y in [sy-.30,sy+.32]:
        B(sofa,'short foot '+str(i)+str(y),(.075,.075,.22),(x,y,.14),wood)
for j,(dx,z) in enumerate([(-.40,1.05),(-.18,1.15),(.06,1.12),(.29,1.01),(-.29,.85),(-.02,.88),(.25,.83)]):
    E(sofa,'tuft button '+str(j),(sx+dx,sy+.184,z),(.025,.013,.025),(.15,.16,.035))
    R(sofa,'tuft crease '+str(j),(sx+dx-.055,sy+.18,z+.07),(sx+dx+.035,sy+.18,z-.06),.009,(.19,.20,.045))
sofa.turn('z',-13,pivot=(sx,sy,0))

screen=asset('Three panel painted folding screen')
blue=(.025,.11,.48)
ochre=(.56,.40,.15)
for i in range(3):
    x=-.36+i*.49
    y=2.10+(0.035 if i==1 else 0)
    B(screen,'ochre panel '+str(i),(.49,.045,1.64),(x,y,1.13),ochre)
    B(screen,'dark panel edge '+str(i),(.018,.065,1.68),(x-.245,y,1.13),(.18,.15,.07))
    B(screen,'upper binding '+str(i),(.49,.065,.018),(x,y,1.96),wood)
    E(screen,'blue flowing landscape upper '+str(i),(x+.12,y-.031,1.52),(.25,.012,.36),blue)
    E(screen,'blue flowing landscape lower '+str(i),(x-.12,y-.035,.69),(.26,.013,.25),blue)
    # Small birds: pale body, long neck, beak, and spread wing.
    z=1.10+(i%2)*.37
    E(screen,'bird body '+str(i),(x-.04,y-.056,z),(.105,.012,.045),(.73,.64,.36))
    R(screen,'bird neck '+str(i),(x+.025,y-.061,z),(x+.07,y-.061,z+.12),.014,(.80,.72,.43))
    E(screen,'bird head '+str(i),(x+.075,y-.061,z+.12),(.026,.013,.022),(.82,.73,.42))
    R(screen,'bird beak '+str(i),(x+.09,y-.062,z+.12),(x+.15,y-.062,z+.10),.009,(.30,.18,.05))
    R(screen,'bird leg '+str(i),(x-.02,y-.059,z-.025),(x+.01,y-.059,z-.17),.007,(.23,.13,.045))
    for k in range(4):
        R(screen,'wing feather '+str(i)+' '+str(k),(x-.06,y-.06,z),(x-.16+k*.024,y-.06,z+.11+k*.008),.012,(.68,.58,.30))
    for k in range(5):
        E(screen,'painted blossom '+str(i)+' '+str(k),(x-.17+.075*k,y-.035,1.78-.07*(k%2)),(.012,.008,.016),(.25,.21,.12))

portrait=asset('Oval gilded portrait')
E(portrait,'outer oval frame',(-2.13,3.075,2.31),(.38,.065,.49),gold)
E(portrait,'raised gold rim',(-2.13,2.998,2.31),(.335,.023,.443),(.72,.51,.18))
E(portrait,'dark portrait canvas',(-2.13,2.966,2.31),(.296,.016,.398),(.055,.043,.030))
E(portrait,'painted coat',(-2.13,2.944,2.15),(.17,.01,.18),(.075,.052,.035))
E(portrait,'painted head',(-2.12,2.941,2.39),(.073,.012,.095),(.45,.28,.15))
E(portrait,'painted hair',(-2.14,2.93,2.45),(.071,.008,.041),(.10,.075,.04))
R(portrait,'painted white collar',(-2.18,2.925,2.30),(-2.08,2.925,2.28),.012,(.65,.62,.48))

picture=asset('Small back wall photograph')
B(picture,'gold outer frame',(.43,.06,.57),(.27,3.08,2.57),(.57,.47,.27))
B(picture,'ivory mat',(.38,.025,.51),(.27,3.035,2.57),(.84,.81,.69))
B(picture,'gray image',(.23,.015,.36),(.27,3.015,2.57),(.44,.44,.39))
E(picture,'portrait silhouette',(.27,2.999,2.59),(.07,.009,.13),(.27,.28,.25))
small=asset('Right wall small framed oval')
B(small,'frame',(.055,.32,.53),(2.73,1.92,2.53),gold)
B(small,'mat',(.025,.28,.48),(2.69,1.92,2.53),(.88,.85,.75))
E(small,'oval print',(2.671,1.92,2.53),(.013,.09,.18),(.43,.42,.38))

cab=asset('Left dark console')
B(cab,'top',(.94,.48,.075),(-3.18,2.66,.77),wood)
B(cab,'drawer apron',(.84,.38,.22),(-3.18,2.67,.63),(.10,.055,.031))
for x in [-3.55,-2.81]:
    for y in [2.49,2.83]:
        R(cab,'slender leg '+str(x)+str(y),(x,y,.07),(x,y,.60),.033,wood)
        E(cab,'leg turning '+str(x)+str(y),(x,y,.27),(.047,.047,.06),wood)
B(cab,'lower stretcher',(.82,.045,.045),(-3.18,2.49,.18),wood)
for j,x in enumerate([-3.45,-3.15]):
    B(cab,'small tabletop frame '+str(j),(.23,.04,.30),(x,2.75,.97),gold)
    B(cab,'small tabletop painting '+str(j),(.18,.018,.24),(x,2.72,.97),(.15,.14,.08))

table=asset('Cloth covered side table')
B(table,'tabletop',(.72,.56,.055),(-2.15,2.56,.74),wood)
for x in [-2.42,-1.88]:
    for y in [2.34,2.78]:
        R(table,'table leg '+str(x)+str(y),(x,y,.10),(x,y,.72),.025,wood)
B(table,'white cloth top',(.73,.57,.018),(-2.15,2.56,.782),(.89,.88,.79))
# A draped pointed cloth is a rotated shallow box with softened visual silhouette.
cloth=box((.47,.025,.36),center=(-2.15,2.264,.64),color=(.88,.87,.78))
cloth.turn('y',40)
table.include('hanging cloth corner',cloth)
for j,x in enumerate([-2.35,-2.10,-1.96]):
    E(table,'small china dish '+str(j),(x,2.55,.811),(.075,.06,.015),(.82,.82,.70))
    E(table,'small cup '+str(j),(x,2.55,.847),(.033,.033,.037),(.79,.78,.66))
pot=asset('Small floor pot')
E(pot,'terracotta vessel',(-2.66,2.80,.16),(.12,.12,.15),(.30,.17,.09))

chair=asset('Thin black chair behind bed')
cx,cy=1.66,2.18
B(chair,'small seat',(.43,.40,.045),(cx,cy,.46),(.10,.07,.035))
for x in [cx-.19,cx+.19]:
    for y in [cy-.16,cy+.16]:
        R(chair,'chair leg '+str(x)+str(y),(x,y,.035),(x,y,.47),.016,wood)
    R(chair,'back upright '+str(x),(x,cy+.16,.44),(x,cy+.16,1.05),.018,wood)
R(chair,'top back rail',(cx-.2,cy+.16,1.04),(cx+.2,cy+.16,1.04),.027,wood)
for k in range(4):
    x=cx-.14+k*.095
    R(chair,'back spindle '+str(k),(x,cy+.16,.65),(x,cy+.16,1.02),.011,wood)
R(chair,'lower back rail',(cx-.19,cy+.16,.66),(cx+.19,cy+.16,.66),.015,wood)

night=asset('Round bedside table at right edge')
E(night,'round top',(2.42,-.73,.58),(.43,.40,.04),wood)
E(night,'round lower shelf',(2.42,-.73,.13),(.36,.34,.035),wood)
for x,y in [(2.17,-.95),(2.68,-.95),(2.43,-.45)]:
    R(night,'leg '+str(x),(x,y,.12),(x,y,.56),.026,wood)

# Flat woven rugs with geometric nested borders.
for idx,(x,y,w,d) in enumerate([(-1.73,1.60,1.18,.72),(.57,-1.43,2.15,.90)]):
    rug=asset('Woven rug '+str(idx))
    B(rug,'outer red field',(w,d,.012),(x,y,.009),(.36,.105,.07))
    for k,col in enumerate([(.65,.55,.34),(.16,.27,.29),(.69,.60,.40),(.39,.16,.10)]):
        pad=.035+k*.045
        for yy in [y-d/2+pad,y+d/2-pad]:
            B(rug,'long border '+str(k)+str(yy),(w-2*pad,.025,.009),(x,yy,.020+k*.001),col)
        for xx in [x-w/2+pad,x+w/2-pad]:
            B(rug,'short border '+str(k)+str(xx),(.025,d-2*pad,.009),(xx,y,.020+k*.001),col)
    for j in range(5):
        tile=box((.11,.11,.008),center=(x+(j-2)*w/6,y,.027),color=(.62,.51,.30))
        tile.turn('z',45)
        rug.include('central woven diamond '+str(j),tile)

realize(scene)

# Shared procedural finishes retain dense wallpaper detail without tiny meshes.
for mat in list(bpy.data.materials):
    c=mat.diffuse_color
    if sum(abs(c[i]-wallcol[i]) for i in range(3)) < .035:
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get('Principled BSDF')
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=115
        tex.inputs['Detail'].default_value=3
        coord=nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(coord.outputs['Generated'],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.25
        ramp.color_ramp.elements[0].color=(.105,.135,.125,1)
        ramp.color_ramp.elements[1].position=.72
        ramp.color_ramp.elements[1].color=(.55,.39,.22,1)
        middle=ramp.color_ramp.elements.new(.47)
        middle.color=(.32,.23,.15,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=.87
    if c[0]>.80 and c[1]>.93 and c[2]>.94:
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Base Color'].default_value=(.83,.96,1,1)
            if 'Emission Color' in bs.inputs:
                bs.inputs['Emission Color'].default_value=(.75,.92,1,1)
                bs.inputs['Emission Strength'].default_value=2.0

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
background.inputs['Color'].default_value=(.67,.73,.78,1)
background.inputs['Strength'].default_value=.27

set_view((-4.55,-6.50,2.72),(-.30,1.25,1.47),lens=40,sensor=36)
area_emitter((-1.25,2.85,2.07),power=650,size=1.7,target=(-.3,-.8,.4),color=(.82,.92,1))
area_emitter((-3.25,2.75,1.9),power=350,size=1.3,target=(-1,-1,.3),color=(.88,.95,1))
area_emitter((-1.5,-3,3.0),power=105,size=4,target=(.2,1,.8),color=(1,.88,.72))
sc.camera.data.clip_start=.05
sc.camera.data.clip_end=100
sc.view_settings.view_transform='AgX'
