from sceneact import *
import bpy, math, random

# Reference inventory, approximate normalized image bounds:
# Architecture: ochre floral walls, pale floor below .62, narrow white cornice.
# Two windows (-.03,.06,.13,.60), (.23,.07,.44,.60), green upper blinds,
# broad white jambs and bright lower panes. Back/right corner near (.57,.06).
# Oval gilt portrait (.13,.16,.25,.36), rectangular portrait (.47,.15,.54,.28),
# small right-wall oval (.66,.16,.71,.30); narrow door partly hidden by screen.
# Bed (.51,.47,.99,.97): dark sleigh frame, cream bedding, two large pillows.
# Olive chair (.28,.50,.54,.94): oblique silhouette, broad seat, tall curved arms,
# tufted back, short exposed legs; overlaps bed foot and painted screen.
# Blue/gold folding screen (.41,.33,.62,.67), left chest and small framed picture,
# lace table with cups, wastebasket, black spindle chair, round bedside cabinet.
# Small rug behind chair and foreground rug cropped along bottom.
# Hidden backs and exact painted motifs remain uncertain.
#
# Feedback comparison: first view exposed too much ceiling, undersized foreground
# furniture, misplaced frontal chair, and overly bright lighting. Preserve the
# asset hierarchy while lowering framing, moving the camera closer, moving and
# turning the chair, and softening illumination.
# Estimated expanded primitives: approximately 330 meshes:
# architecture/windows 40; portraits 70; screen 45; bed/chair 60;
# other furniture 65; carpets 50. No booleans or fillet expansions.

random.seed(13)
scene = Scene('Historic bedroom')
C = {
    'wood': (.055,.025,.016),
    'woodlight': (.13,.061,.031),
    'trim': (.88,.89,.85),
    'linen': (.77,.77,.67),
    'olive': (.25,.26,.047),
    'gold': (.55,.34,.08),
    'wall': (.43,.29,.16)
}

def asset(name):
    a=Asset(name)
    scene.include(name,a)
    return a

def bx(a,n,s,p,c):
    v=box(s,center=p,color=c)
    a.include(n,v)
    return v

def ell(a,n,p,s,c):
    v=ball(1,center=p,color=c)
    v.resize(s)
    a.include(n,v)
    return v

def rd(a,n,p,q,r,c):
    v=rod(r,start=p,end=q,color=c)
    a.include(n,v)
    return v

def oval(a,n,x,y,z,rx,rz,r,c):
    count=24
    pts=[(x+rx*math.cos(2*math.pi*i/count),y,
          z+rz*math.sin(2*math.pi*i/count)) for i in range(count+1)]
    for i in range(count):
        rd(a,n+str(i),pts[i],pts[i+1],r,c)

room=asset('architecture')
bx(room,'stone_floor',(8,10,.12),(0,0,-.08),(.51,.50,.44))
bx(room,'back_wall',(7,.16,3.45),(-.2,3.50,1.71),C['wall'])
bx(room,'right_wall',(.16,9,3.45),(3.22,-.90,1.71),C['wall'])
bx(room,'ceiling',(7.2,9,.12),(-.25,-.8,3.49),(.83,.84,.81))
for z,depth,height in [(3.29,.15,.08),(3.37,.23,.09),(3.43,.30,.06)]:
    bx(room,'back_cornice_'+str(z),(7,depth,height),(-.2,3.37,z),C['trim'])
    bx(room,'right_cornice_'+str(z),(depth,9,height),(3.08,-.8,z),C['trim'])
bx(room,'back_skirt',(7,.10,.16),(-.2,3.36,.08),(.25,.17,.11))
bx(room,'right_skirt',(.10,9,.16),(3.09,-.8,.08),(.25,.17,.11))

for k,x in enumerate([-3.03,-.97]):
    w=1.29 if k==0 else 1.35
    a=asset('window_'+str(k))
    bx(a,'recess',(w+.15,.10,2.61),(x,3.37,1.85),(.14,.19,.16))
    bx(a,'glazing',(w-.11,.045,2.37),(x,3.29,1.87),(.77,.91,.89))
    for j,xx in enumerate([x-w/2,x+w/2]):
        bx(a,'jamb_'+str(j),(.105,.22,2.66),(xx,3.23,1.86),C['trim'])
        bx(a,'molding_'+str(j),(.035,.25,2.78),
           (xx+(-.085 if xx<x else .085),3.24,1.86),(.72,.74,.71))
    for j,zz in enumerate([.54,3.16]):
        bx(a,'cross_frame_'+str(j),(w+.13,.25,.11),(x,3.22,zz),C['trim'])
    bx(a,'sill',(w+.23,.37,.09),(x,3.15,.53),C['trim'])
    bx(a,'green_roller_blind',(w-.17,.035,1.42),(x,3.16,2.36),(.105,.28,.24))
    bx(a,'blind_hem',(w-.15,.045,.025),(x,3.135,1.65),(.27,.42,.35))

a=asset('large_oval_portrait')
ell(a,'black_oval',(-2.02,3.20,2.38),(.39,.035,.51),(.025,.018,.012))
oval(a,'outer_gilt_',-2.02,3.145,2.38,.42,.54,.027,C['gold'])
oval(a,'inner_gilt_',-2.02,3.12,2.38,.365,.475,.012,(.76,.55,.22))
ell(a,'coat',(-2.02,3.10,2.20),(.21,.012,.22),(.035,.025,.020))
ell(a,'face',(-2.03,3.08,2.48),(.075,.013,.11),(.45,.28,.16))
ell(a,'hair',(-2.05,3.07,2.56),(.08,.014,.05),(.065,.035,.020))
bx(a,'collar',(.075,.018,.045),(-2.00,3.075,2.37),(.65,.60,.48))

a=asset('small_back_portrait')
bx(a,'gilt_frame',(.50,.08,.66),(.64,3.24,2.69),(.62,.49,.24))
bx(a,'ivory_mat',(.44,.035,.60),(.64,3.18,2.69),(.81,.79,.67))
ell(a,'gray_picture',(.64,3.15,2.69),(.145,.015,.225),(.36,.36,.32))
ell(a,'head',(.64,3.125,2.76),(.055,.012,.075),(.58,.56,.48))

a=asset('right_wall_miniature')
bx(a,'frame',(.065,.37,.60),(3.08,2.15,2.63),(.68,.51,.23))
bx(a,'mat',(.025,.32,.54),(3.035,2.15,2.63),(.85,.83,.73))
ell(a,'oval_image',(3.015,2.15,2.63),(.014,.10,.20),(.42,.39,.34))

a=asset('back_door')
bx(a,'door_surround',(.67,.13,2.30),(1.56,3.27,1.22),C['trim'])
bx(a,'door_leaf',(.55,.04,2.15),(1.56,3.18,1.20),(.76,.79,.74))
for z in [.64,1.66]:
    bx(a,'panel_'+str(z),(.43,.025,.80),(1.56,3.145,z),(.82,.84,.79))

a=asset('left_chest')
bx(a,'body',(1.03,.51,.65),(-3.12,2.73,.37),C['wood'])
bx(a,'top',(1.12,.60,.065),(-3.12,2.73,.73),C['woodlight'])
for x in [-3.55,-2.69]:
    for y in [2.52,2.95]:
        rd(a,'leg_'+str((x,y)),(x,y,.02),(x,y,.28),.047,C['wood'])
for z in [.27,.49]:
    bx(a,'drawer_'+str(z),(.94,.025,.18),(-3.12,2.46,z),(.105,.048,.023))
    for x in [-3.37,-2.87]:
        ell(a,'knob_'+str((z,x)),(x,2.425,z),(.025,.025,.025),C['gold'])
bx(a,'picture_frame',(.29,.055,.35),(-3.23,2.70,.94),C['gold'])
bx(a,'picture',(.24,.025,.30),(-3.23,2.66,.94),(.10,.13,.085))

a=asset('small_lace_table')
bx(a,'top',(.74,.52,.055),(-1.91,2.74,.73),C['wood'])
for x in [-2.19,-1.63]:
    for y in [2.56,2.91]:
        rd(a,'leg_'+str((x,y)),(x,y,.05),(x,y,.72),.025,C['wood'])
bx(a,'linen_top',(.77,.55,.015),(-1.91,2.72,.77),(.83,.81,.71))
# The apron tapers to the pointed hanging cloth seen in the photograph.
for j,(w,z,h) in enumerate([(.63,.695,.13),(.46,.585,.10),(.24,.505,.07)]):
    bx(a,'hanging_lace_'+str(j),(w,.025,h),(-1.91,2.425,z),(.80,.79,.69))
for x in [-2.08,-1.78]:
    ell(a,'teacup_'+str(x),(x,2.70,.805),(.065,.055,.035),(.78,.73,.55))
    ell(a,'saucer_'+str(x),(x,2.70,.78),(.085,.075,.008),(.88,.83,.66))
a=asset('wastebasket')
bx(a,'basket',(.24,.23,.30),(-2.47,2.65,.15),(.31,.19,.10))

a=asset('painted_folding_screen')
for i,(x,y,ang) in enumerate([(-.12,2.52,-7),(.47,2.55,6),(1.05,2.50,-5)]):
    p=Asset('panel_'+str(i))
    bx(p,'gold_field',(.61,.065,1.68),(x,y,1.28),(.49,.36,.16))
    for j,xx in enumerate([x-.30,x+.30]):
        bx(p,'edge_'+str(j),(.025,.085,1.72),(xx,y-.012,1.28),(.12,.095,.04))
    # Flat blue sweeps and ochre figures are separate painted surface parts.
    for j in range(3):
        z=.72+j*.47
        ex=x+random.uniform(-.14,.14)
        motif=ell(p,'blue_sweep_'+str(j),(ex,y-.049,z),(.28,.010,.16),(.018,.045,.38))
        motif.turn('y',(-1 if j%2 else 1)*22)
    ell(p,'figure_head',(x+.12,y-.070,1.59),(.065,.009,.09),(.57,.37,.15))
    rd(p,'figure_body',(x+.12,y-.072,1.51),(x-.04,y-.072,1.08),.046,(.64,.35,.12))
    rd(p,'figure_arm',(x+.04,y-.075,1.37),(x-.19,y-.075,1.45),.022,(.71,.46,.20))
    for j in range(3):
        ell(p,'gold_leaf_'+str(j),(x-.16+j*.13,y-.075,.95+j*.10),
            (.07,.009,.035),(.71,.50,.20))
    p.turn('z',ang)
    a.include('panel_'+str(i),p)

a=asset('dark_sleigh_bed')
bedx,bedy=1.66,.25
bed_width=1.98
bx(a,'base',(2.69,bed_width,.34),(bedx,bedy,.35),C['wood'])
bx(a,'front_rail',(2.74,.105,.31),(bedx,bedy-bed_width/2,.42),(.075,.031,.020))
for x in [.33,2.98]:
    for y in [bedy-.90,bedy+.90]:
        bx(a,'foot_'+str((x,y)),(.13,.14,.29),(x,y,.145),C['wood'])
bx(a,'headboard',(.13,2.06,.87),(3.00,bedy,.99),C['wood'])
rd(a,'head_crest',(2.98,bedy-1.04,1.44),(2.98,bedy+1.04,1.44),.060,C['wood'])
for y in [bedy-1.04,bedy+1.04]:
    rd(a,'head_post_'+str(y),(2.97,y,.25),(2.97,y,1.49),.055,C['wood'])
bx(a,'footboard',(.13,2.02,.69),(.32,bedy,.73),C['wood'])
rd(a,'foot_crest',(.31,bedy-1.02,1.09),(.31,bedy+1.02,1.09),.065,C['wood'])
for y in [bedy-1.02,bedy+1.02]:
    ell(a,'foot_finial_'+str(y),(.31,y,1.13),(.075,.075,.095),C['wood'])
ell(a,'mattress',(1.68,bedy,.67),(1.28,.94,.20),(.73,.73,.64))
# A rectangular core keeps bedding broad instead of a narrow oval island.
bx(a,'covered_mattress',(2.37,1.83,.17),(1.66,bedy,.75),(.76,.76,.66))
ell(a,'cream_duvet',(1.48,bedy-.02,.84),(1.14,.93,.15),(.77,.77,.67))
for i in range(6):
    x=.73+i*.28
    fold=ell(a,'cover_fold_'+str(i),
             (x,bedy-.28+random.uniform(-.16,.16),.955),
             (.25,.61,.024),(.75+i*.004,.75+i*.004,.65))
    fold.turn('z',random.uniform(-15,15))
for j,y in enumerate([bedy+.48,bedy-.42]):
    # Fuller pillows with a sloping upper plane.
    p=ell(a,'pillow_'+str(j),(2.49,y,1.10),(.44,.44,.19),(.85,.85,.76))
    p.turn('y',-27)
    p.turn('z',-5+j*10)

a=asset('olive_armchair')
cx,cy=-1.45,-.30
for x in [cx-.45,cx+.45]:
    for y in [cy-.40,cy+.40]:
        rd(a,'leg_'+str((x,y)),(x,y,.04),(x,y,.35),.038,C['wood'])
ell(a,'seat',(cx,cy,.49),(.59,.54,.17),(.29,.29,.057))
back=ell(a,'rounded_back',(cx,cy+.37,.94),(.56,.15,.57),C['olive'])
back.turn('x',-9)
for s in [-1,1]:
    ell(a,'padded_side_'+str(s),(cx+s*.49,cy,.67),(.14,.54,.35),(.22,.23,.038))
    rd(a,'arm_roll_'+str(s),(cx+s*.49,cy-.43,.82),
       (cx+s*.49,cy+.35,1.02),.064,(.31,.31,.070))
for i in [-1,0,1]:
    channel=ell(a,'back_channel_'+str(i),(cx+i*.20,cy+.205,1.00),
                (.072,.024,.31),(.29,.30,.060))
    channel.turn('y',i*12)
for i in [-1,1]:
    for z in [.88,1.13]:
        ell(a,'tuft_'+str((i,z)),(cx+i*.19,cy+.17,z),
            (.024,.017,.024),(.16,.18,.025))
a.turn('z',43)

a=asset('black_spindle_chair')
x,y=2.03,2.14
bx(a,'seat',(.49,.44,.055),(x,y,.49),(.045,.033,.019))
for xx in [x-.20,x+.20]:
    for yy in [y-.17,y+.17]:
        rd(a,'leg_'+str((xx,yy)),(xx,yy,.02),(xx,yy,.50),.024,C['wood'])
for xx in [x-.22,x+.22]:
    rd(a,'backpost_'+str(xx),(xx,y+.18,.45),(xx,y+.18,1.10),.025,(.025,.019,.014))
rd(a,'toprail',(x-.23,y+.18,1.10),(x+.23,y+.18,1.10),.032,C['wood'])
for i in range(4):
    xx=x-.15+i*.10
    rd(a,'spindle_'+str(i),(xx,y+.18,.58),(xx,y+.18,1.07),.012,C['wood'])

a=asset('round_bedside_cabinet')
ell(a,'round_body',(3.00,-1.05,.36),(.40,.40,.36),C['wood'])
ell(a,'top',(3.00,-1.05,.72),(.43,.43,.035),(.085,.039,.023))
for z in [.19,.43]:
    for i in range(6):
        t0=math.pi+i*math.pi/6
        t1=math.pi+(i+1)*math.pi/6
        rd(a,'seam_'+str((z,i)),
           (3+.398*math.cos(t0),-1.05+.398*math.sin(t0),z),
           (3+.398*math.cos(t1),-1.05+.398*math.sin(t1),z),
           .005,(.18,.11,.060))

def rug(name,cx,cy,w,h):
    a=asset(name)
    bx(a,'red_field',(w,h,.018),(cx,cy,.016),(.29,.085,.055))
    for inset,col,th in [(.045,(.61,.54,.37),.04),
                         (.11,(.13,.20,.22),.045),
                         (.19,(.61,.42,.24),.035)]:
        bx(a,'left_'+str(inset),(th,h-2*inset,.022),(cx-w/2+inset,cy,.03),col)
        bx(a,'right_'+str(inset),(th,h-2*inset,.022),(cx+w/2-inset,cy,.03),col)
        bx(a,'near_'+str(inset),(w-2*inset,th,.022),(cx,cy-h/2+inset,.03),col)
        bx(a,'far_'+str(inset),(w-2*inset,th,.022),(cx,cy+h/2-inset,.03),col)
    for j in range(7):
        xx=cx-w*.37+j*w*.123
        for sy in [-1,1]:
            v=bx(a,'border_motif_'+str((j,sy)),(.065,.065,.025),
                 (xx,cy+sy*h*.35,.035),(.64,.50,.30))
            v.turn('z',45)
    return a

rug('back_small_carpet',-1.30,1.30,1.60,1.02)
rug('foreground_carpet',1.42,-1.95,2.38,1.02)

realize(scene)

for mat in bpy.data.materials:
    col=mat.diffuse_color
    if abs(col[0]-.43)<.015 and abs(col[1]-.29)<.015:
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get('Principled BSDF')
        coord=nt.nodes.new('ShaderNodeTexCoord')
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=35
        tex.inputs['Detail'].default_value=2
        tex.inputs['Roughness'].default_value=.72
        nt.links.new(coord.outputs['Object'],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.29
        ramp.color_ramp.elements[0].color=(.13,.16,.115,1)
        ramp.color_ramp.elements[1].position=.72
        ramp.color_ramp.elements[1].color=(.43,.30,.18,1)
        e=ramp.color_ramp.elements.new(.46)
        e.color=(.24,.18,.12,1)
        e=ramp.color_ramp.elements.new(.56)
        e.color=(.36,.25,.16,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=.95
    if col[0]>.74 and col[1]>.88 and col[2]>.85:
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if 'Emission Color' in bs.inputs:
            bs.inputs['Emission Color'].default_value=(.72,.90,.93,1)
            bs.inputs['Emission Strength'].default_value=2.2

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
background.inputs['Color'].default_value=(.58,.65,.70,1)
background.inputs['Strength'].default_value=.16

set_view((-3.65,-5.80,2.65),(-.05,1.40,1.16),lens=39,sensor=36)
area_emitter((-1.8,2.92,2.25),power=330,size=2.1,
             target=(.3,-.5,.5),color=(.85,.94,1))
area_emitter((-3.2,1.0,3.1),power=65,size=3,
             target=(1,1,1),color=(1,.91,.77))
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.10
# Rendering and saving are handled by the fixed runtime.
