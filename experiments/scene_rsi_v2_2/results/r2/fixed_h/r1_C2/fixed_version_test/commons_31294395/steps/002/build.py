from sceneact import *
import bpy, math
from mathutils import Vector

# Reference inventory (approximate normalized bounds, inferred from the photograph):
# Room: warm gray floor below y=.60, dense brown wallpaper, white cornice near y=.04.
# Windows: (0,.07)-(.12,.61), (.24,.08)-(.43,.61), white frames and green blinds.
# Bed: (.50,.47)-(1,1), long dark timber frame, tall foreground footboard,
# two white pillows, broad cream cover; right portions are partly cropped.
# Olive settee: (.28,.51)-(.54,.99), curved tufted back, rolled high arms,
# seat and short feet; overlaps the bed foot and the screen.
# Painted folding screen: (.41,.33)-(.61,.65), ochre panels with blue landscape
# and pale bird shapes; its lower portion is occluded.
# Left console and small pictures: (0,.43)-(.12,.68).
# Cloth table and cups: (.14,.48)-(.26,.65); small floor pot beside it.
# Gold oval portrait: (.13,.16)-(.25,.37); small rectangular photograph above screen.
# Door near corner: (.56,.20)-(.63,.54); small oval picture farther right.
# Thin spindle chair behind bed, round bedside table at right edge, two patterned rugs.
# Unseen room extent and hidden furniture construction remain simplified.
#
# Feedback comparison: first view had excessive ceiling, a short distant bed,
# a frontal chair displaced right, pale lighting, and an undersized screen.
# Retain the named hierarchy while correcting those supported discrepancies.
# Estimated expanded meshes: approximately 330, including 52 from two fillet boxes,
# 70 rods, 85 scaled balls, architecture, frames and rug borders. No Booleans.

scene=Scene('Historic bedroom revised')
wood=(.052,.025,.013)
gold=(.48,.30,.085)
wallcol=(.30,.205,.125)
ivory=(.76,.76,.66)
white=(.86,.88,.83)
olive=(.19,.205,.035)

def A(name):
    a=Asset(name)
    scene.include(name,a)
    return a
def B(a,n,s,c,col):
    a.include(n,box(s,center=c,color=col))
def E(a,n,c,s,col):
    a.include(n,ball(1,center=c,color=col).resize(s))
def R(a,n,p,q,r,col):
    a.include(n,rod(r,start=p,end=q,color=col))

room=A('Room architecture')
B(room,'stone floor',(9,11,.12),(-.6,-1,-.08),(.53,.51,.45))
for i,(l,r) in enumerate([(-4.5,-3.65),(-2.65,-1.65),(-.45,2.85)]):
    B(room,'back wall pier '+str(i),(r-l,.15,3.4),((l+r)/2,3.25,1.7),wallcol)
for i,(l,r) in enumerate([(-3.65,-2.65),(-1.65,-.45)]):
    B(room,'below window '+str(i),(r-l,.15,.48),((l+r)/2,3.25,.24),wallcol)
    B(room,'above window '+str(i),(r-l,.15,.30),((l+r)/2,3.25,3.25),wallcol)
B(room,'right wall',(.16,10,3.4),(2.85,-1.75,1.7),wallcol)
B(room,'ceiling',(8,10,.12),(-.8,-1.7,3.45),white)
for z,d,h in [(3.25,.08,.09),(3.32,.13,.08),(3.38,.19,.055)]:
    B(room,'back cornice '+str(z),(7.4,d,h),(-.8,3.12,z),white)
    B(room,'right cornice '+str(z),(d,9.8,h),(2.74,-1.65,z),white)
B(room,'back baseboard',(7.3,.06,.17),(-.8,3.13,.085),(.25,.19,.13))
B(room,'right baseboard',(.06,9.8,.17),(2.73,-1.65,.085),(.25,.19,.13))

for k,(xc,w) in enumerate([(-3.15,1),(-1.05,1.2)]):
    a=A('Window '+str(k+1))
    B(a,'bright glass',(w-.1,.025,2.48),(xc,3.255,1.77),(.83,.97,.98))
    for j,xx in enumerate([xc-w/2,xc+w/2]):
        B(a,'outer jamb '+str(j),(.10,.23,2.72),(xx,3.10,1.77),white)
        B(a,'inner jamb '+str(j),(.035,.27,2.54),
          (xx+(.07 if j==0 else -.07),3.085,1.77),(.67,.70,.65))
    for z in [.42,3.12]:
        B(a,'horizontal frame '+str(z),(w+.16,.24,.11),(xc,3.095,z),white)
    B(a,'deep sill',(w+.25,.37,.075),(xc,3.015,.47),white)
    B(a,'green roller blind',(w-.14,.035,1.30),(xc,3.075,2.36),(.11,.29,.25))
    R(a,'blind rail',(xc-w/2+.07,3.035,1.70),(xc+w/2-.07,3.035,1.70),.014,(.29,.43,.36))
    R(a,'blind cord',(xc+w/2-.02,2.98,2.98),(xc+w/2-.02,2.98,1.15),.005,(.56,.53,.39))

door=A('White door near corner')
B(door,'leaf',(.055,.78,2.23),(2.742,2.69,1.115),(.72,.75,.69))
for y in [2.27,3.10]:
    B(door,'jamb '+str(y),(.11,.07,2.34),(2.70,y,1.17),white)
B(door,'lintel',(.11,.91,.09),(2.70,2.69,2.34),white)
for z in [.68,1.65]:
    B(door,'panel '+str(z),(.018,.61,.72),(2.703,2.69,z),(.66,.69,.64))
E(door,'handle',(2.65,2.36,1.06),(.025,.035,.025),gold)

bed=A('Dark timber double bed')
# Enlarged length and nearer foot preserve the head position against the wall.
bx,by=.99,.17
length,width=3.15,1.91
foot,head=-.60,2.60
B(bed,'deep timber base',(length,width,.30),(bx,by,.34),wood)
bed.include('mattress',fillet_box((3.03,1.83,.24),radius=.09,
                                 center=(bx,by,.60),color=ivory))
bed.include('cream cover',fillet_box((2.78,1.83,.19),radius=.08,
                                    center=(.82,by,.78),color=(.76,.77,.68)))
E(bed,'soft cover crown',(.79,by,.85),(1.34,.86,.09),(.80,.81,.72))
for tag,x,height in [('head',head,1.31),('foot',foot,1.03)]:
    B(bed,tag+' panel',(.10,width+.08,height-.28),(x,by,(height+.28)/2),wood)
    B(bed,tag+' inset',(.012,width-.17,height-.43),(x-.058,by,(height+.29)/2),
      (.070,.034,.017))
    R(bed,tag+' upper rail',(x,by-width/2-.04,height),
      (x,by+width/2+.04,height),.048,(.085,.041,.022))
    for j,y in enumerate([by-width/2-.06,by+width/2+.06]):
        B(bed,tag+' post '+str(j),(.12,.12,height+.03),(x,y,(height+.03)/2),wood)
        E(bed,tag+' cap '+str(j),(x,y,height+.085),(.075,.075,.075),wood)
for y in [by-width/2,by+width/2]:
    B(bed,'side rail '+str(y),(length,.09,.23),(bx,y,.40),wood)
for j,y in enumerate([by-.47,by+.47]):
    p=ball(1,center=(2.16,y,1.03),color=(.86,.86,.78)).resize((.36,.45,.16))
    p.turn('y',-35)
    bed.include('large pillow '+str(j),p)
    p=ball(1,center=(2.36,y,1.00),color=(.71,.73,.66)).resize((.19,.46,.13))
    p.turn('y',-40)
    bed.include('rear pillow '+str(j),p)
for j in range(6):
    y=by-.72+j*.28
    R(bed,'cover fold '+str(j),(-.35,y,.84),(.35,y+.05,.88),.008,(.69,.71,.63))

sofa=A('Olive tufted settee')
sx,sy=-1.55,.02
B(sofa,'seat foundation',(1.26,.94,.22),(sx,sy,.45),(.14,.145,.025))
E(sofa,'seat cushion',(sx,sy-.08,.61),(.63,.47,.15),(.25,.265,.045))
E(sofa,'curved back',(sx,sy+.39,.98),(.64,.15,.50),olive)
E(sofa,'raised back crest',(sx-.07,sy+.39,1.29),(.31,.15,.27),olive)
for j,x in enumerate([sx-.62,sx+.62]):
    E(sofa,'upholstered arm side '+str(j),(x,sy-.035,.77),(.12,.54,.46),(.175,.19,.027))
    E(sofa,'rolled arm '+str(j),(x,sy+.015,1.04),(.13,.54,.115),(.23,.245,.045))
    for k,y in enumerate([sy-.35,sy+.35]):
        B(sofa,'short foot '+str(j)+str(k),(.075,.075,.19),(x,y,.13),wood)
for j,(dx,z) in enumerate([(-.40,1.06),(-.18,1.19),(.06,1.15),(.29,1.02),
                           (-.29,.87),(-.02,.91),(.25,.85)]):
    E(sofa,'tuft button '+str(j),(sx+dx,sy+.237,z),(.025,.013,.025),(.10,.12,.016))
    R(sofa,'tuft seam '+str(j),(sx+dx-.055,sy+.23,z+.07),
      (sx+dx+.035,sy+.23,z-.06),.008,(.135,.155,.022))
sofa.turn('z',-57,pivot=(sx,sy,0))
sofa.resize((1.04,1.04,1.04),pivot=(sx,sy,0))

screen=A('Painted folding screen')
blue=(.018,.065,.36)
ochre=(.48,.33,.115)
for i in range(3):
    x=-.36+i*.49
    y=2.10+(.035 if i==1 else 0)
    B(screen,'ochre panel '+str(i),(.49,.045,1.83),(x,y,1.225),ochre)
    B(screen,'panel binding '+str(i),(.018,.065,1.87),(x-.245,y,1.225),(.13,.105,.045))
    B(screen,'top binding '+str(i),(.49,.065,.018),(x,y,2.16),wood)
    E(screen,'blue landscape upper '+str(i),(x+.12,y-.031,1.63),(.25,.012,.38),blue)
    E(screen,'blue landscape lower '+str(i),(x-.12,y-.035,.76),(.26,.013,.29),blue)
    z=1.15+(i%2)*.39
    E(screen,'bird body '+str(i),(x-.04,y-.056,z),(.105,.012,.045),(.70,.60,.31))
    R(screen,'bird neck '+str(i),(x+.025,y-.061,z),(x+.07,y-.061,z+.12),.014,(.75,.66,.36))
    E(screen,'bird head '+str(i),(x+.075,y-.061,z+.12),(.026,.013,.022),(.78,.67,.36))
    R(screen,'bird beak '+str(i),(x+.09,y-.062,z+.12),(x+.15,y-.062,z+.10),.008,(.25,.14,.035))
    R(screen,'bird leg '+str(i),(x-.02,y-.059,z-.025),(x+.01,y-.059,z-.17),.007,(.20,.11,.03))
    for k in range(4):
        R(screen,'wing '+str(i)+' '+str(k),(x-.06,y-.06,z),
          (x-.16+k*.024,y-.06,z+.11+k*.008),.011,(.63,.53,.25))
    for k in range(5):
        E(screen,'painted detail '+str(i)+' '+str(k),
          (x-.17+.075*k,y-.035,1.98-.07*(k%2)),(.012,.008,.016),(.22,.17,.075))

portrait=A('Oval gilt portrait')
E(portrait,'outer gold frame',(-2.13,3.075,2.31),(.38,.065,.49),gold)
E(portrait,'inner raised rim',(-2.13,2.998,2.31),(.335,.023,.443),(.64,.44,.13))
E(portrait,'dark canvas',(-2.13,2.966,2.31),(.296,.016,.398),(.028,.020,.012))
E(portrait,'painted coat',(-2.13,2.944,2.15),(.17,.01,.18),(.040,.025,.014))
E(portrait,'painted face',(-2.12,2.941,2.39),(.073,.012,.095),(.40,.24,.12))
E(portrait,'painted hair',(-2.14,2.93,2.45),(.071,.008,.041),(.065,.042,.019))
R(portrait,'collar',(-2.18,2.925,2.30),(-2.08,2.925,2.28),.012,(.58,.54,.40))

picture=A('Small back wall photograph')
B(picture,'outer frame',(.43,.06,.57),(.27,3.08,2.57),(.48,.39,.20))
B(picture,'cream mat',(.38,.025,.51),(.27,3.035,2.57),(.77,.74,.62))
B(picture,'gray print',(.23,.015,.36),(.27,3.015,2.57),(.35,.36,.32))
E(picture,'portrait',(.27,2.999,2.59),(.07,.009,.13),(.19,.21,.18))
small=A('Right wall oval picture')
B(small,'gold frame',(.055,.32,.53),(2.73,1.92,2.53),gold)
B(small,'mat',(.025,.28,.48),(2.69,1.92,2.53),(.79,.76,.65))
E(small,'oval print',(2.671,1.92,2.53),(.013,.09,.18),(.34,.34,.30))

cab=A('Left dark console')
B(cab,'top',(.94,.48,.075),(-3.18,2.66,.77),wood)
B(cab,'drawer apron',(.84,.38,.22),(-3.18,2.67,.63),(.075,.036,.016))
for x in [-3.55,-2.81]:
    for y in [2.49,2.83]:
        R(cab,'leg '+str(x)+str(y),(x,y,.07),(x,y,.60),.032,wood)
        E(cab,'turned leg '+str(x)+str(y),(x,y,.27),(.047,.047,.06),wood)
B(cab,'lower stretcher',(.82,.045,.045),(-3.18,2.49,.18),wood)
for j,x in enumerate([-3.45,-3.15]):
    B(cab,'tabletop picture frame '+str(j),(.23,.04,.30),(x,2.75,.97),gold)
    B(cab,'tabletop picture '+str(j),(.18,.018,.24),(x,2.72,.97),(.10,.09,.035))

table=A('Cloth covered table')
B(table,'top',(.72,.56,.055),(-2.15,2.56,.74),wood)
for x in [-2.42,-1.88]:
    for y in [2.34,2.78]:
        R(table,'leg '+str(x)+str(y),(x,y,.10),(x,y,.72),.025,wood)
B(table,'white cloth',(.73,.57,.018),(-2.15,2.56,.782),(.83,.82,.73))
cloth=box((.47,.025,.36),center=(-2.15,2.264,.64),color=(.82,.81,.72))
cloth.turn('y',40)
table.include('hanging cloth corner',cloth)
for j,x in enumerate([-2.35,-2.10,-1.96]):
    E(table,'dish '+str(j),(x,2.55,.811),(.075,.06,.015),(.74,.74,.62))
    E(table,'cup '+str(j),(x,2.55,.847),(.033,.033,.037),(.74,.73,.60))
pot=A('Small floor pot')
E(pot,'terracotta pot',(-2.66,2.80,.16),(.12,.12,.15),(.25,.125,.060))

chair=A('Slender chair behind bed')
cx,cy=1.66,2.18
B(chair,'seat',(.43,.40,.045),(cx,cy,.46),(.075,.044,.019))
for x in [cx-.19,cx+.19]:
    for y in [cy-.16,cy+.16]:
        R(chair,'leg '+str(x)+str(y),(x,y,.035),(x,y,.47),.015,wood)
    R(chair,'back post '+str(x),(x,cy+.16,.44),(x,cy+.16,1.05),.018,wood)
R(chair,'top rail',(cx-.2,cy+.16,1.04),(cx+.2,cy+.16,1.04),.025,wood)
for k in range(4):
    x=cx-.14+k*.095
    R(chair,'spindle '+str(k),(x,cy+.16,.65),(x,cy+.16,1.02),.010,wood)
R(chair,'lower back rail',(cx-.19,cy+.16,.66),(cx+.19,cy+.16,.66),.014,wood)

night=A('Round bedside table')
E(night,'round top',(2.42,-1.04,.58),(.43,.40,.04),wood)
E(night,'lower shelf',(2.42,-1.04,.13),(.36,.34,.035),wood)
for j,(x,y) in enumerate([(2.17,-1.26),(2.68,-1.26),(2.43,-.76)]):
    R(night,'leg '+str(j),(x,y,.12),(x,y,.56),.025,wood)

for idx,(x,y,w,d) in enumerate([(-1.73,1.60,1.18,.72),(.24,-2.0,2.15,.90)]):
    rug=A('Patterned rug '+str(idx))
    B(rug,'red field',(w,d,.012),(x,y,.009),(.30,.065,.038))
    for k,col in enumerate([(.56,.46,.26),(.10,.20,.22),(.58,.49,.30),(.32,.11,.055)]):
        pad=.035+k*.045
        for j,yy in enumerate([y-d/2+pad,y+d/2-pad]):
            B(rug,'long border '+str(k)+str(j),(w-2*pad,.025,.009),(x,yy,.020+k*.001),col)
        for j,xx in enumerate([x-w/2+pad,x+w/2-pad]):
            B(rug,'short border '+str(k)+str(j),(.025,d-2*pad,.009),(xx,y,.020+k*.001),col)
    for j in range(5):
        tile=box((.11,.11,.008),center=(x+(j-2)*w/6,y,.027),color=(.55,.44,.24))
        tile.turn('z',45)
        rug.include('woven diamond '+str(j),tile)

realize(scene)

# Procedural wallpaper uses world coordinates so all wall sections share scale.
for mat in list(bpy.data.materials):
    c=mat.diffuse_color
    if sum(abs(c[i]-wallcol[i]) for i in range(3))<.025:
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get('Principled BSDF')
        coord=nt.nodes.new('ShaderNodeTexCoord')
        noise=nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=48
        noise.inputs['Detail'].default_value=2.4
        noise.inputs['Roughness'].default_value=.73
        nt.links.new(coord.outputs['Object'],noise.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.30
        ramp.color_ramp.elements[0].color=(.075,.095,.080,1)
        ramp.color_ramp.elements[1].position=.67
        ramp.color_ramp.elements[1].color=(.39,.235,.105,1)
        middle=ramp.color_ramp.elements.new(.48)
        middle.color=(.22,.135,.065,1)
        nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.16
        bump.inputs['Distance'].default_value=.012
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
        bs.inputs['Roughness'].default_value=.9
    if c[0]>.80 and c[1]>.93 and c[2]>.94:
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs and 'Emission Color' in bs.inputs:
            bs.inputs['Emission Color'].default_value=(.80,.94,1,1)
            bs.inputs['Emission Strength'].default_value=2.8

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
background.inputs['Color'].default_value=(.62,.69,.76,1)
background.inputs['Strength'].default_value=.10

# Narrower framing, higher image placement, and less ceiling.
set_view((-4.55,-6.50,2.72),(-.38,1.25,1.37),lens=44,sensor=36)
area_emitter((-1.25,2.85,2.07),power=265,size=1.7,
             target=(-.3,-.8,.4),color=(.82,.92,1))
area_emitter((-3.25,2.75,1.9),power=150,size=1.3,
             target=(-1,-1,.3),color=(.88,.95,1))
area_emitter((-1.5,-3,3),power=35,size=4,
             target=(.2,1,.8),color=(1,.88,.72))
sc.camera.data.clip_start=.05
sc.camera.data.clip_end=100
sc.view_settings.view_transform='AgX'
